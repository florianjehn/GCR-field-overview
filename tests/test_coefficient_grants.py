from src.coefficient_grants import (
    build_payload,
    hit_to_row,
    hits_to_frame,
    join_labels,
)

SAMPLE_HIT = {
    "post_id": 557,
    "title": "Nuclear Conflict Climate Modeling",
    "organization_name": ["Rutgers University"],
    "grant_amount": 3000000,
    "award_date": 1587686400,
    "award_year": 2020,
    "focus-area": ["Global Catastrophic Risks Opportunities"],
    "funding_type": ["Grants"],
    "url": "https://coefficientgiving.org/grants/rutgers/",
}


def test_build_payload_without_facets():
    """
    Tests that a payload without facets has no facet keys.
    """
    payload = build_payload([["post_type:Grants"]], 10)
    assert payload["hitsPerPage"] == 10
    assert payload["facetFilters"] == [["post_type:Grants"]]
    assert "facets" not in payload


def test_build_payload_with_facets():
    """
    Tests that requested facets are added to the payload.
    """
    payload = build_payload([], 0, facets=["award_year"])
    assert payload["facets"] == ["award_year"]


def test_join_labels_unescapes_html():
    """
    Tests that HTML entities are unescaped and labels joined with ' | '.
    """
    labels = ["Biosecurity &amp; Pandemic Preparedness", "Forecasting"]
    assert join_labels(labels) == "Biosecurity & Pandemic Preparedness | Forecasting"


def test_join_labels_handles_none():
    """
    Tests that a missing label list becomes an empty string.
    """
    assert join_labels(None) == ""


def test_hit_to_row_fields():
    """
    Tests that a raw hit is flattened with a UTC ISO award date.
    """
    row = hit_to_row(SAMPLE_HIT)
    assert row["recipient"] == "Rutgers University"
    assert row["amount_usd"] == 3000000
    assert row["award_date"] == "2020-04-24"
    assert row["source_url"] == SAMPLE_HIT["url"]


def test_hit_to_row_missing_date():
    """
    Tests that a hit without an award date gets None instead of failing.
    """
    hit = {key: value for key, value in SAMPLE_HIT.items() if key != "award_date"}
    assert hit_to_row(hit)["award_date"] is None


def test_hits_to_frame_sorted_by_date():
    """
    Tests that the frame is sorted by award date.
    """
    later = dict(SAMPLE_HIT, post_id=999, award_date=1700000000)
    frame = hits_to_frame([later, SAMPLE_HIT])
    assert list(frame["grant_id"]) == [557, 999]
