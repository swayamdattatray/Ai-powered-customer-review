# 🛒 AI-Powered E-Commerce Shopping Intelligence & Review Analytics

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Vite](https://img.shields.io/badge/Vite-5.4-646CFF?logo=vite&logoColor=white)](https://vitejs.dev)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-3.4-38B2AC?logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org)

An integrated, production-ready AI shopping intelligence platform featuring a **Chrome Browser Extension (Manifest V3)**, an expansive **Dedicated Full-Page Analytics Dashboard**, a high-performance **FastAPI Backend**, and a **Flask Review Explorer**.

The platform protects online shoppers by performing deep **Review Credibility Auditing**, **Aspect-Based Sentiment Mining**, **Cross-Platform Price Intelligence (Amazon India, Flipkart, etc.)**, and **Seller & Counterfeit Risk Detection**.

---

## 🌟 Key Capabilities

### 1. 🔍 Automatic Product Detection & Dual-Entry Extension
* **Smart Content Extractor**: Automatically detects product listings across Amazon India (`amazon.in`), Flipkart (`flipkart.com`), and Schema.org microdata pages.
* **Contextual Badge**: Injects a clean, non-intrusive floating intelligence badge on e-commerce product pages.
* **Dual Launch Modes**:
  * **Compact Side Panel**: Glanceable summary for immediate ratings, price status, and trust score.
  * **Dedicated Full-Page Dashboard (`dashboard.html`)**: Opens an expansive 1080p+ workspace via `chrome.tabs.create` with tabbed deep-dive visualisations without UI z-index collisions.

### 2. 🛡️ Review Credibility & Scam Risk Audit (Trust Score 0–100)
* **Linguistic & Statistical Analysis**: Identifies duplicate review bodies, template-driven bot phrasing, generic filler feedback, and rating-text polarity discrepancies.
* **Temporal Cluster Detection**: Uncovers suspicious review spikes and coordinated rating bursts.
* **Explainable Trust Breakdown**: Displays overall trust score, proportion of suspicious reviews, confidence rating, and explicit limitations of available data.
* **Counterfeit & Scam Dossier**: Evaluates seller reputation, return-policy red flags, and unauthorized third-party marketplace risks.

### 3. 📊 Aspect-Based Sentiment Mining
* **Granular Product Aspects**: Analyzes feedback across Battery, Performance, Build Quality, Display, Value for Money, and Customer Support.
* **Interactive Sentiment Distributions**: Aspect score bars, sentiment breakdown (positive, neutral, negative), and representative customer quotes.

### 4. 💰 Cross-Platform Price Comparison (INR ₹)
* **Real-Time Retailer Comparison**: Matches identical listings between Amazon, Flipkart, Croma, and Official Brand stores.
* **Transparent Landed Price Calculation**:
  $$\text{Final Price} = \text{Listed Price} + \text{Shipping} + \text{Handling} - \text{Verified Discounts}$$
* **Match Confidence Indicator**: Distinguishes verified model matches from fuzzy title matches.

### 5. 🤖 Shopping Decision Assistant
* **Synthesis & Verdict**: Generates grounded recommendations, key trade-offs, buying caveats, and alternative product suggestions strictly anchored to verified data.

---

## 📁 System Architecture

```
AI-Customer-Review-Intelligence/
├── backend/                       # Production FastAPI Backend
│   └── app/
│       ├── api/v1/endpoints.py    # REST APIs (/audit, /price-compare, /scam-risk, /history)
│       ├── config.py              # CORS, API keys & environment settings
│       ├── main.py                # FastAPI ASGI application entrypoint
│       ├── schemas/contracts.py   # Strict Pydantic v2 data models
│       └── services/              # Domain Intelligence Engines
│           ├── price_engine.py    # Cross-retailer price matcher
│           ├── product_matcher.py # GTIN / ASIN / Fuzzy text normalization
│           ├── review_auditor.py  # Credibility & linguistic heuristic auditor
│           ├── scam_engine.py     # Seller credibility & scam risk evaluator
│           └── history_tracker.py # Query & audit persistence
│
├── extension/                     # Chrome Browser Extension (Manifest V3)
│   ├── manifest.json              # MV3 configuration (side panel, tabs, storage)
│   ├── vite.config.ts             # Multi-page build config (Dashboard + Side Panel)
│   ├── package.json               # TypeScript, React 18, Lucide icons, Tailwind
│   └── src/
│       ├── background/            # Background service worker (state caching, tab launch)
│       ├── content/               # Content scripts & DOM extractors (Amazon, Flipkart)
│       ├── dashboard/             # Full-Page Dashboard SPA
│       │   ├── App.tsx            # Main intelligence dashboard container
│       │   ├── index.html         # Full-page tab entrypoint
│       │   └── components/        # Modular dashboard cards (Decision, Clusters, Prices, Scam)
│       ├── sidepanel/             # Compact Side Panel UI
│       └── types/contracts.ts     # TypeScript interface mirrors of backend schemas
│
├── price_intelligence/            # Python Price Intelligence Modules
│   ├── amazon_price_collector.py  # Amazon India price parser
│   ├── flipkart_price_collector.py# Flipkart price parser
│   └── price_service.py           # Unified multi-source comparator
│
├── app.py                         # Flask Web Controller & Review Explorer
├── database.py                    # SQLite Review persistence
├── templates/                     # Flask HTML templates
├── requirements.txt               # Python package dependencies
└── .env.example                   # Environment configuration template
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
* **Python 3.10+**
* **Node.js 18+** & **npm 9+**
* **Google Chrome** (or Chromium-based browser)

---

### 2. Backend Setup (FastAPI)

1. **Activate Python Virtual Environment**:
   ```powershell
   # Windows PowerShell
   .\venv\Scripts\Activate.ps1
   ```

2. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Copy `.env.example` to `.env` and fill in any optional API keys:
   ```bash
   cp .env.example .env
   ```

4. **Launch FastAPI Backend Server**:
   ```bash
   python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   API interactive documentation will be available at:
   * Swagger UI: **http://127.0.0.1:8000/docs**
   * Redoc: **http://127.0.0.1:8000/redoc**

---

### 3. Extension Setup (Chrome Manifest V3)

1. **Navigate to the extension directory**:
   ```bash
   cd extension
   ```

2. **Install Node Dependencies & Build**:
   ```bash
   npm install
   npm run build
   ```
   This generates the production bundle in `extension/dist/`.

3. **Load Unpacked Extension into Chrome**:
   1. Open Google Chrome and navigate to `chrome://extensions/`.
   2. Toggle **Developer mode** on (top right).
   3. Click **Load unpacked** (top left).
   4. Select the `extension/dist` folder (or `extension` directory).
   5. Navigate to any Amazon India or Flipkart product listing to see the floating AI badge!

---

### 4. Running Backend Unit Tests

Run test suite to verify data contracts and calculation pipelines:
```bash
pytest backend/tests/test_contracts.py -v
```

---

## 🛡️ Privacy & Compliance
* **Grounded Heuristics**: Review credibility scores are calculated objectively from linguistic patterns and distributions; predictions are transparently tagged with explicit data limitations.
* **No CAPTCHA Bypassing**: Respects marketplace access boundaries, relying on permitted DOM extracts and public product metadata.
* **Isolated Extension Architecture**: Extension components operate with scoped permissions (`storage`, `tabs`, `sidePanel`) and isolated Tailwind styles to prevent interfering with host store pages.

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
