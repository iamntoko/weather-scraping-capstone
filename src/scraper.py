from pathlib import Path
import time
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

URL = "https://www.timeanddate.com/weather/"
RAW_OUTPUT = Path("data/raw/raw_weather.csv")
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


def create_driver(headless: bool = True) -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-agent={USER_AGENT}")
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def safe_cell_text(cells: list, index: int, default: str = "") -> str:
    if index >= len(cells):
        return default
    return " ".join(cells[index].text.split())


def safe_link_href(cells: list, index: int, default: str = "") -> str:
    if index >= len(cells):
        return default
    try:
        href = cells[index].find_element(By.TAG_NAME, "a").get_attribute("href")
        return href.strip() if href else default
    except NoSuchElementException:
        return default


def scrape_weather_table(driver: webdriver.Chrome, url: str) -> list[dict]:
    driver.get(url)
    time.sleep(2)

    rows = driver.find_elements(By.CSS_SELECTOR, "table tr")
    records: list[dict] = []
    seen_keys: set[tuple[str, str, str]] = set()

    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) < 5:
            continue

        city = safe_cell_text(cells, 0)
        country = safe_cell_text(cells, 1)
        condition_raw = safe_cell_text(cells, 3)
        temp_raw = safe_cell_text(cells, 4)
        wind_raw = safe_cell_text(cells, 5)
        local_time_raw = safe_cell_text(cells, 6)
        city_url = safe_link_href(cells, 0, default=url)

        if not city:
            continue

        dedup_key = (city.lower(), country.lower(), city_url)
        if dedup_key in seen_keys:
            continue
        seen_keys.add(dedup_key)

        records.append({
            "city": city,
            "country": country,
            "condition_raw": condition_raw,
            "temp_raw": temp_raw,
            "wind_raw": wind_raw,
            "local_time_raw": local_time_raw,
            "source_url": city_url,
        })

    return records


def save_raw_csv(records: list[dict], output_path: Path = RAW_OUTPUT) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(records)
    df.to_csv(output_path, index=False)
    return output_path


def main() -> None:
    driver = create_driver(headless=True)
    try:
        records = scrape_weather_table(driver, URL)
        out_file = save_raw_csv(records, RAW_OUTPUT)
        print(f"Collected {len(records)} unique weather rows -> {out_file}")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()