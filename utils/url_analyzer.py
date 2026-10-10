"""
Product URL Analyzer wrapper.
Delegates collection to modular CollectorFactory, performs security and authenticity checks,
and normalizes outputs.
"""

from urllib.parse import urlparse
from typing import Dict, Any

from collectors import CollectorFactory


def analyze_product_url(url: str) -> Dict[str, Any]:
    try:
        url = (url or "").strip()
        if url and not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url

        parsed_url = urlparse(url)
        if parsed_url.scheme not in ["http", "https"] or not parsed_url.netloc:
            return {
                "success": False,
                "message": "Please enter a valid HTTP or HTTPS product URL."
            }

        domain = parsed_url.netloc.lower()
        collector = CollectorFactory.get_collector(url)
        result = collector.collect(url)

        product_name = result.get("product_name", "Unknown Product")
        reviews = result.get("reviews", [])
        overall_rating = result.get("overall_rating", 0.0)
        source = result.get("source", "Web")
        has_distribution = result.get("has_distribution", False)
        rating_distribution = result.get("rating_distribution", {})

        authenticity = check_authenticity(
            url=url,
            domain=domain,
            product_name=product_name,
            reviews=reviews
        )

        return {
            "success": True,
            "url": url,
            "product_name": product_name,
            "domain": domain,
            "source_name": source,
            "overall_rating": overall_rating,
            "reviews_available": result.get("reviews_available", len(reviews)),
            "reviews_collected": result.get("reviews_collected", len(reviews)),
            "reviews_analyzed": result.get("reviews_analyzed", len(reviews)),
            "limitation_reason": result.get("limitation_reason"),
            "has_distribution": has_distribution,
            "rating_distribution": rating_distribution,
            "reviews": reviews,
            "review_count": len(reviews),
            "authenticity": authenticity
        }

    except Exception as error:
        return {
            "success": False,
            "message": f"Analysis failed: {str(error)}"
        }


def check_authenticity(
    url: str,
    domain: str,
    product_name: str,
    reviews: list
) -> Dict[str, Any]:
    score = 0
    warnings = []
    checks = []

    parsed_url = urlparse(url)

    # 1. HTTPS Security
    if parsed_url.scheme == "https":
        score += 25
        checks.append({
            "name": "HTTPS Security",
            "status": "pass",
            "message": "The webpage uses HTTPS encryption."
        })
    else:
        warnings.append("The webpage does not use HTTPS.")
        checks.append({
            "name": "HTTPS Security",
            "status": "warning",
            "message": "The webpage does not use HTTPS."
        })

    # 2. Known E-Commerce Domain Check
    if any(k in domain for k in ["amazon", "flipkart", "myntra", "walmart", "bestbuy", "target"]):
        score += 35
        checks.append({
            "name": "Verified Marketplace Domain",
            "status": "pass",
            "message": f"Established platform detected: {domain}"
        })
    elif domain:
        score += 20
        checks.append({
            "name": "Domain Recognition",
            "status": "pass",
            "message": f"Accessible domain: {domain}"
        })
    else:
        warnings.append("Domain information unavailable.")
        checks.append({
            "name": "Domain",
            "status": "warning",
            "message": "Domain information unavailable."
        })

    # 3. Product Info Extraction Check
    if product_name and product_name != "Unknown Product":
        score += 20
        checks.append({
            "name": "Product Title Extraction",
            "status": "pass",
            "message": "Valid product metadata verified."
        })
    else:
        warnings.append("Could not extract standard product metadata.")
        checks.append({
            "name": "Product Metadata",
            "status": "warning",
            "message": "Product metadata was minimal or unindexed."
        })

    # 4. Review Content Presence
    if len(reviews) >= 5:
        score += 20
        checks.append({
            "name": "Customer Review Volume",
            "status": "pass",
            "message": f"Found {len(reviews)} accessible review records."
        })
    elif len(reviews) > 0:
        score += 10
        checks.append({
            "name": "Customer Review Volume",
            "status": "pass",
            "message": f"Found {len(reviews)} accessible review records."
        })
    else:
        checks.append({
            "name": "Customer Review Volume",
            "status": "warning",
            "message": "No direct customer reviews were extracted."
        })

    # Score calculation & risk level
    score = min(100, score)
    if score >= 75:
        risk_level = "LOW"
        message = "Webpage and platform credentials meet standard authenticity requirements."
    elif score >= 50:
        risk_level = "MEDIUM"
        message = "Moderate confidence. Minor verification elements were incomplete."
    else:
        risk_level = "HIGH"
        message = "High risk or unverified merchant platform."

    return {
        "available": True,
        "risk_level": risk_level,
        "score": score,
        "checks": checks,
        "warnings": warnings,
        "message": message
    }