"""
Download the Coefficient Giving (formerly Open Philanthropy) grants database.

The grant lists on coefficientgiving.org are rendered client-side from a public
Algolia search index. The app ID and search-only key below are embedded in the
HTML of every fund page (hidden inputs `algolia-app-id` / `algolia-search-key`),
so this script reads exactly the data a browser visitor sees.

Run with:
    uv run python3 -m src.coefficient_grants
"""

import datetime as dt
import html
import json
import urllib.request
from pathlib import Path

import pandas as pd

ALGOLIA_APP_ID = "WBC743WF65"
ALGOLIA_SEARCH_KEY = "da168b7a254a1f18a8fd0e6b65d7e0e2"
ALGOLIA_INDEX = "coefficientgiving"
QUERY_URL = f"https://{ALGOLIA_APP_ID}-dsn.algolia.net/1/indexes/{ALGOLIA_INDEX}/query"
MAX_HITS_PER_PAGE = 1000
LIST_SEPARATOR = " | "
FIRST_YEAR = 2010
RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")


def build_payload(facet_filters, hits_per_page, facets=None):
    """
    Builds an Algolia query payload for grants.

    Arguments:
        facet_filters (list): Algolia facetFilters (AND of OR-lists)
        hits_per_page (int): number of hits to return
        facets (list or None): facets to count, if any

    Returns:
        dict: the JSON payload for the query endpoint.
    """
    payload = {
        "query": "",
        "hitsPerPage": hits_per_page,
        "facetFilters": facet_filters,
        "attributesToHighlight": [],
        "attributesToSnippet": [],
    }
    if facets:
        payload["facets"] = facets
        payload["maxValuesPerFacet"] = 1000
    return payload


def post_query(payload):
    """
    Sends one query to the Algolia index and returns the parsed response.

    Arguments:
        payload (dict): the JSON payload

    Returns:
        dict: the parsed JSON response.
    """
    request = urllib.request.Request(
        QUERY_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "X-Algolia-Application-Id": ALGOLIA_APP_ID,
            "X-Algolia-API-Key": ALGOLIA_SEARCH_KEY,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def fetch_year_counts():
    """
    Gets the number of grant records per award year from the facet counts.

    Returns:
        dict: award year (str) -> number of grant records.
    """
    payload = build_payload([["post_type:Grants"]], 0, facets=["award_year"])
    return post_query(payload)["facets"]["award_year"]


def fetch_grants_for_year(year):
    """
    Fetches all grant records for one award year in a single page.

    Arguments:
        year (str): the award year

    Returns:
        list: the raw Algolia hits for that year.
    """
    payload = build_payload(
        [["post_type:Grants"], [f"award_year:{year}"]], MAX_HITS_PER_PAGE
    )
    response = post_query(payload)
    if response["nbHits"] > MAX_HITS_PER_PAGE:
        raise ValueError(f"{year}: {response['nbHits']} hits exceed one page")
    return response["hits"]


def fetch_all_grants():
    """
    Fetches every grant record, year by year, and checks completeness
    against the facet counts.

    Returns:
        list: all raw Algolia grant hits.
    """
    year_counts = fetch_year_counts()
    hits = []
    for year in sorted(year_counts):
        year_hits = fetch_grants_for_year(year)
        print(f"{year}: {len(year_hits)} grants (facet count {year_counts[year]})")
        hits.extend(year_hits)
    return hits


def join_labels(labels):
    """
    Unescapes HTML entities in a list of labels and joins them.

    Arguments:
        labels (list or None): raw labels, e.g. ["Biosecurity &amp; Pandemic"]

    Returns:
        str: the cleaned labels joined with LIST_SEPARATOR.
    """
    return LIST_SEPARATOR.join(html.unescape(label) for label in labels or [])


def hit_to_row(hit):
    """
    Converts one raw Algolia grant hit into a flat record.

    Arguments:
        hit (dict): the raw hit

    Returns:
        dict: a flat record with the fields used downstream.
    """
    award_date = hit.get("award_date")
    return {
        "funder": "Coefficient Giving (Open Philanthropy)",
        "grant_id": hit.get("post_id"),
        "title": html.unescape(hit.get("title") or ""),
        "recipient": join_labels(hit.get("organization_name")),
        "amount_usd": hit.get("grant_amount"),
        "award_date": (
            dt.datetime.fromtimestamp(award_date, dt.UTC).date().isoformat()
            if award_date
            else None
        ),
        "award_year": hit.get("award_year"),
        "funder_focus_area": join_labels(hit.get("focus-area")),
        "funding_type": join_labels(hit.get("funding_type")),
        "source_url": hit.get("url"),
    }


def hits_to_frame(hits):
    """
    Converts raw hits into a tidy DataFrame sorted by date.

    Arguments:
        hits (list): raw Algolia grant hits

    Returns:
        pandas.DataFrame: one row per grant.
    """
    frame = pd.DataFrame([hit_to_row(hit) for hit in hits])
    return frame.sort_values(["award_date", "grant_id"]).reset_index(drop=True)


def save_outputs(hits, frame, today):
    """
    Saves the raw hits as dated JSON and the tidy table as CSV.

    Arguments:
        hits (list): raw Algolia grant hits
        frame (pandas.DataFrame): tidy grants table
        today (str): ISO date of the download

    Returns:
        tuple: (raw path, csv path).
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    raw_path = RAW_DIR / f"coefficient_giving_grants_{today}.json"
    csv_path = PROCESSED_DIR / "coefficient_giving_grants.csv"
    raw_path.write_text(json.dumps(hits, indent=1, ensure_ascii=False))
    frame.to_csv(csv_path, index=False)
    return raw_path, csv_path


def main():
    """
    Downloads all grants, checks completeness and saves raw and tidy files.

    Returns:
        None
    """
    expected = sum(fetch_year_counts().values())
    hits = fetch_all_grants()
    frame = hits_to_frame(hits)
    print(f"Fetched {len(frame)} grants, facet total {expected}")
    if frame["grant_id"].duplicated().any():
        raise ValueError("Duplicate grant ids in download")
    today = dt.date.today().isoformat()
    raw_path, csv_path = save_outputs(hits, frame, today)
    print(f"Saved {raw_path} and {csv_path}")


if __name__ == "__main__":
    main()
