export type Tenant = {
  id: string;
  name: string;
  currency: string;
  max_daily_minor: number;
  max_increase_pct: number;
};
export type Session = {
  access_token: string;
  tenant: Tenant;
  member: { name: string; role: "owner" | "viewer" };
};
export type Product = {
  id: string;
  name: string;
  description: string;
  price_minor: number;
  margin_pct: number;
};
export type Creative = {
  id: string;
  product_id: string;
  name: string;
  kind: string;
  copy: string;
  has_file: boolean;
  analysis: {
    notes: string[];
    width?: number;
    height?: number;
    bytes?: number;
  };
};
export type Campaign = {
  id: string;
  name: string;
  status: string;
  daily_budget_minor: number;
  spend_minor: number;
  revenue_minor: number;
  purchases: number;
  impressions: number;
  clicks: number;
};
export type Dashboard = {
  period: string;
  spend_minor: number;
  revenue_minor: number;
  purchases: number;
  roas: number | null;
  cpa_minor: number | null;
  active_daily_budget_minor: number;
  campaigns: Campaign[];
};
export type Plan = {
  strategy: string;
  daily_budget_minor: number;
  campaign_budget_minor: number | null;
  reasoning: string[];
  warnings: string[];
  creative_briefs: string[];
  provider: string;
  ad_sets: {
    name: string;
    creative_ids: string[];
    daily_budget_minor: number | null;
    audience: { country: string; age_min: number; age_max: number };
  }[];
};
export type Proposal = {
  id: string;
  title: string;
  status: string;
  plan: Plan;
};
export type Recommendation = {
  id: string;
  campaign_id: string;
  action: string;
  reason: string;
  status: string;
  suggested_budget_minor: number | null;
};
export type Rules = {
  max_daily_minor: number;
  max_increase_pct: number;
  min_days: number;
  min_purchases_scale: number;
  min_roas_scale: number;
};
export type Audit = {
  id: string;
  action: string;
  entity_id: string;
  created_at: string;
  detail: Record<string, unknown>;
};
