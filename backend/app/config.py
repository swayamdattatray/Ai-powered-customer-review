"""
Configuration settings for Backend Intelligence API.
"""

import os
from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "E-Commerce Shopping Intelligence API"
    app_version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    
    # CORS Origins (allow extension origins)
    allowed_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "chrome-extension://*",
        "*"
    ]
    
    # Official API credentials
    amazon_access_key: str = os.getenv("AMAZON_ACCESS_KEY", "")
    amazon_secret_key: str = os.getenv("AMAZON_SECRET_KEY", "")
    amazon_partner_tag: str = os.getenv("AMAZON_PARTNER_TAG", "")
    amazon_country: str = os.getenv("AMAZON_COUNTRY", "IN")

    flipkart_affiliate_id: str = os.getenv("FLIPKART_AFFILIATE_ID", "")
    flipkart_affiliate_token: str = os.getenv("FLIPKART_AFFILIATE_TOKEN", "")

    # Cache TTL (in seconds)
    cache_ttl_seconds: int = 7200


settings = Settings()
