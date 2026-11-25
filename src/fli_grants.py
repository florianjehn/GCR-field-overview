"""
Download and parse Future of Life Institute (FLI) grant programme pages.

Source: https://futureoflife.org/grant-program/<slug>/ for each programme in
data/manual/fli_programs.csv (award years, some inferred, are set there).
Each page lists recipients in accordion blocks with "Project title",
"Amount recommended" and optionally "Primary investigator".

Caveat: the yearly pages (2021-2025) state they only "highlight some of the
grants", so FLI totals are a lower bound. The fellowship programmes list no
amounts and are not included.

Run with:
    uv run python3 -m src.fli_grants
"""

import datetime as dt
import html
import re
import time
import urllib.request
from pathlib import Path

import pandas as pd

BASE_URL = "https://futureoflife.org/grant-program/{slug}/"
RAW_DIR = Path("data/raw/fli")
PROCESSED_DIR = Path("data/processed")
PROGRAMS_PATH = Path("data/manual/fli_programs.csv")
BLOCK_MARKER = 'data-id="div_block-70-45676"'
TITLE_PATTERN = re.compile(r'data-id="span-254-45669">(.*?)</span>', re.S)
AMOUNT_PATTERN = re.compile(r'data-id="code_block-48-45676">([^<]*)<')
PI_PATTERN = re.compile(r'data-id="text_block-340-45669">(.*?)</div>', re.S)
SUMMARY_PATTERN = re.compile(r"Details(.*)", re.S)


def to_text(fragment):
    """
    Strips tags, entities and extra whitespace from an HTML fragment.

    Arguments:
        fragment (str): HTML

    Returns:
        str: plain text.
    """
    text = html.unescape(re.sub(r"<[^>]+>", " ", fragment))
    return re.sub(r"\s+", " ", text).strip()


def parse_amount(amount_text):
    """
    Converts an amount like "$462,024.00" to a float.

    Arguments:
        amount_text (str): the amount text

    Returns:
        float or None: the amount in USD, None if empty.
    """
    digits = re.sub(r"[^\d.]", "", amount_text)
    return float(digits) if digits else None


def parse_block(block):
    """
    Extracts one grant from an accordion block.

    Arguments:
        block (str): HTML of one recipient block

    Returns:
        dict: title, amount_usd, investigator, summary.
    """
    block = re.sub(r"<[^>]*$", "", block)
    pi = PI_PATTERN.search(block)
    summary = SUMMARY_PATTERN.search(block)
    return {
        "title": to_text(TITLE_PATTERN.search(block).group(1)),
        "amount_usd": parse_amount(AMOUNT_PATTERN.search(block).group(1)),
        "investigator": to_text(pi.group(1)) if pi else "",
        "summary": to_text(summary.group(1))[:500] if summary else "",
    }


def parse_page(page_html):
    """
    Extracts all grants on a programme page.

    Arguments:
        page_html (str): the page HTML

    Returns:
        list: one dict per grant.
    """
    return [parse_block(block) for block in page_html.split(BLOCK_MARKER)[1:]]


def recipient_name(grant):
    """
    Picks the recipient: the institution after the investigator's name for
    research calls, otherwise the project title (organisation name).

    Arguments:
        grant (dict): a parsed grant

    Returns:
        str: the recipient name.
    """
    if grant["investigator"] and "," in grant["investigator"]:
        return grant["investigator"].split(",", 1)[1].strip()
    return grant["title"]


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


def programme_rows(program, page_html):
    """
    Builds grant rows for one programme.

    Arguments:
        program (pandas.Series): row from fli_programs.csv
        page_html (str): the programme page HTML

    Returns:
        list: grant records.
    """
    url = BASE_URL.format(slug=program["slug"])
    rows = []
    for index, grant in enumerate(parse_page(page_html)):
        rows.append(
            {
                "funder": "Future of Life Institute",
                "grant_id": f"fli-{program['slug']}-{index:02d}",
                "program": program["program"],
                "award_year": int(program["award_year"]),
                "year_source": program["year_source"],
                "recipient": recipient_name(grant),
                **grant,
                "source_url": url,
            }
        )
    return rows


def main():
    """
    Downloads all programme pages, saves raw HTML and the tidy CSV.

    Returns:
        None
    """
    programs = pd.read_csv(PROGRAMS_PATH)
    raw_dir = RAW_DIR / dt.date.today().isoformat()
    raw_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for _, program in programs.iterrows():
        page_html = download_page(BASE_URL.format(slug=program["slug"]))
        (raw_dir / f"{program['slug']}.html").write_text(page_html)
        rows.extend(programme_rows(program, page_html))
        time.sleep(1)
    frame = pd.DataFrame(rows)
    frame.to_csv(PROCESSED_DIR / "fli_grants.csv", index=False)
    print(f"Parsed {len(frame)} FLI grants")
    print(frame.groupby("award_year")["amount_usd"].agg(["size", "sum"]))


if __name__ == "__main__":
    main()
