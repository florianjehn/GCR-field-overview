"""
Download and parse the Survival and Flourishing Fund (SFF) recommendations table.

Source: https://survivalandflourishing.fund/recommendations (one HTML table,
one row per recommendation). Notes on the "Amount" column:
- "$4,000 and $26,000": amounts from two funders (e.g. Tallinn and Moskovitz),
  summed into `amount_usd`.
- "+$16,000‡" or "$1,607,000‡": a Matching Pledge, paid only if the recipient
  raises outside funds. Stored separately in `matching_pledge_usd`.
SFF lists recommendations; the page notes some may not be finalised as grants.

Run with:
    uv run python3 -m src.sff_grants
"""

import datetime as dt
import html
import re
import urllib.request
from pathlib import Path

import pandas as pd

SOURCE_URL = "https://survivalandflourishing.fund/recommendations"
RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
COLUMNS = ["round", "source", "organization", "amount", "receiving_charity", "purpose"]
DOLLAR_PATTERN = re.compile(r"\$([\d,]+)(‡?)")


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


def clean_cell(cell_html):
    """
    Strips tags and HTML entities from a table cell.

    Arguments:
        cell_html (str): the raw cell HTML

    Returns:
        str: the cell text.
    """
    return html.unescape(re.sub(r"<[^>]+>", "", cell_html)).strip()


def parse_table(page_html):
    """
    Extracts the recommendation rows from the page HTML.

    Arguments:
        page_html (str): the recommendations page HTML

    Returns:
        list: one dict per table row, keyed by COLUMNS.
    """
    rows = []
    for row_html in re.findall(r"<tr>(.*?)</tr>", page_html, flags=re.S):
        cells = re.findall(r"<td[^>]*>(.*?)</td>", row_html, flags=re.S)
        if len(cells) == len(COLUMNS):
            rows.append(dict(zip(COLUMNS, [clean_cell(c) for c in cells])))
    return rows


def parse_amount(amount_text):
    """
    Splits an SFF amount string into firm and matching-pledge dollars.

    Arguments:
        amount_text (str): e.g. "$29,000 +$277,000‡ and $1,541,000"

    Returns:
        tuple: (firm amount in USD, matching pledge in USD).
    """
    firm, matching = 0, 0
    for number, dagger in DOLLAR_PATTERN.findall(amount_text):
        value = int(number.replace(",", ""))
        if dagger:
            matching += value
        else:
            firm += value
    return firm, matching


def round_to_year(round_name):
    """
    Extracts the calendar year from an SFF round name.

    Arguments:
        round_name (str): e.g. "SFF-2023-H2" or "Initiative Committee 2024"

    Returns:
        int: the year.
    """
    return int(re.search(r"20\d\d", round_name).group())


def rows_to_frame(rows):
    """
    Converts parsed rows into a tidy DataFrame with parsed amounts.

    Arguments:
        rows (list): dicts from parse_table

    Returns:
        pandas.DataFrame: one row per recommendation.
    """
    frame = pd.DataFrame(rows)
    amounts = frame["amount"].apply(parse_amount)
    frame["amount_usd"] = [firm for firm, _ in amounts]
    frame["matching_pledge_usd"] = [matching for _, matching in amounts]
    frame["award_year"] = frame["round"].apply(round_to_year)
    frame["funder"] = "Survival and Flourishing Fund"
    frame["grant_id"] = [f"sff-{i:04d}" for i in range(len(frame) - 1, -1, -1)]
    frame["source_url"] = SOURCE_URL
    return frame


def main():
    """
    Downloads the table, parses it and saves raw HTML and tidy CSV.

    Returns:
        None
    """
    today = dt.date.today().isoformat()
    page_html = download_page(SOURCE_URL)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    (RAW_DIR / f"sff_recommendations_{today}.html").write_text(page_html)
    frame = rows_to_frame(parse_table(page_html))
    frame.to_csv(PROCESSED_DIR / "sff_grants.csv", index=False)
    print(f"Parsed {len(frame)} SFF recommendations")
    print(frame.groupby("award_year")[["amount_usd", "matching_pledge_usd"]].sum())


if __name__ == "__main__":
    main()
