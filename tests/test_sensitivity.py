import pandas as pd

from src.sensitivity import metrics, question, recode

GRANTS = pd.DataFrame(
    {
        "award_year": [2025, 2025, 2024, 2025],
        "amount_usd": [80.0, 10.0, 10.0, 100.0],
        "category": ["AI", "Classic GCR", "General x-risk", "Regrant"],
        "question_id": ["", "", "Q1", ""],
        "recipient": ["A", "B", "C", "D"],
    }
)


def test_metrics_excludes_regrants_and_computes_shares():
    """
    Tests that regrants are excluded and shares are computed on GCR money.
    """
    result = metrics(GRANTS)
    assert result["classic_gcr_total_musd"] == 10 / 1e6
    assert round(result["classic_gcr_share_pct"], 6) == 10.0
    assert round(result["ai_share_2025_pct"], 6) == round(100 * 80 / 90, 6)


def test_recode_changes_only_masked_rows():
    """
    Tests that recode changes the masked rows and leaves the original intact.
    """
    changed = recode(GRANTS, question(GRANTS, "Q1"), "Classic GCR")
    assert list(changed["category"])[2] == "Classic GCR"
    assert list(GRANTS["category"])[2] == "General x-risk"
    assert metrics(changed)["classic_gcr_total_musd"] == 20 / 1e6
