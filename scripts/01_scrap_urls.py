from pathlib import Path
import yaml
import datetime

from ..src.scraping.scraper import scrap_urls_pipeline

# Load config for the base URLs
config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

#Find Today
today = datetime.datetime.today()

#Output Path
PATH_URLS = Path(__file__).parent.parent / "data" / "urls" / today

#Scrap all listings URLs
scrap_urls_pipeline(listing_types = config["urls"], pages = 6, path = PATH_URLS)