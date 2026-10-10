"""
Scam Risk & Fraud Detection Engine.
Evaluates pricing anomalies, seller fulfillment, review manipulation, and return policies
to compute consumer scam risk scores and actionable buyer protection recommendations.
"""

from typing import List, Optional
from ..schemas.contracts import (
    ExtractedProductPayload,
    ReviewCredibilityResult,
    PriceHistoryAnalytics,
    ScamRiskAssessment,
)


class ScamRiskEngine:
    """Multi-factor fraud, counterfeit, and scam vulnerability evaluator."""

    TRUSTED_INDIAN_SELLERS = {
        "appario retail", "cocoblu retail", "retailnet", "supercomnet",
        "indiflash mart", "shrishti distribution", "darshita electronics",
        "cloudtail india", "apple", "samsung", "croma", "reliance digital"
    }

    @classmethod
    def evaluate_scam_risk(
        cls,
        payload: ExtractedProductPayload,
        credibility: ReviewCredibilityResult,
        history: Optional[PriceHistoryAnalytics] = None
    ) -> ScamRiskAssessment:
        """
        Calculates holistic scam and fraud risk score (0-100) based on:
        1. Price deviation vs retail benchmarks (counterfeit/bait-and-switch risk)
        2. Review bot manipulation / hijacked listing risk
        3. Seller reputation and platform fulfillment protection
        4. Return policy and catalog rating maturity
        """
        risk_score = 22.0  # Baseline neutral risk for open e-commerce marketplaces
        positive_signals: List[str] = []
        warning_flags: List[str] = []

        # ----------------------------------------------------------------------
        # 1. Price Anomaly & Extreme Discount Detection
        # ----------------------------------------------------------------------
        cur_price = payload.listed_price
        if cur_price and cur_price > 0:
            if history and history.has_history and history.average_recorded:
                avg = history.average_recorded
                # Extremely steep discount (>45% below historical average) is a prime counterfeit / scam indicator
                if cur_price < avg * 0.55:
                    risk_score += 35.0
                    warning_flags.append(
                        f"Price (₹{cur_price:,.0f}) is >45% below historical average (₹{avg:,.0f}). Extreme counterfeit or refurbished scam risk."
                    )
                elif cur_price < avg * 0.80:
                    risk_score += 10.0
                    warning_flags.append(
                        f"Heavily discounted price (₹{cur_price:,.0f} vs typical ₹{avg:,.0f}). Confirm whether item is brand new or renewed."
                    )
                else:
                    risk_score -= 8.0
                    positive_signals.append("Listed price is consistent with genuine market retail valuation.")
            else:
                positive_signals.append("Listed price is within expected consumer category range.")

        # ----------------------------------------------------------------------
        # 2. Review Authenticity & Hijacked Listing Risk
        # ----------------------------------------------------------------------
        fake_pct = credibility.estimated_fake_pct
        if fake_pct >= 40.0 or credibility.trust_score < 45.0:
            risk_score += 28.0
            warning_flags.append(
                f"Severe review manipulation: ~{fake_pct:.0f}% of reviews exhibit automated templates or duplicate bot patterns."
            )
        elif fake_pct >= 25.0:
            risk_score += 12.0
            warning_flags.append(
                f"Noticeable inauthentic reviews (~{fake_pct:.0f}% suspicious). Seller may be artificially inflating ratings."
            )
        else:
            risk_score -= 10.0
            positive_signals.append(
                f"Reviews demonstrate organic credibility (~{credibility.estimated_genuine_pct:.0f}% genuine customer feedback)."
            )

        # ----------------------------------------------------------------------
        # 3. Seller Fulfillment & Merchant Identity
        # ----------------------------------------------------------------------
        seller_clean = (payload.seller_name or "").strip().lower()
        is_known_seller = any(trusted in seller_clean for trusted in cls.TRUSTED_INDIAN_SELLERS)

        if payload.is_fulfilled_by_platform or is_known_seller:
            risk_score -= 14.0
            plat_name = "Amazon Prime / Fulfilled" if "amazon" in payload.platform.lower() else "Flipkart Assured"
            seller_disp = f" ({payload.seller_name})" if payload.seller_name else ""
            positive_signals.append(f"Dispatched with platform buyer assurance{seller_disp} - {plat_name}.")
        elif payload.seller_name:
            risk_score += 10.0
            warning_flags.append(
                f"Sold and dispatched by third-party merchant '{payload.seller_name}'. Check seller profile rating before placing order."
            )
        else:
            # Neutral / unknown seller
            pass

        # ----------------------------------------------------------------------
        # 4. Return Policy & Buyer Protection Window
        # ----------------------------------------------------------------------
        ret_policy = (payload.return_policy or "").strip().lower()
        if "non-returnable" in ret_policy or "no return" in ret_policy:
            risk_score += 18.0
            warning_flags.append("Listing is non-returnable. No refund or replacement protection if defective.")
        elif "replacement" in ret_policy or "return" in ret_policy:
            risk_score -= 6.0
            positive_signals.append(f"Buyer return/replacement window supported ({payload.return_policy}).")

        # ----------------------------------------------------------------------
        # 5. Rating Volume & Maturity
        # ----------------------------------------------------------------------
        if payload.rating_count is not None:
            if payload.rating_count < 10:
                risk_score += 12.0
                warning_flags.append("Very low catalog rating volume (<10 ratings). Newly created or low-volume listing.")
            elif payload.rating_count > 500:
                risk_score -= 6.0
                positive_signals.append(f"Matured catalog presence with {payload.rating_count:,} customer ratings.")

        # Clamp risk score
        final_score = round(max(5.0, min(95.0, risk_score)), 1)

        # Classify Level and Verdict
        if final_score <= 25.0:
            level = "LOW"
            title = "Safe to Buy - Low Scam Risk"
            summary = "Listing demonstrates strong authentic markers: realistic retail pricing, verified platform fulfillment, and credible customer reviews."
        elif final_score <= 52.0:
            level = "MODERATE"
            title = "Exercise Normal Caution - Moderate Risk"
            summary = "Standard marketplace listing with some minor unverified signals (e.g. 3rd-party merchant or review repetition). Proceed with regular care."
        elif final_score <= 74.0:
            level = "HIGH"
            title = "High Alert - Elevated Scam Risk"
            summary = "Multiple suspicious flags detected: abnormally steep discount, unverified seller, or high bot review activity. Verify seller legitimacy."
        else:
            level = "CRITICAL"
            title = "Critical Warning - Extreme Scam Danger"
            summary = "High probability of counterfeit goods, hijacked listing, or fraudulent fulfillment. Do not complete purchase without unboxing protection."

        safety_checklist = [
            "Inspect outer shipping box seals before sharing the delivery OTP with courier.",
            "Record a continuous unboxing video showing the shipping label and sealed packaging.",
            "Verify product IMEI / Serial Number against manufacturer warranty portal upon unboxing.",
            "Confirm that replacement/return window is open before discarding packaging materials."
        ]

        return ScamRiskAssessment(
            risk_score=final_score,
            risk_level=level,
            verdict_title=title,
            verdict_summary=summary,
            positive_safety_signals=positive_signals,
            warning_flags=warning_flags,
            safety_checklist=safety_checklist
        )
