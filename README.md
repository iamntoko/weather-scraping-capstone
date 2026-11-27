# Weather Scraping Capstone

A capstone project collecting global city weather data with Selenium, cleaning and transforming records with Pandas, storing data in SQLite, querying via CLI, and building an interactive Streamlit dashboard.

## Week 1 Scope (Scraping & Data Cleaning)

- **Source:** [Time and Date Weather Around the World](https://www.timeanddate.com/weather/)
- **Scraper (`src/scraper.py`):** Uses Selenium and `webdriver-manager` with a custom User-Agent, safe cell/link extraction, and deduplication to save raw weather rows to `data/raw/raw_weather.csv`.
- **Cleaner (`src/cleaner.py`):** Loads `data/raw/raw_weather.csv` into Pandas, logs before/after cleaning metrics, normalizes missing/malformed fields, converts `°F` to `°C` and temperature tiers, prints grouped summaries, and saves `data/processed/cleaned_weather.csv`.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Usage (Week 1)

```bash
python3 -m src.scraper
python3 -m src.cleaner
```
