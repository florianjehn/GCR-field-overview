"""
Export the processed data as compact JSON for the interactive site in docs/.

Writes docs/data/funding.json, staff.json, publications.json and meta.json.

Run with:
    uv run python3 -m src.build_site
"""

import datetime as dt
import hashlib
import json
import re
from pathlib import Path

import pandas as pd

PROCESSED_DIR = Path("data/processed")
MANUAL_DIR = Path("data/manual")
SITE_DATA_DIR = Path("docs/data")
FUNDER_SHORT = {
    "Coefficient Giving (Open Philanthropy)": "Coefficient Giving",
    "Survival and Flourishing Fund": "SFF",
    "Long-Term Future Fund": "LTFF",
    "Future of Life Institute": "FLI",
}


def records(frame, columns):
    """
    Converts selected columns of a DataFrame to a list of plain dicts.

    Arguments:
        frame (pandas.DataFrame): the table
        columns (list): columns to keep

    Returns:
        list: dicts with JSON-safe values.
    """
    subset = frame[columns].astype(object).where(frame[columns].notna(), None)
    return subset.to_dict(orient="records")


def funding_data():
    """
    Builds the funding rows (one per grant and category share).

    Returns:
        list: grant rows for the site.
    """
    grants = pd.read_csv(
        PROCESSED_DIR / "grants_by_category.csv", keep_default_na=False, na_values=[""]
    )
    grants = grants.dropna(subset=["award_year", "amount_usd_share"])
    grants["funder"] = grants["funder"].map(FUNDER_SHORT)
    grants["year"] = grants["award_year"].astype(int)
    grants["amount"] = grants["amount_usd_share"].round(0)
    grants["activity"] = grants["activity"].fillna("n/a")
    grants["recipient"] = grants["recipient"].fillna("(not named by funder)")
    columns = [
        "funder",
        "year",
        "category",
        "activity",
        "amount",
        "recipient",
        "description",
        "coding_source",
        "source_url",
    ]
    return records(grants, columns)


def documented_functions(headcounts, org_types):
    """
    Turns headcounts from filings into function rows for organizations
    without a usable team page (CLTR's Companies House filings and the
    FernUni Hagen programme).

    Arguments:
        headcounts (pandas.DataFrame): data/manual/org_staff.csv
        org_types (pandas.DataFrame): data/manual/org_types.csv

    Returns:
        pandas.DataFrame: org_id, year, focus, function, people, source.
    """
    rows = headcounts[headcounts["org_id"].isin(["cltr", "fernuni_erh"])].merge(
        org_types, on="org_id"
    )
    return pd.DataFrame(
        {
            "org_id": rows["org_id"],
            "year": rows["year"].astype(int),
            "focus": rows["focus"],
            "function": rows["type"],
            "people": rows["staff"].astype(int),
            "source": "filings",
        }
    )


def staff_data():
    """
    Builds staff counts without names: per organization, year and role, and
    per organization, year, focus and function.

    Returns:
        dict: role counts, function counts, filing headcounts and organizations.
    """
    roles = pd.read_csv(PROCESSED_DIR / "staff_by_year.csv")
    roles = roles.melt(["org_id", "year"], var_name="role", value_name="people")
    functions = pd.read_csv(PROCESSED_DIR / "staff_by_function.csv")
    headcounts = pd.read_csv(MANUAL_DIR / "org_staff.csv", keep_default_na=False)
    org_types = pd.read_csv(MANUAL_DIR / "org_types.csv", keep_default_na=False)
    functions = pd.concat([functions, documented_functions(headcounts, org_types)])
    organizations = pd.read_csv(
        MANUAL_DIR / "organizations.csv", keep_default_na=False
    ).drop(columns=["type"])
    organizations = organizations.merge(org_types, on="org_id", how="left")
    org_columns = ["org_id", "name", "type", "focus", "founded", "closed"]
    head_columns = ["org_id", "year", "staff", "measure", "source"]
    function_columns = ["org_id", "year", "focus", "function", "people", "source"]
    return {
        "roles": records(
            roles[roles["people"] > 0], ["org_id", "year", "role", "people"]
        ),
        "functions": records(functions, function_columns),
        "headcounts": records(headcounts, head_columns),
        "organizations": records(organizations.fillna(""), org_columns),
    }


def publications_data():
    """
    Builds the publication rows and yearly author counts.

    Returns:
        dict: works and per-year unique authors for both scopes.
    """
    works = pd.read_csv(
        PROCESSED_DIR / "publications.csv",
        keep_default_na=False,
        na_values={"year": [""]},
    )
    works = works.dropna(subset=["year"]).astype({"year": int})
    summary = pd.read_csv(PROCESSED_DIR / "publications_by_year.csv")
    return {
        "works": records(
            works,
            [
                "scope",
                "year",
                "title",
                "type",
                "source",
                "n_authors",
                "cited_by",
                "topics",
                "url",
            ],
        ),
        "by_year": records(summary, ["scope", "year", "works", "unique_authors"]),
    }


def write_json(name, payload):
    """
    Writes one JSON file into docs/data without extra whitespace.

    Arguments:
        name (str): file name
        payload (object): JSON-serializable data

    Returns:
        pathlib.Path: the file written.
    """
    SITE_DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = SITE_DATA_DIR / name
    path.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    return path


DOCS_DIR = Path("docs")
ASSET_LINK = re.compile(r'(assets/[\w.-]+\.(?:js|css))(?:\?v=\w+)?"')


def stamp_assets(page_html, asset_dir):
    """
    Adds a content hash to every asset link (assets/x.js?v=<hash>), so that
    browsers load a changed file instead of an old cached copy.

    Arguments:
        page_html (str): HTML of one page
        asset_dir (pathlib.Path): folder that holds the assets/ folder

    Returns:
        str: the HTML with versioned asset links.
    """

    def versioned(match):
        digest = hashlib.sha1((asset_dir / match.group(1)).read_bytes()).hexdigest()
        return f'{match.group(1)}?v={digest[:8]}"'

    return ASSET_LINK.sub(versioned, page_html)


def main():
    """
    Writes all site data files.

    Returns:
        None
    """
    for name, payload in [
        ("funding.json", funding_data()),
        ("staff.json", staff_data()),
        ("publications.json", publications_data()),
        ("meta.json", {"built": dt.date.today().isoformat()}),
    ]:
        path = write_json(name, payload)
        print(f"{path}: {path.stat().st_size / 1e3:.0f} kB")
    for page in DOCS_DIR.glob("*.html"):
        page.write_text(stamp_assets(page.read_text(), DOCS_DIR))


if __name__ == "__main__":
    main()
