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

def scrap_urls_pipeline(listing_types: dict, pages: int, path: str) -> None:
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.delete_all_cookies()
    for k, v in listing_types:
        logger.info("Started scraping: ", k)
        listings = scrap_urls(driver=driver, base_url=v, pages=pages, path=path, file_name=k)
        logger.info("Scraped %s listings from %c", len(listings), k)
    logger.info("Completed scraping the urls for all listing types")
    driver.close()
    driver.quit()