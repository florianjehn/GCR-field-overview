import pandas as pd
import pytest

from src.classify_grants import (
    add_matching_pledges,
    apply_purpose_overrides,
    apply_url_overrides,
    classify_coefficient,
    classify_sff,
    explode_categories,
    funder_label_category,
    parse_category_shares,
)

CODES = {
    "category": "Nuclear, natural & resilience",
    "coding_source": "LLM-coded",
    "confidence": "high",
    "question_id": "",
    "rationale": "test",
}


def test_funder_label_ai_wins_over_others():
    """
    Tests that an AI fund label maps to AI even with other labels present.
    """
    labels = "Global Catastrophic Risks Opportunities | Navigating Transformative AI"
    assert funder_label_category(labels) == "AI"


def test_funder_label_bio_subfund():
    """
    Tests that the biosecurity science sub-fund maps to Bio.
    """
    labels = "Science and Global Health R&D | Science Supporting Biosecurity and "
    labels += "Pandemic Preparedness"
    assert funder_label_category(labels) == "Bio"


def test_funder_label_other_is_not_gcr():
    """
    Tests that unrelated funds map to Not GCR.
    """
    assert funder_label_category("Farm Animal Welfare") == "Not GCR"


def test_classify_coefficient_manual_overrides_label():
    """
    Tests that a manual code replaces the fund-label default.
    """
    grants = pd.DataFrame(
        {
            "grant_id": [1, 2],
            "title": ["Nuclear winter", "Alignment"],
            "funder_focus_area": [
                "Global Catastrophic Risks Opportunities",
                "Navigating Transformative AI",
            ],
        }
    )
    manual = pd.DataFrame([dict(grant_id=1, **CODES)])
    coded = classify_coefficient(grants, manual).set_index("grant_id")
    assert coded.loc[1, "category"] == "Nuclear, natural & resilience"
    assert coded.loc[1, "coding_source"] == "LLM-coded"
    assert coded.loc[2, "category"] == "AI"
    assert coded.loc[2, "coding_source"] == "funder-label"


def test_apply_purpose_overrides_matches_phrase_only():
    """
    Tests that only rows containing the phrase are overridden.
    """
    coded = pd.DataFrame(
        {
            "organization": ["Lightcone", "Lightcone"],
            "purpose": ["General support", "General support of flexHEG prototyping"],
            "category": ["EA & community", "EA & community"],
            "coding_source": ["LLM-coded"] * 2,
            "confidence": ["low"] * 2,
            "question_id": ["Q8"] * 2,
            "rationale": ["x"] * 2,
        }
    )
    overrides = pd.DataFrame(
        [dict(organization="Lightcone", purpose_contains="flexheg", **CODES)]
    )
    result = apply_purpose_overrides(coded, overrides)
    assert list(result["category"]) == [
        "EA & community",
        "Nuclear, natural & resilience",
    ]


def test_classify_sff_raises_for_uncoded_organization():
    """
    Tests that an SFF organization without a manual code is an error.
    """
    grants = pd.DataFrame(
        {"organization": ["New Org"], "round": ["SFF-2026"], "purpose": ["x"]}
    )
    manual = pd.DataFrame([dict(organization="Other Org", **CODES)])
    overrides = pd.DataFrame(columns=["organization", "purpose_contains"] + list(CODES))
    with pytest.raises(ValueError):
        classify_sff(grants, manual, overrides)


def test_parse_category_shares_single():
    """
    Tests that a plain category gets the full share.
    """
    assert parse_category_shares("AI") == [("AI", 1.0)]


def test_parse_category_shares_split():
    """
    Tests that a split category is parsed into shares.
    """
    assert parse_category_shares("AI=0.5;Bio=0.5") == [("AI", 0.5), ("Bio", 0.5)]


def test_parse_category_shares_rejects_bad_sum():
    """
    Tests that shares not summing to 1 raise an error.
    """
    with pytest.raises(ValueError):
        parse_category_shares("AI=0.5;Bio=0.4")


def test_explode_categories_conserves_amount():
    """
    Tests that splitting keeps the total amount unchanged.
    """
    grants = pd.DataFrame(
        {
            "grant_id": [1, 2],
            "amount_usd": [100.0, 50.0],
            "category": ["AI", "AI=0.5;Bio=0.5"],
        }
    )
    long = explode_categories(grants)
    assert len(long) == 3
    assert long["amount_usd_share"].sum() == 150.0
    assert long.loc[long["category"] == "Bio", "amount_usd_share"].item() == 25.0


def test_url_override_replaces_only_matching_grant():
    """
    Tests that a URL override hits the same funder and grant id only.
    """
    grants = pd.DataFrame(
        {
            "funder": ["A", "A", "B"],
            "grant_id": [1, 2, "1"],
            "source_url": ["old1", "old2", "oldB"],
        }
    )
    overrides = pd.DataFrame({"funder": ["A"], "grant_id": [1], "source_url": ["new"]})
    fixed = apply_url_overrides(grants, overrides)
    assert fixed["source_url"].tolist() == ["new", "old2", "oldB"]


def test_matching_pledges_are_counted_in_amount():
    """
    Tests that the pledge is added to the amount and still shown separately.
    """
    grants = pd.DataFrame({"amount_usd": [100.0, 0.0], "matching_pledge_usd": [50, 0]})
    result = add_matching_pledges(grants)
    assert result["amount_usd"].tolist() == [150.0, 0.0]
    assert result["matching_pledge_usd"].tolist() == [50, 0]
