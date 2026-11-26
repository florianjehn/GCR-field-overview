"""
Assign every grant to a GCR category and combine all funders in one table.

Categories: AI, Bio, Classic GCR, General x-risk, Climate, Geoengineering,
Forecasting, EA & community, Not GCR, Regrant (money passed to another fund,
excluded from totals), Duplicate (same money already counted under another
funder, excluded from totals) and Unknown. See data/manual/decisions.md.

A category can be split across several categories, written as
"AI=0.5;Bio=0.5". The long table grants_by_category.csv has one row per
grant and category share, with `amount_usd_share` = amount x share.

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

from src.classify_activity import classify_activity, load_activity_inputs

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


def classify_by_grant_id(grants, manual_codes, description):
    """
    Classifies grants coded one by one (LTFF, FLI); every grant needs a code.

    Arguments:
        grants (pandas.DataFrame): processed grants with grant_id
        manual_codes (pandas.DataFrame): rows keyed by grant_id
        description (pandas.Series): description text for each grant

    Returns:
        pandas.DataFrame: grants with the code columns added.
    """
    coded = grants.assign(description=description.values).merge(
        manual_codes[["grant_id"] + CODE_COLUMNS], on="grant_id", how="left"
    )
    missing = coded.loc[coded["category"].isna(), "grant_id"].tolist()
    if missing:
        raise ValueError(f"Grants without a code: {missing[:5]}")
    coded["matching_pledge_usd"] = 0
    coded["funder_focus_area"] = ""
    return coded


def load_ltff_and_fli():
    """
    Loads and classifies LTFF and FLI grants.

    Returns:
        list: the two classified DataFrames.
    """
    ltff = load_csv(PROCESSED_DIR / "ltff_grants.csv")
    fli = load_csv(PROCESSED_DIR / "fli_grants.csv")
    return [
        classify_by_grant_id(
            ltff, load_csv(MANUAL_DIR / "ltff_manual_codes.csv"), ltff["description"]
        ),
        classify_by_grant_id(
            fli,
            load_csv(MANUAL_DIR / "fli_manual_codes.csv"),
            fli["program"] + ": " + fli["title"],
        ),
    ]


def parse_category_shares(category):
    """
    Parses a category string into (category, share) pairs.

    Arguments:
        category (str): e.g. "AI" or "AI=0.5;Bio=0.5"

    Returns:
        list: (category, share) tuples whose shares sum to 1.
    """
    if "=" not in category:
        return [(category, 1.0)]
    pairs = [part.split("=") for part in category.split(";")]
    shares = [(name.strip(), float(value)) for name, value in pairs]
    if abs(sum(share for _, share in shares) - 1) > 1e-9:
        raise ValueError(f"Shares do not sum to 1: {category}")
    return shares


def explode_categories(grants):
    """
    Expands split categories into one row per grant and category share.

    Arguments:
        grants (pandas.DataFrame): grants with a `category` column

    Returns:
        pandas.DataFrame: rows with `category`, `share` and `amount_usd_share`.
    """
    long = grants.copy()
    long["category"] = long["category"].apply(parse_category_shares)
    long = long.explode("category", ignore_index=True)
    long["share"] = long["category"].str[1]
    long["category"] = long["category"].str[0]
    long["amount_usd_share"] = long["amount_usd"] * long["share"]
    return long


def apply_url_overrides(grants, overrides):
    """
    Replaces source URLs that do not load with a working page.

    Arguments:
        grants (pandas.DataFrame): classified grants of all funders
        overrides (pandas.DataFrame): rows with funder, grant_id and source_url

    Returns:
        pandas.DataFrame: grants with the overridden URLs.
    """
    fixed = grants.copy()
    keys = fixed["funder"] + "|" + fixed["grant_id"].astype(str)
    new_urls = dict(
        zip(
            overrides["funder"] + "|" + overrides["grant_id"].astype(str),
            overrides["source_url"],
        )
    )
    hit = keys.isin(new_urls)
    fixed.loc[hit, "source_url"] = keys[hit].map(new_urls)
    return fixed


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
    frames = [coefficient, sff] + load_ltff_and_fli()
    combined = pd.concat([frame[OUTPUT_COLUMNS] for frame in frames], ignore_index=True)
    combined = apply_url_overrides(
        combined, load_csv(MANUAL_DIR / "source_url_overrides.csv")
    )
    combined = classify_activity(combined, *load_activity_inputs())
    combined.to_csv(PROCESSED_DIR / "grants_classified.csv", index=False)
    long = explode_categories(combined)
    long.to_csv(PROCESSED_DIR / "grants_by_category.csv", index=False)
    print(f"Wrote {len(combined)} grants, {len(long)} category rows")
    totals = long.pivot_table("amount_usd_share", "category", "funder", "sum")
    print((totals / 1e6).round(1))
    print(combined["activity"].value_counts())


if __name__ == "__main__":
    main()
