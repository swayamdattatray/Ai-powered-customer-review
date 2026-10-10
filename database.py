import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional


BASE_DIR = Path(__file__).resolve().parent
DATABASE_FILE = BASE_DIR / "customer_reviews.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_FILE)
    connection.row_factory = sqlite3.Row
    return connection


def create_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            review_text TEXT NOT NULL,
            rating INTEGER,
            sentiment TEXT,
            source TEXT,
            title TEXT,
            review_date TEXT,
            verified_status INTEGER DEFAULT 0,
            suspicion_score INTEGER DEFAULT 0,
            suspicion_signals TEXT,
            cluster_id INTEGER,
            aspects TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Safe migration: ensure new columns exist if table was created previously
    cursor.execute("PRAGMA table_info(reviews)")
    existing_cols = [row["name"] for row in cursor.fetchall()]
    new_cols = {
        "title": "TEXT",
        "review_date": "TEXT",
        "verified_status": "INTEGER DEFAULT 0",
        "suspicion_score": "INTEGER DEFAULT 0",
        "suspicion_signals": "TEXT",
        "cluster_id": "INTEGER",
        "aspects": "TEXT"
    }

    for col, col_type in new_cols.items():
        if col not in existing_cols:
            try:
                cursor.execute(f"ALTER TABLE reviews ADD COLUMN {col} {col_type}")
            except Exception:
                pass

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            product_url TEXT,
            source TEXT NOT NULL,
            price REAL NOT NULL,
            currency TEXT DEFAULT 'INR',
            availability INTEGER DEFAULT 1,
            match_confidence TEXT DEFAULT 'exact',
            status TEXT DEFAULT 'success',
            error_message TEXT,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


def add_review(
    product_name: str,
    review_text: str,
    rating: int,
    source: str = "Direct",
    title: str = "",
    review_date: str = "",
    verified_status: bool = False,
    suspicion_score: int = 0,
    suspicion_signals: Optional[List[str]] = None,
    cluster_id: Optional[int] = None,
    aspects: Optional[Dict[str, Any]] = None
):
    connection = get_connection()
    cursor = connection.cursor()

    if rating <= 2:
        sentiment = "Negative"
    elif rating == 3:
        sentiment = "Neutral"
    else:
        sentiment = "Positive"

    signals_json = json.dumps(suspicion_signals or [])
    aspects_json = json.dumps(aspects or {})

    cursor.execute("""
        INSERT INTO reviews (
            product_name,
            review_text,
            rating,
            sentiment,
            source,
            title,
            review_date,
            verified_status,
            suspicion_score,
            suspicion_signals,
            cluster_id,
            aspects
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        product_name,
        review_text,
        rating,
        sentiment,
        source,
        title,
        review_date,
        1 if verified_status else 0,
        suspicion_score,
        signals_json,
        cluster_id,
        aspects_json
    ))

    connection.commit()
    connection.close()


def save_collected_reviews_batch(product_name: str, reviews: List[Dict[str, Any]], default_source: str = "Web"):
    """Inserts or merges a batch of collected reviews into the database."""
    if not reviews:
        return

    connection = get_connection()
    cursor = connection.cursor()

    for r in reviews:
        text = r.get("text", "").strip()
        if not text:
            continue

        rating = r.get("rating") or 5
        try:
            rating_val = int(round(float(rating)))
        except Exception:
            rating_val = 5

        if rating_val <= 2:
            sentiment = "Negative"
        elif rating_val == 3:
            sentiment = "Neutral"
        else:
            sentiment = "Positive"

        source = r.get("source") or default_source
        title = r.get("title", "")
        review_date = r.get("date", "")
        verified = 1 if r.get("verified_purchase") else 0

        # Avoid duplicate insert for exact same product + text
        cursor.execute(
            "SELECT id FROM reviews WHERE product_name = ? AND review_text = ?",
            (product_name, text)
        )
        if cursor.fetchone():
            continue

        cursor.execute("""
            INSERT INTO reviews (
                product_name, review_text, rating, sentiment, source,
                title, review_date, verified_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            product_name, text, rating_val, sentiment, source,
            title, review_date, verified
        ))

    connection.commit()
    connection.close()


def get_all_reviews():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            product_name,
            review_text,
            rating,
            sentiment,
            source,
            title,
            review_date,
            verified_status,
            suspicion_score,
            suspicion_signals,
            cluster_id,
            aspects,
            created_at
        FROM reviews
        ORDER BY created_at DESC
    """)

    reviews = cursor.fetchall()
    connection.close()
    return reviews


def get_distinct_products():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT DISTINCT product_name, COUNT(*) as count
        FROM reviews
        GROUP BY product_name
        ORDER BY count DESC
    """)

    products = [row["product_name"] for row in cursor.fetchall()]
    connection.close()
    return products


def get_reviews_filtered(product_name=None, source=None):
    connection = get_connection()
    cursor = connection.cursor()

    query = """
        SELECT
            id,
            product_name,
            review_text,
            rating,
            sentiment,
            source,
            title,
            review_date,
            verified_status,
            suspicion_score,
            suspicion_signals,
            cluster_id,
            aspects,
            created_at
        FROM reviews
        WHERE 1=1
    """
    params = []

    if product_name and product_name.strip() and product_name != "All Products":
        query += " AND product_name = ?"
        params.append(product_name.strip())

    if source and source.strip() and source != "All Sources":
        query += " AND LOWER(source) = LOWER(?)"
        params.append(source.strip())

    query += " ORDER BY created_at DESC"

    cursor.execute(query, params)
    reviews = cursor.fetchall()
    connection.close()
    return reviews


def save_price_record(
    product_name: str,
    source: str,
    price: float,
    product_url: Optional[str] = None,
    currency: str = "INR",
    availability: int = 1,
    match_confidence: str = "exact",
    status: str = "success",
    error_message: Optional[str] = None
):
    """Persists a successfully fetched price record into price_history table."""
    if price is None or price <= 0:
        return

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO price_history (
            product_name, product_url, source, price, currency,
            availability, match_confidence, status, error_message
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        product_name,
        product_url,
        source,
        float(price),
        currency,
        availability,
        match_confidence,
        status,
        error_message
    ))

    connection.commit()
    connection.close()


def get_price_history(product_name: str, source: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves chronological price history records for a product."""
    connection = get_connection()
    cursor = connection.cursor()

    query = """
        SELECT id, product_name, product_url, source, price, currency,
               availability, match_confidence, status, error_message, fetched_at
        FROM price_history
        WHERE product_name = ?
    """
    params = [product_name]

    if source and source != "All Sources":
        query += " AND LOWER(source) = LOWER(?)"
        params.append(source)

    query += " ORDER BY fetched_at ASC"

    cursor.execute(query, params)
    rows = [dict(r) for r in cursor.fetchall()]
    connection.close()
    return rows