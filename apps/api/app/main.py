import secrets
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import select, text, update
from sqlalchemy.orm import Session
from PIL import Image
from .auth import current_member, digest, owner
from .config import get_settings
from .db import SessionLocal, get_db
from .models import Audit, Campaign, Creative, Member, Product, Proposal, Recommendation, SessionToken, Tenant
from .schemas import (
    ApplyOut,
    AuditOut,
    CreativeOut,
    DashboardOut,
    DecisionIn,
    LoginIn,
    ProductIn,
    ProductOut,
    ProposalIn,
    ProposalOut,
    RecommendationOut,
    RulesIn,
)
from .seed import seed
from .strategy import analyze, build_plan, evaluate

settings = get_settings()


@asynccontextmanager
async def lifespan(app):
    with SessionLocal() as db:
        seed(db)
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title="Meta Ads AI · Demo API",
    version="0.1.0",
    lifespan=lifespan,
    description="Simulación local: ninguna operación contacta Meta ni genera gasto.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_methods=["GET", "POST", "PUT"],
    allow_headers=["Authorization", "Content-Type"],
)


def row(obj):
    return {column.name: getattr(obj, column.name) for column in obj.__table__.columns if column.name not in ("storage_key", "token_hash")}


def scoped(db, model, member):
    return select(model).where(model.tenant_id == member.tenant_id)


def get_owned(db, model, entity_id, member, lock=False):
    query = scoped(db, model, member).where(model.id == entity_id)
    obj = db.scalar(query.with_for_update() if lock else query)
    if not obj:
        raise HTTPException(404, "Recurso no encontrado")
    return obj


def tenant_for(db, member, lock=False):
    query = select(Tenant).where(Tenant.id == member.tenant_id)
    return db.scalar(query.with_for_update() if lock else query)


def log(db, member, action, entity_id, detail=None):
    db.add(Audit(tenant_id=member.tenant_id, actor_id=member.id, action=action, entity_id=entity_id, detail=detail or {}))


@app.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok", "mode": "demo", "meta_connected": False}


@app.post("/api/auth/demo")
def login(payload: LoginIn, db: Session = Depends(get_db)):
    tenant = db.scalar(select(Tenant).where(Tenant.slug == payload.tenant))
    if not tenant:
        raise HTTPException(503, "Ejecutar migraciones y seed")
    member = db.scalar(select(Member).where(Member.tenant_id == tenant.id, Member.role == payload.role))
    token = secrets.token_urlsafe(48)
    expires = datetime.now(timezone.utc) + timedelta(hours=settings.session_ttl_hours)
    db.add(SessionToken(token_hash=digest(token), member_id=member.id, expires_at=expires.isoformat()))
    db.commit()
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_at": expires.isoformat(),
        "tenant": row(tenant),
        "member": row(member),
        "mode": "demo",
    }


@app.post("/api/auth/logout")
def logout(member: Member = Depends(current_member), db: Session = Depends(get_db)):
    # Revocación de todas las sesiones del miembro de demo, deliberadamente compartido.
    for session in db.scalars(select(SessionToken).where(SessionToken.member_id == member.id)):
        db.delete(session)
    db.commit()
    return {"revoked": True}


@app.get("/api/me")
def me(member: Member = Depends(current_member), db: Session = Depends(get_db)):
    return {"tenant": row(tenant_for(db, member)), "member": row(member), "mode": "demo"}


@app.get("/api/dashboard", response_model=DashboardOut)
def dashboard(member: Member = Depends(current_member), db: Session = Depends(get_db)):
    campaigns = list(db.scalars(scoped(db, Campaign, member).order_by(Campaign.created_at, Campaign.id)))
    spend = sum(c.spend_minor for c in campaigns)
    revenue = sum(c.revenue_minor for c in campaigns)
    purchases = sum(c.purchases for c in campaigns)
    return {
        "period": "7 días · datos ficticios fijos",
        "currency": tenant_for(db, member).currency,
        "spend_minor": spend,
        "revenue_minor": revenue,
        "purchases": purchases,
        "roas": round(revenue / spend, 2) if spend else None,
        "cpa_minor": round(spend / purchases) if purchases else None,
        "active_daily_budget_minor": sum(c.daily_budget_minor for c in campaigns if c.status == "active"),
        "campaigns": [row(c) for c in campaigns],
        "source": "demo-seed",
    }


@app.get("/api/products", response_model=list[ProductOut])
def products(member: Member = Depends(current_member), db: Session = Depends(get_db)):
    return [row(p) for p in db.scalars(scoped(db, Product, member).order_by(Product.created_at, Product.id))]


@app.post("/api/products", status_code=201, response_model=ProductOut)
def create_product(payload: ProductIn, member: Member = Depends(owner), db: Session = Depends(get_db)):
    product = Product(tenant_id=member.tenant_id, **payload.model_dump())
    db.add(product)
    db.flush()
    log(db, member, "product.created", product.id)
    db.commit()
    return row(product)


@app.put("/api/products/{entity_id}", response_model=ProductOut)
def edit_product(entity_id: str, payload: ProductIn, member: Member = Depends(owner), db: Session = Depends(get_db)):
    product = get_owned(db, Product, entity_id, member)
    for key, value in payload.model_dump().items():
        setattr(product, key, value)
    log(db, member, "product.updated", product.id)
    db.commit()
    return row(product)


@app.get("/api/creatives", response_model=list[CreativeOut])
def creatives(member: Member = Depends(current_member), db: Session = Depends(get_db)):
    return [
        row(c) | {"has_file": bool(c.storage_key)}
        for c in db.scalars(scoped(db, Creative, member).order_by(Creative.created_at, Creative.id))
    ]


@app.post("/api/creatives/upload", status_code=201, response_model=CreativeOut)
async def upload(
    product_id: str = Form(...),
    ad_copy: str = Form("", alias="copy", max_length=4000),
    file: UploadFile = File(...),
    member: Member = Depends(owner),
    db: Session = Depends(get_db),
):
    get_owned(db, Product, product_id, member)
    data = await file.read(25 * 1024 * 1024 + 1)
    await file.close()
    if len(data) > 25 * 1024 * 1024:
        raise HTTPException(413, "Máximo 25 MiB por archivo")
    try:
        analysis = analyze(data, ad_copy)
    except (ValueError, OSError, Image.DecompressionBombError):
        # Errores de decodificación son entrada inválida, nunca se devuelven rutas internas.
        raise HTTPException(422, "Archivo inválido; usar JPEG, PNG, WEBP, MP4 o WEBM válidos.") from None
    key = str(uuid4())
    destination = Path(settings.upload_dir) / member.tenant_id / key
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    creative = Creative(
        tenant_id=member.tenant_id,
        product_id=product_id,
        name=(file.filename or "Anuncio")[:160],
        kind=analysis["kind"],
        mime=analysis["mime"],
        storage_key=key,
        copy=ad_copy,
        analysis=analysis,
    )
    try:
        db.add(creative)
        db.flush()
        log(db, member, "creative.uploaded", creative.id, {"bytes": len(data), "kind": creative.kind})
        db.commit()
    except Exception:
        db.rollback()
        destination.unlink(missing_ok=True)
        raise
    return row(creative) | {"has_file": True}


@app.get("/api/creatives/{entity_id}/file")
def creative_file(entity_id: str, member: Member = Depends(current_member), db: Session = Depends(get_db)):
    creative = get_owned(db, Creative, entity_id, member)
    if not creative.storage_key:
        raise HTTPException(404, "Ficha de muestra sin archivo")
    path = Path(settings.upload_dir) / member.tenant_id / creative.storage_key
    if not path.is_file():
        raise HTTPException(404, "Archivo no disponible")
    return FileResponse(
        path,
        media_type=creative.mime,
        headers={"Cache-Control": "private, no-store", "X-Content-Type-Options": "nosniff", "Content-Disposition": "attachment"},
    )


@app.get("/api/proposals", response_model=list[ProposalOut])
def proposals(member: Member = Depends(current_member), db: Session = Depends(get_db)):
    return [row(p) for p in db.scalars(scoped(db, Proposal, member).order_by(Proposal.created_at.desc(), Proposal.id))]


@app.post("/api/proposals", status_code=201, response_model=ProposalOut)
def create_proposal(payload: ProposalIn, member: Member = Depends(owner), db: Session = Depends(get_db)):
    tenant = tenant_for(db, member)
    if payload.daily_budget_minor > tenant.max_daily_minor:
        raise HTTPException(422, "El presupuesto supera el límite diario de la empresa")
    product = get_owned(db, Product, payload.product_id, member)
    selected = [get_owned(db, Creative, creative_id, member) for creative_id in payload.creative_ids]
    if any(c.product_id != product.id for c in selected):
        raise HTTPException(422, "Todos los anuncios deben pertenecer al producto elegido")
    plan = build_plan(payload, selected, product, tenant)
    proposal = Proposal(tenant_id=member.tenant_id, title=f"{product.name} · {plan['strategy']}", plan=plan)
    db.add(proposal)
    db.flush()
    log(db, member, "proposal.created", proposal.id)
    db.commit()
    return row(proposal)


@app.post("/api/proposals/{entity_id}/decision", response_model=ProposalOut)
def decide_proposal(entity_id: str, payload: DecisionIn, member: Member = Depends(owner), db: Session = Depends(get_db)):
    proposal = get_owned(db, Proposal, entity_id, member, lock=True)
    if proposal.status != "pending":
        raise HTTPException(409, "La propuesta ya fue revisada")
    proposal.status = "approved" if payload.decision == "approve" else "rejected"
    log(db, member, f"proposal.{proposal.status}", proposal.id, {"published": False})
    db.commit()
    return row(proposal)


@app.get("/api/rules")
def rules(member: Member = Depends(current_member), db: Session = Depends(get_db)):
    tenant = tenant_for(db, member)
    return {
        "max_daily_minor": tenant.max_daily_minor,
        "max_increase_pct": tenant.max_increase_pct,
        "min_days": 3,
        "min_purchases_scale": 10,
        "min_roas_scale": 3,
        "mode": "supervised-demo",
    }


@app.put("/api/rules")
def save_rules(payload: RulesIn, member: Member = Depends(owner), db: Session = Depends(get_db)):
    tenant = tenant_for(db, member, lock=True)
    total = sum(c.daily_budget_minor for c in db.scalars(scoped(db, Campaign, member).where(Campaign.status == "active")))
    if total > payload.max_daily_minor:
        raise HTTPException(422, "El límite no puede quedar por debajo del presupuesto activo simulado")
    tenant.max_daily_minor = payload.max_daily_minor
    tenant.max_increase_pct = payload.max_increase_pct
    # Las aprobaciones pertenecen a una versión de las reglas. Se exige revisión nueva.
    for recommendation in db.scalars(scoped(db, Recommendation, member).where(Recommendation.status.in_(["pending", "approved"]))):
        recommendation.status = "rejected"
        log(db, member, "recommendation.invalidated_by_rules", recommendation.id)
    for campaign in db.scalars(scoped(db, Campaign, member).where(Campaign.status == "active")):
        campaign.revision += 1
    log(db, member, "rules.updated", tenant.id, payload.model_dump())
    db.commit()
    return rules(member, db)


@app.get("/api/recommendations", response_model=list[RecommendationOut])
def recommendations(member: Member = Depends(current_member), db: Session = Depends(get_db)):
    return [row(r) for r in db.scalars(scoped(db, Recommendation, member).order_by(Recommendation.created_at.desc(), Recommendation.id))]


@app.post("/api/optimization/evaluate", response_model=list[RecommendationOut])
def run_evaluation(member: Member = Depends(owner), db: Session = Depends(get_db)):
    tenant = tenant_for(db, member, lock=True)
    for campaign in db.scalars(scoped(db, Campaign, member)):
        found = db.scalar(
            scoped(db, Recommendation, member).where(
                Recommendation.campaign_id == campaign.id, Recommendation.campaign_revision == campaign.revision
            )
        )
        result = evaluate(campaign, tenant)
        if result and not found:
            db.add(Recommendation(tenant_id=member.tenant_id, campaign_id=campaign.id, campaign_revision=campaign.revision, **result))
    log(db, member, "optimization.evaluated", tenant.id)
    db.commit()
    return recommendations(member, db)


@app.post("/api/recommendations/{entity_id}/decision", response_model=RecommendationOut)
def decide_recommendation(entity_id: str, payload: DecisionIn, member: Member = Depends(owner), db: Session = Depends(get_db)):
    tenant_for(db, member, lock=True)
    recommendation = get_owned(db, Recommendation, entity_id, member, lock=True)
    if recommendation.status != "pending":
        raise HTTPException(409, "La recomendación ya fue revisada")
    recommendation.status = "approved" if payload.decision == "approve" else "rejected"
    log(db, member, f"recommendation.{recommendation.status}", entity_id)
    db.commit()
    return row(recommendation)


@app.post("/api/recommendations/{entity_id}/apply", response_model=ApplyOut)
def apply_recommendation(entity_id: str, member: Member = Depends(owner), db: Session = Depends(get_db)):
    tenant = tenant_for(db, member, lock=True)
    recommendation = get_owned(db, Recommendation, entity_id, member, lock=True)
    campaign = get_owned(db, Campaign, recommendation.campaign_id, member, lock=True)
    if recommendation.status == "applied":
        return {"recommendation": row(recommendation), "campaign": row(campaign), "simulated": True}
    if recommendation.status != "approved":
        raise HTTPException(409, "Aprobar antes de aplicar la simulación")
    if campaign.revision != recommendation.campaign_revision or campaign.status != "active":
        raise HTTPException(409, "La campaña cambió. Volver a evaluar antes de aprobar cambios")
    before_budget = campaign.daily_budget_minor
    new_budget = before_budget
    if recommendation.action == "increase_budget":
        new_budget = recommendation.suggested_budget_minor
        if new_budget > campaign.daily_budget_minor * (100 + tenant.max_increase_pct) // 100:
            raise HTTPException(409, "Las reglas cambiaron. Rechazar la recomendación anterior")
        total = sum(c.daily_budget_minor for c in db.scalars(scoped(db, Campaign, member).where(Campaign.status == "active")))
        if total - campaign.daily_budget_minor + new_budget > tenant.max_daily_minor:
            raise HTTPException(409, "El aumento supera el límite agregado de la empresa")
    # Compare-and-swap protege también frente a revisiones concurrentes.
    changed = db.execute(
        update(Campaign)
        .where(Campaign.id == campaign.id, Campaign.tenant_id == member.tenant_id, Campaign.revision == recommendation.campaign_revision)
        .values(
            daily_budget_minor=new_budget,
            status="paused" if recommendation.action == "pause" else campaign.status,
            revision=Campaign.revision + 1,
        )
    )
    if changed.rowcount != 1:
        raise HTTPException(409, "La campaña cambió durante la revisión")
    recommendation.status = "applied"
    log(
        db,
        member,
        "recommendation.simulated",
        recommendation.id,
        {"before_budget_minor": before_budget, "after_budget_minor": new_budget, "external_write": False},
    )
    db.commit()
    db.refresh(campaign)
    return {"recommendation": row(recommendation), "campaign": row(campaign), "simulated": True}


@app.get("/api/audit", response_model=list[AuditOut])
def audit(member: Member = Depends(current_member), db: Session = Depends(get_db)):
    return [row(a) for a in db.scalars(scoped(db, Audit, member).order_by(Audit.created_at.desc()).limit(100))]


@app.get("/api/integrations/meta")
def integration(member: Member = Depends(current_member)):
    return {
        "connected": False,
        "mode": "demo",
        "oauth_available": False,
        "publishing_enabled": False,
        "message": "OAuth y Marketing API pendientes. No se han solicitado credenciales ni sincronizado cuentas.",
    }


@app.post("/api/integrations/meta/connect", status_code=501)
def meta_connect(member: Member = Depends(owner)):
    return {"detail": "OAuth de Meta no implementado; revisar docs/META_API.md"}


@app.post("/api/proposals/{entity_id}/publish", status_code=403)
def publish(entity_id: str, member: Member = Depends(owner), db: Session = Depends(get_db)):
    get_owned(db, Proposal, entity_id, member)
    return {"detail": "Publicación real bloqueada. El demo no contacta Meta ni gasta presupuesto."}
