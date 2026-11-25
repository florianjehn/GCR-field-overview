"""
Download and parse Long-Term Future Fund (LTFF) grants from EA Funds.

Source: https://funds.effectivealtruism.org/grants. The page embeds all
published grants as JSON in its __NEXT_DATA__ script tag. Only grants from
the "Long-Term Future Fund" are kept.

Caveat: the database lists published grants only. Anonymous or unpublished
grants are missing, so yearly totals are a lower bound (e.g. 2023 sums to
$5.2M here, below LTFF's reported total payouts).

Run with:
    uv run python3 -m src.ltff_grants
"""

import datetime as dt
import json
import re
import urllib.request
from pathlib import Path

import pandas as pd

SOURCE_URL = "https://funds.effectivealtruism.org/grants"
FUND_NAME = "Long-Term Future Fund"
RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
NEXT_DATA_PATTERN = re.compile(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.S)


def download_page(url):
    """
    Downloads a web page as text.

    Arguments:
        url (str): the page URL

    Returns:
        str: the page HTML.
    """
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read().decode("utf-8")


def extract_grants(page_html):
    """
    Extracts the embedded grants list from the page.

    Arguments:
        page_html (str): the EA Funds grants page HTML

    Returns:
        list: grant dicts as published by EA Funds.
    """
    data = json.loads(NEXT_DATA_PATTERN.search(page_html).group(1))
    return data["props"]["pageProps"]["grantsList"]


def grants_to_frame(grants, fund_name=FUND_NAME):
    """
    Converts grants of one fund into a tidy DataFrame.

    Arguments:
        grants (list): grant dicts from extract_grants
        fund_name (str): the fund to keep

    Returns:
        pandas.DataFrame: one row per grant.
    """
    rows = [
        {
            "funder": fund_name,
            "grant_id": f"ltff-{grant['id']}",
            "award_year": grant["year"],
            "round": grant["round"],
            "recipient": grant["grantee"],
            "description": grant["description"],
            "amount_usd": grant["amount"],
            "source_url": SOURCE_URL,
        }
        for grant in grants
        if grant["fund"] == fund_name
    ]
    return pd.DataFrame(rows)


def main():
    """
    Downloads the page, saves the raw JSON and the tidy LTFF CSV.

    Returns:
        None
    """
    grants = extract_grants(download_page(SOURCE_URL))
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    raw_path = RAW_DIR / f"ea_funds_grants_{dt.date.today().isoformat()}.json"
    raw_path.write_text(json.dumps(grants, indent=1, ensure_ascii=False))
    frame = grants_to_frame(grants)
    if frame["grant_id"].duplicated().any():
        raise ValueError("Duplicate LTFF grant ids")
    frame.to_csv(PROCESSED_DIR / "ltff_grants.csv", index=False)
    print(f"Parsed {len(frame)} LTFF grants")
    print(frame.groupby("award_year")["amount_usd"].agg(["size", "sum"]))


if __name__ == "__main__":
    main()
