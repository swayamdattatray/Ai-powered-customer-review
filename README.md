# 🧠 AI-Powered Customer Review Intelligence Platform

A Flask-based web application that leverages **Google Gemini AI** and **Machine Learning** to perform real-time sentiment analysis, aspect-based opinion mining, and fake review detection on customer feedback.

---

## ✨ Features & Recent Updates

### 🤖 Gemini AI Integration
- **LLM-Powered Sentiment Analysis**: Uses Google's `gemini-3.6-flash` model for nuanced understanding of review sentiment.
- **AI Confidence Scoring**: Provides a 0–100% confidence level for sentiment classification.
- **Natural Language Explanations**: Generates concise AI reasoning explaining *why* a review was classified as positive, neutral, or negative.
- **Graceful Fallback**: Automatically falls back to an offline Scikit-Learn (TF-IDF + Logistic Regression/SVM) model if the AI API is unavailable.

### 🔍 Fake Review Detection
- **Authenticity Analysis**: Scans reviews for generic praise, repetitive language, suspicious patterns, or lack of specific details.
- **Suspicion Score**: Assigns a 0–100 risk score and marks reviews as **Appears Authentic** (low risk) or **Potentially Fake** (high risk).

### 📊 Comprehensive Dashboard & Analytics
- **Aspect-Based Opinion Mining**: Identifies key product aspects (camera, battery, performance, price, quality, delivery, display, sound) and detects aspect-specific sentiment.
- **Product-Wise Analytics**: Groups reviews by product name to track positive, neutral, and negative feedback percentages.
- **Review History**: Stores and logs past review submissions in a local SQLite database.
- **Automated Summarization API**: Endpoint (`/ai-summary?product=...`) that generates key strengths, weaknesses, and actionable recommendations.

---

## 🛠️ Tech Stack

- **Backend**: Python, Flask
- **Generative AI**: Google GenAI SDK (`google-genai`), `gemini-3.6-flash`
- **Machine Learning**: Scikit-Learn, TF-IDF Vectorizer, Joblib
- **Database**: SQLite3 (with automatic column migration)
- **Frontend**: HTML5, CSS3, Jinja2 Templates

---

## 🚀 Quick Start

### 1. Clone & Setup Environment
```bash
git clone https://github.com/swayamdattatray/Ai-powered-customer-review.git
cd Ai-powered-customer-review
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Key
Create a `.env` file in the project root directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```
> *Get a free API key from [Google AI Studio](https://aistudio.google.com).*

### 4. Run the Application
```bash
python app.py
```
Open your browser and navigate to `http://127.0.0.1:5000`.

---

## 📁 Project Structure

```
AI-Customer-Review-Intelligence/
├── app.py                          # Main Flask server and routes
├── database.py                     # SQLite database creation & migration
├── requirements.txt                # Python package dependencies
├── .env                            # API Keys (Git ignored)
├── utils/
│   ├── gemini_service.py           # Gemini API integration (Sentiment, Fake Detection, Summary)
│   └── aspect_analyzer.py          # Rule-based aspect sentiment analyzer
├── preprocessing/
│   └── text_preprocessor.py        # Text cleaning routines
├── models/
│   ├── sentiment_model.pkl         # Fallback ML classification model
│   └── tfidf_vectorizer.pkl        # TF-IDF vectorizer model
├── templates/
│   ├── index.html                  # Main dashboard with AI panels
│   ├── reviews.html                # Review history page
│   └── product_analytics.html      # Product-wise performance breakdown
└── training/
    ├── train_model.py              # ML model comparison and training script
    └── evaluate_model.py           # Evaluation script for offline ML model
```
