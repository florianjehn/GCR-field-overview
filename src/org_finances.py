"""
Yearly revenue and expenses of US-registered GCR organizations from IRS
Form 990 data, via the ProPublica Nonprofit Explorer API.

Organizations and EINs are listed in EINS below (only core organizations
that file their own 990; fiscally sponsored projects such as GCRI and Global
Shield have no separate filings). Each row links to the filing on ProPublica.

Run with:
    uv run python3 -m src.org_finances
"""

import datetime as dt
import json
import urllib.request
from pathlib import Path

import pandas as pd

API_URL = "https://projects.propublica.org/nonprofits/api/v2/organizations/{ein}.json"
ORG_URL = "https://projects.propublica.org/nonprofits/organizations/{ein}"
EINS = {"fli": 471052538, "beri": 814820272, "allfed": 831717756}
RAW_DIR = Path("data/raw/propublica")
PROCESSED_DIR = Path("data/processed")


def fetch_organization(ein):
    """
    Downloads the ProPublica record for one EIN.

    Arguments:
        ein (int): the employer identification number

    Returns:
        dict: the parsed JSON response.
    """
    request = urllib.request.Request(
        API_URL.format(ein=ein), headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def filings_to_rows(org_id, ein, record):
    """
    Extracts one row per filing year with revenue and expenses.

    Arguments:
        org_id (str): short organization id
        ein (int): the EIN
        record (dict): ProPublica organization record

    Returns:
        list: dicts with year, revenue and expenses in USD.
    """
    return [
        {
            "org_id": org_id,
            "ein": ein,
            "fiscal_year": filing["tax_prd_yr"],
            "revenue_usd": filing.get("totrevenue"),
            "expenses_usd": filing.get("totfuncexpns"),
            "source": "IRS Form 990 via ProPublica",
            "source_url": ORG_URL.format(ein=ein),
        }
        for filing in record.get("filings_with_data", [])
    ]


def filings_without_data(record):
    """
    Lists fiscal years that were filed but have no extracted figures.

    Arguments:
        record (dict): ProPublica organization record

    Returns:
        list: fiscal years (int) of filings without data.
    """
    return sorted(
        filing.get("tax_prd_yr")
        for filing in record.get("filings_without_data", []) or []
        if filing.get("tax_prd_yr")
    )


def main():
    """
    Downloads all organizations, saves raw JSON and a tidy finances table.

    Returns:
        None
    """
    raw_dir = RAW_DIR / dt.date.today().isoformat()
    raw_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for org_id, ein in EINS.items():
        record = fetch_organization(ein)
        (raw_dir / f"{ein}.json").write_text(json.dumps(record, indent=1))
        rows.extend(filings_to_rows(org_id, ein, record))
        print(f"{org_id}: years without extracted data {filings_without_data(record)}")
    frame = pd.DataFrame(rows).sort_values(["org_id", "fiscal_year"])
    frame.to_csv(PROCESSED_DIR / "org_finances_990.csv", index=False)
    print(frame.to_string(index=False))


if __name__ == "__main__":
    main()
