"""
Multi-Retailer Purchase Recommender Tool.
Generates verified, safe purchasing options across multiple retailers:
1. Official Brand Store (Apple, Samsung, Sony, OnePlus, Dell, HP, etc. - Highest Trust)
2. Amazon (Prime / Verified Merchants)
3. Flipkart (Flipkart Assured)
4. Croma (Authorized Electronics Retailer)
5. Reliance Digital (Authorized Store)
6. Best Buy / Walmart (Global Retailers)
"""

import urllib.parse
from typing import List, Dict, Any


class PurchaseRecommender:
    """Tool for providing multi-retailer verified purchase links and trust ratings."""

    # Brand official store mappings
    BRAND_OFFICIAL_STORES = {
        "apple": {"name": "Apple Official Store", "domain": "apple.com", "badge": "Official Direct · 100% Genuine Warranty", "trust_rating": 99},
        "iphone": {"name": "Apple Official Store", "domain": "apple.com", "badge": "Official Direct · 100% Genuine Warranty", "trust_rating": 99},
        "samsung": {"name": "Samsung Official Store", "domain": "samsung.com", "badge": "Official Direct · Brand Warranty", "trust_rating": 98},
        "galaxy": {"name": "Samsung Official Store", "domain": "samsung.com", "badge": "Official Direct · Brand Warranty", "trust_rating": 98},
        "sony": {"name": "Sony Center Direct", "domain": "sony.com", "badge": "Authorized Direct · Full Warranty", "trust_rating": 98},
        "boat": {"name": "boAt Lifestyle Official", "domain": "boat-lifestyle.com", "badge": "Official Brand Store", "trust_rating": 96},
        "dell": {"name": "Dell Official Store", "domain": "dell.com", "badge": "Official Direct · Onsite Warranty", "trust_rating": 98},
        "macbook": {"name": "Apple Store Online", "domain": "apple.com", "badge": "Official Direct · AppleCare Eligible", "trust_rating": 99},
        "oneplus": {"name": "OnePlus Official Store", "domain": "oneplus.com", "badge": "Official Direct · Brand Support", "trust_rating": 97}
    }

    @classmethod
    def get_purchase_options(cls, product_name: str, category: str = "") -> List[Dict[str, Any]]:
        """
        Generates structured multi-retailer purchasing recommendations for a given product.
        """
        encoded_query = urllib.parse.quote_plus(product_name.strip())
        lower_name = product_name.lower()
        options = []

        # 1. Official Brand Store (if recognized)
        brand_match = None
        for brand_key, brand_info in cls.BRAND_OFFICIAL_STORES.items():
            if brand_key in lower_name:
                brand_match = brand_info
                break

        if brand_match:
            options.append({
                "store_name": brand_match["name"],
                "store_type": "Official Brand Store",
                "badge": brand_match["badge"],
                "trust_score": brand_match["trust_rating"],
                "security_status": "Highest Trust (Direct Manufacturer)",
                "buy_url": f"https://www.{brand_match['domain']}/search?q={encoded_query}",
                "icon": "🏢",
                "recommended": True
            })

        # 2. Amazon Option
        options.append({
            "store_name": "Amazon",
            "store_type": "Major Marketplace",
            "badge": "Prime Verified · A-to-z Guarantee",
            "trust_score": 92,
            "security_status": "Verified Marketplace",
            "buy_url": f"https://www.amazon.in/s?k={encoded_query}",
            "icon": "📦",
            "recommended": True if not brand_match else False
        })

        # 3. Flipkart Option
        options.append({
            "store_name": "Flipkart",
            "store_type": "Major Marketplace",
            "badge": "Flipkart Assured · 7-Day Replacement",
            "trust_score": 90,
            "security_status": "Verified Marketplace",
            "buy_url": f"https://www.flipkart.com/search?q={encoded_query}",
            "icon": "🛍️",
            "recommended": False
        })

        # 4. Croma (Electronics Specialist)
        options.append({
            "store_name": "Croma Electronics",
            "store_type": "Authorized Retail Chain",
            "badge": "Tata Enterprise · Store Pickup Available",
            "trust_score": 95,
            "security_status": "Authorized Retailer",
            "buy_url": f"https://www.croma.com/searchB?q={encoded_query}",
            "icon": "🏬",
            "recommended": False
        })

        # 5. Reliance Digital
        options.append({
            "store_name": "Reliance Digital",
            "store_type": "Authorized Retail Chain",
            "badge": "Brand Warranty · ResQ Service Support",
            "trust_score": 94,
            "security_status": "Authorized Retailer",
            "buy_url": f"https://www.reliancedigital.in/search?q={encoded_query}",
            "icon": "🛒",
            "recommended": False
        })

        # 6. Global Retailer (Best Buy)
        options.append({
            "store_name": "Best Buy",
            "store_type": "International Retailer",
            "badge": "Price Match Guarantee · Geek Squad",
            "trust_score": 93,
            "security_status": "Authorized Retailer",
            "buy_url": f"https://www.bestbuy.com/site/searchpage.jsp?st={encoded_query}",
            "icon": "🌐",
            "recommended": False
        })

        return options
