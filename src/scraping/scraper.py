from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from pathlib import Path
import pandas as pd
import time
import random
import logging
import yaml
import queue
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from .utils import scrap_urls, get_all_properties
from ..io import ensure_dir, save_json, read_json
from ..logging_config import setup_logging, get_logger

# Seting up logging
logger = setup_logging(name="scraper")

def build_driver(page_load_timeout: int | None = None):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.page_load_strategy = "eager"
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.managed_default_content_settings.fonts": 2,
        "profile.managed_default_content_settings.notifications": 2,
    }
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=options)
    if page_load_timeout is not None:
        driver.set_page_load_timeout(page_load_timeout)
    driver.delete_all_cookies()
    return driver

def wait_for_ready(driver, timeout: int = 20):
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") in ("interactive", "complete")
        )
    except Exception:
        # Fall back to whatever loaded state we have; downstream waits handle element presence.
        return

### URL Scraping pipeline
def scrap_urls_pipeline(listing_types: dict, scrap_classes: dict, path: Path) -> None:
    driver = build_driver()
    for k, v in listing_types.items():
        logger.info("Started scraping: %s", k)
        listings = scrap_urls(driver=driver, base_url=v, scrap_classes=scrap_classes, path=path, file_name=f"{k}.json")
        logger.info("Scraped %s listings from %s", len(listings), k)
    logger.info("Completed scraping the urls for all listing types")
    driver.close()
    driver.quit()

### Listing Scraping pipeline

def iterate_listings(driver, urls_data, config_elem, history: Path | None):
    if history is None or not history.exists():
        listings = []
        done = []
    else:
        history_json = read_json(history)
        if len(history_json) > 0:
            listings = history_json
            done = [u["url"] for u in history_json]
        else:
            listings = []
            done = []

    remaining = [r for r in urls_data if r["url"] not in done]
    
    for i, row in enumerate(remaining, start=1):
        if i % 20 == 0:
            save_json(history, data=listings)
        driver.get(row["url"])
        wait_for_ready(driver)
        properties = get_all_properties(driver=driver, row=row, scrap_elements=config_elem)
        if properties is None:
            logger.error("Listing skipped, missing information. URL: %s", row["url"])
            continue
        listings.append(properties)
    save_json(history, data=listings)

def _load_history(history: Path | None):
    if history is None or not history.exists():
        return [], set()
    history_json = read_json(history)
    if len(history_json) > 0:
        return history_json, {u["url"] for u in history_json}
    return [], set()

def _scrap_listing_file_parallel(
    file_path: Path,
    folder_output: Path,
    config_elem,
    max_workers: int,
    save_every: int,
    page_load_timeout: int | None,
):
    history = folder_output / file_path.name
    urls = read_json(file_path)
    listings, done = _load_history(history)
    remaining = [r for r in urls if r["url"] not in done]

    if not remaining:
        logger.info("No remaining URLs for %s", file_path.name)
        return

    q: queue.Queue = queue.Queue()
    for row in remaining:
        q.put(row)

    listings_lock = threading.Lock()
    processed = {"count": 0}

    def worker(worker_id: int):
        driver = build_driver(page_load_timeout=page_load_timeout)
        try:
            while True:
                try:
                    row = q.get_nowait()
                except queue.Empty:
                    break
                try:
                    driver.get(row["url"])
                    wait_for_ready(driver)
                    properties = get_all_properties(driver=driver, row=row, scrap_elements=config_elem)
                    if properties is None:
                        logger.error("Listing skipped, missing information. URL: %s", row["url"])
                    else:
                        with listings_lock:
                            listings.append(properties)
                            processed["count"] += 1
                            if processed["count"] % save_every == 0:
                                save_json(history, data=listings)
                except Exception as e:
                    logger.exception("Worker %s failed for URL %s: %s", worker_id, row.get("url"), e)
                    time.sleep(random.uniform(0.5, 1.5))
                finally:
                    q.task_done()
        finally:
            driver.close()
            driver.quit()

    logger.info("Processing %s URLs from %s with %s workers", len(remaining), file_path.name, max_workers)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(worker, i) for i in range(1, max_workers + 1)]
        for future in as_completed(futures):
            _ = future.result()

    save_json(history, data=listings)

def scrap_listing(
    folder_urls: Path,
    folder_output: Path,
    config_elem,
    max_workers: int = 6,
    save_every: int = 50,
    page_load_timeout: int | None = 25,
):
    ensure_dir(folder_output)
    
    for file_path in folder_urls.iterdir():
        if file_path.is_file():
            _scrap_listing_file_parallel(
                file_path=file_path,
                folder_output=folder_output,
                config_elem=config_elem,
                max_workers=max_workers,
                save_every=save_every,
                page_load_timeout=page_load_timeout,
            )
