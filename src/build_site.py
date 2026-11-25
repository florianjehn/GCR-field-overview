"""
Export the processed data as compact JSON for the interactive site in docs/.

Writes docs/data/funding.json, staff.json, publications.json and meta.json.

Run with:
    uv run python3 -m src.build_site
"""

import datetime as dt
import json
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
    grants["split"] = grants["share"] < 1
    columns = [
        "funder",
        "year",
        "category",
        "activity",
        "amount",
        "recipient",
        "description",
        "coding_source",
        "split",
        "source_url",
    ]
    return records(grants, columns)


def staff_data():
    """
    Builds the person rows from the team pages plus documented headcounts.

    Returns:
        dict: people (one per person, organization and year), headcounts
        from filings and reports, and organization metadata.
    """
    people = pd.read_csv(PROCESSED_DIR / "team_people.csv", keep_default_na=False)
    headcounts = pd.read_csv(MANUAL_DIR / "org_staff.csv", keep_default_na=False)
    organizations = pd.read_csv(MANUAL_DIR / "organizations.csv", keep_default_na=False)
    return {
        "people": records(
            people, ["org_id", "year", "name", "section", "title", "role", "snapshot"]
        ),
        "headcounts": records(
            headcounts, ["org_id", "year", "staff", "measure", "source"]
        ),
        "organizations": records(
            organizations,
            [
                "org_id",
                "name",
                "group",
                "type",
                "country",
                "founded",
                "closed",
                "status_2026",
                "focus_now",
            ],
        ),
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


if __name__ == "__main__":
    main()
