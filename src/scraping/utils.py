from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path
import time
import random

from ..io import save_json, read_json
from ..logging_config import setup_logging, get_logger

logger = setup_logging(name="scraper-utils")

def scrap_element_url(element_type, wrapper, identifier: str, extract_type: str = "text") -> str | None:
    try:
        elem = wrapper.find_element(element_type, identifier)
        if extract_type == "text":
            return elem.text
        else:
            return elem.get_attribute(extract_type)
    except Exception as e:
        print(f"Error extracting {extract_type}: {e}")
        return None

def scrap_page(driver, page: int) -> list[dict]:

    time.sleep(random.uniform(1, 2))

    wrapper_selector = "[class^='AdShort_wrapper__']"

    # Wait for the page to load (adjust selector as needed)
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, wrapper_selector))
        )
        print("Successfully found wrapper")
    except Exception as e:
        print(f"Timeout waiting for elements: {e}")
        return []  # Return empty if failed
    
    url_identifier_class = "[class^='AdShort_title__link__']"
    square_m2_class = "[class^='AdShort_distance__']"
    price_class = "[class^='AdShort_price__']"
    date_class = "[class^='AdShort_date__']"
    
    # Find all wrapper elements (each represents one listing)
    wrappers = driver.find_elements(By.CSS_SELECTOR, wrapper_selector)
    listings = []
    for i, wrapper in enumerate(wrappers):
        try:
            # Extract elements within each wrapper
            listing_url = scrap_element_url(element_type=By.CSS_SELECTOR, wrapper=wrapper, identifier=url_identifier_class, extract_type="href")

            description = scrap_element_url(element_type=By.CSS_SELECTOR, wrapper=wrapper, identifier=url_identifier_class, extract_type="text")
            
            square_m2 = scrap_element_url(element_type=By.CSS_SELECTOR, wrapper=wrapper, identifier=square_m2_class, extract_type="text")
            
            price = scrap_element_url(element_type=By.CSS_SELECTOR, wrapper=wrapper, identifier=price_class, extract_type="text")
            
            date = scrap_element_url(element_type=By.CSS_SELECTOR, wrapper=wrapper, identifier=date_class, extract_type="text")
            
            # Store in a dict
            listing = {
                "page": page,
                "url": listing_url,
                "description": description,
                "square_m2": square_m2,
                "price": price,
                "date": date,
            }
            listings.append(listing)
        except Exception as e:
            if "stale element" in str(e).lower():
                print(f"Stale element for listing {i}, skipping.")
            else:
                print(f"Error extracting data from listing {i}: {e}")
            continue  # Skip problematic listings
    
    return listings

def next_page(driver):
    next_button = "[class^='Pagination_pagination__container__buttons__wrapper__icon__next']"
    try:
        n_elem = driver.find_element(By.CSS_SELECTOR, next_button)
        n_elem.click()
        return True
    except Exception as e:
        return False

def scrap_urls(driver, base_url: str, pages: int, path: Path, file_name: str):
    try:
        existing_listings = read_json(Path(path, file_name))
    except Exception as e:
        logger.error(f"Failed to load existing listings: {e}. Starting fresh.")
        existing_listings = None
        
    if existing_listings is None or len(existing_listings) == 0:
        listings = []
        p = 1
    else:
        listings = existing_listings
        p = listings[-1]["page"]
        logger.info(f"Resuming scraping from page{p}")
    page_availability = True
    driver.get(base_url)
    while page_availability and p <= pages:
        listings_page = scrap_page(driver, p)
        listings.extend(listings_page)
        page_availability = next_page(driver)
        p += 1
        save_json(Path(path, file_name), listings=listings)
    return listings
# map_url_class = "adPage__content__map-redirect"
# ^ get.attribute("href")
# contains the longitude and latitude