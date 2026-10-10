"""
Data Contracts and Schema Definitions
Shared representation between Browser Extension and Backend API.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


# ------------------------------------------------------------------------------
# 1. Client-Side Ingestion Payload (from Content Script)
# ------------------------------------------------------------------------------
class ClientReviewItem(BaseModel):
    id: Optional[str] = None
    rating: Optional[float] = None
    title: Optional[str] = None
    text: str
    date: Optional[str] = None
    verified_purchase: bool = False
    author: Optional[str] = None


class ExtractedProductPayload(BaseModel):
    url: str
    platform: str  # "AMAZON_IN" | "FLIPKART"
    sku: str  # ASIN or FSN/PID
    title: str
    brand: Optional[str] = None
    model_number: Optional[str] = None
    listed_price: Optional[float] = None
    currency: str = "INR"
    rating: Optional[float] = None
    rating_count: Optional[int] = None
    availability: bool = True
    seller_name: Optional[str] = None
    is_fulfilled_by_platform: bool = False
    return_policy: Optional[str] = None
    attributes: Dict[str, Any] = Field(default_factory=dict)  # e.g., {"storage": "128GB", "ram": "8GB", "color": "Black"}
    raw_microdata: Optional[Dict[str, Any]] = None
    reviews: List[ClientReviewItem] = Field(default_factory=list)


# ------------------------------------------------------------------------------
# 2. Review Credibility & Sentiment Models
# ------------------------------------------------------------------------------
class SuspiciousPatternSignal(BaseModel):
    signal_type: str  # e.g., "NEAR_DUPLICATE_CLUSTER", "POLARITY_INCONGRUENCE", "GENERIC_HYPERBOLE"
    description: str
    severity: str  # "HIGH" | "MEDIUM" | "LOW"
    affected_review_ids: List[str] = Field(default_factory=list)


class AspectSentiment(BaseModel):
    aspect: str
    score: float  # 1.0 to 5.0
    sentiment: str  # "Positive" | "Negative" | "Neutral"
    mentions: int
    positive_ratio: float
    negative_ratio: float
    grounded_snippets: List[str] = Field(default_factory=list)


class ReviewCredibilityResult(BaseModel):
    trust_score: float  # 0.0 to 100.0
    anomaly_level: str  # "LOW" | "ELEVATED" | "HIGH"
    sample_size: int
    total_ratings_available: Optional[int] = None
    duplicate_cluster_ratio: float  # 0.0 to 1.0
    entropy_score: float  # Shannon entropy on rating distribution
    polarity_drift_ratio: float  # Mismatched star-to-text polarity
    estimated_genuine_pct: float = 85.0  # 0.0 to 100.0
    estimated_fake_pct: float = 15.0     # 0.0 to 100.0
    authenticity_status: str = "LIKELY_AUTHENTIC"  # "LIKELY_AUTHENTIC" | "MODERATE_SUSPICION" | "HIGH_FAKE_RISK"
    authenticity_reason: str = ""
    signals: List[SuspiciousPatternSignal] = Field(default_factory=list)
    aspects: List[AspectSentiment] = Field(default_factory=list)
    executive_summary: str
    data_limitation_notice: str


# ------------------------------------------------------------------------------
# 3. Price Arbitrage & Matching Models
# ------------------------------------------------------------------------------
class PlatformPriceItem(BaseModel):
    platform: str
    product_name: str
    product_url: str
    listed_price: Optional[float] = None
    shipping_charge: float = 0.0
    verified_discount: float = 0.0
    final_landed_price: Optional[float] = None
    currency: str = "INR"
    availability: bool = True
    seller_name: Optional[str] = None
    match_confidence: str  # "EXACT" | "HIGH" | "UNCERTAIN" | "MISMATCH"
    spec_deltas: List[str] = Field(default_factory=list)
    data_provenance: str  # "OFFICIAL_PAAPI" | "FLIPKART_AFFILIATE" | "ON_PAGE_DOM"
    last_checked: str
    status: str  # "SUCCESS" | "UNAVAILABLE" | "ERROR"
    error_reason: Optional[str] = None


class PriceArbitrageSummary(BaseModel):
    lowest_price: Optional[float] = None
    highest_price: Optional[float] = None
    potential_savings: Optional[float] = None
    cheapest_platform: Optional[str] = None
    sources_compared: int
    has_arbitrage: bool
    status_notice: str


class PriceHistoryPoint(BaseModel):
    date: str
    price: float
    platform: str


class PriceHistoryAnalytics(BaseModel):
    has_history: bool = False
    current_price: Optional[float] = None
    lowest_recorded: Optional[float] = None
    highest_recorded: Optional[float] = None
    average_recorded: Optional[float] = None
    recommendation: str = "FAIR"  # "GOOD_TIME_TO_BUY" | "FAIR" | "WAIT_FOR_SALE"
    recommendation_reason: str = ""
    history_points: List[PriceHistoryPoint] = Field(default_factory=list)


# ------------------------------------------------------------------------------
# 4. Scam Risk & Consumer Safety Model
# ------------------------------------------------------------------------------
class ScamRiskAssessment(BaseModel):
    risk_score: float = 12.0  # 0.0 to 100.0 (higher = greater danger)
    risk_level: str = "LOW"   # "LOW" | "MODERATE" | "HIGH" | "CRITICAL"
    verdict_title: str = "Safe to Buy - Low Scam Risk"
    verdict_summary: str = "Standard authenticated product listing with normal pricing and verified seller indicators."
    positive_safety_signals: List[str] = Field(default_factory=list)
    warning_flags: List[str] = Field(default_factory=list)
    safety_checklist: List[str] = Field(default_factory=list)


# ------------------------------------------------------------------------------
# 5. Master Consolidated Intelligence Response (For Side Panel)
# ------------------------------------------------------------------------------
class ProductIntelligenceResponse(BaseModel):
    canonical_id: str
    title: str
    brand: Optional[str] = None
    primary_platform: str
    current_price: Optional[float] = None
    currency: str = "INR"
    credibility: ReviewCredibilityResult
    prices: List[PlatformPriceItem] = Field(default_factory=list)
    arbitrage: PriceArbitrageSummary
    history: PriceHistoryAnalytics = Field(default_factory=PriceHistoryAnalytics)
    scam_risk: ScamRiskAssessment = Field(default_factory=ScamRiskAssessment)
    generated_at: str
