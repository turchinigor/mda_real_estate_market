from pathlib import Path
from datetime import datetime

from src.cleaning.clean_raw import iter_over_files

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
    folder_urls = latest_folder / "urls" / "raw"
    folder_output = latest_folder / "urls" / "clean"

    exchange_to_eur = {
        "€": 1,
        "$": 0.84,
        "MDL": 0.05,
        "lei": 0.05,
    }

    iter_over_files(path_in=folder_urls, path_out=folder_output, e=exchange_to_eur)

if __name__ == "__main__":
    main()