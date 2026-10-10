from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from pathlib import Path
import sqlite3
import joblib

from database import (
    create_database,
    get_connection,
    add_review,
    get_all_reviews,
    get_distinct_products,
    get_reviews_filtered,
    save_collected_reviews_batch
)

from preprocessing.text_preprocessor import clean_text
from utils.aspect_analyzer import analyze_aspects
from utils.url_analyzer import analyze_product_url
from utils.rating_aspect_intelligence import run_complete_review_intelligence
from price_intelligence import PriceService


app = Flask(__name__)

app.secret_key = "change-this-secret-key"

price_service = PriceService()

BASE_DIR = Path(__file__).resolve().parent

MODEL_FILE = BASE_DIR / "models" / "sentiment_model.pkl"
VECTORIZER_FILE = BASE_DIR / "models" / "tfidf_vectorizer.pkl"

create_database()


@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))

    product_filter = request.args.get("product", "All Products").strip()
    source_filter = request.args.get("source", "All Sources").strip()

    available_products = get_distinct_products()
    reviews = get_reviews_filtered(product_filter, source_filter)

    # Master Intelligence Pipeline
    intelligence = run_complete_review_intelligence(
        reviews,
        product_name=product_filter if product_filter != "All Products" else "Catalog Overview",
        selected_source=source_filter
    )
    stats = get_dashboard_stats(product_filter, source_filter)

    return render_template(
        "index.html",
        stats=stats,
        total_reviews=stats["total"],
        positive_percent=stats["positive_percentage"],
        neutral_percent=stats["neutral_percentage"],
        negative_percent=stats["negative_percentage"],
        product=intelligence["product"],
        review_statistics=intelligence["review_statistics"],
        rating_dist=intelligence["rating_distribution"],
        aspect_intel=intelligence["aspect_intelligence"],
        ai_explanation=intelligence["ai_explanation"],
        suspicious_reviews=intelligence["suspicious_reviews"],
        suspicion_tiers=intelligence["suspicion_tiers"],
        suspicious_aspect_stats=intelligence["suspicious_aspect_stats"],
        review_clusters=intelligence["review_clusters"],
        available_sources=intelligence["available_sources"],
        selected_source=source_filter,
        available_products=available_products,
        selected_product=product_filter
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not name or not email or not password:
            return render_template("register.html", error="All fields are required.")

        password_hash = generate_password_hash(password)
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO users
                (name, email, password_hash)
                VALUES (?, ?, ?)
                """,
                (name, email, password_hash)
            )
            connection.commit()
        except sqlite3.IntegrityError:
            connection.close()
            return render_template("register.html", error="Email already registered.")

        connection.close()
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
            """,
            (email,)
        )
        user = cursor.fetchone()
        connection.close()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            return redirect(url_for("index"))

        return render_template("login.html", error="Invalid email or password.")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/add-review", methods=["POST"])
def add_customer_review():
    if "user_id" not in session:
        return redirect(url_for("login"))

    product_name = request.form.get("product_name", "").strip()
    review_text = request.form.get("review_text", "").strip()
    rating_value = request.form.get("rating", "").strip()
    source = request.form.get("source", "").strip() or "Direct"

    if not product_name or not review_text:
        return redirect(url_for("index"))

    try:
        rating = int(rating_value)
    except ValueError:
        rating = 3

    if rating < 1:
        rating = 1
    if rating > 5:
        rating = 5

    add_review(product_name, review_text, rating, source=source)

    sentiment = predict_sentiment(review_text)
    aspects = analyze_aspects(review_text)

    available_products = get_distinct_products()
    reviews = get_reviews_filtered(product_name, "All Sources")
    intelligence = run_complete_review_intelligence(
        reviews,
        product_name=product_name,
        selected_source="All Sources"
    )
    stats = get_dashboard_stats(product_name, "All Sources")

    return render_template(
        "index.html",
        stats=stats,
        total_reviews=stats["total"],
        positive_percent=stats["positive_percentage"],
        neutral_percent=stats["neutral_percentage"],
        negative_percent=stats["negative_percentage"],
        prediction=sentiment,
        analyzed_review=review_text,
        aspects=aspects,
        product=intelligence["product"],
        review_statistics=intelligence["review_statistics"],
        rating_dist=intelligence["rating_distribution"],
        aspect_intel=intelligence["aspect_intelligence"],
        ai_explanation=intelligence["ai_explanation"],
        suspicious_reviews=intelligence["suspicious_reviews"],
        suspicion_tiers=intelligence["suspicion_tiers"],
        suspicious_aspect_stats=intelligence["suspicious_aspect_stats"],
        review_clusters=intelligence["review_clusters"],
        available_sources=intelligence["available_sources"],
        selected_source="All Sources",
        available_products=available_products,
        selected_product=product_name
    )


@app.route("/analyze", methods=["POST"])
def analyze_review():
    if "user_id" not in session:
        return redirect(url_for("login"))

    review_text = request.form.get("review_text", "").strip()
    if not review_text:
        return redirect(url_for("index"))

    sentiment = predict_sentiment(review_text)
    aspects = analyze_aspects(review_text)

    available_products = get_distinct_products()
    reviews = get_reviews_filtered("All Products", "All Sources")
    intelligence = run_complete_review_intelligence(reviews, selected_source="All Sources")
    stats = get_dashboard_stats("All Products", "All Sources")

    return render_template(
        "index.html",
        stats=stats,
        total_reviews=stats["total"],
        positive_percent=stats["positive_percentage"],
        neutral_percent=stats["neutral_percentage"],
        negative_percent=stats["negative_percentage"],
        prediction=sentiment,
        analyzed_review=review_text,
        aspects=aspects,
        product=intelligence["product"],
        review_statistics=intelligence["review_statistics"],
        rating_dist=intelligence["rating_distribution"],
        aspect_intel=intelligence["aspect_intelligence"],
        ai_explanation=intelligence["ai_explanation"],
        suspicious_reviews=intelligence["suspicious_reviews"],
        suspicion_tiers=intelligence["suspicion_tiers"],
        suspicious_aspect_stats=intelligence["suspicious_aspect_stats"],
        review_clusters=intelligence["review_clusters"],
        available_sources=intelligence["available_sources"],
        selected_source="All Sources",
        available_products=available_products,
        selected_product="All Products"
    )


def predict_sentiment(text):
    if not MODEL_FILE.exists():
        return "Model Not Trained"
    if not VECTORIZER_FILE.exists():
        return "Vectorizer Not Found"

    try:
        model = joblib.load(MODEL_FILE)
        vectorizer = joblib.load(VECTORIZER_FILE)
        cleaned_text = clean_text(text)
        transformed_text = vectorizer.transform([cleaned_text])
        prediction = model.predict(transformed_text)[0]
        return str(prediction).title()
    except Exception as error:
        print("Prediction error:", error)
        return "Prediction Error"


def get_dashboard_stats(product_name="All Products", source="All Sources"):
    connection = get_connection()
    cursor = connection.cursor()

    query = """
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN sentiment = 'Positive' THEN 1 ELSE 0 END) AS positive,
            SUM(CASE WHEN sentiment = 'Neutral' THEN 1 ELSE 0 END) AS neutral,
            SUM(CASE WHEN sentiment = 'Negative' THEN 1 ELSE 0 END) AS negative
        FROM reviews
        WHERE 1=1
    """
    params = []

    if product_name and product_name != "All Products":
        query += " AND product_name = ?"
        params.append(product_name)

    if source and source != "All Sources":
        query += " AND LOWER(source) = LOWER(?)"
        params.append(source)

    cursor.execute(query, params)
    row = cursor.fetchone()
    connection.close()

    total = row["total"] or 0
    positive = row["positive"] or 0
    neutral = row["neutral"] or 0
    negative = row["negative"] or 0

    if total > 0:
        positive_percentage = round((positive / total) * 100, 1)
        neutral_percentage = round((neutral / total) * 100, 1)
        negative_percentage = round((negative / total) * 100, 1)
    else:
        positive_percentage = 0
        neutral_percentage = 0
        negative_percentage = 0

    return {
        "total": total,
        "positive": positive,
        "neutral": neutral,
        "negative": negative,
        "positive_percentage": positive_percentage,
        "neutral_percentage": neutral_percentage,
        "negative_percentage": negative_percentage
    }


@app.route("/reviews")
def reviews():
    if "user_id" not in session:
        return redirect(url_for("login"))

    review_list = get_all_reviews()
    return render_template("reviews.html", reviews=review_list)


@app.route("/analytics")
def analytics():
    if "user_id" not in session:
        return redirect(url_for("login"))

    product_data = get_product_analytics()
    return render_template("product_analytics.html", products=product_data)


def get_product_analytics():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            product_name,
            COUNT(*) AS total_reviews,
            SUM(CASE WHEN sentiment = 'Positive' THEN 1 ELSE 0 END) AS positive,
            SUM(CASE WHEN sentiment = 'Neutral' THEN 1 ELSE 0 END) AS neutral,
            SUM(CASE WHEN sentiment = 'Negative' THEN 1 ELSE 0 END) AS negative
        FROM reviews
        GROUP BY product_name
        ORDER BY total_reviews DESC
        """
    )
    rows = cursor.fetchall()
    connection.close()

    products = []
    for row in rows:
        p_name = row["product_name"]
        reviews_for_p = get_reviews_filtered(p_name, "All Sources")
        intel = run_complete_review_intelligence(reviews_for_p, product_name=p_name)

        products.append({
            "product_name": p_name,
            "total_reviews": row["total_reviews"],
            "positive": row["positive"] or 0,
            "neutral": row["neutral"] or 0,
            "negative": row["negative"] or 0,
            "average_rating": intel["product"]["overall_rating"],
            "aspects": intel["aspect_intelligence"],
            "explanation": intel["ai_explanation"]
        })

    return products


@app.route("/analyze-url", methods=["POST"])
def analyze_url():
    if "user_id" not in session:
        return redirect(url_for("login"))

    product_url = request.form.get("product_url", "").strip()
    if not product_url:
        return render_template("url_result.html", error="Please enter a product URL.")

    result = analyze_product_url(product_url)

    if not result.get("success"):
        return render_template(
            "url_result.html",
            error=result.get("message", "Unable to analyze the product URL.")
        )

    product_name = result.get("product_name", "Unknown Product")
    source_name = result.get("source_name", "Web")
    overall_rating = result.get("overall_rating", 0.0)
    has_distribution = result.get("has_distribution", False)
    source_histogram = result.get("rating_distribution", {}) if has_distribution else None
    extracted_reviews = result.get("reviews", [])

    analyzed_reviews = []
    for review in extracted_reviews:
        if isinstance(review, dict):
            review_text = review.get("text", "")
            rating = review.get("rating", 5)
            source = review.get("source", source_name)
            title = review.get("title", "")
            date_str = review.get("date", "")
            verified = review.get("verified_purchase", False)
        else:
            review_text = str(review)
            rating = 5
            source = source_name
            title = ""
            date_str = ""
            verified = False

        if not review_text:
            continue

        sentiment = predict_sentiment(review_text)
        aspects = analyze_aspects(review_text)

        analyzed_reviews.append({
            "title": title,
            "text": review_text,
            "rating": rating,
            "sentiment": sentiment,
            "aspects": aspects,
            "date": date_str,
            "verified_purchase": verified,
            "source": source
        })

    # Save to local database for product persistence
    if analyzed_reviews:
        try:
            save_collected_reviews_batch(product_name, analyzed_reviews, default_source=source_name)
        except Exception as e:
            print("Batch save notice:", e)

    # Master Intelligence Pipeline on 100% of collected reviews
    intelligence = run_complete_review_intelligence(
        analyzed_reviews,
        product_name=product_name,
        canonical_rating=overall_rating if overall_rating > 0 else None,
        extracted_histogram=source_histogram,
        selected_source=source_name,
        reviews_available_count=result.get("reviews_available"),
        limitation_reason=result.get("limitation_reason")
    )

    authenticity = result.get(
        "authenticity",
        {
            "available": False,
            "risk_level": "UNKNOWN",
            "score": 0,
            "checks": [],
            "warnings": [],
            "message": "Authenticity analysis not available."
        }
    )

    # Modular Price Intelligence Pipeline (isolated so failure never breaks reviews)
    price_comparison = None
    try:
        price_comparison = price_service.compare_prices(
            product_url=result.get("url", product_url),
            product_name=product_name,
            current_source=source_name
        )
    except Exception as price_err:
        print("Price comparison notice:", price_err)
        price_comparison = {
            "summary": {
                "has_comparison": False,
                "status_message": f"Price comparison notice: {str(price_err)}",
                "sources_compared": 0,
                "total_sources_checked": 2,
                "lowest_price": None,
                "highest_price": None,
                "price_difference": None
            },
            "prices": [],
            "valid_prices": [],
            "chart_data": {"labels": [], "values": [], "formatted_values": [], "percentages": []},
            "supported_sources": ["Amazon", "Flipkart"]
        }

    return render_template(
        "url_result.html",
        product_name=product_name,
        product_url=result.get("url", product_url),
        domain=result.get("domain", ""),
        source_name=source_name,
        product=intelligence["product"],
        review_statistics=intelligence["review_statistics"],
        reviews=analyzed_reviews,
        review_count=len(analyzed_reviews),
        rating_dist=intelligence["rating_distribution"],
        aspect_intel=intelligence["aspect_intelligence"],
        ai_explanation=intelligence["ai_explanation"],
        suspicious_reviews=intelligence["suspicious_reviews"],
        suspicion_tiers=intelligence["suspicion_tiers"],
        suspicious_aspect_stats=intelligence["suspicious_aspect_stats"],
        review_clusters=intelligence["review_clusters"],
        authenticity=authenticity,
        price_comparison=price_comparison
    )


@app.route("/url-agent")
def url_agent():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)