from pathlib import Path
import yaml
from datetime import datetime

from src.scraping.scraper import scrap_listing
from src.io import ensure_dir

def get_latest_date_folder(path: Path) -> Path | None:
    """
    Finds the folder with the latest date name in the given path.
    Assumes folder names are in date formats like YYYY-MM-DD, YYYYMMDD, or YYYY_MM_DD.
    Ignores non-date folders.
    """
    folders = [f for f in path.iterdir() if f.is_dir()]
    date_folders = {}
    for folder in folders:
        folder_name = folder.name
        for date_format in ["%Y-%m-%d", "%Y%m%d", "%Y_%m_%d"]:
            try:
                date_obj = datetime.strptime(folder_name, date_format)
                date_folders[folder_name] = date_obj
                break
            except ValueError:
                continue
    if date_folders:
        latest_folder_name = max(date_folders, key=date_folders.get)
        return path / latest_folder_name
    return None

def main():
    # Load config
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Root path
    PATH = Path(__file__).parent.parent
    DATA_PATH = Path(PATH,"data")

    # Get the latest date folder
    latest_folder = get_latest_date_folder(DATA_PATH)
    if latest_folder is None:
        print("No date-formatted folders found. Exiting.")
        exit(1)

    print(f"Using latest folder: {latest_folder.name}")

    # Define paths
    folder_urls = latest_folder / "urls" / "clean"
    folder_output = latest_folder / "listings"

    # Ensure output folder exists
    ensure_dir(folder_output)

    # Run the scraping
    scraping_cfg = config.get("scraping", {})
    max_workers = scraping_cfg.get("max_workers", 6)
    save_every = scraping_cfg.get("save_every", 50)
    page_load_timeout = scraping_cfg.get("page_load_timeout", 25)

    scrap_listing(
        folder_urls=folder_urls,
        folder_output=folder_output,
        config_elem=config["listing_classes"],
        max_workers=max_workers,
        save_every=save_every,
        page_load_timeout=page_load_timeout,
    )

if __name__ == "__main__":
    main()
