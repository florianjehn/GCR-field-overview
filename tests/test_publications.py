import pandas as pd

from src.publications import abstract_text, author_rows, topic_tags, yearly_summary

TOPICS = pd.DataFrame(
    {"topic": ["AI", "nuclear"], "pattern": [r"\bAI\b|artificial", r"nuclear"]}
)


def test_abstract_text_rebuilds_order():
    """
    Tests that the inverted index is turned back into text in order.
    """
    assert (
        abstract_text({"world": [1], "hello": [0], "again": [2]}) == "hello world again"
    )
    assert abstract_text(None) == ""


def test_topic_tags_multiple_and_none():
    """
    Tests that several topics can match and none gives an empty string.
    """
    assert topic_tags("AI and nuclear war", TOPICS) == "AI;nuclear"
    assert topic_tags("volcanoes", TOPICS) == ""


def test_author_rows_handles_missing_institutions():
    """
    Tests that authorships without institutions still produce rows.
    """
    work = {
        "id": "W1",
        "publication_year": 2020,
        "authorships": [{"author": {"id": "A1", "display_name": "X"}}],
    }
    rows = author_rows(work, "s")
    assert rows[0]["author_id"] == "A1" and rows[0]["institution"] == ""


def test_yearly_summary_counts():
    """
    Tests works, unique authors and topic mention counts per year.
    """
    works = pd.DataFrame(
        {
            "scope": ["s", "s", "s"],
            "year": [2020, 2020, 2021],
            "work_id": ["W1", "W2", "W3"],
            "topics": ["AI", "AI;nuclear", ""],
        }
    )
    authors = pd.DataFrame(
        {"scope": ["s"] * 3, "year": [2020, 2020, 2021], "author_id": ["A", "A", "B"]}
    )
    out = yearly_summary(works, authors, TOPICS).set_index("year")
    assert out.loc[2020, "works"] == 2 and out.loc[2020, "unique_authors"] == 1
    assert out.loc[2020, "mentions_AI"] == 2 and out.loc[2020, "mentions_nuclear"] == 1
    assert out.loc[2021, "no_topic_tag"] == 1
