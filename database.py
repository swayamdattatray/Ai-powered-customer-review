import sqlite3

DATABASE_NAME = "customer_reviews.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def create_database():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT,
            review_text TEXT NOT NULL,
            rating INTEGER,
            sentiment TEXT,
            source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()

    # --------------------------------------------------------
    # MIGRATE: Add AI columns if they don't exist
    # --------------------------------------------------------

    _migrate_ai_columns(connection)

    connection.close()


def _migrate_ai_columns(connection):
    """
    Add AI-related columns to the reviews table
    if they don't already exist. This preserves
    all existing data.
    """

    cursor = connection.cursor()

    # Get existing column names
    cursor.execute("PRAGMA table_info(reviews)")

    existing_columns = [
        row[1] for row in cursor.fetchall()
    ]

    # New AI columns to add
    new_columns = {
        "is_fake": "BOOLEAN DEFAULT 0",
        "fake_score": "INTEGER DEFAULT 0",
        "fake_reason": "TEXT",
        "ai_explanation": "TEXT",
        "confidence_score": "REAL DEFAULT 0"
    }

    for column_name, column_type in new_columns.items():

        if column_name not in existing_columns:

            try:
                connection.execute(
                    f"ALTER TABLE reviews "
                    f"ADD COLUMN {column_name} {column_type}"
                )

                print(
                    f"[Database] Added column: {column_name}"
                )

            except sqlite3.OperationalError:
                # Column already exists
                pass

    connection.commit()


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
    connection = get_connection()

    connection.execute("""
        INSERT INTO reviews
        (
            product_name,
            review_text,
            rating,
            sentiment,
            source,
            is_fake,
            fake_score,
            fake_reason,
            ai_explanation,
            confidence_score
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        product_name,
        review_text,
        rating,
        sentiment,
        source,
        is_fake,
        fake_score,
        fake_reason,
        ai_explanation,
        confidence_score
    ))

    connection.commit()
    connection.close()


if __name__ == "__main__":
    create_database()
    print("Database created successfully!")