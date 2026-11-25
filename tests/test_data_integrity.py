"""
Checks on the committed data: manual files must point at records that exist,
rules must match something, and processed tables must agree with the raw
downloads and with each other. These catch silent errors such as a typo in a
name that makes a removal do nothing.
"""

import json
import re
from pathlib import Path

import pandas as pd
import pytest

MANUAL = Path("data/manual")
PROCESSED = Path("data/processed")
RAW = Path("data/raw")
GCR_CATEGORIES = {
    "AI",
    "Bio",
    "Classic GCR",
    "Climate",
    "Forecasting",
    "General x-risk",
    "Geoengineering",
    "Unknown",
}
OTHER_CATEGORIES = {"Duplicate", "EA & community", "Not GCR", "Regrant"}


def manual(name):
    """
    Reads a file from data/manual without turning empty cells into NaN.

    Arguments:
        name (str): file name

    Returns:
        pandas.DataFrame: the file.
    """
    return pd.read_csv(MANUAL / name, keep_default_na=False)


@pytest.fixture(scope="module")
def grants():
    """
    Loads the classified grants.

    Returns:
        pandas.DataFrame: data/processed/grants_classified.csv
    """
    return pd.read_csv(PROCESSED / "grants_classified.csv", keep_default_na=False)


@pytest.fixture(scope="module")
def people():
    """
    Loads parsed and hand-added people, before roles are assigned.

    Returns:
        pandas.DataFrame: team_people_raw.csv plus team_additions.csv
    """
    raw = pd.read_csv(PROCESSED / "team_people_raw.csv", keep_default_na=False)
    return pd.concat([raw, manual("team_additions.csv")], ignore_index=True)


def test_grant_ids_unique(grants):
    """
    Tests that every grant appears once per funder.
    """
    assert not grants.duplicated(["funder", "grant_id"]).any()


def test_categories_known_and_shares_sum_to_one(grants):
    """
    Tests category names and that split shares add up to 1.
    """
    for value in grants["category"]:
        parts = [part.split("=") for part in value.split(";")]
        assert {p[0] for p in parts} <= GCR_CATEGORIES | OTHER_CATEGORIES, value
        if len(parts) > 1:
            assert sum(float(p[1]) for p in parts) == pytest.approx(1), value


def test_split_table_keeps_total(grants):
    """
    Tests that grants_by_category.csv neither loses nor adds money.
    """
    split = pd.read_csv(PROCESSED / "grants_by_category.csv")
    total = pd.to_numeric(grants["amount_usd"], errors="coerce").sum()
    assert split["amount_usd_share"].sum() == pytest.approx(total)


def test_activity_only_for_gcr_grants():
    """
    Tests that every in-scope grant has an activity and others have n/a.
    """
    split = pd.read_csv(PROCESSED / "grants_by_category.csv", keep_default_na=False)
    in_scope = split["category"].isin(GCR_CATEGORIES)
    assert (split.loc[in_scope, "activity"] != "n/a").all()
    assert (split.loc[~in_scope, "activity"] == "n/a").all()


@pytest.mark.parametrize(
    "file_name, funder",
    [
        ("coefficient_manual_codes.csv", "Coefficient"),
        ("ltff_manual_codes.csv", "Long-Term"),
        ("fli_manual_codes.csv", "Future of Life"),
    ],
)
def test_manual_grant_codes_applied(grants, file_name, funder):
    """
    Tests that every hand-coded grant exists and carries its hand code.
    """
    coded = grants[grants["funder"].str.startswith(funder)]
    category = dict(zip(coded["grant_id"].astype(str), coded["category"]))
    for row in manual(file_name).itertuples():
        assert category.get(str(row.grant_id)) == row.category, row.grant_id


def test_sff_codes_cover_all_organizations():
    """
    Tests that the SFF organization codes and the SFF grants match one to one.
    """
    sff = pd.read_csv(PROCESSED / "sff_grants.csv", keep_default_na=False)
    codes = manual("sff_manual_codes.csv")
    assert set(codes["organization"]) == set(sff["organization"])


def test_activity_references_exist(grants):
    """
    Tests that activity overrides and recipient defaults point at real grants.
    """
    keys = set(grants["funder"] + "|" + grants["grant_id"].astype(str))
    for row in manual("activity_grant_overrides.csv").itertuples():
        assert f"{row.funder}|{row.grant_id}" in keys, row.grant_id
    recipients = set(grants["funder"] + "|" + grants["recipient"])
    for row in manual("activity_recipient_codes.csv").itertuples():
        assert f"{row.funder}|{row.recipient}" in recipients, row.recipient


def test_coefficient_matches_raw_download():
    """
    Tests that the processed Coefficient grants add up to the raw download.
    """
    raw = json.loads(next(RAW.glob("coefficient_giving_grants_*.json")).read_text())
    amounts = [
        float(re.sub(r"[^\d.]", "", str(hit["grant_amount"])))
        for hit in raw
        if hit.get("grant_amount") not in (None, "")
    ]
    processed = pd.read_csv(PROCESSED / "coefficient_giving_grants.csv")
    assert len(processed) == len(raw)
    assert processed["amount_usd"].sum() == pytest.approx(sum(amounts))


def test_ltff_matches_raw_download():
    """
    Tests that the processed LTFF grants are exactly the raw LTFF entries.
    """
    raw = json.loads(next(RAW.glob("ea_funds_grants_*.json")).read_text())
    ltff = [g for g in raw if g["fund"] == "Long-Term Future Fund"]
    processed = pd.read_csv(PROCESSED / "ltff_grants.csv")
    assert len(processed) == len(ltff)
    total = sum(float(g["amount"] or 0) for g in ltff)
    assert processed["amount_usd"].sum() == pytest.approx(total)


def test_organizations_have_types():
    """
    Tests that org types refer to known organizations and that every
    organization with people has a type.
    """
    orgs = set(manual("organizations.csv")["org_id"])
    types = set(manual("org_types.csv")["org_id"])
    assert types <= orgs
    counted = pd.read_csv(PROCESSED / "team_people.csv", keep_default_na=False)
    assert set(counted["org_id"]) <= types


@pytest.mark.parametrize("file_name", ["team_removals.csv", "team_person_focus.csv"])
def test_person_corrections_name_real_people(people, file_name):
    """
    Tests that every hand correction names someone found on that org's pages.
    """
    names = set(people["org_id"] + "|" + people["name"])
    for row in manual(file_name).itertuples():
        assert f"{row.org_id}|{row.name}" in names, row.name


def test_removals_applied():
    """
    Tests that removed people are gone from the counted table.
    """
    counted = pd.read_csv(PROCESSED / "team_people.csv", keep_default_na=False)
    for row in manual("team_removals.csv").itertuples():
        hit = counted[
            (counted["org_id"] == row.org_id)
            & (counted["name"] == row.name)
            & (counted["year"] >= row.from_year)
        ]
        assert hit.empty, row.name


def test_no_unknown_roles():
    """
    Tests that every person found on a team page got a role.
    """
    counted = pd.read_csv(PROCESSED / "team_people.csv", keep_default_na=False)
    assert (counted["role"] != "unknown").all()


@pytest.mark.parametrize(
    "file_name, table",
    [("team_role_rules.csv", "raw"), ("team_function_rules.csv", "counted")],
)
def test_staff_rules_all_match_someone(people, file_name, table):
    """
    Tests that no role or function rule is dead (matches nobody).
    """
    pool = people
    if table == "counted":
        pool = pd.read_csv(PROCESSED / "team_people.csv", keep_default_na=False)
    for rule in manual(file_name).itertuples():
        scope = pool if rule.org_id == "*" else pool[pool["org_id"] == rule.org_id]
        texts = scope[rule.field].astype(str)
        assert texts.apply(lambda t: bool(re.search(rule.pattern, t, re.I))).any(), (
            rule.org_id,
            rule.pattern,
        )


def test_site_data_matches_processed(grants):
    """
    Tests that the site's funding JSON has every grant with an amount (one
    Coefficient investment has none) and the same total.
    """
    site = json.loads(Path("docs/data/funding.json").read_text())
    split = pd.read_csv(PROCESSED / "grants_by_category.csv")
    split = split.dropna(subset=["amount_usd_share"])
    assert len(site) == len(split)
    site_total = sum(g["amount"] or 0 for g in site)
    assert site_total == pytest.approx(split["amount_usd_share"].sum())
