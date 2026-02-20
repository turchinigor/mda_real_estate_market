from selenium.webdriver.common.by import By
from selenium import webdriver
from datetime import datetime
from pathlib import Path
import pandas as pd
import time
import random
import logging
import yaml

from .utils import scrap_urls, get_all_properties
from ..io import ensure_dir, save_json, read_json
from ..logging_config import setup_logging, get_logger

# Seting up logging
logger = setup_logging(name="scraper")

### URL Scraping pipeline
def scrap_urls_pipeline(listing_types: dict, scrap_classes: dict, path: Path) -> None:
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.delete_all_cookies()
    for k, v in listing_types.items():
        logger.info("Started scraping: %s", k)
        listings = scrap_urls(driver=driver, base_url=v, scrap_classes=scrap_classes, path=path, file_name=f"{k}.json")
        logger.info("Scraped %s listings from %s", len(listings), k)
    logger.info("Completed scraping the urls for all listing types")
    driver.close()
    driver.quit()

### Listing Scraping pipeline

def iterate_listings(driver, urls_data, config_elem, history):
    history_json = read_json(history)
    if len(history_json) > 0:
        listings = history_json
    else:
        listings = []

    done = [u["url"] for u in history_json]
    remaining = [r for r in urls_data if r["url"] not in done]
    
    for i, row in enumerate(remaining, start=1):
        if i % 20 == 0:
            save_json(history, data=listings)
        driver.get(row["url"])
        time.sleep(random.uniform(1,2))
        properties = get_all_properties(driver=driver, row=row, scrap_elements=config_elem)
        if properties is None:
            logger.error("Listing skipped, missing information. URL: %s", row["url"])
            continue
        listings.append(properties)
    save_json(history, data=listings)
        


def scrap_listing():
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.delete_all_cookies()