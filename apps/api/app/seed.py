from sqlalchemy import select
from .db import SessionLocal
from .models import Campaign, Creative, Member, Product, Tenant


def seed(db):
    for slug, name in [("cristal-demo", "Cristal · Demo"), ("norte-demo", "Norte · Demo")]:
        if db.scalar(select(Tenant).where(Tenant.slug == slug)):
            continue
        tenant = Tenant(slug=slug, name=name, max_daily_minor=500000, max_increase_pct=20)
        db.add(tenant)
        db.flush()
        db.add_all([Member(tenant_id=tenant.id, name=f"{role} de demo", role=role) for role in ["owner", "viewer"]])
        product = Product(
            tenant_id=tenant.id,
            name="Olla de vidrio" if slug == "cristal-demo" else "Botella térmica",
            description="Producto ficticio para explorar el flujo del SaaS.",
            price_minor=249000,
            margin_pct=45,
        )
        db.add(product)
        db.flush()
        for index in range(6):
            kind = "image" if index < 3 else "video"
            db.add(
                Creative(
                    tenant_id=tenant.id,
                    product_id=product.id,
                    name=f"{'Imagen' if kind == 'image' else 'Video'} de ejemplo {index % 3 + 1}",
                    kind=kind,
                    mime="image/svg+xml" if kind == "image" else "video/mp4",
                    copy="Descubrí una forma distinta de disfrutar tu cocina.",
                    analysis={
                        "engine": "seed-demo",
                        "notes": [
                            "Ficha de muestra; no contiene un archivo subido.",
                            "Probar demostración, beneficio y comparación de aperturas.",
                        ],
                        "width": 1080 if kind == "image" else None,
                        "height": 1350 if kind == "image" else None,
                    },
                )
            )
        for values in [
            dict(
                name="Ventas · Descubrimiento",
                daily_budget_minor=100000,
                spend_minor=700000,
                revenue_minor=3010000,
                purchases=18,
                impressions=42000,
                clicks=1050,
            ),
            dict(
                name="Test · Nuevos ángulos",
                daily_budget_minor=50000,
                spend_minor=350000,
                revenue_minor=0,
                purchases=0,
                impressions=25000,
                clicks=210,
            ),
            dict(
                name="Retorno · Catálogo",
                daily_budget_minor=35000,
                spend_minor=245000,
                revenue_minor=550000,
                purchases=4,
                impressions=12000,
                clicks=360,
            ),
        ]:
            db.add(Campaign(tenant_id=tenant.id, **values))
    db.commit()


if __name__ == "__main__":
    with SessionLocal() as session:
        seed(session)
