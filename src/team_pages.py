"""
Extract people listed on archived team pages, year by year.

data/manual/team_pages.csv configures, per organization and period:
- url, from_year, to_year: the team page and the years to sample
- mode: "link" (people are links to profile pages; person_pattern is a regex
  on the href whose group 1 is the slug) or "element" (person_pattern is a
  regex on the HTML whose group 1 contains the name)
- section_pattern: regex whose group 1 is a section label (default: h1-h4)

People are assigned to the nearest section label above them. Section labels
are mapped to roles (staff, affiliate, ...) in data/manual/team_sections.csv
so counts can be audited and changed.

Run with:
    uv run python3 -m src.team_pages
"""

import html
import re
from pathlib import Path

import pandas as pd

from src.wayback import VIEW_URL, fetch_snapshot, yearly_snapshots

MANUAL_DIR = Path("data/manual")
PROCESSED_DIR = Path("data/processed")
GENERIC_LINK = re.compile(
    r"^(show|read|learn|see|view)\b.*|^(more|bio|profile)\b.*", re.I
)
HREF = r"""href=(?:"([^"]*)"|'([^']*)'|([^\s>]+))"""
LINK_PATTERN = re.compile(r"<a\b[^>]*" + HREF + r"[^>]*>(.*?)</a>", re.S | re.I)
HEADING_PATTERN = r"<h[1-4]\b[^>]*>(.*?)</h[1-4]>"
NAME_NOISE = re.compile(
    r"\(.*?\)|,?\s*\b(Ph\.?\s?D|MD|MPH|MSc|M\.?Phil|DPhil|J\.?D)\b\.?|^(Dr|Prof|Professor)\.?\s+",
    re.I,
)


def clean_text(fragment):
    """
    Strips tags, entities and extra whitespace.

    Arguments:
        fragment (str): HTML fragment

    Returns:
        str: plain text.
    """
    text = html.unescape(re.sub(r"<[^>]+>", " ", fragment))
    return re.sub(r"\s+", " ", text).strip()


def clean_name(text):
    """
    Removes degrees, titles and bracketed notes from a displayed name.

    Arguments:
        text (str): displayed name, e.g. "Seth Baum, Ph.D."

    Returns:
        str: the bare name, e.g. "Seth Baum".
    """
    return re.sub(r"\s+", " ", NAME_NOISE.sub("", text)).strip(" ,;-")


def slugify(name):
    """
    Turns a name into a lowercase slug.

    Arguments:
        name (str): a person's name

    Returns:
        str: slug like "seth-baum".
    """
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def slug_to_name(slug):
    """
    Turns a profile slug like "anders-sandberg-2" into "Anders Sandberg".

    Arguments:
        slug (str): the profile slug

    Returns:
        str: a readable name.
    """
    words = [w for w in re.split(r"[-_]+", slug) if w and not w.isdigit()]
    return " ".join(word.capitalize() for word in words)


def main_content(page_html):
    """
    Drops scripts, styles and navigation (headers are kept: some sites put
    section titles in <header> elements).

    Arguments:
        page_html (str): full page HTML

    Returns:
        str: HTML of the main content.
    """
    return re.sub(r"<(script|style|nav)\b.*?</\1>", "", page_html, flags=re.S | re.I)


def link_people(page, person_regex):
    """
    Finds profile links as (position, slug, name, raw text, title) tuples.

    Arguments:
        page (str): page HTML
        person_regex (re.Pattern): regex on href; group 1 is the slug

    Returns:
        list: person tuples in page order.
    """
    people = []
    for match in LINK_PATTERN.finditer(page):
        href = next(h for h in match.groups()[:3] if h is not None)
        found = person_regex.search(href)
        if not found:
            continue
        slug, inner = found.group(1).lower(), match.group(4)
        heading = re.search(r"<h[1-6][^>]*>(.*?)</h[1-6]>", inner, re.S)
        raw = clean_text(heading.group(1) if heading else inner)
        title = clean_text(inner.replace(heading.group(0), "")) if heading else ""
        name = slug_to_name(slug) if not raw or GENERIC_LINK.match(raw) else raw
        people.append((match.start(), slug, clean_name(name), raw, title))
    return people


def looks_like_name(text):
    """
    Checks loosely whether a text could be a person's name.

    Arguments:
        text (str): candidate text

    Returns:
        bool: True for 2-5 words without digits.
    """
    words = text.split()
    return 2 <= len(words) <= 5 and not re.search(r"\d", text)


def element_people(page, person_regex):
    """
    Finds names inside matching elements as (position, slug, name, raw, title)
    tuples. If the regex has a second group, it is taken as the job title.

    Arguments:
        page (str): page HTML
        person_regex (re.Pattern): regex whose group 1 holds the name

    Returns:
        list: person tuples in page order.
    """
    people = []
    for match in person_regex.finditer(page):
        raw = clean_text(match.group(1))
        title = clean_text(match.group(2)) if person_regex.groups > 1 else ""
        name = clean_name(raw)
        if name:
            people.append((match.start(), slugify(name), name, raw, title))
    return people


def sections(page, section_regex, person_regex, mode):
    """
    Finds section labels as (start, end, text) tuples, skipping labels that
    are themselves a person (a heading that contains a profile link).

    Arguments:
        page (str): page HTML
        section_regex (re.Pattern): regex whose group 1 is the label
        person_regex (re.Pattern): the person regex
        mode (str): "link" or "element"

    Returns:
        list: section tuples in page order.
    """
    found = []
    for match in section_regex.finditer(page):
        inner = match.group(1)
        if mode == "link" and link_people(inner, person_regex):
            continue
        text = clean_text(inner)
        if text:
            found.append((match.start(), match.end(), text))
    return found


def extract_people(
    page_html, person_pattern, mode="link", section_pattern=None, name_filter=False
):
    """
    Lists the people on a team page with the section they appear under.

    Arguments:
        page_html (str): page HTML
        person_pattern (str): regex, see module docstring
        mode (str): "link" or "element"
        section_pattern (str or None): regex for section labels
        name_filter (bool): keep only texts that look like names

    Returns:
        list: dicts with section, slug, name, raw text and title (first per slug).
    """
    page = main_content(page_html)
    person_regex = re.compile(person_pattern, re.S | re.I)
    section_regex = re.compile(section_pattern or HEADING_PATTERN, re.S | re.I)
    finder = link_people if mode == "link" else element_people
    labels = sections(page, section_regex, person_regex, mode)
    people, seen = [], set()
    for position, slug, name, raw, title in finder(page, person_regex):
        inside_label = any(start <= position < end for start, end, _ in labels)
        if slug in seen or not name or inside_label:
            continue
        if name_filter and not looks_like_name(name):
            continue
        seen.add(slug)
        above = [text for start, _, text in labels if start < position]
        people.append(
            {
                "section": above[-1] if above else "",
                "slug": slug,
                "name": name,
                "raw": raw,
                "title": title,
            }
        )
    return people


def people_for_year(org, year, capture):
    """
    Fetches one snapshot and extracts its people.

    Arguments:
        org (pandas.Series): row of team_pages.csv
        year (int): calendar year
        capture (tuple): (timestamp, original url)

    Returns:
        list: person records with org, year and snapshot link.
    """
    timestamp, url = capture
    page = fetch_snapshot(org["org_id"], timestamp, url)
    snapshot = VIEW_URL.format(timestamp=timestamp, url=url)
    people = extract_people(
        page,
        org["person_pattern"],
        org["mode"],
        org["section_pattern"] or None,
        org.get("name_filter", "") == "yes",
    )
    return [
        {"org_id": org["org_id"], "year": year, "snapshot": snapshot, **person}
        for person in people
    ]


def collect(pages):
    """
    Extracts people for every configured organization, URL and year.

    Arguments:
        pages (pandas.DataFrame): rows of team_pages.csv

    Returns:
        pandas.DataFrame: one row per person, organization and year.
    """
    rows = []
    for _, org in pages.iterrows():
        years = range(int(org["from_year"]), int(org["to_year"]) + 1)
        for year, capture in yearly_snapshots(org["url"], years).items():
            found = people_for_year(org, year, capture)
            rows.extend(found)
            print(f"{org['org_id']} {year}: {len(found)} people", flush=True)
    return pd.DataFrame(rows)


def main():
    """
    Collects people from all configured team pages and saves them.

    Returns:
        None
    """
    pages = pd.read_csv(MANUAL_DIR / "team_pages.csv", keep_default_na=False)
    people = collect(pages)
    people.to_csv(PROCESSED_DIR / "team_people_raw.csv", index=False)
    print(people.groupby(["org_id", "year"]).size().unstack(0).fillna(0).astype(int))


if __name__ == "__main__":
    main()
