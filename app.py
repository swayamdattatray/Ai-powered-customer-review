"""
Flask Web Application for AI-Powered Customer Review Intelligence Agent.
Handles dashboard rendering, dynamic product investigations, multi-product comparisons,
review intelligence explorer with evidence modals, and conversational 'Ask the Review Agent'.
"""

import logging
from flask import Flask, render_template, request, redirect, url_for, jsonify

import config
from database.db_manager import DatabaseManager
from agent.orchestrator import ReviewIntelligenceAgent
from agent.chat_agent import ReviewChatAgent
from tools.comparator import ProductComparator

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# Initialize Agent, Database, and Chat Agent
db_manager = DatabaseManager()
agent = ReviewIntelligenceAgent()
chat_agent = ReviewChatAgent()


# ============================================================
# MAIN DASHBOARD / PRODUCT INTELLIGENCE ROUTE
# ============================================================

@app.route("/", methods=["GET", "POST"])
def home():
    """
    Main entry point for the ReviewInsight AI Dashboard.
    Accepts product names or URLs, coordinates agent investigation,
    and renders the rich intelligence report.
    """
    product_query = request.args.get("product") or request.form.get("product")
    source_filter = request.args.get("source") or request.form.get("source")
    
    if not product_query:
        product_query = "Samsung Galaxy S25"

    product_query = product_query.strip()
    sources = [source_filter] if source_filter and source_filter != "auto" else None

    # Execute Agent Analysis Workflow
    report = agent.analyze_product(product_query, sources=sources)
    db_manager.save_product_report(report)

    return render_template(
        "index.html",
        report=report,
        product_query=product_query,
        source_filter=source_filter or "auto"
    )


# ============================================================
# CONVERSATIONAL "ASK THE REVIEW AGENT" API ROUTE
# ============================================================

@app.route("/api/chat", methods=["POST"])
def api_chat():
    """
    Interactive Q&A API endpoint.
    Accepts: { "question": "Why are battery complaints high?", "product": "Samsung Galaxy S25" }
    """
    data = request.get_json() or {}
    question = data.get("question", "").strip()
    product_name = data.get("product", "Samsung Galaxy S25").strip()

    if not question:
        return jsonify({"status": "error", "message": "Question is required."}), 400

    # Retrieve or generate product report
    report = db_manager.get_latest_report(product_name)
    if not report:
        report = agent.analyze_product(product_name)

    reply = chat_agent.answer_question(question, report)
    return jsonify({
        "status": "success",
        "answer": reply.get("answer", ""),
        "grounded_facts": reply.get("grounded_facts", [])
    })


# ============================================================
# PRODUCT COMPARISON ROUTE
# ============================================================

@app.route("/compare", methods=["GET", "POST"])
def compare():
    """
    Side-by-side product comparison interface.
    """
    product_a = request.args.get("product_a") or request.form.get("product_a") or "Samsung Galaxy S25"
    product_b = request.args.get("product_b") or request.form.get("product_b") or "iPhone 16 Pro"

    report_a = agent.analyze_product(product_a)
    report_b = agent.analyze_product(product_b)

    comparison_data = ProductComparator.compare_reports(report_a, report_b)

    return render_template(
        "compare.html",
        product_a=product_a,
        product_b=product_b,
        comparison=comparison_data,
        report_a=report_a,
        report_b=report_b
    )


# ============================================================
# ASYNC API ENDPOINT FOR PRODUCT ANALYSIS
# ============================================================

@app.route("/api/analyze", methods=["POST"])
def api_analyze_product():
    """
    Programmatic JSON API endpoint for agent analysis.
    """
    data = request.get_json() or {}
    product_name = data.get("product", "").strip()
    sources = data.get("sources")
    max_reviews = int(data.get("max_reviews", 50))

    if not product_name:
        return jsonify({"status": "error", "message": "Product name is required."}), 400

    report = agent.analyze_product(product_name, sources=sources, max_reviews=max_reviews)
    db_manager.save_product_report(report)

    return jsonify({"status": "success", "report": report})


# ============================================================
# INDIVIDUAL REVIEW SUBMISSION (MANUAL INPUT)
# ============================================================

@app.route("/add-review", methods=["POST"])
def add_customer_review():
    """Handles single review submissions."""
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

    sentiment_res = agent.sentiment_analyzer.analyze_sentiment(review_text)
    fake_res = agent.fake_detector.evaluate_review(review_text, rating_int)

    db_manager.add_review(
        product_name=product_name,
        review_text=review_text,
        rating=rating_int,
        source=source,
        sentiment=sentiment_res.get("sentiment", "neutral"),
        is_fake=fake_res.get("is_suspicious", False),
        fake_score=fake_res.get("suspicion_score", 0),
        fake_reason="; ".join(fake_res.get("why_flagged", [])),
        ai_explanation=sentiment_res.get("explanation", ""),
        confidence_score=sentiment_res.get("confidence", 85)
    )

    return redirect(url_for("home", product=product_name))


# ============================================================
# REVIEW HISTORY & INTELLIGENCE EXPLORER ROUTE
# ============================================================

@app.route("/reviews")
def reviews():
    """Displays stored customer reviews with filtering options."""
    all_reviews = db_manager.get_all_reviews()
    return render_template("reviews.html", reviews=all_reviews)


# ============================================================
# PRODUCT ANALYTICS SUMMARY ROUTE
# ============================================================

@app.route("/product-analytics")
def product_analytics():
    """Displays multi-product aggregated sentiment comparisons."""
    analytics_summary = db_manager.get_product_analytics_summary()
    return render_template("product_analytics.html", product_analytics=analytics_summary)


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":
    app.run(
        debug=config.FLASK_DEBUG,
        port=config.FLASK_PORT
    )