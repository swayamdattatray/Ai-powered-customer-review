"""
Price Intelligence Service.
Coordinates price fetching across all registered collectors, computes comparison metrics,
persists price records, and formats data for dashboard rendering.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from .price_collector_factory import PriceCollectorFactory
from .models import PriceResult


class PriceService:
    """Service layer for e-commerce price comparison and analytics."""

    def __init__(self):
        self.factory = PriceCollectorFactory

    def compare_prices(
        self,
        product_url: Optional[str] = None,
        product_name: Optional[str] = None,
        current_source: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Compare current prices across all registered e-commerce platforms.
        Guarantees that no fake prices are ever created.
        """
        collectors = self.factory.get_all_collectors()
        results: List[PriceResult] = []

        target_url = product_url.strip() if product_url else None
        target_name = product_name.strip() if product_name else None
        current_src_lower = current_source.lower().strip() if current_source else ""

        for collector in collectors:
            src_name = collector.name.lower()
            try:
                # If target URL belongs to this collector's platform, provide URL
                if target_url and src_name in target_url.lower():
                    res = collector.get_price(product_url=target_url, product_name=target_name)
                else:
                    # Cross-platform lookup using product_name
                    res = collector.get_price(product_url=None, product_name=target_name)
            except Exception as e:
                res = PriceResult(
                    source=collector.name,
                    status="unavailable",
                    product_name=target_name,
                    error=f"Unexpected error: {str(e)}",
                    match_confidence="none"
                )
            results.append(res)

        # Separate successful price results from unavailable ones
        valid_prices = [r for r in results if r.status == "success" and r.price is not None and r.price > 0]

        summary = self._compute_summary(valid_prices, total_checked=len(results))
        chart_data = self._build_chart_data(valid_prices)

        # Attempt to persist valid prices to DB if database helper exists
        self._persist_prices(valid_prices, fallback_name=target_name or "Unknown Product", fallback_url=target_url)

        return {
            "summary": summary,
            "prices": [r.to_dict() for r in results],
            "valid_prices": [r.to_dict() for r in valid_prices],
            "chart_data": chart_data,
            "supported_sources": self.factory.list_supported_sources()
        }

    def _compute_summary(self, valid_prices: List[PriceResult], total_checked: int) -> Dict[str, Any]:
        timestamp = datetime.now().strftime("%d %b %Y, %I:%M %p")

        if not valid_prices:
            return {
                "lowest_price": None,
                "highest_price": None,
                "price_difference": None,
                "lowest_source": None,
                "sources_compared": 0,
                "total_sources_checked": total_checked,
                "last_updated": timestamp,
                "has_comparison": False,
                "status_message": "Price comparison unavailable. Official API credentials not configured."
            }

        sorted_by_price = sorted(valid_prices, key=lambda x: x.price)  # type: ignore
        lowest = sorted_by_price[0]
        highest = sorted_by_price[-1]
        diff = round(highest.price - lowest.price, 2)  # type: ignore

        return {
            "lowest_price": lowest.price,
            "lowest_price_formatted": f"₹{lowest.price:,.0f}" if lowest.currency == "INR" else f"{lowest.currency} {lowest.price:,.2f}",
            "lowest_source": lowest.source,
            "highest_price": highest.price,
            "highest_price_formatted": f"₹{highest.price:,.0f}" if highest.currency == "INR" else f"{highest.currency} {highest.price:,.2f}",
            "highest_source": highest.source,
            "price_difference": diff,
            "price_difference_formatted": f"₹{diff:,.0f}" if lowest.currency == "INR" else f"{lowest.currency} {diff:,.2f}",
            "sources_compared": len(valid_prices),
            "total_sources_checked": total_checked,
            "last_updated": timestamp,
            "has_comparison": True,
            "status_message": f"Successfully compared prices across {len(valid_prices)} source(s)."
        }

    def _build_chart_data(self, valid_prices: List[PriceResult]) -> Dict[str, Any]:
        labels = [r.source for r in valid_prices]
        values = [r.price for r in valid_prices]
        formatted = [
            f"₹{r.price:,.0f}" if r.currency == "INR" else f"{r.currency} {r.price:,.2f}"  # type: ignore
            for r in valid_prices
        ]

        # Calculate relative percentages for CSS bar heights/widths
        max_val = max(values) if values else 1
        percentages = [round((v / max_val) * 100, 1) for v in values] if values else []

        return {
            "labels": labels,
            "values": values,
            "formatted_values": formatted,
            "percentages": percentages,
            "max_value": max_val
        }

    def _persist_prices(
        self,
        valid_prices: List[PriceResult],
        fallback_name: str,
        fallback_url: Optional[str]
    ):
        """Save successfully fetched prices into the database for future history tracking."""
        try:
            from database import save_price_record
            for r in valid_prices:
                save_price_record(
                    product_name=r.product_name or fallback_name,
                    product_url=r.product_url or fallback_url,
                    source=r.source,
                    price=r.price,
                    currency=r.currency,
                    availability=1 if r.availability is not False else 0,
                    match_confidence=r.match_confidence,
                    status=r.status,
                    error_message=r.error
                )
        except Exception:
            # Failure to record price history must never break live flow
            pass
