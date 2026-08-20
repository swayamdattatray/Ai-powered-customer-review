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
    connection.close()


def add_review(
    product_name,
    review_text,
    rating,
    source,
    sentiment=None
):
    connection = get_connection()

    connection.execute("""
        INSERT INTO reviews
        (
            product_name,
            review_text,
            rating,
            sentiment,
            source
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        product_name,
        review_text,
        rating,
        sentiment,
        source
    ))

    connection.commit()
    connection.close()


if __name__ == "__main__":
    create_database()
    print("Database created successfully!")