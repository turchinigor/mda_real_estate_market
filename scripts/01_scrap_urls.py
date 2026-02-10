from pathlib import Path
import yaml
import datetime

from src.scraping.scraper import scrap_urls_pipeline
from src.io import ensure_dir

# Load config for the base URLs
config_path = Path(__file__).parent.parent / "config" / "config.yaml"
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

#Find Today
today = datetime.date.today()

#Output Path
PATH_URLS = Path(Path(__file__).parent.parent / "data" / str(today)) / "urls" / "raw"

#Scrap all listings URLs
scrap_urls_pipeline(listing_types = config["urls"], scrap_classes = config["url_classes"], path = PATH_URLS)