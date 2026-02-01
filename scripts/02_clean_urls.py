from pathlib import Path

from src.cleaning.clean_raw import iter_over_files


PATH_IN = Path(__file__).parent.parent / "data" / "2026-01-29" / "urls" / "raw"
PATH_OUT = Path(__file__).parent.parent / "data" / "2026-01-29" / "urls" / "clean"

exchange_to_eur = {
    "€": 1,
    "$": 0.84,
    "MDL": 0.05,
    "lei": 0.05,
}

iter_over_files(path_in=PATH_IN, path_out=PATH_OUT, e=exchange_to_eur)