from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import joblib

from database import create_database, add_review
from preprocessing.text_preprocessor import clean_text
from utils.aspect_analyzer import analyze_aspects


# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(__name__)


# ============================================================
# CREATE DATABASE
# ============================================================

create_database()


# ============================================================
# LOAD MACHINE LEARNING MODEL
# ============================================================

model = joblib.load(
    "models/sentiment_model.pkl"
)

vectorizer = joblib.load(
    "models/tfidf_vectorizer.pkl"
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():

    connection = sqlite3.connect(
        "customer_reviews.db"
    )

    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# PREDICT SENTIMENT
# ============================================================

def predict_sentiment(review_text):

    if not review_text:

        return "neutral"

    # Clean review text
    cleaned = clean_text(
        review_text
    )

    # Convert text into TF-IDF vector
    vector = vectorizer.transform(
        [cleaned]
    )

    # Predict sentiment
    prediction = model.predict(
        vector
    )[0]

    # Convert result to lowercase
    prediction = str(
        prediction
    ).strip().lower()

    return prediction


# ============================================================
# DASHBOARD STATISTICS
# ============================================================

def get_dashboard_stats():

    connection = get_connection()

    rows = connection.execute("""
        SELECT review_text
        FROM reviews
    """).fetchall()

    connection.close()

    total = 0

    positive = 0
    neutral = 0
    negative = 0


    # --------------------------------------------------------
    # ANALYZE ALL REVIEWS
    # --------------------------------------------------------

    for row in rows:

        review_text = row["review_text"]

        if not review_text:
            continue

        total += 1

        prediction = predict_sentiment(
            review_text
        )


        if prediction == "positive":

            positive += 1

        elif prediction == "neutral":

            neutral += 1

        elif prediction == "negative":

            negative += 1


    # --------------------------------------------------------
    # CALCULATE PERCENTAGES
    # --------------------------------------------------------

    if total > 0:

        positive_percent = round(
            (positive / total) * 100,
            1
        )

        neutral_percent = round(
            (neutral / total) * 100,
            1
        )

        negative_percent = round(
            (negative / total) * 100,
            1
        )

    else:

        positive_percent = 0
        neutral_percent = 0
        negative_percent = 0


    return (
        total,
        positive_percent,
        neutral_percent,
        negative_percent
    )


# ============================================================
# SENTIMENT ANALYTICS COUNTS
# ============================================================

def get_sentiment_counts():

    connection = get_connection()

    rows = connection.execute("""
        SELECT review_text
        FROM reviews
    """).fetchall()

    connection.close()

    positive = 0
    neutral = 0
    negative = 0


    # --------------------------------------------------------
    # COUNT SENTIMENTS
    # --------------------------------------------------------

    for row in rows:

        review_text = row["review_text"]

        if not review_text:
            continue

        prediction = predict_sentiment(
            review_text
        )


        if prediction == "positive":

            positive += 1

        elif prediction == "neutral":

            neutral += 1

        elif prediction == "negative":

            negative += 1


    return (
        positive,
        neutral,
        negative
    )


# ============================================================
# PRODUCT-WISE ANALYTICS
# ============================================================

def get_product_analytics():

    connection = get_connection()

    rows = connection.execute("""
        SELECT
            product_name,
            review_text
        FROM reviews
        WHERE product_name IS NOT NULL
        AND TRIM(product_name) != ''
    """).fetchall()

    connection.close()

    product_data = {}


    # ========================================================
    # PROCESS EACH REVIEW
    # ========================================================

    for row in rows:

        # Clean product name
        product = row["product_name"]

        if product:

            product = product.strip()

        else:

            continue


        # Get review
        review_text = row["review_text"]

        if not review_text:
            continue


        # ----------------------------------------------------
        # PREDICT SENTIMENT
        # ----------------------------------------------------

        prediction = predict_sentiment(
            review_text
        )


        # ----------------------------------------------------
        # CREATE PRODUCT ENTRY
        # ----------------------------------------------------

        if product not in product_data:

            product_data[product] = {

                "total": 0,

                "positive": 0,

                "neutral": 0,

                "negative": 0,

                "positive_percent": 0,

                "neutral_percent": 0,

                "negative_percent": 0

            }


        # ----------------------------------------------------
        # INCREASE TOTAL
        # ----------------------------------------------------

        product_data[product]["total"] += 1


        # ----------------------------------------------------
        # INCREASE SENTIMENT COUNT
        # ----------------------------------------------------

        if prediction == "positive":

            product_data[product]["positive"] += 1

        elif prediction == "neutral":

            product_data[product]["neutral"] += 1

        elif prediction == "negative":

            product_data[product]["negative"] += 1


    # ========================================================
    # CALCULATE PRODUCT PERCENTAGES
    # ========================================================

    for product, data in product_data.items():

        total = data["total"]


        if total > 0:

            data["positive_percent"] = round(
                (data["positive"] / total) * 100,
                1
            )

            data["neutral_percent"] = round(
                (data["neutral"] / total) * 100,
                1
            )

            data["negative_percent"] = round(
                (data["negative"] / total) * 100,
                1
            )


    return product_data


# ============================================================
# HOME PAGE / DASHBOARD
# ============================================================

@app.route("/")
def home():

    # --------------------------------------------------------
    # GET DASHBOARD STATISTICS
    # --------------------------------------------------------

    stats = get_dashboard_stats()


    # --------------------------------------------------------
    # GET SENTIMENT COUNTS
    # --------------------------------------------------------

    sentiment_counts = get_sentiment_counts()


    # --------------------------------------------------------
    # GET PRODUCT ANALYTICS
    # --------------------------------------------------------

    product_analytics = get_product_analytics()


    # --------------------------------------------------------
    # DISPLAY DASHBOARD
    # --------------------------------------------------------

    return render_template(

        "index.html",

        # Dashboard statistics
        total_reviews=stats[0],

        positive_percent=stats[1],

        neutral_percent=stats[2],

        negative_percent=stats[3],

        # Sentiment counts
        positive_count=sentiment_counts[0],

        neutral_count=sentiment_counts[1],

        negative_count=sentiment_counts[2],

        # Product analytics
        product_analytics=product_analytics

    )


# ============================================================
# ADD AND ANALYZE CUSTOMER REVIEW
# ============================================================

@app.route(
    "/add-review",
    methods=["POST"]
)
def add_customer_review():

    # ========================================================
    # GET FORM DATA
    # ========================================================

    product_name = request.form.get(
        "product_name",
        ""
    ).strip()


    review_text = request.form.get(
        "review_text",
        ""
    ).strip()


    rating = request.form.get(
        "rating",
        ""
    ).strip()


    source = request.form.get(
        "source",
        ""
    ).strip()


    # ========================================================
    # CHECK REVIEW TEXT
    # ========================================================

    if not review_text:

        return redirect(
            url_for("home")
        )


    # ========================================================
    # CHECK PRODUCT NAME
    # ========================================================

    if not product_name:

        product_name = "Unknown Product"


    # ========================================================
    # CHECK SOURCE
    # ========================================================

    if not source:

        source = "Unknown"


    # ========================================================
    # CONVERT AND VALIDATE RATING
    # ========================================================

    if rating:

        try:

            rating = int(
                rating
            )


            # Rating must be between 1 and 5

            if rating < 1 or rating > 5:

                rating = None


        except ValueError:

            rating = None

    else:

        rating = None


    # ========================================================
    # SENTIMENT ANALYSIS
    # ========================================================

    prediction = predict_sentiment(
        review_text
    )


    # ========================================================
    # ASPECT ANALYSIS
    # ========================================================

    aspects = analyze_aspects(
        review_text
    )


    # ========================================================
    # SAVE REVIEW TO DATABASE
    # ========================================================

    add_review(

        product_name,

        review_text,

        rating,

        source,

        prediction

    )


    # ========================================================
    # UPDATE DASHBOARD
    # ========================================================

    stats = get_dashboard_stats()


    sentiment_counts = get_sentiment_counts()


    product_analytics = get_product_analytics()


    # ========================================================
    # DISPLAY RESULTS
    # ========================================================

    return render_template(

        "index.html",

        # ----------------------------------------------------
        # Dashboard
        # ----------------------------------------------------

        total_reviews=stats[0],

        positive_percent=stats[1],

        neutral_percent=stats[2],

        negative_percent=stats[3],


        # ----------------------------------------------------
        # Sentiment counts
        # ----------------------------------------------------

        positive_count=sentiment_counts[0],

        neutral_count=sentiment_counts[1],

        negative_count=sentiment_counts[2],


        # ----------------------------------------------------
        # Current review analysis
        # ----------------------------------------------------

        prediction=prediction,

        analyzed_review=review_text,

        aspects=aspects,


        # ----------------------------------------------------
        # Product analytics
        # ----------------------------------------------------

        product_analytics=product_analytics

    )


# ============================================================
# REVIEW HISTORY
# ============================================================

@app.route("/reviews")
def reviews():

    connection = get_connection()


    reviews = connection.execute("""
        SELECT *
        FROM reviews
        ORDER BY created_at DESC
    """).fetchall()


    connection.close()


    return render_template(

        "reviews.html",

        reviews=reviews

    )


# ============================================================
# PRODUCT ANALYTICS PAGE
# ============================================================

@app.route("/product-analytics")
def product_analytics():

    # --------------------------------------------------------
    # GET PRODUCT ANALYTICS
    # --------------------------------------------------------

    product_data = get_product_analytics()


    # --------------------------------------------------------
    # DISPLAY PRODUCT ANALYTICS PAGE
    # --------------------------------------------------------

    return render_template(

        "product_analytics.html",

        product_analytics=product_data

    )


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )