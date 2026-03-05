# 🕷️ Smart Scraper & Notifier

An automated web scraping tool with scheduled monitoring and notifications. Track prices, job listings, news, or any web content — get notified via email or Telegram when something changes.

## 🚀 Features

- **Multi-Site Scraping** — Configure multiple websites with CSS selectors
- **Smart Scheduling** — Run scrapes at custom intervals (minutes, hours, daily)
- **Change Detection** — Automatically detects when content changes
- **Notifications** — Get alerts via Email or Telegram
- **Data Storage** — Save scraped data to CSV for analysis
- **Rate Limiting** — Respectful scraping with configurable delays
- **Error Handling** — Retries, timeouts, and graceful failure
- **CLI Interface** — Easy-to-use command-line tool

## 🛠️ Tech Stack

| Technology | Purpose |
|-----------|---------|
| Python 3.10+ | Core language |
| BeautifulSoup4 | HTML parsing |
| Requests | HTTP client |
| APScheduler | Task scheduling |
| smtplib | Email notifications |
| python-telegram-bot | Telegram notifications |
| Pytest | Testing |

## 📁 Project Structure

```
smart-scraper/
├── scraper/
│   ├── __init__.py
│   ├── core.py              # Main scraper engine
│   ├── parser.py            # HTML parsing utilities
│   ├── scheduler.py         # Job scheduling
│   ├── notifier.py          # Email & Telegram notifications
│   ├── storage.py           # Data persistence (CSV)
│   └── config.py            # Configuration management
├── tests/
│   ├── __init__.py
│   ├── test_core.py
│   ├── test_parser.py
│   └── test_notifier.py
├── jobs.yaml                # Scraping job definitions
├── main.py                  # CLI entry point
├── requirements.txt
├── .gitignore
└── README.md
```

## ⚡ Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/noa-ravivo/smart-scraper.git
cd smart-scraper
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure a scraping job
Edit `jobs.yaml`:
```yaml
jobs:
  - name: "Tech News Monitor"
    url: "https://news.ycombinator.com"
    selector: ".titleline > a"
    interval_minutes: 60
    notify: ["email"]
```

### 5. Run the scraper
```bash
# Run once
python main.py scrape --job "Tech News Monitor"

# Run with scheduler (continuous monitoring)
python main.py monitor

# List all configured jobs
python main.py list
```

## 📋 Job Configuration

Define scraping jobs in `jobs.yaml`:

```yaml
jobs:
  - name: "Price Tracker"
    url: "https://example.com/product"
    selector: ".price-tag"
    extract: "text"           # text, attribute, or html
    interval_minutes: 30
    notify: ["email", "telegram"]
    on_change: true           # Only notify when value changes
    
  - name: "Job Listings"
    url: "https://example.com/careers"
    selector: ".job-card .title"
    extract: "text"
    interval_minutes: 120
    max_items: 10
    notify: ["telegram"]
```

### Configuration Options

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Job identifier |
| `url` | string | Target URL |
| `selector` | string | CSS selector for target elements |
| `extract` | string | What to extract: `text`, `html`, or attribute name |
| `interval_minutes` | int | How often to scrape (in minutes) |
| `notify` | list | Notification channels: `email`, `telegram` |
| `on_change` | bool | Only notify on content changes (default: true) |
| `max_items` | int | Limit number of extracted items |
| `headers` | dict | Custom HTTP headers |

## 🔔 Notification Setup

### Email
Set environment variables:
```bash
export SMTP_HOST=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USER=your@email.com
export SMTP_PASSWORD=your-app-password
export NOTIFY_EMAIL=recipient@email.com
```

### Telegram
```bash
export TELEGRAM_BOT_TOKEN=your-bot-token
export TELEGRAM_CHAT_ID=your-chat-id
```

## 🧪 Running Tests

```bash
pytest tests/ -v
```

```
tests/test_core.py::test_fetch_page_success PASSED
tests/test_core.py::test_fetch_page_timeout PASSED
tests/test_core.py::test_fetch_page_retry PASSED
tests/test_parser.py::test_extract_text PASSED
tests/test_parser.py::test_extract_multiple PASSED
tests/test_parser.py::test_extract_attribute PASSED
tests/test_notifier.py::test_email_notification PASSED
tests/test_notifier.py::test_telegram_notification PASSED
tests/test_notifier.py::test_change_detection PASSED
```

## 📊 Output Example

```
$ python main.py scrape --job "Tech News Monitor"

[2026-03-05 10:30:00] Scraping: Tech News Monitor
[2026-03-05 10:30:01] Found 30 items
[2026-03-05 10:30:01] 3 new items detected
[2026-03-05 10:30:02] Notification sent via Telegram ✓
[2026-03-05 10:30:02] Data saved to output/tech_news_2026-03-05.csv
```

## 🔮 Future Improvements

- [ ] Headless browser support (Playwright) for JavaScript-rendered sites
- [ ] Dashboard UI for monitoring jobs
- [ ] Webhook notifications
- [ ] Docker deployment
- [ ] Proxy rotation support

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
