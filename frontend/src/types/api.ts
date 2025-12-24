export type ModelTier = 'small' | 'medium' | 'api';

export interface GenerateRequest {
  prompt: string;
  context: string[];
  constraints: {
    max_latency_ms: number;
    max_cost_usd: number;
    risk_level: 'low' | 'medium' | 'high';
  };
  debug: boolean;
}

export interface TokenUsage {
  input: number;
  output: number;
}

export interface ContextWindow {
  total_tokens: number;
  max_allowed: number;
  overflow: boolean;
  escalated_from?: string;
  warning?: string;
}

export interface StaticRule {
  rule_name: string;
  matched_condition: Record<string, any>;
  route_to: string;
}

export interface Classifier {
  predicted_task: string;
  confidence: number;
  confidence_band?: string;
}

export interface Heuristics {
  context_ratio: number;
  generation_weight: string;
  override?: string;
  estimated_output_tokens?: number;
}

export interface DebugInfo {
  static_rule?: StaticRule;
  classifier?: Classifier;
  heuristics?: Heuristics;
  context_window?: ContextWindow;
  fallback?: any;
}

export interface GenerateResponse {
  response: string;
  model_used: ModelTier;
  tokens_used: TokenUsage;
  estimated_cost_usd: number;
  cache_hit: boolean;
  debug?: DebugInfo;
}