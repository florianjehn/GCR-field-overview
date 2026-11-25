"""
Publications mentioning "global catastrophic risk", from OpenAlex.

Two scopes, reported side by side (author decision):
- title_abstract: the phrase in title or abstract
  (filter title_and_abstract.search:"global catastrophic risk")
- fulltext: OpenAlex default search over title, abstract and full text
  (search="global catastrophic risk"), which also catches passing mentions

OpenAlex stems search terms, so "risks" matches too. Each work gets keyword
topic tags (data/manual/publication_topics.csv) from its title and abstract.

Run with:
    uv run python3 -m src.publications
"""

import datetime as dt
import gzip
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd

API_URL = "https://api.openalex.org/works"
PHRASE = '"global catastrophic risk"'
SCOPES = {
    "title_abstract": {"filter": f"title_and_abstract.search:{PHRASE}"},
    "fulltext": {"search": PHRASE},
}
FIELDS = (
    "id,doi,display_name,publication_year,type,authorships,cited_by_count,"
    "abstract_inverted_index,primary_location"
)
RAW_DIR = Path("data/raw/openalex")
PROCESSED_DIR = Path("data/processed")
MANUAL_DIR = Path("data/manual")


def fetch_page(params, page):
    """
    Fetches one page of OpenAlex results. Uses page numbers, which work
    without an API key up to 10,000 results (cursor paging needs a key).

    Arguments:
        params (dict): query parameters (filter or search)
        page (int): page number, starting at 1

    Returns:
        dict: the parsed JSON response.
    """
    query = urllib.parse.urlencode(
        {**params, "per_page": 200, "page": page, "select": FIELDS},
        safe=':",',
    )
    request = urllib.request.Request(
        f"{API_URL}?{query}", headers={"User-Agent": "gcr-field-overview"}
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.load(response)


def fetch_all(params):
    """
    Fetches all works for a query page by page.

    Arguments:
        params (dict): query parameters

    Returns:
        list: all work records.
    """
    works, page = [], 1
    while True:
        response = fetch_page(params, page)
        works.extend(response["results"])
        if not response["results"] or len(works) >= response["meta"]["count"]:
            return works
        page += 1
        time.sleep(0.5)


def abstract_text(inverted_index):
    """
    Rebuilds an abstract from OpenAlex's inverted index.

    Arguments:
        inverted_index (dict or None): word -> list of positions

    Returns:
        str: the abstract text ("" if missing).
    """
    if not inverted_index:
        return ""
    positions = [(pos, word) for word, poss in inverted_index.items() for pos in poss]
    return " ".join(word for _, word in sorted(positions))


def topic_tags(text, topics):
    """
    Lists the topics whose pattern occurs in a text.

    Arguments:
        text (str): title and abstract
        topics (pandas.DataFrame): columns topic, pattern

    Returns:
        str: matching topics joined with ";" ("" if none).
    """
    found = [
        row.topic
        for row in topics.itertuples(index=False)
        if re.search(row.pattern, text, flags=re.I)
    ]
    return ";".join(found)


def work_row(work, scope, topics):
    """
    Flattens one OpenAlex work.

    Arguments:
        work (dict): OpenAlex work record
        scope (str): search scope name
        topics (pandas.DataFrame): topic patterns

    Returns:
        dict: the flat record.
    """
    title = work.get("display_name") or ""
    text = f"{title} {abstract_text(work.get('abstract_inverted_index'))}"
    source = ((work.get("primary_location") or {}).get("source") or {}).get(
        "display_name"
    )
    return {
        "scope": scope,
        "work_id": work["id"],
        "year": work.get("publication_year"),
        "type": work.get("type"),
        "title": title,
        "source": source,
        "n_authors": len(work.get("authorships") or []),
        "cited_by": work.get("cited_by_count"),
        "has_abstract": bool(work.get("abstract_inverted_index")),
        "topics": topic_tags(text, topics),
        "doi": work.get("doi"),
        "url": work["id"].replace(
            "https://openalex.org/", "https://openalex.org/works/"
        ),
    }


def author_rows(work, scope):
    """
    Lists the authors of one work.

    Arguments:
        work (dict): OpenAlex work record
        scope (str): search scope name

    Returns:
        list: one dict per authorship.
    """
    rows = []
    for authorship in work.get("authorships") or []:
        author = authorship.get("author") or {}
        institutions = authorship.get("institutions") or []
        rows.append(
            {
                "scope": scope,
                "work_id": work["id"],
                "year": work.get("publication_year"),
                "author_id": author.get("id"),
                "author_name": author.get("display_name"),
                "institution": "; ".join(
                    i.get("display_name", "") for i in institutions
                ),
            }
        )
    return rows


def save_raw(works, scope, today):
    """
    Saves raw OpenAlex records as gzipped JSON.

    Arguments:
        works (list): work records
        scope (str): search scope name
        today (str): ISO date

    Returns:
        pathlib.Path: the file written.
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / f"{scope}_{today}.json.gz"
    with gzip.open(path, "wt") as handle:
        json.dump(works, handle)
    return path


def yearly_summary(works, authors, topics):
    """
    Counts works, unique authors and topic mentions per scope and year.

    Arguments:
        works (pandas.DataFrame): output of work_row for all works
        authors (pandas.DataFrame): output of author_rows for all works
        topics (pandas.DataFrame): topic patterns (column topic)

    Returns:
        pandas.DataFrame: one row per scope and year.
    """
    works = works.dropna(subset=["year"]).assign(topics=works["topics"].fillna(""))
    works = works.astype({"year": int})
    authors = authors.dropna(subset=["year"]).astype({"year": int})
    keys = ["scope", "year"]
    summary = works.groupby(keys).size().rename("works").to_frame()
    summary["unique_authors"] = authors.groupby(keys)["author_id"].nunique()
    for topic in topics["topic"]:
        mentions = works[works["topics"].str.split(";").apply(lambda t: topic in t)]
        summary[f"mentions_{topic}"] = mentions.groupby(keys).size()
    summary["no_topic_tag"] = works[works["topics"] == ""].groupby(keys).size()
    return summary.fillna(0).astype(int).reset_index()


def main():
    """
    Downloads both scopes and writes works and authors tables.

    Returns:
        None
    """
    topics = pd.read_csv(MANUAL_DIR / "publication_topics.csv")
    today = dt.date.today().isoformat()
    works, authors = [], []
    for scope, params in SCOPES.items():
        records = fetch_all(params)
        save_raw(records, scope, today)
        works.extend(work_row(w, scope, topics) for w in records)
        for w in records:
            authors.extend(author_rows(w, scope))
        print(f"{scope}: {len(records)} works")
    works, authors = pd.DataFrame(works), pd.DataFrame(authors)
    works.to_csv(PROCESSED_DIR / "publications.csv", index=False)
    authors.to_csv(PROCESSED_DIR / "publication_authors.csv", index=False)
    summary = yearly_summary(works, authors, topics)
    summary.to_csv(PROCESSED_DIR / "publications_by_year.csv", index=False)


if __name__ == "__main__":
    main()
