"""
Data Models for Price Intelligence.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class PriceResult:
    source: str
    status: str  # "success", "unavailable", "error"
    product_name: Optional[str] = None
    product_url: Optional[str] = None
    price: Optional[float] = None
    currency: str = "INR"
    availability: Optional[bool] = None
    timestamp: str = ""
    error: Optional[str] = None
    match_confidence: str = "exact"  # "exact", "high", "uncertain", "none"

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().strftime("%d %b %Y, %I:%M %p")

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        # Format display price cleanly
        if self.price is not None and self.status == "success":
            data["formatted_price"] = f"₹{self.price:,.0f}" if self.currency == "INR" else f"{self.currency} {self.price:,.2f}"
        else:
            data["formatted_price"] = "Price unavailable"
        return data
