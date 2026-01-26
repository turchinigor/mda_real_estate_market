from selenium.webdriver.common.by import By
from selenium import webdriver
import time
import random
from datetime import datetime
import pandas as pd
from pathlib import Path
from .utils import scrap_url
from ..io import ensure_dir, save_json
import yaml

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

#TODO: Fix scrap_url / Reads the wrapper, but returns an empty list
listings = scrap_url(driver=driver, url=URL_AP)
save_json(Path(PATH_OUT, "listings.json"), listings=listings)

driver.close()
driver.quit()