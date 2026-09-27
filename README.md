# 🚀 TrendTracker
### *Next-Generation Real-Time Competitor Content Monitoring & Intelligence Platform*


> Built with **FastAPI**, **React 19**, **Tailwind CSS**, **SQLAlchemy 2.0 Async**, **HTTPX Async**, **BeautifulSoup4**, **feedparser**, and **APScheduler**. Featuring a newly modernized, premium dark-mode UI.

---

## 1. System Overview & Architecture

TrendTracker is a real-time intelligence and monitoring platform designed to detect when competitor websites publish new articles as quickly as possible. The primary engineering challenge is **detection intelligence, timing accuracy, and non-blocking scale**, rather than simple page scraping.

```text
                  Competitor Website / Target URL
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │    Website Analyzer     │
                    │ (Autonomous Discovery)  │
                    └────────────┬────────────┘
                                 │
                    Find available sources
                                 │
          ┌──────────────────────┼──────────────────────┐
          ▼                      ▼                      ▼
    Method 1: RSS        Method 2: Sitemap      Method 3: Direct Page
  (/feed, /rss.xml)     (/sitemap.xml, Index)       (/blog, /news)
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 ▼
                   Concurrent Monitoring Engine
                   (Bounded Async Worker Pool)
                                 │
                                 ▼
                          New Article?
                           /        \
                        NO            YES
                        │              │
                        │              ▼
                        │     Article Extraction
                        │ (Title, Author, Body, Images)
                        │              │
                        │              ▼
                        │      Deduplication
                        │ (Canonical URL Unique Index)
                        │              │
                        │              ▼
                        │   Calculate Detection Delay
                        │ (Delay = Detected_at - Published_at)
                        │              │
                        └──────────────┴─────► Real-Time Dashboard (WebSocket)
```

---

## 2. Key Features

### ⏱️ 1. High-Precision Detection Delay Analytics & SLA Benchmark
Unlike ordinary web scrapers, TrendTracker measures the exact latency between when an article is published by a competitor and when the monitoring engine discovers it:
$$\text{Detection Delay} = \text{Detected Time (UTC)} - \text{Published Time (UTC)}$$

- **Primary Performance Target**: $\le 5\text{ minutes}$ ($300\text{ seconds}$).
- **Transparent Metrics**: Exact delays are displayed without rounding (e.g. `47s`, `3m 12s`, `14m 22s`).
- **Dashboard KPIs**: Average Detection Time, Fastest Detection, Slowest Detection, and % Within 5-Minute Target SLA.

### 🧠 2. Autonomous Website Analyzer (Strategy Selection)
When an admin adds a website URL (e.g. `techcrunch.com` or `aws.amazon.com/blogs`), the system autonomously investigates the domain without requiring technical configurations:
1. Probes HTML `<link>` tags and common endpoints for RSS 2.0 / Atom feeds.
2. Checks `robots.txt` and XML sitemaps / sitemap indexes (e.g. `post-sitemap.xml`).
3. Discovers blog index pages and semantic article container patterns.
4. Identifies structured publication metadata signals (JSON-LD `datePublished`, OpenGraph `article:published_time`, `<time datetime="...">`).
5. Generates the optimal monitoring strategy (e.g., `RSS + Sitemap` or `Sitemap + Direct Page`).

### 📡 3. The Three Mandatory Detection Methods
1. **Method 1 — RSS / Atom Feeds**: Fast XML parser reading standard feeds, extracting publication timestamps (`pubDate`, `published_parsed`).
2. **Method 2 — XML Sitemaps & Sitemap Indexes**: Recursive sitemap index traverser checking `<urlset>` and `<lastmod>` timestamps.
3. **Method 3 — Direct Blog Page Monitoring**: DOM-based article link pattern extraction and content change detection for websites without feeds or sitemaps.

### ⚡ 4. The 100-Website Problem: Non-Blocking Concurrent Scaling
- **Bounded Async Worker Pool**: Uses `asyncio.Semaphore` (25-50 workers) and async HTTPX requests.
- **Fault Isolation**: Each site check executes inside an isolated coroutine with individual timeouts (5.0s default). If Site #27 hangs or errors, it never blocks Sites #28 through #100.
- **Scale Benchmark Studio**: Built-in interactive stress-testing panel capable of simulating 100 concurrent targets, measuring throughput (req/s), latency percentiles (p50, p95, p99), and proving zero-blocking resilience.

### 🧪 5. Built-in Controlled Demo Testbed
TrendTracker comes equipped with a live interactive publisher at `/demo/blog`, `/demo/rss.xml`, and `/demo/sitemap.xml`:
- Admin can publish custom or preset articles with adjustable publication timestamps (e.g., "Published right now", "Published 3 minutes ago", "Published 12 minutes ago").
- Live verification: Watch the engine detect the article within seconds, compute the exact Detection Delay, and broadcast the notification over WebSockets.

### 💎 6. Premium UI & Modern Aesthetics
Following a comprehensive UI rebranding, the frontend features a deeply immersive, modern design:
- **Obsidian & Violet Theme**: A striking dark mode leveraging deep slate/obsidian backgrounds with vibrant violet and indigo accents.
- **Micro-Animations & Glassmorphism**: Interactive hover states, smooth transitions, and premium glassmorphism effects for modal dialogs and navigation bars.
- **Dynamic Dashboards**: Responsive grids and Recharts integration providing a state-of-the-art data visualization experience for monitoring latency and system metrics.

---

## 3. Project Structure

```text
TrendTracker/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI entrypoint, lifespan, WebSockets
│   │   ├── config.py                  # Environment settings & SLA configuration
│   │   ├── database/
│   │   │   ├── models.py              # SQLAlchemy models (Competitors, Sources, Articles, Logs)
│   │   │   └── session.py             # Async database session & engine
│   │   ├── analyzers/
│   │   │   ├── website_analyzer.py    # Master Autonomous Website Analyzer
│   │   │   ├── rss_detector.py        # RSS / Atom feed detector
│   │   │   ├── sitemap_detector.py    # XML Sitemap & Sitemap Index detector
│   │   │   └── blog_detector.py       # Blog section & article structure detector
│   │   ├── monitors/
│   │   │   ├── rss_monitor.py         # Method 1: RSS Monitor
│   │   │   ├── sitemap_monitor.py     # Method 2: XML Sitemap Monitor
│   │   │   ├── page_monitor.py        # Method 3: Direct Blog Page Monitor
│   │   │   ├── timing_engine.py       # Detection delay & SLA calculation engine
│   │   │   ├── concurrency_pool.py    # Multi-worker async scheduler & deduplicator
│   │   │   └── scheduler.py           # Continuous APScheduler background job
│   │   ├── extraction/
│   │   │   └── article_extractor.py   # Full article body, metadata & image extractor
│   │   ├── api/
│   │   │   ├── competitors.py         # Competitor management endpoints
│   │   │   ├── articles.py            # Detected articles & deep inspector API
│   │   │   ├── dashboard.py           # KPI analytics & latency time-series API
│   │   │   ├── analysis.py            # Standalone site inspection endpoint
│   │   │   ├── benchmark.py           # 100-Website scale benchmark test engine
│   │   │   ├── demo_publisher.py      # Controlled demo testing blog & RSS feed
│   │   │   └── websocket.py           # Real-time WebSocket event broadcaster
│   │   └── utils/
│   │       └── http_client.py         # Async HTTP client with timeout & latency tracking
│   ├── tests/
│   │   └── test_detection.py          # Pytest suite for timing engine & monitors
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx             # Top bar, live status, quick navigation
│   │   │   ├── StatCards.jsx          # KPI cards (Delay, Speed Extremes, SLA %)
│   │   │   ├── PerformanceCharts.jsx  # Recharts detection delay timeline & methods
│   │   │   ├── CompetitorModal.jsx    # Add Competitor with live AI discovery
│   │   │   ├── CompetitorsView.jsx    # Competitor fleet management
│   │   │   ├── ArticlesView.jsx       # Filterable detected articles feed
│   │   │   ├── ArticleModal.jsx       # Deep article content & metadata viewer
│   │   │   ├── DemoPublisherStudio.jsx# Interactive testbed publisher
│   │   │   ├── BenchmarkStudio.jsx    # 100-Website concurrency test studio
│   │   │   └── LiveEventTicker.jsx    # Real-time WebSocket alert toasts
│   │   ├── services/
│   │   │   └── api.js                 # Axios API service
│   │   ├── App.jsx                    # Root state & view orchestration
│   │   └── index.css                  # Tailwind CSS v4 styling & animations
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
│
├── docker-compose.yml
├── start_dev.bat                      # 1-Click Windows development launcher
└── README.md
```

---

## 4. Quick Start & Setup Instructions

### Prerequisites
- **Python 3.10+**
- **Node.js 18+** & **npm**
- *(Optional)* **Docker & Docker Compose**

### Running Locally (Zero-Config Development Mode)

#### 1. Start the Backend
```bash
cd backend
python -m venv venv

# Windows:
.\venv\Scripts\activate

# Linux/macOS:
# source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
*Backend API will run at `http://127.0.0.1:8000` (Swagger UI at `/docs`)*.

#### 2. Start the Frontend
```bash
cd frontend
npm install
npm run dev
```
*Frontend will run at `http://localhost:3000` with automatic backend proxying*.

#### 3. Or 1-Click Launch on Windows
Double-click `start_dev.bat` in the project root directory.

---

## 5. Running with Docker Compose

To launch the complete distributed stack with PostgreSQL:
```bash
docker-compose up --build
```
- Frontend UI: `http://localhost:3000`
- FastAPI API: `http://localhost:8000`
- PostgreSQL Database: `localhost:5432`

---

## 6. Running Unit & Integration Tests

```bash
cd backend
.\venv\Scripts\pytest
```

---

## 7. Examination Live Demonstration Guide

| Step | Action | Expected Outcome |
| :--- | :--- | :--- |
| **1. Add Competitor** | Navigate to **Competitors** $\rightarrow$ Click **+ Add Target** $\rightarrow$ Enter URL (e.g. `techcrunch.com` or `aws.amazon.com/blogs/architecture`) | System performs autonomous probing, locates RSS feed / Sitemap / Blog section, displays capabilities matrix, and saves configuration. |
| **2. Test Demo Blog** | Navigate to **Interactive Demo Blog** tab $\rightarrow$ Choose preset or custom title $\rightarrow$ Set simulated publish time (e.g. 2 mins ago) $\rightarrow$ Click **Publish & Trigger Live Detection Scan** | Article is published to `/demo/blog` and `/demo/rss.xml`. TrendTracker detects it immediately, computes exact Detection Delay (`2m 00s`), and displays a real-time toast alert. |
| **3. Inspect Articles** | Navigate to **Detected Articles** tab $\rightarrow$ Click on the article row | Modal opens showing extracted full body text, author, publication time, detection time, delay badge, and OpenGraph/JSON-LD metadata. |
| **4. Scale Benchmark** | Navigate to **100-Website Scale Bench** $\rightarrow$ Configure 100 sites and 25 workers $\rightarrow$ Click **Execute Scale Test** | Runs concurrent async simulation, demonstrating 15x-25x speedup over sequential execution, zero-blocking on slow endpoints, and percentile latency breakdown. |

---

## 8. License
Academic & Examination Distribution — Developed for Pillai College Advanced Web Engineering Curriculum.
