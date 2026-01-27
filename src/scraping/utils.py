from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random


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

    time.sleep(1 + random.uniform(0.1, 0.3))

    wrapper_selector = "[class^='AdShort_wrapper__']"

    # Wait for the page to load (adjust selector as needed)
    try:
        WebDriverWait(driver, 10).until(
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

# map_url_class = "adPage__content__map-redirect"
# ^ get.attribute("href")
# contains the longitude and latitude