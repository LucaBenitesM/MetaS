from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import JSON, CheckConstraint, ForeignKey, ForeignKeyConstraint, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base


def uid():
    return str(uuid4())


def now():
    return datetime.now(timezone.utc).isoformat()


class Tenant(Base):
    __tablename__ = "tenants"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    slug: Mapped[str] = mapped_column(String(80), unique=True)
    name: Mapped[str] = mapped_column(String(120))
    currency: Mapped[str] = mapped_column(String(3), default="UYU")
    country: Mapped[str] = mapped_column(String(2), default="UY")
    max_daily_minor: Mapped[int] = mapped_column(Integer, default=500000)
    max_increase_pct: Mapped[int] = mapped_column(Integer, default=20)


class Scoped:
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    created_at: Mapped[str] = mapped_column(String(40), default=now)


class Member(Scoped, Base):
    __tablename__ = "members"
    name: Mapped[str] = mapped_column(String(120))
    role: Mapped[str] = mapped_column(String(20))
    __table_args__ = (UniqueConstraint("tenant_id", "id"), CheckConstraint("role IN ('owner', 'viewer')"))


class SessionToken(Base):
    __tablename__ = "sessions"
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    member_id: Mapped[str] = mapped_column(ForeignKey("members.id"))
    expires_at: Mapped[str] = mapped_column(String(40))


class Product(Scoped, Base):
    __tablename__ = "products"
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(String(2000), default="")
    price_minor: Mapped[int] = mapped_column(Integer)
    margin_pct: Mapped[int] = mapped_column(Integer, default=40)
    __table_args__ = (
        UniqueConstraint("tenant_id", "id"),
        CheckConstraint("price_minor > 0"),
        CheckConstraint("margin_pct BETWEEN 1 AND 100"),
    )


class Creative(Scoped, Base):
    __tablename__ = "creatives"
    product_id: Mapped[str] = mapped_column(String(36))
    name: Mapped[str] = mapped_column(String(160))
    kind: Mapped[str] = mapped_column(String(12))
    copy: Mapped[str] = mapped_column(String(4000), default="")
    storage_key: Mapped[str | None] = mapped_column(String(80), nullable=True)
    mime: Mapped[str] = mapped_column(String(80))
    analysis: Mapped[dict] = mapped_column(JSON, default=dict)
    __table_args__ = (
        UniqueConstraint("tenant_id", "id"),
        ForeignKeyConstraint(["tenant_id", "product_id"], ["products.tenant_id", "products.id"]),
    )


class Campaign(Scoped, Base):
    __tablename__ = "campaigns"
    name: Mapped[str] = mapped_column(String(160))
    status: Mapped[str] = mapped_column(String(20), default="active")
    daily_budget_minor: Mapped[int] = mapped_column(Integer)
    spend_minor: Mapped[int] = mapped_column(Integer, default=0)
    revenue_minor: Mapped[int] = mapped_column(Integer, default=0)
    purchases: Mapped[int] = mapped_column(Integer, default=0)
    impressions: Mapped[int] = mapped_column(Integer, default=0)
    clicks: Mapped[int] = mapped_column(Integer, default=0)
    days_observed: Mapped[int] = mapped_column(Integer, default=7)
    revision: Mapped[int] = mapped_column(Integer, default=1)
    __table_args__ = (UniqueConstraint("tenant_id", "id"), CheckConstraint("daily_budget_minor > 0"))


class Proposal(Scoped, Base):
    __tablename__ = "proposals"
    title: Mapped[str] = mapped_column(String(160))
    status: Mapped[str] = mapped_column(String(24), default="pending")
    plan: Mapped[dict] = mapped_column(JSON)
    __table_args__ = (CheckConstraint("status IN ('pending','approved','rejected')"),)


class Recommendation(Scoped, Base):
    __tablename__ = "recommendations"
    campaign_id: Mapped[str] = mapped_column(String(36))
    action: Mapped[str] = mapped_column(String(24))
    reason: Mapped[str] = mapped_column(String(1000))
    status: Mapped[str] = mapped_column(String(24), default="pending")
    campaign_revision: Mapped[int] = mapped_column(Integer)
    suggested_budget_minor: Mapped[int | None] = mapped_column(Integer, nullable=True)
    __table_args__ = (
        ForeignKeyConstraint(["tenant_id", "campaign_id"], ["campaigns.tenant_id", "campaigns.id"]),
        UniqueConstraint("tenant_id", "campaign_id", "campaign_revision", name="uq_recommendation_revision"),
        CheckConstraint("status IN ('pending','approved','rejected','applied')"),
    )


class Audit(Scoped, Base):
    __tablename__ = "audit_events"
    actor_id: Mapped[str] = mapped_column(String(36))
    action: Mapped[str] = mapped_column(String(80))
    entity_id: Mapped[str] = mapped_column(String(36))
    detail: Mapped[dict] = mapped_column(JSON, default=dict)
    __table_args__ = (Index("ix_audit_tenant_created", "tenant_id", "created_at"),)
