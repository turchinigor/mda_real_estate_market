from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrap_url(driver, url: str) -> list[dict]:
    driver.get(url)
    
    # Wait for the page to load (adjust selector as needed)
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[class^='AdShort_wrapper__']"))
        )
    except Exception as e:
        print(f"Timeout waiting for elements: {e}")
        return []  # Return empty if failed
    
    wrapper_selector = "[class^='AdShort_wrapper__']"
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
            url_elem = wrapper.find_element(By.CSS_SELECTOR, url_identifier_class)
            listing_url = url_elem.get_attribute("href")
            description = url_elem.text
            
            square_m2_elem = wrapper.find_element(By.CSS_SELECTOR, square_m2_class)
            square_m2 = square_m2_elem.text
            
            price_elem = wrapper.find_element(By.CSS_SELECTOR, price_class)
            price = price_elem.text
            
            date_elem = wrapper.find_element(By.CSS_SELECTOR, date_class)
            date = date_elem.text
            
            # Store in a dict
            listing = {
                "url": listing_url,
                "description": description,
                "square_m2": square_m2,
                "price": price,
                "date": date
            }
            listings.append(listing)
        except Exception as e:
            if "stale element" in str(e).lower():
                print(f"Stale element for listing {i}, skipping.")
            else:
                print(f"Error extracting data from listing {i}: {e}")
            continue  # Skip problematic listings
    
    return listings