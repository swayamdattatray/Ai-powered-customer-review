"""
Configuration Module for AI Customer Review Intelligence Platform.
All configurable parameters, API keys, thresholds, and paths are defined here.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base project directory
BASE_DIR = Path(__file__).resolve().parent

# Database Configuration
DATABASE_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "customer_reviews.db"))

# LLM Provider Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")  # Options: 'gemini', 'openai', 'fallback'
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-3.6-flash")

# Machine Learning Fallback Paths
ML_MODEL_PATH = os.getenv("ML_MODEL_PATH", str(BASE_DIR / "models" / "sentiment_model.pkl"))
VECTORIZER_PATH = os.getenv("VECTORIZER_PATH", str(BASE_DIR / "models" / "tfidf_vectorizer.pkl"))

# Agent Analysis Settings & Thresholds
SUSPICION_THRESHOLD = int(os.getenv("SUSPICION_THRESHOLD", "60"))  # >= 60% flags as potentially suspicious
MAX_REVIEWS_FOR_LLM_SUMMARY = int(os.getenv("MAX_REVIEWS_FOR_LLM_SUMMARY", "30"))
DEFAULT_REVIEW_COLLECTION_LIMIT = int(os.getenv("DEFAULT_REVIEW_COLLECTION_LIMIT", "50"))

# Flask Configuration
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "t")
FLASK_PORT = int(os.getenv("PORT", "5000"))
SECRET_KEY = os.getenv("SECRET_KEY", "customer-review-agent-secret-key-2026")
