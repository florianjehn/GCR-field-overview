"""
Sensitivity of headline funding numbers to individual classification choices.

Each scenario changes the category of one group of grants (identified by its
question id from data/manual/decisions.md, or by recipient/category) to the
main alternative, then recomputes the headline metrics. Results go to
results/sensitivity.csv.

Run with:
    uv run python3 -m src.sensitivity
"""

from pathlib import Path

import pandas as pd

from src.classify_grants import explode_categories

PROCESSED_DIR = Path("data/processed")
RESULTS_DIR = Path("results")
EXCLUDED = ("Regrant", "Duplicate", "EA & community", "Not GCR")
NON_AI_NON_BIO = ("Classic GCR", "General x-risk", "Geoengineering", "Climate")
FIRST_YEAR, LAST_YEAR = 2015, 2025


def gcr_rows(grants):
    """
    Explodes split categories and keeps GCR-relevant rows in the year range.

    Arguments:
        grants (pandas.DataFrame): classified grants (one row per grant)

    Returns:
        pandas.DataFrame: one row per grant and category share.
    """
    long = explode_categories(grants)
    in_years = long["award_year"].between(FIRST_YEAR, LAST_YEAR)
    return long[in_years & ~long["category"].isin(EXCLUDED)]


def metrics(grants):
    """
    Computes the headline metrics for a classification.

    Arguments:
        grants (pandas.DataFrame): classified grants

    Returns:
        dict: metric name -> value (USD millions or percent).
    """
    long = gcr_rows(grants)
    by_category = long.groupby("category")["amount_usd_share"].sum()
    total = by_category.sum()
    classic = by_category.get("Classic GCR", 0.0)
    recent = long[long["award_year"].between(2023, 2025)]
    non_ai_bio = recent[recent["category"].isin(NON_AI_NON_BIO)]
    latest = long[long["award_year"] == LAST_YEAR]
    ai_latest = latest.loc[latest["category"] == "AI", "amount_usd_share"].sum()
    return {
        "classic_gcr_total_musd": classic / 1e6,
        "classic_gcr_share_pct": 100 * classic / total,
        "non_ai_non_bio_per_year_2023_2025_musd": non_ai_bio["amount_usd_share"].sum()
        / 3
        / 1e6,
        "ai_share_2025_pct": 100 * ai_latest / latest["amount_usd_share"].sum(),
    }


def recode(grants, mask, category):
    """
    Returns a copy of the grants with the masked rows set to a new category.

    Arguments:
        grants (pandas.DataFrame): classified grants
        mask (pandas.Series): boolean rows to change
        category (str): new category (may be a split like "AI=0.5;Bio=0.5")

    Returns:
        pandas.DataFrame: the modified copy.
    """
    changed = grants.copy()
    changed.loc[mask, "category"] = category
    return changed


def question(grants, question_id, category=None):
    """
    Selects grants answered under a question id, optionally by category.

    Arguments:
        grants (pandas.DataFrame): classified grants
        question_id (str): e.g. "Q3"
        category (str or None): restrict to this current category

    Returns:
        pandas.Series: boolean mask.
    """
    mask = grants["question_id"].fillna("") == question_id
    if category is not None:
        mask &= grants["category"] == category
    return mask


def recipient(grants, pattern):
    """
    Selects grants whose recipient matches a regex.

    Arguments:
        grants (pandas.DataFrame): classified grants
        pattern (str): regex on recipient names

    Returns:
        pandas.Series: boolean mask.
    """
    return grants["recipient"].fillna("").str.contains(pattern, regex=True)


def scenarios(grants):
    """
    Defines the alternative classifications to test.

    Arguments:
        grants (pandas.DataFrame): classified grants

    Returns:
        list: (name, description, mask, new category) tuples.
    """
    g = grants
    split = g["category"].str.contains("AI=0.5;Bio=0.5", regex=False)
    return [
        (
            "Q1 multi-hazard -> Classic GCR",
            "CSER, FHI, BERI, GCRI, Global Shield etc. counted as classic GCR",
            (question(g, "Q1") | question(g, "Q1b"))
            & (g["category"] == "General x-risk"),
            "Classic GCR",
        ),
        ("Q2 FLI -> 100% AI", "FLI general support fully AI", question(g, "Q2"), "AI"),
        (
            "Q3 student x-risk -> EA & community",
            "Student/early-career x-risk programmes excluded",
            question(g, "Q3"),
            "EA & community",
        ),
        (
            "Q4 geoengineering+climate -> Classic GCR",
            "Climate and geoengineering counted as classic GCR",
            g["category"].isin(["Geoengineering", "Climate"]),
            "Classic GCR",
        ),
        (
            "Q5 global priorities -> General x-risk",
            "GPI etc. counted as GCR research",
            question(g, "Q5"),
            "General x-risk",
        ),
        (
            "Q6 regrants counted (as AI)",
            "Regrants to LTFF etc. counted at first funder (double counting)",
            g["category"] == "Regrant",
            "AI",
        ),
        (
            "Q7 forecasting -> Not GCR",
            "Generic forecasting excluded",
            g["category"] == "Forecasting",
            "Not GCR",
        ),
        (
            "Q8 Lightcone -> AI",
            "Lightcone Infrastructure general support counted as AI",
            recipient(g, r"^Lightcone") & (g["category"] == "EA & community"),
            "AI",
        ),
        (
            "Q9 media -> AI",
            "Outreach media (Kurzgesagt etc.) counted as AI",
            question(g, "Q9"),
            "AI",
        ),
        (
            "Q10 mixed field-building -> 50/50 AI/Bio",
            "BlueDot, Successif etc. split",
            question(g, "Q10"),
            "AI=0.5;Bio=0.5",
        ),
        (
            "Q12 Longview -> General x-risk",
            "Longview general support counted as GCR",
            question(g, "Q12"),
            "General x-risk",
        ),
        (
            "AI+Bio orgs -> 100% AI",
            "50/50 splits (Foresight, Pour Demain, Langsikt, ALTER) fully AI",
            split,
            "AI",
        ),
        (
            "FLI duplicates kept",
            "FLI 2023 grants counted again (double counting)",
            g["category"] == "Duplicate",
            "AI",
        ),
        (
            "Unknown -> Classic GCR (upper bound)",
            "All unclassified money assumed classic GCR",
            g["category"] == "Unknown",
            "Classic GCR",
        ),
    ]


def combined_classic_case(grants):
    """
    Applies all alternatives that favour classic GCR at once: multi-hazard
    organisations, climate/geoengineering and all Unknown money as classic GCR.

    Arguments:
        grants (pandas.DataFrame): classified grants

    Returns:
        pandas.DataFrame: the modified copy.
    """
    names = (
        "Q1 multi-hazard -> Classic GCR",
        "Q4 geoengineering+climate -> Classic GCR",
        "Unknown -> Classic GCR (upper bound)",
    )
    mask = pd.Series(False, index=grants.index)
    for name, _, scenario_mask, _ in scenarios(grants):
        if name in names:
            mask |= scenario_mask
    return recode(grants, mask, "Classic GCR")


def run(grants):
    """
    Computes metrics for the baseline and every scenario.

    Arguments:
        grants (pandas.DataFrame): classified grants

    Returns:
        pandas.DataFrame: one row per scenario with metrics and deltas.
    """
    base = metrics(grants)
    rows = [
        {"scenario": "Baseline", "description": "As classified", "n_grants": 0, **base}
    ]
    for name, description, mask, category in scenarios(grants):
        values = metrics(recode(grants, mask, category))
        rows.append(
            {
                "scenario": name,
                "description": description,
                "n_grants": int(mask.sum()),
                **values,
            }
        )
    combined = combined_classic_case(grants)
    rows.append(
        {
            "scenario": "Combined: Q1 + Q4 + Unknown -> Classic GCR",
            "description": "Most generous reading for classic GCR",
            "n_grants": int((combined["category"] != grants["category"]).sum()),
            **metrics(combined),
        }
    )
    return pd.DataFrame(rows).round(2)


def main():
    """
    Runs the sensitivity analysis and saves the table.

    Returns:
        None
    """
    grants = pd.read_csv(
        PROCESSED_DIR / "grants_classified.csv", keep_default_na=False, na_values=[""]
    )
    table = run(grants)
    RESULTS_DIR.mkdir(exist_ok=True)
    table.to_csv(RESULTS_DIR / "sensitivity.csv", index=False)
    print(table.drop(columns="description").to_string(index=False))


if __name__ == "__main__":
    main()
