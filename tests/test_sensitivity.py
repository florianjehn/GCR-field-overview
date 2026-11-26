import pandas as pd

from src.sensitivity import metrics, question, recode, without_matching_pledges

GRANTS = pd.DataFrame(
    {
        "award_year": [2025, 2025, 2024, 2025],
        "amount_usd": [80.0, 10.0, 10.0, 100.0],
        "category": [
            "AI",
            "Nuclear, natural & resilience",
            "General x-risk",
            "Regrant",
        ],
        "question_id": ["", "", "Q1", ""],
        "recipient": ["A", "B", "C", "D"],
    }
)


def test_metrics_excludes_regrants_and_computes_shares():
    """
    Tests that regrants are excluded and shares are computed on GCR money.
    """
    result = metrics(GRANTS)
    assert result["nnr_total_musd"] == 10 / 1e6
    assert round(result["nnr_share_pct"], 6) == 10.0
    assert round(result["ai_share_2025_pct"], 6) == round(100 * 80 / 90, 6)


def test_recode_changes_only_masked_rows():
    """
    Tests that recode changes the masked rows and leaves the original intact.
    """
    changed = recode(GRANTS, question(GRANTS, "Q1"), "Nuclear, natural & resilience")
    assert list(changed["category"])[2] == "Nuclear, natural & resilience"
    assert list(GRANTS["category"])[2] == "General x-risk"
    assert metrics(changed)["nnr_total_musd"] == 20 / 1e6


def test_without_matching_pledges_subtracts_pledge():
    """
    Tests that the pledge part is taken out of the amount.
    """
    grants = pd.DataFrame(
        {"amount_usd": [150.0, 10.0], "matching_pledge_usd": [50, None]}
    )
    assert without_matching_pledges(grants)["amount_usd"].tolist() == [100.0, 10.0]
