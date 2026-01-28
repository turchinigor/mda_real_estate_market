"""
Used for reading and writing files
"""
from pathlib import Path
import json

from .logging_config import setup_logging, get_logger

logger = setup_logging(name="io")

def ensure_dir(path: Path) -> None:
    """
    Ensure path exists
    """
    if path.suffix:
        path = path.parent
    path.mkdir(parents=True, exist_ok=True)

def save_json(path: Path, data) -> None:
    ensure_dir(path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def read_json(path: Path) -> list[dict] | None:
    if not path.exists():
        logger.warning(f"File doesn't exist: {path}")
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info(f"Successfully loaded {len(data)}")
        return data
    except json.JSONDecodeError as e:
        logger.error(f"JSON file corrupted at {path}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error reading file {path}: {e}")
        return None