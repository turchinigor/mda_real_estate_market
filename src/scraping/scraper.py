from selenium.webdriver.common.by import By
from selenium import webdriver
import time
import random
from datetime import datetime
import pandas as pd
from pathlib import Path
from .utils import scrap_page, next_page
from ..io import ensure_dir, save_json
import yaml

#TODO: Add function to read file per real estate type if exists
#TODO: Save listings after each page
#TODO: Implement fall back in case the script fails, to start where it stoped
#TODO: Add all of it to one function only

# Load config
config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

#Output Path
PATH_OUT = Path(__file__).parent.parent.parent / "data" / "tests"
ensure_dir(PATH_OUT)

driver = webdriver.Chrome()
driver.maximize_window()
driver.delete_all_cookies()

#Base URL for Appartments
URL_AP = config['urls']['apartments']

#Base URL for Houses
URL_HOUSES = config['urls']['houses']

#Base URL for Land lots
URL_LAND = config['urls']['land']

driver.get(URL_AP)

def scrap_urls(driver, base_url, pages):
    page_availability = True
    p = 1
    listings = []
    driver.get(base_url)
    while page_availability and p <= pages:
        listings_page = scrap_page(driver, p)
        listings.extend(listings_page)
        page_availability = next_page(driver)
        p += 1
    return listings
listings = scrap_urls(driver=driver, base_url=URL_AP, pages=6)
save_json(Path(PATH_OUT, "listings.json"), listings=listings)

driver.close()
driver.quit()

