"""
Amazon Review Collector with multi-page pagination, star histogram extraction,
verified purchase detection, and source limitation reporting.

Fixes applied (2026-10-03):
- Extract embedded reviews from product page using correct Amazon.in data-hooks
  (reviewText / reviewTitle instead of review-body / review-title)
- Detect sign-in page redirect on review pagination and stop gracefully
- Parse rating distribution via filterByStar links (the approach that actually
  works on Amazon.in product pages)
- Report accurate limitation_reason when full pagination is blocked
- Clean "Brief content visible..." / "Read moreRead less" artefacts from bodies
"""

import re
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from typing import Dict, Any, List, Tuple

from .base_collector import BaseCollector


class AmazonCollector(BaseCollector):
    def __init__(self, max_pages: int = 10, timeout: int = 15):
        super().__init__(timeout=timeout)
        self.max_pages = max_pages

    # ------------------------------------------------------------------ helpers
    def extract_asin(self, url: str) -> str:
        patterns = [
            r"/dp/([A-Z0-9]{10})",
            r"/gp/product/([A-Z0-9]{10})",
            r"/gp/aw/d/([A-Z0-9]{10})",
            r"/product-reviews/([A-Z0-9]{10})",
            r"/ASIN/([A-Z0-9]{10})",
            r"[?&]asin=([A-Z0-9]{10})"
        ]
        for p in patterns:
            m = re.search(p, url, re.IGNORECASE)
            if m:
                return m.group(1).upper()
        return ""

    def _is_signin_page(self, resp: requests.Response) -> bool:
        """Return True if Amazon redirected the request to its sign-in wall."""
        if "ap/signin" in resp.url:
            return True
        # Quick title check (first 4 KB is enough)
        if "<title>Sign in" in resp.text[:4096] or "<title> Sign in" in resp.text[:4096]:
            return True
        return False

    def _clean_body(self, text: str) -> str:
        """Strip Amazon's accessibility/navigation artefacts from review text."""
        if not text:
            return text
        for pat in [
            r"Brief content visible, double tap to read full content\.\s*",
            r"Full content visible, double tap to read brief content\.\s*",
            r"Read more\s*Read less\s*$",
            r"Read more\s*$",
        ]:
            text = re.sub(pat, "", text)
        return text.strip()

    # ------------------------------------------------------- product-page parse
    def _extract_product_name(self, soup: BeautifulSoup) -> str:
        elem = soup.select_one("#productTitle") or soup.select_one("#title")
        if elem:
            return self.normalize_text(elem.get_text())
        meta = soup.select_one('meta[property="og:title"]')
        if meta and meta.get("content"):
            return self.normalize_text(meta["content"])
        h1 = soup.select_one("h1")
        if h1:
            return self.normalize_text(h1.get_text())
        return "Amazon Product"

    def _extract_ratings_meta(self, soup: BeautifulSoup) -> Tuple[float, int, int]:
        rating = 0.0
        ratings_count = 0
        reviews_count = 0

        # Try 1: span[data-hook="rating-out-of-text"]
        rate_elem = soup.select_one('[data-hook="rating-out-of-text"]')
        if rate_elem:
            m = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*out of 5", rate_elem.get_text())
            if m:
                try:
                    rating = round(float(m.group(1)), 1)
                except Exception:
                    pass

        # Try 2: i[data-hook="average-star-rating"]
        if rating == 0.0:
            rate_elem = soup.select_one('[data-hook="average-star-rating"]')
            if rate_elem:
                m = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*out of 5", rate_elem.get_text())
                if m:
                    try:
                        rating = round(float(m.group(1)), 1)
                    except Exception:
                        pass

        # Try 3: #acrPopover title attribute
        if rating == 0.0:
            acr = soup.select_one("#acrPopover")
            if acr:
                title_attr = acr.get("title", "")
                m = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*out of 5", title_attr)
                if m:
                    try:
                        rating = round(float(m.group(1)), 1)
                    except Exception:
                        pass

        # Ratings count – handles "(165)", "165 ratings", "1,247 ratings"
        count_elem = (
            soup.select_one("#acrCustomerReviewText")
            or soup.select_one('[data-hook="total-review-count"]')
        )
        if count_elem:
            c_text = count_elem.get_text()
            m = re.search(r"([0-9,]+)", c_text)
            if m:
                try:
                    ratings_count = int(m.group(1).replace(",", ""))
                except Exception:
                    pass

        # Also check JSON-LD structured data
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string or script.get_text() or "{}")
                items = data if isinstance(data, list) else [data]
                for item in items:
                    agg = item.get("aggregateRating")
                    if agg:
                        r_val = agg.get("ratingValue")
                        if r_val and rating == 0.0:
                            rating = round(float(r_val), 1)
                        r_count = agg.get("ratingCount") or agg.get("reviewCount")
                        if r_count and ratings_count == 0:
                            ratings_count = int(r_count)
            except Exception:
                continue

        return rating, ratings_count, reviews_count

    def _extract_histogram(self, soup: BeautifulSoup) -> Tuple[Dict[int, float], bool]:
        distribution: Dict[int, float] = {5: 0.0, 4: 0.0, 3: 0.0, 2: 0.0, 1: 0.0}
        has_data = False

        # Primary: filterByStar links (the approach that works on Amazon.in product pages)
        # Each link text contains all 5 percentages; the last one belongs to this star.
        star_names = {5: "five_star", 4: "four_star", 3: "three_star", 2: "two_star", 1: "one_star"}
        hist_links = soup.find_all("a", href=re.compile(r"filterByStar"))
        for link in hist_links:
            href = link.get("href", "")
            link_text = link.get_text(strip=True)
            for star, name in star_names.items():
                if name in href:
                    percentages = re.findall(r"(\d+)%", link_text)
                    if percentages:
                        distribution[star] = float(percentages[-1])
                        has_data = True
                    break

        # Fallback: histogram table rows
        if not has_data:
            rows = (
                soup.select("#histogramTable tr")
                or soup.select('[data-hook="histogram-row"]')
                or soup.select(".a-histogram-row")
            )
            for row in rows:
                text = row.get_text()
                star_m = re.search(r"(\d)\s*star", text, re.IGNORECASE)
                pct_m = re.search(r"(\d+)%", text)
                if star_m and pct_m:
                    star = int(star_m.group(1))
                    pct = float(pct_m.group(1))
                    if 1 <= star <= 5:
                        distribution[star] = pct
                        has_data = True

        # Fallback: aria-labels
        if not has_data:
            for link in soup.select("a[aria-label]"):
                label = link.get("aria-label", "")
                m = re.search(r"(\d+)%.*?(\d)\s*star", label, re.IGNORECASE)
                if m:
                    pct = float(m.group(1))
                    star = int(m.group(2))
                    if 1 <= star <= 5:
                        distribution[star] = pct
                        has_data = True

        return distribution, has_data

    # ---------------------------------------------------------- review parsing
    def _extract_review_blocks(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Parse all div[data-hook='review'] blocks in a page.
        Supports both the standard desktop hooks (review-title, review-body)
        AND Amazon.in's product-page hooks (reviewTitle, reviewText).
        """
        page_reviews: List[Dict[str, Any]] = []
        review_elements = soup.select('[data-hook="review"]')

        for elem in review_elements:
            # --- body: try all known hooks ---
            text = ""
            for hook in ("reviewText", "review-body", "review-text-content", "review-text"):
                body_elem = elem.select_one(f'[data-hook="{hook}"]')
                if not body_elem:
                    # also try without data-hook, by class
                    if hook == "review-text-content":
                        body_elem = elem.select_one(".review-text-content")
                if body_elem:
                    text = self._clean_body(self.normalize_text(body_elem.get_text()))
                    if text:
                        break
            if len(text) < 5:
                continue

            # --- title ---
            title = ""
            for hook in ("reviewTitle", "review-title"):
                title_elem = elem.select_one(f'[data-hook="{hook}"]')
                if title_elem:
                    title = self.normalize_text(title_elem.get_text())
                    break

            # --- rating ---
            rating = 5
            star_elem = (
                elem.select_one('[data-hook="review-star-rating"]')
                or elem.select_one(".a-icon-alt")
            )
            if star_elem:
                s_text = star_elem.get_text()
                s_m = re.search(r"([0-9]+(?:\.[0-9]+)?)", s_text)
                if s_m:
                    try:
                        rating = int(round(float(s_m.group(1))))
                    except Exception:
                        rating = 5

            # --- date ---
            date_str = ""
            date_elem = elem.select_one('[data-hook="review-date"]')
            if date_elem:
                date_str = self.normalize_text(date_elem.get_text())

            # --- verified purchase ---
            verified = False
            vp_elem = (
                elem.select_one('[data-hook="avp-badge"]')
                or elem.find(string=re.compile(r"Verified Purchase", re.I))
            )
            if vp_elem:
                verified = True

            page_reviews.append({
                "title": title,
                "text": text,
                "rating": rating,
                "date": date_str,
                "verified_purchase": verified,
                "source": "Amazon",
            })

        return page_reviews

    # --------------------------------------------------------------- main entry
    def collect(self, url: str) -> Dict[str, Any]:
        parsed = urlparse(url)
        domain = parsed.netloc.lower() or "www.amazon.in"
        asin = self.extract_asin(url)

        product_name = "Amazon Product"
        overall_rating = 0.0
        total_ratings_count = 0
        rating_distribution: Dict[int, float] = {5: 0.0, 4: 0.0, 3: 0.0, 2: 0.0, 1: 0.0}
        has_distribution = False
        limitation_reason = None
        collected_reviews: List[Dict[str, Any]] = []

        session = requests.Session()
        session.headers.update(self.headers)

        # ── Step 1: Product landing page ──────────────────────────────────────
        try:
            resp = session.get(url, timeout=self.timeout)
            if resp.status_code == 200:
                final_url = resp.url
                if final_url and final_url != url:
                    asin = self.extract_asin(final_url) or asin
                    final_domain = urlparse(final_url).netloc.lower()
                    if final_domain:
                        domain = final_domain

                soup = BeautifulSoup(resp.text, "html.parser")
                product_name = self._extract_product_name(soup)
                overall_rating, total_ratings_count, _ = self._extract_ratings_meta(soup)
                rating_distribution, has_distribution = self._extract_histogram(soup)
                # Extract the 8 "top reviews" embedded on the product page
                embedded = self._extract_review_blocks(soup)
                collected_reviews.extend(embedded)
            else:
                limitation_reason = f"Landing page returned HTTP {resp.status_code}"
        except Exception as e:
            limitation_reason = f"Connection issue: {str(e)}"

        # ── Step 2: Dedicated review pagination (may be auth-gated) ──────────
        pagination_blocked = False
        if asin and not limitation_reason:
            review_url_template = (
                f"https://{domain}/product-reviews/{asin}"
                f"/ref=cm_cr_dp_d_show_all_btm?reviewerType=all_reviews&pageNumber="
            )
            for page in range(1, self.max_pages + 1):
                page_url = review_url_template + str(page)
                try:
                    p_resp = session.get(page_url, timeout=self.timeout)

                    # Detect sign-in redirect (Amazon.in auth-gates review pages)
                    if self._is_signin_page(p_resp):
                        pagination_blocked = True
                        break

                    if p_resp.status_code == 200:
                        p_soup = BeautifulSoup(p_resp.text, "html.parser")
                        page_reviews = self._extract_review_blocks(p_soup)

                        if not page_reviews:
                            break   # last page reached

                        # Update histogram/rating if not found on landing page
                        if not has_distribution:
                            rating_distribution, has_distribution = self._extract_histogram(p_soup)
                        if overall_rating == 0.0:
                            r, rc, _ = self._extract_ratings_meta(p_soup)
                            if r > 0:
                                overall_rating = r
                            if rc > 0:
                                total_ratings_count = rc

                        collected_reviews.extend(page_reviews)

                        # Stop if the "next" button is absent
                        if not p_soup.select_one("li.a-last a"):
                            break

                    elif p_resp.status_code in (403, 429, 503):
                        limitation_reason = f"Amazon rate-limited at page {page}."
                        break
                    else:
                        break
                except Exception:
                    break

        # ── Step 3: Deduplicate ───────────────────────────────────────────────
        unique_reviews = self.deduplicate_reviews(collected_reviews)
        reviews_collected = len(unique_reviews)

        # ── Step 4: Limitation message ────────────────────────────────────────
        reviews_available = total_ratings_count or reviews_collected

        if not limitation_reason:
            if pagination_blocked and reviews_collected > 0:
                limitation_reason = (
                    f"Amazon requires sign-in to access full review pages. "
                    f"Only {reviews_collected} review(s) embedded on the product page "
                    f"could be collected out of {reviews_available} total ratings."
                )
            elif pagination_blocked:
                limitation_reason = (
                    "Amazon requires sign-in to access review pages. "
                    "No reviews could be collected."
                )
            elif reviews_available > reviews_collected:
                limitation_reason = (
                    f"Pagination boundary or platform access policy limits collection. "
                    f"Collected {reviews_collected} of {reviews_available}."
                )

        return {
            "success": True,
            "product_name": product_name,
            "canonical_url": url,
            "source": "Amazon",
            "overall_rating": overall_rating,
            "reviews_available": reviews_available,
            "reviews_collected": reviews_collected,
            "reviews_analyzed": reviews_collected,
            "limitation_reason": limitation_reason,
            "has_distribution": has_distribution,
            "rating_distribution": rating_distribution,
            "reviews": unique_reviews,
        }
