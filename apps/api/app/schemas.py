from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator


class LoginIn(BaseModel):
    tenant: Literal["cristal-demo", "norte-demo"] = "cristal-demo"
    role: Literal["owner", "viewer"] = "owner"


class ProductIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    name: str = Field(min_length=2, max_length=120)
    description: str = Field(default="", max_length=2000)
    price_minor: int = Field(gt=0, le=100_000_000)
    margin_pct: int = Field(default=40, ge=1, le=100)


class ProposalIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    product_id: str
    creative_ids: list[str] = Field(min_length=1, max_length=20)
    daily_budget_minor: int = Field(gt=0, le=100_000_000)
    target_cpa_minor: int = Field(gt=0, le=100_000_000)
    country: str = Field(default="UY", pattern=r"^[A-Z]{2}$")
    age_min: int = Field(default=18, ge=18, le=65)
    age_max: int = Field(default=65, ge=18, le=65)

    @model_validator(mode="after")
    def validate_ages(self):
        if self.age_min > self.age_max:
            raise ValueError("La edad mínima no puede superar la máxima")
        if len(self.creative_ids) != len(set(self.creative_ids)):
            raise ValueError("No repetir creatividades")
        return self


class RulesIn(BaseModel):
    max_daily_minor: int = Field(gt=0, le=100_000_000)
    max_increase_pct: int = Field(ge=1, le=20)


class DecisionIn(BaseModel):
    decision: Literal["approve", "reject"]


class ResourceOut(BaseModel):
    id: str
    tenant_id: str
    created_at: str


class ProductOut(ResourceOut):
    name: str
    description: str
    price_minor: int
    margin_pct: int


class CreativeOut(ResourceOut):
    product_id: str
    name: str
    kind: str
    ad_copy: str = Field(alias="copy")
    mime: str
    analysis: dict
    has_file: bool


class CampaignOut(ResourceOut):
    name: str
    status: str
    daily_budget_minor: int
    spend_minor: int
    revenue_minor: int
    purchases: int
    impressions: int
    clicks: int
    days_observed: int
    revision: int


class ProposalOut(ResourceOut):
    title: str
    status: str
    plan: dict


class RecommendationOut(ResourceOut):
    campaign_id: str
    action: str
    reason: str
    status: str
    campaign_revision: int
    suggested_budget_minor: int | None


class AuditOut(ResourceOut):
    actor_id: str
    action: str
    entity_id: str
    detail: dict


class DashboardOut(BaseModel):
    period: str
    currency: str
    spend_minor: int
    revenue_minor: int
    purchases: int
    roas: float | None
    cpa_minor: int | None
    active_daily_budget_minor: int
    campaigns: list[CampaignOut]
    source: str


class ApplyOut(BaseModel):
    recommendation: RecommendationOut
    campaign: CampaignOut
    simulated: Literal[True]
