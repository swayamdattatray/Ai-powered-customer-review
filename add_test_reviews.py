from database import create_database, add_review

create_database()

reviews = [
    ("Phone A", "Excellent phone with great camera quality", 5, "Test"),
    ("Phone A", "Very good performance and battery life", 5, "Test"),
    ("Phone A", "Amazing display and fast performance", 5, "Test"),
    ("Phone A", "I really like this product", 4, "Test"),
    ("Phone A", "Good quality and useful features", 4, "Test"),

    ("Phone B", "Very bad battery life", 1, "Test"),
    ("Phone B", "Camera quality is terrible", 1, "Test"),
    ("Phone B", "The phone is slow and disappointing", 2, "Test"),
    ("Phone B", "Poor product quality", 2, "Test"),
    ("Phone B", "Not worth the money", 1, "Test"),

    ("Phone C", "The product is okay", 3, "Test"),
    ("Phone C", "Average performance", 3, "Test"),
    ("Phone C", "It is neither good nor bad", 3, "Test"),
    ("Phone C", "Average camera and battery", 3, "Test"),
    ("Phone C", "The product is acceptable", 3, "Test")
]

for product, review, rating, source in reviews:
    add_review(
        product,
        review,
        rating,
        source
    )

print("Test reviews added successfully!")
print("Total test reviews:", len(reviews))