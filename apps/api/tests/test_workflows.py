import io
import os
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import pytest
from PIL import Image
from sqlalchemy.exc import IntegrityError
from app.auth import digest
from app.models import Creative, SessionToken


def proposal_payload(client, headers, budget=100000):
    product = client.get("/api/products", headers=headers).json()[0]
    ads = client.get("/api/creatives", headers=headers).json()
    return {"product_id": product["id"], "creative_ids": [a["id"] for a in ads], "daily_budget_minor": budget, "target_cpa_minor": 25000}


def recommendations(client, headers):
    response = client.post("/api/optimization/evaluate", headers=headers)
    assert response.status_code == 200
    return response.json()


def test_health_and_no_meta(client):
    assert client.get("/health").json() == {"status": "ok", "mode": "demo", "meta_connected": False}


@pytest.mark.parametrize(
    "path",
    [
        "/api/products",
        "/api/creatives",
        "/api/dashboard",
        "/api/proposals",
        "/api/rules",
        "/api/recommendations",
        "/api/audit",
        "/api/integrations/meta",
        "/api/me",
    ],
)
def test_reads_require_session(client, path):
    assert client.get(path).status_code == 401
    assert client.get(path, headers={"Authorization": "Bearer invalid"}).status_code == 401


def test_tenant_separation(client, owner_headers, other_headers):
    first = client.get("/api/products", headers=owner_headers).json()
    second = client.get("/api/products", headers=other_headers).json()
    assert {p["id"] for p in first}.isdisjoint(p["id"] for p in second)
    payload = proposal_payload(client, owner_headers)
    assert client.post("/api/proposals", headers=other_headers, json=payload).status_code == 404
    response = client.put(f"/api/products/{first[0]['id']}", headers=other_headers, json={"name": "Intrusión", "price_minor": 1})
    assert response.status_code == 404


def test_reader_cannot_mutate(client, viewer_headers):
    assert client.get("/api/dashboard", headers=viewer_headers).status_code == 200
    assert client.post("/api/products", headers=viewer_headers, json={"name": "Prueba", "price_minor": 100}).status_code == 403
    assert client.post("/api/optimization/evaluate", headers=viewer_headers).status_code == 403
    assert client.put("/api/rules", headers=viewer_headers, json={"max_daily_minor": 500000, "max_increase_pct": 10}).status_code == 403
    assert client.post("/api/proposals", headers=viewer_headers, json=proposal_payload(client, viewer_headers)).status_code == 403


def test_catalog_persists_and_audits(client, owner_headers, other_headers):
    response = client.post("/api/products", headers=owner_headers, json={"name": "Sartén", "price_minor": 199900, "margin_pct": 35})
    assert response.status_code == 201
    product = response.json()
    assert product["price_minor"] == 199900
    assert product["id"] in [p["id"] for p in client.get("/api/products", headers=owner_headers).json()]
    assert product["id"] not in [p["id"] for p in client.get("/api/products", headers=other_headers).json()]
    updated = client.put(
        f"/api/products/{product['id']}", headers=owner_headers, json={"name": "Sartén nueva", "price_minor": 180000, "margin_pct": 35}
    )
    assert updated.json()["name"] == "Sartén nueva"
    assert len(client.get("/api/audit", headers=owner_headers).json()) == 2
    assert client.get("/api/audit", headers=other_headers).json() == []


def test_upload_image_and_private_file(client, owner_headers, other_headers):
    product = client.get("/api/products", headers=owner_headers).json()[0]
    buffer = io.BytesIO()
    Image.new("RGB", (400, 500), "green").save(buffer, "PNG")
    content = buffer.getvalue()
    response = client.post(
        "/api/creatives/upload",
        headers=owner_headers,
        data={"product_id": product["id"], "copy": "Comprá hoy"},
        files={"file": ("../../escape.png", content, "text/plain")},
    )
    assert response.status_code == 201
    creative = response.json()
    assert creative["analysis"]["width"] == 400
    assert creative["analysis"]["height"] == 500
    assert creative["mime"] == "image/png"
    assert creative["has_file"] is True
    assert "storage_key" not in creative
    path = f"/api/creatives/{creative['id']}/file"
    assert client.get(path, headers=owner_headers).content == content
    assert client.get(path, headers=other_headers).status_code == 404
    assert client.get(path).status_code == 401


@pytest.mark.parametrize("content", [b"<script>alert(1)</script>", b"", b"not an image"])
def test_invalid_upload(client, owner_headers, content):
    product = client.get("/api/products", headers=owner_headers).json()[0]
    response = client.post(
        "/api/creatives/upload",
        headers=owner_headers,
        data={"product_id": product["id"]},
        files={"file": ("fake.png", content, "image/png")},
    )
    assert response.status_code == 422


def test_video_is_explicitly_not_semantic_ai(client, owner_headers):
    product = client.get("/api/products", headers=owner_headers).json()[0]
    response = client.post(
        "/api/creatives/upload",
        headers=owner_headers,
        data={"product_id": product["id"]},
        files={"file": ("clip.mp4", b"\x00\x00\x00\x18ftypisom" + b"0" * 20, "video/mp4")},
    )
    assert response.status_code == 201
    assert response.json()["kind"] == "video"
    assert any("no verificados" in note for note in response.json()["analysis"]["notes"])


@pytest.mark.parametrize("budget,strategy", [(100000, "ABO"), (300000, "CBO")])
def test_proposal_distributes_all_ads_once(client, owner_headers, budget, strategy):
    payload = proposal_payload(client, owner_headers, budget)
    response = client.post("/api/proposals", headers=owner_headers, json=payload)
    assert response.status_code == 201
    plan = response.json()["plan"]
    assert plan["strategy"] == strategy
    assert plan["publishable"] is False
    assigned = [i for group in plan["ad_sets"] for i in group["creative_ids"]]
    assert sorted(assigned) == sorted(payload["creative_ids"])
    if strategy == "ABO":
        assert sum(group["daily_budget_minor"] for group in plan["ad_sets"]) == budget
    else:
        assert plan["campaign_budget_minor"] == budget
        assert all(group["daily_budget_minor"] is None for group in plan["ad_sets"])


@pytest.mark.parametrize(
    "patch",
    [
        {"daily_budget_minor": -1},
        {"daily_budget_minor": 500001},
        {"age_min": 66},
        {"age_min": 40, "age_max": 20},
        {"creative_ids": []},
        {"target_cpa_minor": 0},
    ],
)
def test_proposal_validates(client, owner_headers, patch):
    payload = proposal_payload(client, owner_headers)
    assert client.post("/api/proposals", headers=owner_headers, json=payload | patch).status_code == 422


def test_repeated_and_mismatched_creatives_rejected(client, owner_headers):
    payload = proposal_payload(client, owner_headers)
    payload["creative_ids"] = [payload["creative_ids"][0]] * 2
    assert client.post("/api/proposals", headers=owner_headers, json=payload).status_code == 422
    product = client.post("/api/products", headers=owner_headers, json={"name": "Otro producto", "price_minor": 100}).json()
    payload["creative_ids"] = payload["creative_ids"][:1]
    payload["product_id"] = product["id"]
    assert client.post("/api/proposals", headers=owner_headers, json=payload).status_code == 422


def test_review_never_publishes(client, owner_headers, other_headers):
    proposal = client.post("/api/proposals", headers=owner_headers, json=proposal_payload(client, owner_headers)).json()
    path = f"/api/proposals/{proposal['id']}/decision"
    assert client.post(path, headers=other_headers, json={"decision": "approve"}).status_code == 404
    assert client.post(path, headers=owner_headers, json={"decision": "approve"}).json()["status"] == "approved"
    assert client.post(path, headers=owner_headers, json={"decision": "approve"}).status_code == 409
    assert client.post(f"/api/proposals/{proposal['id']}/publish", headers=owner_headers).status_code == 403
    assert client.post("/api/integrations/meta/connect", headers=owner_headers).status_code == 501
    assert client.get("/api/integrations/meta", headers=owner_headers).json()["connected"] is False


def test_evaluation_does_not_modify_campaigns_and_is_deduplicated(client, owner_headers):
    before = client.get("/api/dashboard", headers=owner_headers).json()["campaigns"]
    first = recommendations(client, owner_headers)
    second = recommendations(client, owner_headers)
    assert len(first) == len(second) == 2
    assert {r["action"] for r in first} == {"pause", "increase_budget"}
    assert client.get("/api/dashboard", headers=owner_headers).json()["campaigns"] == before


def test_approval_required_apply_is_idempotent_and_tenant_scoped(client, owner_headers, other_headers, viewer_headers):
    rec = next(r for r in recommendations(client, owner_headers) if r["action"] == "increase_budget")
    path = f"/api/recommendations/{rec['id']}"
    assert client.post(path + "/apply", headers=owner_headers).status_code == 409
    assert client.post(path + "/decision", headers=other_headers, json={"decision": "approve"}).status_code == 404
    assert client.post(path + "/decision", headers=viewer_headers, json={"decision": "approve"}).status_code == 403
    assert client.post(path + "/decision", headers=owner_headers, json={"decision": "approve"}).status_code == 200
    assert client.post(path + "/apply", headers=other_headers).status_code == 404
    assert client.post(path + "/apply", headers=viewer_headers).status_code == 403
    applied = client.post(path + "/apply", headers=owner_headers)
    repeated = client.post(path + "/apply", headers=owner_headers)
    assert applied.status_code == repeated.status_code == 200
    assert applied.json()["campaign"]["daily_budget_minor"] == repeated.json()["campaign"]["daily_budget_minor"] == 120000
    assert applied.json()["simulated"] is True
    events = client.get("/api/audit", headers=owner_headers).json()
    assert len([e for e in events if e["action"] == "recommendation.simulated"]) == 1


def test_aggregate_limit_is_rechecked_at_application(client, owner_headers):
    assert client.put("/api/rules", headers=owner_headers, json={"max_daily_minor": 185000, "max_increase_pct": 20}).status_code == 200
    rec = next(r for r in recommendations(client, owner_headers) if r["action"] == "increase_budget")
    client.post(f"/api/recommendations/{rec['id']}/decision", headers=owner_headers, json={"decision": "approve"})
    response = client.post(f"/api/recommendations/{rec['id']}/apply", headers=owner_headers)
    assert response.status_code == 409
    assert client.get("/api/dashboard", headers=owner_headers).json()["active_daily_budget_minor"] == 185000


def test_lower_scaling_rule_invalidates_old_recommendation(client, owner_headers):
    rec = next(r for r in recommendations(client, owner_headers) if r["action"] == "increase_budget")
    client.post(f"/api/recommendations/{rec['id']}/decision", headers=owner_headers, json={"decision": "approve"})
    client.put("/api/rules", headers=owner_headers, json={"max_daily_minor": 500000, "max_increase_pct": 5})
    assert client.post(f"/api/recommendations/{rec['id']}/apply", headers=owner_headers).status_code == 409
    fresh = next(r for r in recommendations(client, owner_headers) if r["action"] == "increase_budget" and r["status"] == "pending")
    assert fresh["suggested_budget_minor"] == 105000
    assert fresh["id"] != rec["id"]


def test_pause_and_rejection(client, owner_headers):
    recs = recommendations(client, owner_headers)
    pause = next(r for r in recs if r["action"] == "pause")
    scale = next(r for r in recs if r["action"] == "increase_budget")
    client.post(f"/api/recommendations/{scale['id']}/decision", headers=owner_headers, json={"decision": "reject"})
    assert client.post(f"/api/recommendations/{scale['id']}/apply", headers=owner_headers).status_code == 409
    client.post(f"/api/recommendations/{pause['id']}/decision", headers=owner_headers, json={"decision": "approve"})
    response = client.post(f"/api/recommendations/{pause['id']}/apply", headers=owner_headers)
    assert response.json()["campaign"]["status"] == "paused"


def test_rule_guardrails(client, owner_headers):
    assert client.put("/api/rules", headers=owner_headers, json={"max_daily_minor": 100, "max_increase_pct": 20}).status_code == 422
    assert client.put("/api/rules", headers=owner_headers, json={"max_daily_minor": 500000, "max_increase_pct": 21}).status_code == 422


def test_logout_revokes_session(client, owner_headers):
    assert client.post("/api/auth/logout", headers=owner_headers).status_code == 200
    assert client.get("/api/me", headers=owner_headers).status_code == 401


def test_expired_session_rejected(client, owner_headers):
    from app.db import get_db
    from app.main import app

    override = app.dependency_overrides[get_db]
    with contextmanager(override)() as db:
        session = db.get(SessionToken, digest(owner_headers["Authorization"].split()[1]))
        session.expires_at = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()
        db.commit()
    assert client.get("/api/me", headers=owner_headers).status_code == 401


def test_composite_foreign_key_rejects_cross_tenant_relation(client, owner_headers, other_headers):
    from app.db import get_db
    from app.main import app

    foreign_product = client.get("/api/products", headers=other_headers).json()[0]
    own_tenant = client.get("/api/me", headers=owner_headers).json()["tenant"]["id"]
    with contextmanager(app.dependency_overrides[get_db])() as db:
        db.add(
            Creative(tenant_id=own_tenant, product_id=foreign_product["id"], name="Intrusión", kind="image", mime="image/png", analysis={})
        )
        with pytest.raises(IntegrityError):
            db.commit()


def test_engine_refuses_non_demo_mode(monkeypatch):
    from app.config import Settings, get_settings

    monkeypatch.setenv("APP_MODE", "production")
    get_settings.cache_clear()
    with pytest.raises(RuntimeError):
        get_settings()
    monkeypatch.setenv("APP_MODE", "demo")
    get_settings.cache_clear()
    assert Settings().app_mode == "demo"


@pytest.mark.skipif(not os.getenv("TEST_DATABASE_URL", "").startswith("postgresql"), reason="Requiere locks PostgreSQL")
def test_concurrent_increases_cannot_exceed_aggregate_cap(client, owner_headers):
    from app.db import get_db
    from app.main import app
    from app.models import Campaign

    tenant_id = client.get("/api/me", headers=owner_headers).json()["tenant"]["id"]
    with contextmanager(app.dependency_overrides[get_db])() as db:
        db.add(
            Campaign(
                tenant_id=tenant_id,
                name="Segunda ganadora",
                daily_budget_minor=50000,
                spend_minor=350000,
                revenue_minor=1400000,
                purchases=12,
            )
        )
        db.commit()
    assert client.put("/api/rules", headers=owner_headers, json={"max_daily_minor": 260000, "max_increase_pct": 20}).status_code == 200
    increases = [r for r in recommendations(client, owner_headers) if r["action"] == "increase_budget"]
    assert len(increases) == 2
    for recommendation in increases:
        assert (
            client.post(
                f"/api/recommendations/{recommendation['id']}/decision", headers=owner_headers, json={"decision": "approve"}
            ).status_code
            == 200
        )

    def apply(recommendation):
        return client.post(f"/api/recommendations/{recommendation['id']}/apply", headers=owner_headers).status_code

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(apply, increases))
    assert sorted(results) == [200, 409]
    assert client.get("/api/dashboard", headers=owner_headers).json()["active_daily_budget_minor"] <= 260000


def test_upload_size_limit(client, owner_headers):
    product = client.get("/api/products", headers=owner_headers).json()[0]
    response = client.post(
        "/api/creatives/upload",
        headers=owner_headers,
        data={"product_id": product["id"]},
        files={"file": ("large.mp4", b"0" * (25 * 1024 * 1024 + 1), "video/mp4")},
    )
    assert response.status_code == 413
