"""
Database Manager Module.
Enhanced with tables for Monitored Products and Periodic Review Scan Activity Logs.
"""

import json
import logging
import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime
import config

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database creation, migrations, and operations."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or config.DATABASE_PATH
        self.init_database()

    def get_connection(self) -> sqlite3.Connection:
        """Returns a configured SQLite database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self) -> None:
        """Initializes database tables for reviews, saved reports, monitored products, and logs."""
        conn = self.get_connection()
        
        # 1. Customer Reviews Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT,
                review_text TEXT NOT NULL,
                rating INTEGER,
                sentiment TEXT,
                source TEXT,
                is_fake BOOLEAN DEFAULT 0,
                fake_score INTEGER DEFAULT 0,
                fake_reason TEXT,
                ai_explanation TEXT,
                confidence_score REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 2. Product Intelligence Reports Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS product_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                overall_perception TEXT,
                customer_satisfaction INTEGER,
                suspicious_percentage INTEGER,
                key_takeaway TEXT,
                report_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 3. Monitored Products Table (Watchlist)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS monitored_products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT UNIQUE NOT NULL,
                product_url TEXT,
                last_scanned TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 4. Review Scan Activity Logs
        conn.execute("""
            CREATE TABLE IF NOT EXISTS review_activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                event_type TEXT NOT NULL,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def add_review(
        self,
        product_name: str,
        review_text: str,
        rating: Optional[int] = None,
        source: str = "Manual Entry",
        sentiment: Optional[str] = None,
        is_fake: bool = False,
        fake_score: int = 0,
        fake_reason: Optional[str] = None,
        ai_explanation: Optional[str] = None,
        confidence_score: float = 0.0
    ) -> int:
        """Inserts a single review record."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO reviews (
                product_name, review_text, rating, sentiment, source,
                is_fake, fake_score, fake_reason, ai_explanation, confidence_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            product_name, review_text, rating, sentiment, source,
            is_fake, fake_score, fake_reason, ai_explanation, confidence_score
        ))
        conn.commit()
        review_id = cursor.lastrowid
        conn.close()
        return review_id

    def save_product_report(self, report_data: Dict[str, Any]) -> int:
        """Saves or updates a product intelligence report."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        product_name = report_data.get("product_name", "Unknown Product")
        perception = report_data.get("overall_perception", "Positive")
        satisfaction = report_data.get("customer_satisfaction", 75)
        suspicious_pct = report_data.get("suspicious_percentage", 0)
        key_takeaway = report_data.get("key_takeaway", "")
        report_json = json.dumps(report_data)

        cursor.execute("""
            INSERT INTO product_reports (
                product_name, overall_perception, customer_satisfaction,
                suspicious_percentage, key_takeaway, report_json
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            product_name, perception, satisfaction, suspicious_pct, key_takeaway, report_json
        ))
        conn.commit()
        report_id = cursor.lastrowid
        conn.close()
        return report_id

    def toggle_monitoring(self, product_name: str, product_url: str = "") -> bool:
        """Adds or removes a product from the background monitoring watchlist."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT is_active FROM monitored_products WHERE LOWER(product_name) = LOWER(?)", (product_name.strip(),))
        row = cursor.fetchone()

        if row:
            new_state = 0 if row["is_active"] else 1
            cursor.execute("UPDATE monitored_products SET is_active = ?, last_scanned = CURRENT_TIMESTAMP WHERE LOWER(product_name) = LOWER(?)", (new_state, product_name.strip()))
            active = bool(new_state)
        else:
            cursor.execute("INSERT INTO monitored_products (product_name, product_url, is_active) VALUES (?, ?, 1)", (product_name.strip(), product_url.strip()))
            active = True

        conn.commit()
        conn.close()
        return active

    def is_monitored(self, product_name: str) -> bool:
        """Checks if a product is actively monitored."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT is_active FROM monitored_products WHERE LOWER(product_name) = LOWER(?) AND is_active = 1", (product_name.strip(),))
        row = cursor.fetchone()
        conn.close()
        return row is not None

    def log_activity(self, product_name: str, event_type: str, details: str) -> None:
        """Logs a scan or monitoring event."""
        conn = self.get_connection()
        conn.execute("INSERT INTO review_activity_logs (product_name, event_type, details) VALUES (?, ?, ?)", (product_name, event_type, details))
        conn.commit()
        conn.close()

    def get_recent_activity(self, product_name: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieves recent review monitoring activity logs."""
        conn = self.get_connection()
        cursor = conn.cursor()
        if product_name:
            cursor.execute("SELECT * FROM review_activity_logs WHERE LOWER(product_name) = LOWER(?) ORDER BY created_at DESC LIMIT ?", (product_name.strip(), limit))
        else:
            cursor.execute("SELECT * FROM review_activity_logs ORDER BY created_at DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_latest_report(self, product_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Retrieves the latest saved report."""
        conn = self.get_connection()
        cursor = conn.cursor()
        if product_name:
            cursor.execute("SELECT report_json FROM product_reports WHERE LOWER(product_name) LIKE LOWER(?) ORDER BY created_at DESC LIMIT 1", (f"%{product_name}%",))
        else:
            cursor.execute("SELECT report_json FROM product_reports ORDER BY created_at DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        if row and row["report_json"]:
            try:
                return json.loads(row["report_json"])
            except json.JSONDecodeError:
                return None
        return None

    def get_all_reviews(self) -> List[Dict[str, Any]]:
        """Fetches all stored customer reviews."""
        conn = self.get_connection()
        rows = conn.execute("SELECT * FROM reviews ORDER BY created_at DESC").fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_product_analytics_summary(self) -> Dict[str, Any]:
        """Calculates product-by-product sentiment summary stats."""
        conn = self.get_connection()
        rows = conn.execute("SELECT product_name, sentiment FROM reviews WHERE product_name IS NOT NULL AND TRIM(product_name) != '' AND sentiment IS NOT NULL").fetchall()
        conn.close()

        product_data = {}
        for row in rows:
            prod = row["product_name"].strip()
            sent = str(row["sentiment"]).strip().lower()
            if prod not in product_data:
                product_data[prod] = {"total": 0, "positive": 0, "neutral": 0, "negative": 0, "positive_percent": 0, "neutral_percent": 0, "negative_percent": 0}
            product_data[prod]["total"] += 1
            if sent == "positive": product_data[prod]["positive"] += 1
            elif sent == "negative": product_data[prod]["negative"] += 1
            else: product_data[prod]["neutral"] += 1

        for prod, data in product_data.items():
            tot = data["total"]
            if tot > 0:
                data["positive_percent"] = round((data["positive"] / tot) * 100, 1)
                data["neutral_percent"] = round((data["neutral"] / tot) * 100, 1)
                data["negative_percent"] = round((data["negative"] / tot) * 100, 1)

        return product_data
