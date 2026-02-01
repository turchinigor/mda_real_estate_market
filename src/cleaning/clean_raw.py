from pathlib import Path
import pandas as pd
from .utils import get_currency, get_price_eur
from ..io import read_json, save_excel

PATH_DATA = Path(__file__).parent.parent.parent / "data" / "2026-01-29" / "urls" / "raw"

def clean_urls_df(df: pd.DataFrame, e: dict) -> pd.DataFrame:

    df = df.dropna(subset=["url"]).reset_index(drop=True)
    df["currency"] = get_currency(df["price"])
    df["currency_m2"] = get_currency(df["square_m2"])
    df["price"] = get_price_eur(p=df["price"], c=df["currency"], e=e)
    df["price_m2"] = get_price_eur(p=df["square_m2"], c=df["currency_m2"], e=e)
    df["url"] = df["url"].astype("string").str.split("?", n=1).str[0]
    s = df["date"].astype("string").str.lower()

    month_map = {
        "ian.": "01", "feb.": "02", "mar.": "03", "apr.": "04",
        "mai": "05", "iun.": "06", "iul.": "07", "aug.": "08",
        "sept.": "09", "oct.": "10", "nov.": "11", "dec.": "12",
    }

    # replace month name with number
    for k, v in month_map.items():
        s = s.str.replace(k, v, regex=False)

    # now parse: "29 01 2026, 21:20"
    df["date"] = pd.to_datetime(s, format="%d %m %Y, %H:%M", errors="coerce")
    df = df.drop(columns=["square_m2"])
    df = df.drop_duplicates(subset=["url"]).drop_duplicates(subset=["description", "price", "price_m2"])
    df = df[df["price"] > 3000]
    return df.reset_index(drop=True)

def iter_over_files(path_in: Path, path_out: Path, e: dict) -> None:

    for p in path_in.iterdir():
        if p.is_file():
            data = read_json(p)
            df = pd.DataFrame(data)
            out = clean_urls_df(df=df, e=e)
            save_excel(path=Path(path_out, f"{p.stem}.xlsx"), df=out)

