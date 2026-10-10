"""
Variant-Isolated Product Matching Service.
Prevents erroneous comparisons across diverging storage, RAM, or generation configurations.
"""

import re
from typing import Dict, Any, Tuple, List, Optional


class ProductMatcher:
    """Evaluates cross-platform product identity and variant conformity."""

    STORAGE_PATTERN = re.compile(r"\b(\d{1,4})\s*(gb|tb)\b", re.IGNORECASE)
    RAM_PATTERN = re.compile(r"\b(\d{1,2})\s*gb\s*(?:ram)?\b", re.IGNORECASE)
    MODEL_NUM_PATTERN = re.compile(r"\b([a-z0-9]{2,10}-[a-z0-9]{2,10})\b", re.IGNORECASE)

    @classmethod
    def extract_spec_tokens(cls, title: str) -> Dict[str, Any]:
        """Extracts key hardware and variant tokens from raw title."""
        text = (title or "").lower().strip()
        # Separate numeric values from units (e.g. 128gb -> 128 gb, 8gb -> 8 gb)
        text = re.sub(r"(\d+)(gb|tb|mb|hz|mp)\b", r"\1 \2", text)

        # Strip marketplace boilerplate
        text = re.sub(r"\b(add to compare|ratings?|reviews?|free delivery|bank offer)\b", " ", text, flags=re.IGNORECASE)

        # Storage capacity
        storages = cls.STORAGE_PATTERN.findall(text)
        storage_val = f"{storages[0][0]}{storages[0][1].upper()}" if storages else None

        # Generation / numeric token
        gen_match = re.search(r"\b(iphone|galaxy|pixel|oneplus|thinkpad|macbook|ipad)\s*([a-z0-9\s\+]+?)(?=\b(?:\d+gb|5g|4g|,|\(|$))", text)
        core_model = gen_match.group(0).strip() if gen_match else ""

        # Condition
        is_refurbished = any(w in text for w in ["refurbished", "renewed", "pre-owned", "unboxed"])

        return {
            "storage": storage_val,
            "core_model": core_model,
            "is_refurbished": is_refurbished,
            "raw_text": text
        }

    @classmethod
    def evaluate_match(
        cls,
        source_title: str,
        target_title: str,
        source_sku: Optional[str] = None,
        target_sku: Optional[str] = None
    ) -> Tuple[str, float, List[str]]:
        """
        Determines matching confidence:
        Returns (confidence_level, similarity_score, spec_deltas)
        Confidence: "EXACT" | "HIGH" | "UNCERTAIN" | "MISMATCH"
        """
        if not source_title or not target_title:
            return "UNCERTAIN", 0.0, ["Missing product specification"]

        # 1. Exact SKU Identity
        if source_sku and target_sku and source_sku.upper() == target_sku.upper():
            return "EXACT", 1.0, []

        specs_a = cls.extract_spec_tokens(source_title)
        specs_b = cls.extract_spec_tokens(target_title)

        deltas = []

        # 2. Condition Mismatch (Brand New vs. Renewed/Refurbished)
        if specs_a["is_refurbished"] != specs_b["is_refurbished"]:
            deltas.append("Condition mismatch (Brand New vs. Refurbished/Renewed)")
            return "MISMATCH", 0.1, deltas

        # 3. Storage Variant Check
        if specs_a["storage"] and specs_b["storage"]:
            if specs_a["storage"] != specs_b["storage"]:
                deltas.append(f"Storage capacity diverged: {specs_a['storage']} vs {specs_b['storage']}")
                return "MISMATCH", 0.2, deltas

        # 4. Word Token Jaccard Overlap & Containment
        words_a = set(re.findall(r"\b[a-z0-9]{3,}\b", specs_a["raw_text"]))
        words_b = set(re.findall(r"\b[a-z0-9]{3,}\b", specs_b["raw_text"]))

        if not words_a or not words_b:
            return "UNCERTAIN", 0.5, ["Insufficient token representation"]

        intersection = words_a.intersection(words_b)
        union = words_a.union(words_b)
        jaccard = len(intersection) / len(union) if union else 0.0

        smaller = words_a if len(words_a) <= len(words_b) else words_b
        containment = len(intersection) / len(smaller) if smaller else 0.0

        if deltas:
            return "MISMATCH", jaccard, deltas

        if jaccard >= 0.70 or containment >= 0.75:
            return "EXACT", max(jaccard, containment), []
        elif jaccard >= 0.50 or containment >= 0.60:
            return "HIGH", max(jaccard, containment), []
        elif jaccard >= 0.35:
            return "UNCERTAIN", jaccard, ["Partial title token overlap"]
        else:
            return "MISMATCH", jaccard, ["Substantially divergent product titles"]
