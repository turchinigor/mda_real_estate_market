"""
Used for reading and writing files
"""
from pathlib import Path
import json

def ensure_dir(path: Path) -> None:
    """
    Ensure path exists
    """
    if path.suffix:
        path = path.parent
    path.mkdir(parents=True, exist_ok=True)

def save_json(path: Path, listings: list[dict]) -> None:

    with open(path, "w", encoding="utf-8") as f:
        json.dump(listings, f, indent=2)