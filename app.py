"""
Flask Web Application for AI-Powered Customer Review Intelligence Agent.
Delegates heavy processing to the ReviewIntelligenceAgent and DatabaseManager.
"""

import logging
from flask import Flask, render_template, request, redirect, url_for, jsonify

import config
from database.db_manager import DatabaseManager
from agent.orchestrator import ReviewIntelligenceAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# Initialize Agent & Database
db_manager = DatabaseManager()
agent = ReviewIntelligenceAgent()


# ============================================================
# MAIN DASHBOARD / PRODUCT INTELLIGENCE ROUTE
# ============================================================

@app.route("/", methods=["GET", "POST"])
def home():
    """
    Main entry point for the ReviewInsight AI Dashboard.
    Accepts search queries for product analysis, executes agent workflow,
    and displays comprehensive product intelligence report.
    """
    product_query = request.args.get("product") or request.form.get("product")
    
    # Default initial product demonstration if none provided
    if not product_query:
        product_query = "Samsung Galaxy S25"

    product_query = product_query.strip()

    # Execute Agent Analysis Workflow
    report = agent.analyze_product(product_query)
    
    # Save generated report to history
    db_manager.save_product_report(report)

    return render_template(
        "index.html",
        report=report,
        product_query=product_query
    )


# ============================================================
# API ENDPOINT FOR PRODUCT ANALYSIS (AJAX / JSON)
# ============================================================

@app.route("/api/analyze", methods=["POST"])
def api_analyze_product():
    """
    JSON API endpoint for programmatic or asynchronous agent analysis.
    Accepts: { "product": "Product Name", "max_reviews": 50 }
    """
    data = request.get_json() or {}
    product_name = data.get("product", "").strip()
    max_reviews = int(data.get("max_reviews", 50))

    if not product_name:
        return jsonify({"status": "error", "message": "Product name is required."}), 400

    report = agent.analyze_product(product_name, max_reviews=max_reviews)
    db_manager.save_product_report(report)

    return jsonify({"status": "success", "report": report})


# ============================================================
# INDIVIDUAL REVIEW SUBMISSION (FOR TESTING / MANUAL INPUT)
# ============================================================

@app.route("/add-review", methods=["POST"])
def add_customer_review():
    """
    Handles single review submissions from the manual review form.
    Analyzes review with tools and stores it in the database.
    """
    product_name = request.form.get("product_name", "Unknown Product").strip()
    review_text = request.form.get("review_text", "").strip()
    rating = request.form.get("rating", "5")
    source = request.form.get("source", "Manual Input").strip()

    if not review_text:
        return redirect(url_for("home", product=product_name))

    try:
        rating_int = int(rating)
    except ValueError:
        rating_int = 5

    # Run sentiment & authenticity evaluation using agent tools
    sentiment_res = agent.sentiment_analyzer.analyze_sentiment(review_text)
    fake_res = agent.fake_detector.evaluate_review(review_text, rating_int)

    # Save to SQLite
    db_manager.add_review(
        product_name=product_name,
        review_text=review_text,
        rating=rating_int,
        source=source,
        sentiment=sentiment_res.get("sentiment", "neutral"),
        is_fake=fake_res.get("is_suspicious", False),
        fake_score=fake_res.get("suspicion_score", 0),
        fake_reason=fake_res.get("reasoning", ""),
        ai_explanation=sentiment_res.get("explanation", ""),
        confidence_score=sentiment_res.get("confidence", 75)
    )

    # Re-run agent intelligence report for this product
    return redirect(url_for("home", product=product_name))


# ============================================================
# REVIEW HISTORY ROUTE
# ============================================================

@app.route("/reviews")
def reviews():
    """Displays raw customer reviews stored in the database."""
    all_reviews = db_manager.get_all_reviews()
    return render_template("reviews.html", reviews=all_reviews)


# ============================================================
# PRODUCT ANALYTICS COMPARISON ROUTE
# ============================================================

@app.route("/product-analytics")
def product_analytics():
    """Displays aggregated sentiment comparisons across all products."""
    analytics_summary = db_manager.get_product_analytics_summary()
    return render_template("product_analytics.html", product_analytics=analytics_summary)


# ============================================================
# AI SUMMARY ROUTE (COMPATIBILITY)
# ============================================================

@app.route("/ai-summary")
def ai_summary():
    """Generates an executive summary for a product."""
    product = request.args.get("product", "Samsung Galaxy S25")
    report = agent.analyze_product(product)
    return jsonify({
        "product": product,
        "summary": report.get("ai_insights", ""),
        "key_takeaway": report.get("key_takeaway", ""),
        "recommendations": report.get("recommendations", [])
    })


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":
    app.run(
        debug=config.FLASK_DEBUG,
        port=config.FLASK_PORT
    )