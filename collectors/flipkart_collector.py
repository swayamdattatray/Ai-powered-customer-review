"""
Flipkart Review Collector with review page discovery, rating parsing, and pagination.
"""

import re
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from typing import Dict, Any, List

from .base_collector import BaseCollector


class FlipkartCollector(BaseCollector):
    def __init__(self, max_pages: int = 10, timeout: int = 15):
        super().__init__(timeout=timeout)
        self.max_pages = max_pages

    def collect(self, url: str) -> Dict[str, Any]:
        product_name = "Flipkart Product"
        overall_rating = 0.0
        reviews_available = 0
        rating_distribution = {5: 0.0, 4: 0.0, 3: 0.0, 2: 0.0, 1: 0.0}
        has_distribution = False
        limitation_reason = None
        collected_reviews: List[Dict[str, Any]] = []

        session = requests.Session()
        session.headers.update(self.headers)

        try:
            resp = session.get(url, timeout=self.timeout)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                product_name = self._extract_name(soup)
                overall_rating, reviews_available = self._extract_rating_meta(soup)
                collected_reviews.extend(self._extract_reviews_from_soup(soup))

                # Check if there is a 'All reviews' link
                all_reviews_link = soup.select_one('a[href*="/product-reviews/"]')
                if all_reviews_link and all_reviews_link.get("href"):
                    base_review_url = "https://www.flipkart.com" + all_reviews_link["href"].split("&page=")[0]
                    
                    for page in range(1, self.max_pages + 1):
                        p_url = f"{base_review_url}&page={page}" if "?" in base_review_url else f"{base_review_url}?page={page}"
                        try:
                            p_resp = session.get(p_url, timeout=self.timeout)
                            if p_resp.status_code == 200:
                                p_soup = BeautifulSoup(p_resp.text, "html.parser")
                                p_revs = self._extract_reviews_from_soup(p_soup)
                                if not p_revs:
                                    break
                                collected_reviews.extend(p_revs)
                            else:
                                break
                        except Exception:
                            break
            else:
                limitation_reason = f"Flipkart returned HTTP {resp.status_code}"
        except Exception as e:
            limitation_reason = f"Connection error: {str(e)}"

        unique_reviews = self.deduplicate_reviews(collected_reviews)
        reviews_collected = len(unique_reviews)

        if reviews_available == 0:
            reviews_available = reviews_collected

        if reviews_available > reviews_collected and not limitation_reason:
            limitation_reason = "Pagination boundary reached on public review stream."

        return {
            "success": True,
            "product_name": product_name,
            "canonical_url": url,
            "source": "Flipkart",
            "overall_rating": overall_rating,
            "reviews_available": reviews_available,
            "reviews_collected": reviews_collected,
            "reviews_analyzed": reviews_collected,
            "limitation_reason": limitation_reason,
            "has_distribution": has_distribution,
            "rating_distribution": rating_distribution,
            "reviews": unique_reviews
        }

    def _extract_name(self, soup: BeautifulSoup) -> str:
        elem = soup.select_one("span.B_NuCI") or soup.select_one("h1.yhB1nd") or soup.select_one("h1")
        if elem:
            return self.normalize_text(elem.get_text())
        return "Flipkart Product"

    def _extract_rating_meta(self, soup: BeautifulSoup):
        rating = 0.0
        count = 0
        rate_elem = soup.select_one("div._3LWZlK") or soup.select_one("div.XQDdHH")
        if rate_elem:
            m = re.search(r"(\d+(\.\d+)?)", rate_elem.get_text())
            if m:
                try:
                    rating = round(float(m.group(1)), 1)
                except Exception:
                    pass

        count_elem = soup.select_one("span._2_R_DZ") or soup.select_one("span.Wphh3N")
        if count_elem:
            m = re.search(r"([\d,]+)\s*(Ratings|Reviews)", count_elem.get_text(), re.IGNORECASE)
            if m:
                try:
                    count = int(m.group(1).replace(",", ""))
                except Exception:
                    pass

        return rating, count

    def _extract_reviews_from_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        reviews = []
        review_cards = soup.select("div.col.EPCmJX") or soup.select("div._1AtVbE div._2w1YVo") or soup.select("div.t-ZTKy")

        for card in review_cards:
            text_elem = card.select_one("div.t-ZTKy") or card.select_one("div.ZmyHeo") or card
            if not text_elem:
                continue
            text = self.normalize_text(text_elem.get_text())
            if len(text) < 10:
                continue

            rating = 5
            star_elem = card.select_one("div._3LWZlK") or card.select_one("div.XQDdHH")
            if star_elem:
                m = re.search(r"(\d+(\.\d+)?)", star_elem.get_text())
                if m:
                    try:
                        rating = int(round(float(m.group(1))))
                    except Exception:
                        pass

            title = ""
            title_elem = card.select_one("p._2-N8zT") or card.select_one("p.z9E0IG")
            if title_elem:
                title = self.normalize_text(title_elem.get_text())

            reviews.append({
                "title": title,
                "text": text,
                "rating": rating,
                "date": "",
                "verified_purchase": True,
                "source": "Flipkart"
            })

        return reviews
