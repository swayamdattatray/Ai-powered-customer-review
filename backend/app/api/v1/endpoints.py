"""
API Router for Shopping Intelligence Endpoints.
"""

from datetime import datetime
import hashlib
from fastapi import APIRouter, HTTPException

from ...schemas.contracts import (
    ExtractedProductPayload,
    ProductIntelligenceResponse,
)
from ...services.review_auditor import ReviewAuditor
from ...services.price_engine import PriceEngine
from ...services.history_tracker import PriceHistoryTracker
from ...services.scam_engine import ScamRiskEngine

router = APIRouter()


@router.get("/health")
async def health_check():
    return {
        "status": "online",
        "service": "AI Shopping Intelligence API",
        "timestamp": datetime.now().isoformat()
    }


@router.post("/intelligence/analyze", response_model=ProductIntelligenceResponse)
async def analyze_product(payload: ExtractedProductPayload):
    """
    Core Ingestion and Analysis Endpoint:
    Receives on-page extracted payload from Browser Extension Content Script,
    runs review credibility auditing, price comparison, historical price tracking,
    and scam/fraud risk evaluation.
    """
    try:
        # Generate stable canonical hash from platform + SKU
        canonical_id = hashlib.sha256(f"{payload.platform}:{payload.sku}".encode()).hexdigest()[:16]

        # 1. Execute Review Credibility & Sentiment Audit
        credibility_result = ReviewAuditor.audit_reviews(
            reviews=payload.reviews,
            total_ratings=payload.rating_count
        )

        # 2. Execute Cross-Platform Price Arbitrage & Match Analysis
        price_items, arbitrage_summary = PriceEngine.evaluate_pricing(
            source_platform=payload.platform,
            source_title=payload.title,
            source_url=payload.url,
            source_price=payload.listed_price
        )

        # 3. Retrieve Historical Price Analytics & Purchase Timing Recommendation
        price_history = PriceHistoryTracker.get_analytics(
            product_name=payload.title,
            current_price=payload.listed_price,
            platform=payload.platform
        )

        # 4. Evaluate Scam & Counterfeit Fraud Risk
        scam_assessment = ScamRiskEngine.evaluate_scam_risk(
            payload=payload,
            credibility=credibility_result,
            history=price_history
        )

        return ProductIntelligenceResponse(
            canonical_id=canonical_id,
            title=payload.title,
            brand=payload.brand,
            primary_platform=payload.platform,
            current_price=payload.listed_price,
            currency=payload.currency,
            credibility=credibility_result,
            prices=price_items,
            arbitrage=arbitrage_summary,
            history=price_history,
            scam_risk=scam_assessment,
            generated_at=datetime.now().strftime("%d %b %Y, %I:%M %p")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process shopping intelligence: {str(e)}")
