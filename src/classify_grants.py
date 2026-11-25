"""
Assign every grant to a GCR category and combine all funders in one table.

Categories: AI, Bio, Classic GCR, General x-risk, EA & community, Not GCR,
and Unknown (open question, see data/manual/decisions.md).

Each grant carries a `coding_source`:
- "funder-label": category follows the funder's own fund (Coefficient Giving
  "Navigating Transformative AI" -> AI, "Biosecurity & Pandemic
  Preparedness" -> Bio, everything outside GCR-related funds -> Not GCR).
- "LLM-coded": assigned by Claude from title, recipient and purpose
  (data/manual/*_manual_codes.csv), with a confidence level.
- "human-coded": confirmed or set by the author.

Run with:
    uv run python3 -m src.classify_grants
"""

from pathlib import Path

import pandas as pd

PROCESSED_DIR = Path("data/processed")
MANUAL_DIR = Path("data/manual")
AI_FUNDS = ("Navigating Transformative AI",)
BIO_FUNDS = (
    "Biosecurity & Pandemic Preparedness",
    "Science Supporting Biosecurity and Pandemic Preparedness",
)
EA_FUNDS = ("Effective Giving & Careers",)
CODE_COLUMNS = ["category", "coding_source", "confidence", "question_id", "rationale"]
OUTPUT_COLUMNS = (
    [
        "funder",
        "grant_id",
        "award_year",
        "recipient",
        "description",
        "amount_usd",
        "matching_pledge_usd",
        "funder_focus_area",
    ]
    + CODE_COLUMNS
    + ["source_url"]
)


def funder_label_category(focus_areas):
    """
    Maps Coefficient Giving fund labels to a category.

    Arguments:
        focus_areas (str): fund labels joined with " | "

    Returns:
        str: the category implied by the fund labels.
    """
    labels = set(str(focus_areas).split(" | "))
    if labels & set(AI_FUNDS):
        return "AI"
    if labels & set(BIO_FUNDS):
        return "Bio"
    if labels & set(EA_FUNDS):
        return "EA & community"
    return "Not GCR"


def classify_coefficient(grants, manual_codes):
    """
    Classifies Coefficient Giving grants: manual codes override fund labels.

    Arguments:
        grants (pandas.DataFrame): processed Coefficient grants
        manual_codes (pandas.DataFrame): rows keyed by grant_id

    Returns:
        pandas.DataFrame: grants with the code columns added.
    """
    coded = grants.merge(
        manual_codes[["grant_id"] + CODE_COLUMNS], on="grant_id", how="left"
    )
    is_label = coded["category"].isna()
    coded.loc[is_label, "category"] = coded.loc[is_label, "funder_focus_area"].apply(
        funder_label_category
    )
    coded.loc[is_label, "coding_source"] = "funder-label"
    coded.loc[is_label, "confidence"] = "high"
    coded.loc[is_label, "rationale"] = "Category of the funder's own fund"
    coded["description"] = coded["title"]
    coded["matching_pledge_usd"] = 0
    return coded


def apply_purpose_overrides(coded, overrides):
    """
    Overrides SFF codes for rows whose purpose contains a given phrase.

    Arguments:
        coded (pandas.DataFrame): SFF grants with code columns
        overrides (pandas.DataFrame): organization, purpose_contains + codes

    Returns:
        pandas.DataFrame: the grants with overrides applied.
    """
    coded = coded.copy()
    for override in overrides.itertuples(index=False):
        mask = (coded["organization"] == override.organization) & coded[
            "purpose"
        ].str.contains(override.purpose_contains, case=False, na=False)
        for column in CODE_COLUMNS:
            coded.loc[mask, column] = getattr(override, column)
    return coded


def classify_sff(grants, manual_codes, overrides):
    """
    Classifies SFF recommendations by organization, then purpose overrides.

    Arguments:
        grants (pandas.DataFrame): processed SFF recommendations
        manual_codes (pandas.DataFrame): rows keyed by organization
        overrides (pandas.DataFrame): purpose-level overrides

    Returns:
        pandas.DataFrame: grants with the code columns added.
    """
    coded = grants.merge(
        manual_codes[["organization"] + CODE_COLUMNS], on="organization", how="left"
    )
    missing = coded.loc[coded["category"].isna(), "organization"].unique()
    if len(missing):
        raise ValueError(f"SFF organizations without a code: {list(missing)}")
    coded = apply_purpose_overrides(coded, overrides)
    coded["recipient"] = coded["organization"]
    coded["description"] = coded["round"] + ": " + coded["purpose"]
    coded["funder_focus_area"] = ""
    return coded


def load_csv(path):
    """
    Reads a CSV with empty strings instead of NaN in text columns.

    Arguments:
        path (pathlib.Path): the CSV path

    Returns:
        pandas.DataFrame: the table.
    """
    return pd.read_csv(path, keep_default_na=False, na_values=[""])


def main():
    """
    Classifies all funders' grants and writes the combined table.

    Returns:
        None
    """
    coefficient = classify_coefficient(
        load_csv(PROCESSED_DIR / "coefficient_giving_grants.csv"),
        load_csv(MANUAL_DIR / "coefficient_manual_codes.csv"),
    )
    sff = classify_sff(
        load_csv(PROCESSED_DIR / "sff_grants.csv"),
        load_csv(MANUAL_DIR / "sff_manual_codes.csv"),
        load_csv(MANUAL_DIR / "sff_purpose_overrides.csv"),
    )
    combined = pd.concat(
        [coefficient[OUTPUT_COLUMNS], sff[OUTPUT_COLUMNS]], ignore_index=True
    )
    combined.to_csv(PROCESSED_DIR / "grants_classified.csv", index=False)
    print(f"Wrote {len(combined)} grants")
    print(combined.pivot_table("amount_usd", "category", "funder", "sum") / 1e6)


if __name__ == "__main__":
    main()
