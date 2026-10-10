/**
 * TypeScript Contracts mirroring Backend Schema Specifications
 */

export interface ClientReviewItem {
  id?: string;
  rating?: number;
  title?: string;
  text: string;
  date?: string;
  verified_purchase: boolean;
  author?: string;
}

export interface ExtractedProductPayload {
  url: string;
  platform: 'AMAZON_IN' | 'FLIPKART' | 'UNKNOWN';
  sku: string;
  title: string;
  brand?: string;
  model_number?: string;
  listed_price?: number;
  currency: string;
  rating?: number;
  rating_count?: number;
  availability: boolean;
  seller_name?: string;
  is_fulfilled_by_platform?: boolean;
  return_policy?: string;
  attributes: Record<string, any>;
  reviews: ClientReviewItem[];
}

export interface SuspiciousPatternSignal {
  signal_type: string;
  description: string;
  severity: 'HIGH' | 'MEDIUM' | 'LOW';
  affected_review_ids?: string[];
}

export interface AspectSentiment {
  aspect: string;
  score: number;
  sentiment: 'Positive' | 'Negative' | 'Mixed / Neutral';
  mentions: number;
  positive_ratio: number;
  negative_ratio: number;
  grounded_snippets: string[];
}

export interface ReviewCredibilityResult {
  trust_score: number;
  anomaly_level: 'LOW' | 'ELEVATED' | 'HIGH';
  sample_size: number;
  total_ratings_available?: number;
  duplicate_cluster_ratio: number;
  entropy_score: number;
  polarity_drift_ratio: number;
  estimated_genuine_pct: number;
  estimated_fake_pct: number;
  authenticity_status: 'LIKELY_AUTHENTIC' | 'MODERATE_SUSPICION' | 'HIGH_FAKE_RISK';
  authenticity_reason: string;
  signals: SuspiciousPatternSignal[];
  aspects: AspectSentiment[];
  executive_summary: string;
  data_limitation_notice: string;
}

export interface PlatformPriceItem {
  platform: string;
  product_name: string;
  product_url: string;
  listed_price?: number;
  shipping_charge: number;
  verified_discount: number;
  final_landed_price?: number;
  currency: string;
  availability: boolean;
  seller_name?: string;
  match_confidence: 'EXACT' | 'HIGH' | 'UNCERTAIN' | 'MISMATCH';
  spec_deltas: string[];
  data_provenance: string;
  last_checked: string;
  status: 'SUCCESS' | 'UNAVAILABLE' | 'ERROR';
  error_reason?: string;
}

export interface PriceArbitrageSummary {
  lowest_price?: number;
  highest_price?: number;
  potential_savings?: number;
  cheapest_platform?: string;
  sources_compared: number;
  has_arbitrage: boolean;
  status_notice: string;
}

export interface PriceHistoryPoint {
  date: string;
  price: number;
  platform: string;
}

export interface PriceHistoryAnalytics {
  has_history: boolean;
  current_price?: number;
  lowest_recorded?: number;
  highest_recorded?: number;
  average_recorded?: number;
  recommendation: 'GOOD_TIME_TO_BUY' | 'FAIR' | 'WAIT_FOR_SALE';
  recommendation_reason: string;
  history_points: PriceHistoryPoint[];
}

export interface ScamRiskAssessment {
  risk_score: number;
  risk_level: 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';
  verdict_title: string;
  verdict_summary: string;
  positive_safety_signals: string[];
  warning_flags: string[];
  safety_checklist: string[];
}

export interface ProductIntelligenceResponse {
  canonical_id: string;
  title: string;
  brand?: string;
  primary_platform: string;
  current_price?: number;
  currency: string;
  credibility: ReviewCredibilityResult;
  prices: PlatformPriceItem[];
  arbitrage: PriceArbitrageSummary;
  history?: PriceHistoryAnalytics;
  scam_risk?: ScamRiskAssessment;
  generated_at: string;
}
