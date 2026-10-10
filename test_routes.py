import json
from app import app
from collectors import CollectorFactory, AmazonCollector, FlipkartCollector
from utils.rating_aspect_intelligence import run_complete_review_intelligence

print("=== 1. TESTING COLLECTOR FACTORY ===")
col_amazon = CollectorFactory.get_collector("https://www.amazon.in/dp/B0D1234567")
assert isinstance(col_amazon, AmazonCollector)
print("Amazon Collector Dispatch: [OK]")

col_flipkart = CollectorFactory.get_collector("https://www.flipkart.com/samsung-galaxy-s24/p/itm12345")
assert isinstance(col_flipkart, FlipkartCollector)
print("Flipkart Collector Dispatch: [OK]")

print("\n=== 2. TESTING CANONICAL RATING & EXPLANATION UNIFICATION ===")
sample_reviews = [
    {"text": "Amazing camera and display, but battery drains so fast and it heats up.", "rating": 4, "source": "Amazon"},
    {"text": "The camera lens is phenomenal. Great photos.", "rating": 5, "source": "Amazon"},
    {"text": "Battery life is terrible and price is overpriced.", "rating": 2, "source": "Amazon"},
    {"text": "Best phone ever! Amazing! Must buy!", "rating": 5, "source": "Amazon"}
]

intel = run_complete_review_intelligence(
    sample_reviews,
    product_name="Samsung Galaxy Z Fold8 Ultra 5G",
    canonical_rating=4.3,
    extracted_histogram={5: 71.0, 4: 10.0, 3: 7.0, 2: 0.0, 1: 12.0},
    selected_source="Amazon",
    reviews_available_count=1247
)

assert intel["product"]["overall_rating"] == 4.3, f"Expected 4.3, got {intel['product']['overall_rating']}"
assert intel["review_statistics"]["available"] == 1247
assert intel["review_statistics"]["collected"] == 4
assert intel["review_statistics"]["analyzed"] == 4
assert "4.3" in str(intel["product"]["overall_rating"])
assert len(intel["aspect_intelligence"]) > 0
print(f"Product Canonical Rating: {intel['product']['overall_rating']}/5 [OK]")
print(f"Reviews Available: {intel['review_statistics']['available']}, Collected: {intel['review_statistics']['collected']}, Analyzed: {intel['review_statistics']['analyzed']} [OK]")
print(f"AI Explanation: '{intel['ai_explanation']}' [OK]")
print(f"Suspicious Tiers: {intel['suspicion_tiers']} [OK]")

print("\n=== 3. TESTING FLASK APPLICATION ROUTES ===")
client = app.test_client()

with client.session_transaction() as sess:
    sess['user_id'] = 1
    sess['user_name'] = 'Test User'

res_index = client.get('/')
assert res_index.status_code == 200
assert b"E-Commerce Rating Distribution" in res_index.data
print("/ (Dashboard) GET: [OK]")

res_filter = client.get('/?product=Samsung+Galaxy+Z+Fold8+Ultra+5G&source=Amazon')
assert res_filter.status_code == 200
print("/?product=... GET: [OK]")

res_analytics = client.get('/analytics')
assert res_analytics.status_code == 200
print("/analytics GET: [OK]")

res_reviews = client.get('/reviews')
assert res_reviews.status_code == 200
print("/reviews GET: [OK]")

print("\nALL ARCHITECTURAL TESTS PASSED SUCCESSFULLY! [OK]")
