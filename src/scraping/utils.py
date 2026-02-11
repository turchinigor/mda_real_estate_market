from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path
import time
import random

from ..io import save_json, read_json
from ..logging_config import setup_logging, get_logger

logger = setup_logging(name="scraper-utils")

########################################################
#Scrap URLs
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

def scrap_page(driver, scrap_classes: dict, page: int) -> list[dict]:

    time.sleep(random.uniform(1, 2))

    wrapper_selector = scrap_classes["wrapper"]

    # Wait for the page to load (adjust selector as needed)
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, wrapper_selector))
        )
        print("Successfully found wrapper")
    except Exception as e:
        print(f"Timeout waiting for elements: {e}")
        return []  # Return empty if failed
    
    url_identifier_class = scrap_classes["url_identifier_class"]
    square_m2_class = scrap_classes["square_m2_class"]
    price_class = scrap_classes["price_class"]
    date_class = scrap_classes["date_class"]
    
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

def next_page(driver, next_button):
    try:
        n_elem = driver.find_element(By.CSS_SELECTOR, next_button)
        # Check if button is enabled (not disabled)
        if n_elem.get_attribute("disabled") is None:
            n_elem.click()
            return True
        else:
            logger.info("Next button is disabled - reached last page")
            return False
    except Exception as e:
        logger.warning(f"Could not find next button: {e}")
        return False

def scrap_urls(driver, base_url: str, scrap_classes: dict, path: Path, file_name: str):
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
        p = listings[-1]["page"] + 1
        logger.info(f"Resuming scraping from page{p}")
    page_availability = True
    driver.get(base_url)
    if p > 1:
        for _ in range(p-1):
            next_page(driver, scrap_classes["next_button"])
    while page_availability:
        listings_page = scrap_page(driver, scrap_classes, p)
        listings.extend(listings_page)
        page_availability = next_page(driver, scrap_classes["next_button"])
        p += 1
        save_json(Path(path, file_name), data=listings)
    return listings


##############################################################
#Scrap listings
def get_features(driver, feature_elem: str) -> dict | None:
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, feature_elem))
        )
    except Exception as e:
        logger.info("Features elements not found")
        return None
    features = driver.find_elements(By.CSS_SELECTOR, f"div{feature_elem} li")
    properties = {}
    for feature_point in features:
        feature = feature_point.find_elements("xpath", ".//span | .//a")
        if len(feature) >= 2:
            label = feature[0].text.strip()
            value = feature[1].text.strip()
            if label and value:
                properties[label] = value
    return properties

def get_price(driver, price_elem):
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, price_elem["price_main"]))
        )
        logger.info("Located price element in listing")
    except:
        logger.info("Price element not located")
        return None
    
    properties = {}
    
    try:
        # Base price
        price1 = driver.find_element(By.CSS_SELECTOR, f'span{price_elem["price_main"]}').text.strip()
        print(f"1st Price {price1}")
    except:
        print("Price not available")
        price1 = ""

    # Converted prices
    try:
        converted = driver.find_elements(By.CSS_SELECTOR, f'ul {price_elem["price_converted"]} li')
        price2 = converted[0].text.strip().replace("≈", "") if len(converted) > 0 else ""
        price3 = converted[1].text.strip().replace("≈", "") if len(converted) > 1 else ""
    except:
        print("Prices not available")
        price2, price3 = "", ""

    # Clean and assign by currency
    for price in [price1, price2, price3]:
        if "€" in price:
            properties["Price €"] = int(price.replace("€", "").replace(" ", "").replace(",", ""))
        elif "$" in price:
            properties["Price $"] = int(price.replace("$", "").replace(" ", "").replace(",", ""))
        elif "MDL" in price:
            properties["Price MDL"] = int(price.replace("MDL", "").replace(" ", "").replace(",", ""))

    return properties

def get_region(driver, region_elem):

    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, region_elem))
        )
        logger.info("Located region element in listing")
    except:
        logger.info("Region element not located")
        return {"Address": ""}
    
    address = driver.find_element(By.CSS_SELECTOR, f'div{region_elem}').text
    return {"Address": address}

def get_coordinates(driver, coordinates_elem):
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, coordinates_elem))
        )
        logger.info("Located URL containing the coordinates")
    except Exception as e:
        logger.info("URL not found")
        return None
    
    properties = {}
    url_elem = driver.find_element(By.CSS_SELECTOR, coordinates_elem)
    url = url_elem.get_attribute("href")
    url_parts = url.split("/")
    if len(url_parts) < 2:
        logger.error("Can't extract coordinates")
        return None
    
    latitude = url_parts[-2].strip()
    longitude = url_parts[-1].strip()
    properties["latitude"] = latitude
    properties["longitude"] = longitude
    return properties

def get_all_properties(driver, scrap_elements) -> dict | None:
    features = get_features(driver, feature_elem=scrap_elements["features"])
    if features is None:
        logger.info("Features not found, listing is skiped")
        return None
    price = get_price(driver, price_elem=scrap_elements)
    if price is None:
        logger.info("Price not found, listing is skiped")
        return None
    coordinates = get_coordinates(driver, coordinates_elem=scrap_elements["map_url_class"])
    if coordinates is None:
        logger.info("Coordinates not found, listing is skiped")
    region = get_region(driver, region_elem=scrap_elements["region"])
    properties = features | price | coordinates | region
    return properties

def move_listings(driver, scrap_elements):
    ...