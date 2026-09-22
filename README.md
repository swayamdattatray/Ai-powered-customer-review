# 🤖 AI-Powered Customer Review Intelligence Agent (ReviewInsight AI)

An autonomous, modular **AI Review Intelligence Agent** built with Python and Flask. The agent independently collects customer reviews, executes multi-tool natural language processing, discovers product aspects, evaluates review authenticity, tracks recurring customer pain points, and synthesizes executive product intelligence reports with strategic recommendations.

![ReviewInsight AI Dashboard](templates/preview_dashboard.png)

---

## 🌟 Why is this an "AI Agent"?

Unlike traditional review classifiers that require you to feed in one review at a time to predict Positive or Negative, **ReviewInsight AI** acts as an autonomous agent:
1. **Goal-Oriented Input**: You provide a target product (e.g. *Samsung Galaxy S25*, *iPhone 16*, or an e-commerce URL).
2. **Autonomous Tool Coordination**: The orchestrator (`ReviewIntelligenceAgent`) plans and executes the required steps:
   - **Review Collection**: Queries local databases or gathers multi-source review feeds.
   - **Preprocessing & Deduplication**: Cleans noise, normalizes text, and strips duplicate content.
   - **Sentiment Analysis**: Fast batch scoring with trained ML model and deep LLM reasoning.
   - **Aspect Mining**: Analyzes 8+ key aspects (Camera, Battery, Performance, Price, Build Quality, Display, Software, Delivery).
   - **Authenticity & Fake Review Detection**: Calculates a 0–100 suspicion risk score based on linguistic heuristics and AI patterns.
   - **Trend & Pattern Extraction**: Pinpoints top liked features and recurring customer complaints.
   - **Executive Synthesis**: Generates punchy key takeaways, nuanced paragraphs, and 5 actionable recommendations.
3. **Product Intelligence Dashboard**: Renders an executive UI matching modern enterprise analytics tools.

---

## 📁 Modular Project Architecture

```
AI-Customer-Review-Intelligence/
├── config.py                      # Centralized configuration, thresholds & environment variables
├── app.py                         # Clean Flask web controller (delegates to Agent)
│
├── core/                          # Swappable LLM Providers
│   ├── llm.py                     # Abstract BaseLLMProvider interface
│   └── gemini_provider.py         # Google Gemini (gemini-3.6-flash) implementation
│
├── agent/                         # Autonomous Orchestrator Layer
│   ├── orchestrator.py            # ReviewIntelligenceAgent coordination logic
│   └── prompts.py                 # Centralized AI prompt templates
│
├── tools/                         # Independent, Reusable Analysis Tools
│   ├── collector.py               # Review Collection Tool (DB + domain data feeds)
│   ├── preprocessor.py            # Sanitization, normalization & deduplication
│   ├── sentiment_analyzer.py      # Dual-engine Sentiment Analyzer (ML + LLM)
│   ├── aspect_analyzer.py         # Aspect extraction & aspect sentiment mining
│   ├── fake_detector.py           # Authenticity and suspicion scoring tool
│   ├── trend_analyzer.py          # Recurring complaints & positive patterns extractor
│   └── report_generator.py        # Executive report and recommendations synthesizer
│
├── database/                      # Swappable Database Layer
│   └── db_manager.py              # SQLite storage for reviews & full product reports
│
├── templates/                     # Modern ReviewInsight AI UI
│   ├── index.html                 # Main Agent Dashboard
│   ├── reviews.html               # Raw Reviews viewer
│   └── product_analytics.html     # Multi-product comparison
│
└── models/                        # Pre-trained Offline Scikit-Learn Fallback Models
    ├── sentiment_model.pkl        # Offline sentiment classifier
    └── tfidf_vectorizer.pkl       # TF-IDF vocabulary vectorizer
```

---

## 🎓 Student Extension Guide: How to Modify the Project

### 1. How to swap Gemini with OpenAI or another LLM
1. Open `core/llm.py` to see the `BaseLLMProvider` contract (`generate_text`, `generate_json`, `is_available`).
2. Create `core/openai_provider.py` implementing `BaseLLMProvider`.
3. In `core/__init__.py`, import and return your new provider when `config.LLM_PROVIDER == "openai"`.

### 2. How to add a real scraper (e.g., Amazon, Flipkart, Reddit)
1. Open `tools/collector.py`.
2. Add your scraping method (e.g. `scrape_amazon_reviews(product_url)`).
3. Call it inside `ReviewCollector.collect_reviews()`.

### 3. How to modify AI Prompts or Add New Product Aspects
- **Prompts**: Edit `agent/prompts.py` to modify the phrasing, rules, or tone of the AI analysis.
- **Aspects**: Open `tools/aspect_analyzer.py` and add new keywords to `DEFAULT_KEYWORDS` (e.g., `"packaging"`, `"warranty"`).

### 4. How to switch from SQLite to PostgreSQL / MySQL
- Open `database/db_manager.py` and update the connection method and queries. The rest of the application will continue working without any changes.

---

## 🚀 Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Your `.env` File
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL_NAME=gemini-3.6-flash
```
*(Get a free API key from [Google AI Studio](https://aistudio.google.com).)*

### 3. Run the Application
```bash
python app.py
```
Open **http://127.0.0.1:5000** in your browser to start analyzing products with your AI Agent!
