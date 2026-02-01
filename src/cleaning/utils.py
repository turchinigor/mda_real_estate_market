import pandas as pd

def get_currency(s: pd.Series) -> pd.Series:
    s = s.astype("string")
    has_slash = s.str.contains("/", regex=False, na=False).any()
    if has_slash:
        out = s.str.split().str[-1].str.split("/", regex=False).str[0]
    else:
        out = s.str.split().str[-1]
    return out

def get_price_eur(p: pd.Series, c: pd.Series, e: dict) -> pd.Series:
    str_p = p.astype("string").str.split().str[:-1].str.join("").str.strip()
    num_p = pd.to_numeric(str_p, errors="coerce")
    converted = num_p * c.map(e)
    return converted