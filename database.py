"""
Legacy database.py shim for backward compatibility with existing tests and scripts.
Redirects calls to the new modular DatabaseManager.
"""

from database.db_manager import DatabaseManager

_db = DatabaseManager()

def get_connection():
    return _db.get_connection()

def create_database():
    _db.init_database()

def add_review(
    product_name,
    review_text,
    rating,
    source,
    sentiment=None,
    is_fake=False,
    fake_score=0,
    fake_reason=None,
    ai_explanation=None,
    confidence_score=0
):
    return _db.add_review(
        product_name=product_name,
        review_text=review_text,
        rating=rating,
        source=source,
        sentiment=sentiment,
        is_fake=is_fake,
        fake_score=fake_score,
        fake_reason=fake_reason,
        ai_explanation=ai_explanation,
        confidence_score=confidence_score
    )

if __name__ == "__main__":
    create_database()
    print("Database initialized successfully!")