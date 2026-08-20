from database import create_database, add_review


def collect_review(product_name, review_text, rating, source):
    create_database()

    add_review(
        product_name=product_name,
        review_text=review_text,
        rating=rating,
        source=source
    )

    print("Review collected successfully!")


if __name__ == "__main__":
    collect_review(
        product_name="Sample Product",
        review_text="This product has excellent quality and performance.",
        rating=5,
        source="Manual Test"
    )