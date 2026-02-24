export interface Run {
  run_id: string;
  started_at: string;
  finished_at: string | null;
  prompt_count: number;
  provider_count: number;
  repeats: number;
  status: string;
}

export interface EngineOverview {
  provider: string;
  display_name: string;
  total_responses: number;
  visibility: number;
  sov: number;
  rec_rate: number;
  avg_position: number | null;
  sentiment_dist: Record<string, number>;
  citation_rate: number;
}

export interface PromptData {
  prompt_id: string;
  prompt_text: string;
  provider: string;
  total: number;
  visible: number;
  recommended: number;
  visibility_pct: number;
  rec_pct: number;
}

export interface Competitor {
  brand: string;
  mention_count: number;
  avg_position: number;
  sentiment_mode: string;
  recommendation_count: number;
}

export interface CitationDomain {
  domain: string;
  count: number;
  is_coke_domain: boolean;
}

export interface CostEntry {
  provider: string;
  model: string;
  queries: number;
  input_tokens: number;
  output_tokens: number;
  total_cost: number;
}

export interface ResponseDetail {
  response_id: string;
  repeat_num: number;
  raw_text: string;
  coke_brands_found: string[];
  competitor_brands_found: string[];
  coke_is_primary_recommendation: boolean;
  response_type: string;
}
