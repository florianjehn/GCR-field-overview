import pandas as pd
import pytest

from src.classify_grants import (
    apply_purpose_overrides,
    classify_coefficient,
    classify_sff,
    funder_label_category,
)

CODES = {
    "category": "Classic GCR",
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
    assert coded.loc[1, "category"] == "Classic GCR"
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
    assert list(result["category"]) == ["EA & community", "Classic GCR"]


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
