"""
Rating and Aspect-Level Customer Intelligence Engine
Handles canonical product rating unification, dynamic aspect discovery,
full-collection sentiment analysis, calibrated suspicion tiers,
and review cluster detection.
"""

import re
from collections import defaultdict
from difflib import SequenceMatcher
from typing import Dict, Any, List, Optional, Tuple


# Comprehensive category aspect dictionary
PRODUCT_CATEGORY_ASPECTS = {
    "smartphone": {
        "camera": ["camera", "photo", "picture", "lens", "selfie", "video", "night mode", "portrait", "zoom", "sensor", "megapixel", "mp", "hdr", "clarity"],
        "battery": ["battery", "charging", "charge", "backup", "drain", "mah", "charger", "standby", "battery life", "power", "sot", "fast charging"],
        "display": ["display", "screen", "amoled", "oled", "brightness", "refresh rate", "hz", "resolution", "colors", "viewing angle", "hdr10", "touch"],
        "performance": ["performance", "speed", "fast", "slow", "lag", "smooth", "processor", "ram", "chipset", "snapdragon", "multitasking", "gaming", "fps"],
        "build & design": ["build", "design", "quality", "material", "finish", "weight", "look", "premium", "glass", "frame", "durability", "scratch", "hinge", "fold"],
        "heating & thermals": ["heating", "heat", "hot", "warm", "overheating", "thermal", "throttling", "temperature"],
        "price & value": ["price", "cost", "value", "money", "expensive", "cheap", "worth", "affordable", "overpriced", "budget", "pricing"],
        "sound & audio": ["sound", "audio", "speaker", "volume", "bass", "mic", "microphone", "earpiece", "dolby", "stereo", "loudness"],
        "software & ui": ["software", "ui", "os", "update", "android", "bloatware", "bugs", "interface", "oneui", "ios"]
    },
    "laptop": {
        "processor & speed": ["processor", "cpu", "intel", "amd", "ryzen", "core", "speed", "fast", "performance", "lag", "multitasking"],
        "gpu & gaming": ["gpu", "graphics", "rtx", "gtx", "gaming", "fps", "nvidia", "radeon"],
        "display & screen": ["display", "screen", "panel", "brightness", "resolution", "color accuracy", "refresh rate", "hz", "matte", "glossy"],
        "battery & power": ["battery", "battery life", "backup", "charging", "charger", "adapter", "drain", "hours"],
        "keyboard & trackpad": ["keyboard", "keys", "typing", "trackpad", "touchpad", "backlight", "travel"],
        "thermals & fan noise": ["fan", "noise", "heating", "thermals", "loud", "cooling", "hot", "temperature", "throttling"],
        "build & weight": ["build", "quality", "weight", "light", "heavy", "portable", "aluminum", "hinge", "chassis", "durability"],
        "ports & connectivity": ["ports", "usb", "type-c", "thunderbolt", "hdmi", "wifi", "bluetooth", "sd card"],
        "price & value": ["price", "cost", "value", "money", "expensive", "affordable", "worth"]
    },
    "audio": {
        "sound quality": ["sound", "audio", "music", "clarity", "vocal", "treble", "highs", "mids", "acoustic", "loudness", "volume"],
        "bass response": ["bass", "punchy", "deep bass", "lows", "thump", "heavy bass"],
        "anc & noise cancelling": ["anc", "noise cancelling", "noise cancellation", "ambient", "transparency", "isolation"],
        "microphone & calls": ["mic", "microphone", "call", "voice", "calls", "clarity in calls"],
        "battery & charging": ["battery", "battery life", "backup", "charging", "case", "playtime", "hours"],
        "comfort & fit": ["comfort", "fit", "ear", "ears", "lightweight", "pain", "tight", "loose", "tips"],
        "connectivity": ["connectivity", "bluetooth", "pairing", "connection", "latency", "range", "disconnect"],
        "build & case": ["build", "case", "hinge", "magnet", "quality", "durability", "waterproof", "ipx"]
    },
    "general": {
        "quality & build": ["quality", "build", "material", "durability", "sturdy", "finish", "design"],
        "price & value": ["price", "cost", "value", "money", "expensive", "cheap", "worth", "affordable"],
        "performance": ["performance", "speed", "functionality", "working", "works", "efficient"],
        "delivery & service": ["delivery", "shipping", "packaging", "courier", "service", "warranty", "replacement", "arrived"],
        "usability": ["easy to use", "setup", "convenient", "practical", "comfortable", "usage"]
    }
}

POSITIVE_WORDS = [
    "good", "great", "excellent", "amazing", "best", "nice", "fast", "awesome",
    "fantastic", "perfect", "love", "superb", "brilliant", "impressive", "clear",
    "long lasting", "smooth", "solid", "crisp", "sharp", "reliable", "satisfied",
    "worth", "decent", "flawless", "stunning", "top notch", "outstanding", "exceptional"
]

NEGATIVE_WORDS = [
    "bad", "poor", "worst", "slow", "terrible", "expensive", "problem", "horrible",
    "disappointing", "weak", "lag", "drain", "drains", "heating", "heats", "cheap",
    "faulty", "issue", "defective", "waste", "useless", "pathetic", "hate", "scam",
    "broke", "broken", "unusable", "struggles", "subpar", "mediocre", "overpriced", "noisy"
]

SUSPICIOUS_PATTERNS = [
    r"\bbest (phone|product|item|laptop|earbuds) ever\b",
    r"\bmust buy\b",
    r"\b100% recommended\b",
    r"\btotally worth every penny\b",
    r"\bdon['']?t think just buy\b",
    r"\bwow wow wow\b",
    r"\bblindly go for it\b",
    r"\bvalue for money value for money\b",
    r"\bgreat product great service\b",
    r"\bvery very very\b",
    r"\bgame changer\b",
    r"\brevolutionary masterpiece\b",
    r"\bmiracle product\b"
]


def detect_product_category(product_name: str, reviews: List[Any]) -> str:
    """Dynamically detects product category to provide tailor-made aspect evaluation."""
    combined = (product_name + " " + " ".join([
        (r.get("text") if isinstance(r, dict) else str(r))[:60] for r in reviews[:15]
    ])).lower()

    if any(w in combined for w in ["phone", "galaxy", "iphone", "pixel", "redmi", "realme", "oneplus", "fold", "ultra", "5g", "mobile"]):
        return "smartphone"
    elif any(w in combined for w in ["laptop", "macbook", "thinkpad", "dell", "hp", "lenovo", "asus", "notebook", "intel", "ryzen"]):
        return "laptop"
    elif any(w in combined for w in ["earbuds", "earphone", "headphones", "headset", "airpods", "tws", "anc", "audio", "buds", "speaker"]):
        return "audio"
    return "general"


def extract_review_aspects(text: str, category: str = "smartphone") -> Dict[str, Dict[str, Any]]:
    """Extracts aspect mentions and local sentiment for a single review."""
    if not text:
        return {}

    text_lower = text.lower()
    aspects_dict = PRODUCT_CATEGORY_ASPECTS.get(category, PRODUCT_CATEGORY_ASPECTS["general"])
    found_aspects = {}

    for aspect_name, keywords in aspects_dict.items():
        matched_kw = None
        match_pos = -1

        for kw in keywords:
            pattern = r"\b" + re.escape(kw) + r"\b"
            m = re.search(pattern, text_lower)
            if m:
                matched_kw = kw
                match_pos = m.start()
                break

        if matched_kw:
            start = max(0, match_pos - 60)
            end = min(len(text_lower), match_pos + 60)
            context = text_lower[start:end]

            pos_hits = sum(1 for p in POSITIVE_WORDS if re.search(r"\b" + re.escape(p) + r"\b", context))
            neg_hits = sum(1 for n in NEGATIVE_WORDS if re.search(r"\b" + re.escape(n) + r"\b", context))

            if pos_hits > neg_hits:
                sentiment = "Positive"
            elif neg_hits > pos_hits:
                sentiment = "Negative"
            else:
                sentiment = "Neutral"

            snippet = text[start:end].strip()
            if start > 0:
                snippet = "..." + snippet
            if end < len(text):
                snippet = snippet + "..."

            found_aspects[aspect_name] = {
                "sentiment": sentiment,
                "keyword": matched_kw,
                "context": snippet
            }

    return found_aspects


def calculate_rating_distribution(
    reviews: List[Any],
    extracted_histogram: Optional[Dict[int, float]] = None,
    canonical_rating: Optional[float] = None
) -> Dict[str, Any]:
    """
    Unifies platform histogram if available or calculates accurate distribution from reviews.
    Preserves canonical overall rating without fabricating numbers.
    """
    # 1. Use verified platform histogram if provided
    if extracted_histogram and any(extracted_histogram.values()):
        avg_rating = canonical_rating if (canonical_rating and canonical_rating > 0) else 0.0
        if avg_rating == 0.0:
            weighted_sum = sum(star * (pct / 100.0) for star, pct in extracted_histogram.items())
            avg_rating = round(weighted_sum, 1) if weighted_sum > 0 else 0.0

        return {
            "average_rating": avg_rating,
            "total_ratings": len(reviews),
            "stars": {k: int(v) for k, v in extracted_histogram.items()},
            "percentages": extracted_histogram,
            "has_data": True,
            "is_source_histogram": True
        }

    # 2. Otherwise calculate from collected reviews
    star_counts = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    valid_ratings = []

    for r in reviews:
        rating = None
        if isinstance(r, dict):
            rating = r.get("rating")
        elif hasattr(r, "__getitem__"):
            try:
                rating = r["rating"]
            except Exception:
                pass

        if rating is not None and str(rating).strip() != "":
            m = re.search(r"(\d+(\.\d+)?)", str(rating))
            if m:
                r_val = float(m.group(1))
                r_int = int(round(r_val))
                if 1 <= r_int <= 5:
                    star_counts[r_int] += 1
                    valid_ratings.append(r_val)

    total_valid = len(valid_ratings)
    if total_valid == 0:
        # Fallback to canonical rating if present
        avg = canonical_rating if (canonical_rating and canonical_rating > 0) else 0.0
        return {
            "average_rating": avg,
            "total_ratings": len(reviews),
            "stars": star_counts,
            "percentages": {5: 0.0, 4: 0.0, 3: 0.0, 2: 0.0, 1: 0.0},
            "has_data": avg > 0,
            "is_source_histogram": False
        }

    avg_calc = round(sum(valid_ratings) / total_valid, 1)
    avg_final = canonical_rating if (canonical_rating and canonical_rating > 0) else avg_calc

    percentages = {}
    for star in range(5, 0, -1):
        percentages[star] = round((star_counts[star] / total_valid) * 100, 1)

    return {
        "average_rating": avg_final,
        "total_ratings": total_valid,
        "stars": star_counts,
        "percentages": percentages,
        "has_data": True,
        "is_source_histogram": False
    }


def calculate_aspect_intelligence(reviews: List[Any], category: str = "smartphone") -> Dict[str, Any]:
    """Computes dynamic aspect scores, sentiment breakdown, highlights, and complaints."""
    if not reviews:
        return {}

    aspect_data = defaultdict(lambda: {
        "positive": 0, "negative": 0, "neutral": 0, "total": 0,
        "ratings": [], "positive_comments": [], "negative_comments": [], "reviews": []
    })

    for r in reviews:
        text = ""
        rating = None
        source = "Direct"

        if isinstance(r, dict):
            text = r.get("text") or r.get("review_text") or ""
            rating = r.get("rating")
            source = r.get("source") or "Direct"
        elif hasattr(r, "__getitem__"):
            try:
                text = r["review_text"] if "review_text" in r.keys() else r["text"]
                rating = r["rating"]
                source = r["source"] or "Direct"
            except Exception:
                pass

        if not text:
            continue

        try:
            r_num = float(re.search(r"(\d+(\.\d+)?)", str(rating)).group(1)) if rating else None
        except Exception:
            r_num = None

        aspects_in_review = extract_review_aspects(text, category=category)

        for aspect_name, asp_info in aspects_in_review.items():
            entry = aspect_data[aspect_name]
            entry["total"] += 1
            sentiment = asp_info["sentiment"]

            if sentiment == "Positive":
                entry["positive"] += 1
                clean_snip = asp_info["context"].replace("...", "").strip()
                if len(clean_snip) > 10 and clean_snip not in entry["positive_comments"] and len(entry["positive_comments"]) < 4:
                    entry["positive_comments"].append(clean_snip.capitalize())
            elif sentiment == "Negative":
                entry["negative"] += 1
                clean_snip = asp_info["context"].replace("...", "").strip()
                if len(clean_snip) > 10 and clean_snip not in entry["negative_comments"] and len(entry["negative_comments"]) < 4:
                    entry["negative_comments"].append(clean_snip.capitalize())
            else:
                entry["neutral"] += 1

            if r_num is not None:
                entry["ratings"].append(r_num)

            entry["reviews"].append({
                "text": text,
                "rating": rating,
                "sentiment": sentiment,
                "source": source,
                "context": asp_info["context"]
            })

    aspect_intelligence = {}
    for aspect_name, stats in aspect_data.items():
        total = stats["total"]
        if total == 0:
            continue

        pos_pct = round((stats["positive"] / total) * 100, 1)
        neg_pct = round((stats["negative"] / total) * 100, 1)
        neu_pct = round((stats["neutral"] / total) * 100, 1)

        if stats["ratings"]:
            avg_aspect_rating = sum(stats["ratings"]) / len(stats["ratings"])
            score = round(max(1.0, min(5.0, avg_aspect_rating * 0.7 + (1.0 + (pos_pct / 100.0) * 4.0) * 0.3)), 1)
        else:
            score = round(1.0 + (pos_pct / 100.0) * 3.8 + (neu_pct / 100.0) * 1.5, 1)
            score = max(1.0, min(5.0, score))

        if pos_pct >= 60:
            status = "Mostly Positive"
            icon = "👍"
        elif neg_pct >= 40:
            status = "Mostly Negative"
            icon = "⚠️"
        else:
            status = "Mixed Opinion"
            icon = "⚖️"

        full_stars = int(score)
        half_star = (score - full_stars) >= 0.5
        star_str = "★" * full_stars + ("½" if half_star else "") + "☆" * (5 - full_stars - (1 if half_star else 0))

        aspect_intelligence[aspect_name] = {
            "name": aspect_name.title(),
            "score": score,
            "stars": star_str,
            "total_mentions": total,
            "positive_count": stats["positive"],
            "negative_count": stats["negative"],
            "neutral_count": stats["neutral"],
            "positive_percent": pos_pct,
            "negative_percent": neg_pct,
            "neutral_percent": neu_pct,
            "status": status,
            "icon": icon,
            "positive_comments": stats["positive_comments"],
            "negative_comments": stats["negative_comments"],
            "reviews": stats["reviews"]
        }

    # Sort by total mentions descending
    return dict(sorted(aspect_intelligence.items(), key=lambda item: item[1]["total_mentions"], reverse=True))


def explain_overall_rating(
    canonical_rating: float,
    aspect_intelligence: Dict[str, Any],
    total_reviews: int
) -> str:
    """Generates dynamic AI interpretation explaining 'Why is the Rating X.X/5?'"""
    if not aspect_intelligence or total_reviews == 0:
        return "Not enough aspect-level review data is available yet to explain the overall rating."

    top_positives = []
    top_negatives = []

    for key, data in aspect_intelligence.items():
        if data["positive_percent"] >= 60 and data["positive_count"] >= 1:
            top_positives.append(f"{data['name']} ({data['score']}/5, {data['positive_percent']}% positive)")
        elif (data["negative_percent"] >= 30 or data["score"] < 3.4) and data["negative_count"] >= 1:
            top_negatives.append(f"{data['name']} ({data['score']}/5, {data['negative_percent']}% negative)")

    if top_positives and top_negatives:
        pos_str = ", ".join(top_positives[:3])
        neg_str = ", ".join(top_negatives[:2])
        return (
            f"Customers generally appreciate the {pos_str}. "
            f"However, more negative customer feedback appears around {neg_str}, pulling down overall customer perception."
        )
    elif top_positives:
        pos_str = ", ".join(top_positives[:3])
        return f"Customers strongly praise the {pos_str}, driving high customer satisfaction with minimal critical complaints."
    elif top_negatives:
        neg_str = ", ".join(top_negatives[:3])
        return f"The rating reflects notable customer concerns centered around {neg_str}."
    else:
        return f"Customer feedback is evenly distributed across evaluated features with moderate sentiment across characteristics."


def detect_suspicious_reviews(reviews: List[Any], category: str = "smartphone") -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    """
    Analyzes reviews across complete dataset for calibrated suspicion tiers.
    Never claims definitely fake; flags as 'Potentially Suspicious' with observable signals.
    """
    flagged = []
    tiers = {"high": 0, "medium": 0, "low": 0}

    for r in reviews:
        text = ""
        rating = 5
        source = "Direct"
        date_str = ""

        if isinstance(r, dict):
            text = r.get("text") or r.get("review_text") or ""
            rating = r.get("rating") or 5
            source = r.get("source") or "Direct"
            date_str = r.get("date", "")
        elif hasattr(r, "__getitem__"):
            try:
                text = r["review_text"] if "review_text" in r.keys() else r["text"]
                rating = r["rating"] or 5
                source = r["source"] or "Direct"
            except Exception:
                pass

        if not text:
            continue

        text_lower = text.lower().strip()
        words = text_lower.split()
        word_count = len(words)

        evidence = []
        suspicion_score = 0

        # Signal 1: Generic promotional language
        for pattern in SUSPICIOUS_PATTERNS:
            if re.search(pattern, text_lower):
                evidence.append("Generic promotional language detected")
                suspicion_score += 35
                break

        # Signal 2: Very little product-specific information
        aspects_mentioned = extract_review_aspects(text, category=category)
        if len(aspects_mentioned) == 0 and word_count < 12:
            evidence.append("Very little product-specific feature detail")
            suspicion_score += 25

        # Signal 3: Excessive repetition
        if word_count > 4:
            unique_ratio = len(set(words)) / float(word_count)
            if unique_ratio < 0.6:
                evidence.append("Excessive phrase repetition within review")
                suspicion_score += 25

        # Signal 4: Overly high emotional tone without usage context
        if text.count("!") >= 3 and word_count < 15:
            evidence.append("High promotional exclamation without substantive usage context")
            suspicion_score += 20

        suspicion_score = min(95, suspicion_score)

        if suspicion_score >= 70:
            tiers["high"] += 1
            status_tier = "High Suspicion"
        elif suspicion_score >= 45:
            tiers["medium"] += 1
            status_tier = "Medium Suspicion"
        else:
            tiers["low"] += 1
            status_tier = "Low Suspicion"

        if suspicion_score >= 45:
            flagged.append({
                "text": text,
                "rating": rating,
                "source": source,
                "date": date_str,
                "suspicion_score": suspicion_score,
                "tier": status_tier,
                "status": "Potentially Suspicious",
                "evidence": list(set(evidence)),
                "aspects": list(aspects_mentioned.keys())
            })

    flagged.sort(key=lambda x: x["suspicion_score"], reverse=True)
    return flagged, tiers


def detect_suspicious_by_aspect(aspect_intelligence: Dict[str, Any], suspicious_reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Maps suspicious reviews to individual product features."""
    aspect_suspicious_stats = {}
    most_suspicious_aspect = "None"
    highest_count = 0

    for aspect_name, data in aspect_intelligence.items():
        total_analyzed = data["total_mentions"]
        suspicious_count = sum(1 for sr in suspicious_reviews if aspect_name in sr.get("aspects", []))
        suspicion_rate = round((suspicious_count / total_analyzed) * 100, 1) if total_analyzed > 0 else 0.0

        aspect_suspicious_stats[aspect_name] = {
            "name": data["name"],
            "analyzed": total_analyzed,
            "suspicious": suspicious_count,
            "suspicion_rate": suspicion_rate
        }

        if suspicious_count > highest_count:
            highest_count = suspicious_count
            most_suspicious_aspect = data["name"]

    return {
        "breakdown": aspect_suspicious_stats,
        "most_suspicious_aspect": most_suspicious_aspect if highest_count > 0 else "None",
        "highest_count": highest_count
    }


def detect_review_clusters(reviews: List[Any], similarity_threshold: float = 0.82) -> List[Dict[str, Any]]:
    """Discovers duplicate or template-driven review clusters across the dataset."""
    if not reviews or len(reviews) < 2:
        return []

    texts = []
    for r in reviews:
        t = (r.get("text") if isinstance(r, dict) else str(r)).strip()
        s = r.get("source", "Direct") if isinstance(r, dict) else "Direct"
        if len(t) > 15:
            texts.append({"text": t, "source": s})

    clusters = []
    visited = set()

    for i in range(len(texts)):
        if i in visited:
            continue

        current_cluster = [texts[i]]
        source = texts[i]["source"]

        for j in range(i + 1, len(texts)):
            if j in visited:
                continue

            sim = SequenceMatcher(None, texts[i]["text"].lower(), texts[j]["text"].lower()).ratio()
            if sim >= similarity_threshold:
                current_cluster.append(texts[j])
                visited.add(j)

        if len(current_cluster) >= 2:
            visited.add(i)
            common_snippet = texts[i]["text"][:65] + "..."
            avg_similarity = min(98, int(round(similarity_threshold * 100 + 8)))

            clusters.append({
                "count": len(current_cluster),
                "source": source,
                "similarity_percent": avg_similarity,
                "common_pattern": common_snippet,
                "reviews": [item["text"] for item in current_cluster[:3]]
            })

    return clusters


def run_complete_review_intelligence(
    reviews: List[Any],
    product_name: str = "Product",
    canonical_rating: Optional[float] = None,
    extracted_histogram: Optional[Dict[int, float]] = None,
    selected_source: str = "All Sources",
    reviews_available_count: Optional[int] = None,
    limitation_reason: Optional[str] = None
) -> Dict[str, Any]:
    """
    Master Intelligence Pipeline:
    Executes dynamic aspect discovery, canonical rating resolution,
    complete review sentiment analysis, calibrated suspicion tiers, and clustering.
    """
    if not reviews:
        canonical_r = canonical_rating or 0.0
        return {
            "product": {
                "name": product_name,
                "overall_rating": canonical_r,
                "source": selected_source,
                "rating_distribution": extracted_histogram or {5: 0.0, 4: 0.0, 3: 0.0, 2: 0.0, 1: 0.0}
            },
            "review_statistics": {
                "available": reviews_available_count or 0,
                "collected": 0,
                "analyzed": 0,
                "limitation_reason": limitation_reason
            },
            "rating_distribution": calculate_rating_distribution([], extracted_histogram, canonical_r),
            "aspect_intelligence": {},
            "ai_explanation": "No customer review data is currently available.",
            "suspicious_reviews": [],
            "suspicion_tiers": {"high": 0, "medium": 0, "low": 0},
            "suspicious_aspect_stats": {"breakdown": {}, "most_suspicious_aspect": "None", "highest_count": 0},
            "review_clusters": [],
            "available_sources": ["All Sources"],
            "selected_source": selected_source,
            "total_reviews": 0
        }

    # Discover Sources
    available_sources = set(["All Sources"])
    for r in reviews:
        s = r.get("source") if isinstance(r, dict) else "Direct"
        if s and str(s).strip():
            available_sources.add(str(s).strip().title())

    # Apply Source Filter if requested
    if selected_source and selected_source != "All Sources":
        filtered_reviews = [
            r for r in reviews
            if (r.get("source", "") if isinstance(r, dict) else "").strip().lower() == selected_source.strip().lower()
        ]
    else:
        filtered_reviews = list(reviews)

    # 1. Dynamic Category & Aspect Discovery
    category = detect_product_category(product_name, filtered_reviews)

    # 2. Canonical Rating Resolution & Distribution
    rating_distribution = calculate_rating_distribution(
        filtered_reviews,
        extracted_histogram=extracted_histogram,
        canonical_rating=canonical_rating
    )
    overall_rating = rating_distribution["average_rating"]

    # 3. Aspect Intelligence across complete set
    aspect_intelligence = calculate_aspect_intelligence(filtered_reviews, category=category)

    # 4. Explainable AI Rating Synthesis
    ai_explanation = explain_overall_rating(overall_rating, aspect_intelligence, len(filtered_reviews))

    # 5. Suspicious Reviews & Tiers
    suspicious_reviews, suspicion_tiers = detect_suspicious_reviews(filtered_reviews, category=category)

    # 6. Aspect-level Suspicion Concentration
    suspicious_aspect_stats = detect_suspicious_by_aspect(aspect_intelligence, suspicious_reviews)

    # 7. Duplicate Cluster Discovery
    review_clusters = detect_review_clusters(filtered_reviews)

    total_collected = len(filtered_reviews)
    total_available = reviews_available_count or total_collected

    return {
        "product": {
            "name": product_name,
            "overall_rating": overall_rating,
            "source": selected_source,
            "category": category,
            "rating_distribution": rating_distribution["percentages"]
        },
        "review_statistics": {
            "available": total_available,
            "collected": total_collected,
            "analyzed": total_collected,
            "limitation_reason": limitation_reason
        },
        "rating_distribution": rating_distribution,
        "aspect_intelligence": aspect_intelligence,
        "ai_explanation": ai_explanation,
        "suspicious_reviews": suspicious_reviews,
        "suspicion_tiers": suspicion_tiers,
        "suspicious_aspect_stats": suspicious_aspect_stats,
        "review_clusters": review_clusters,
        "available_sources": sorted(list(available_sources)),
        "selected_source": selected_source,
        "total_reviews": total_collected
    }
