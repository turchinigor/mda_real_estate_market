from selenium.webdriver.common.by import By
from selenium import webdriver
from datetime import datetime
from pathlib import Path
import pandas as pd
import time
import random
import logging
import yaml

from .utils import scrap_page, next_page, scrap_urls
from ..io import ensure_dir, save_json
from ..logging_config import setup_logging, get_logger

# Seting up logging
logger = setup_logging(name="scraper")

def scrap_urls_pipeline(listing_types: dict, path: Path) -> None:
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.delete_all_cookies()
    for k, v in listing_types.items():
        logger.info("Started scraping: %s", k)
        listings = scrap_urls(driver=driver, base_url=v, path=path, file_name=f"{k}.json")
        logger.info("Scraped %s listings from %s", len(listings), k)
    logger.info("Completed scraping the urls for all listing types")
    driver.close()
    driver.quit()