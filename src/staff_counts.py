"""
Assign roles to people found on team pages and count staff per year.

Roles come from data/manual/team_role_rules.csv: ordered regex rules per
organization on either the section label or the job title (first match
wins). Roles: staff, scholar (paid fixed-term research fellows), student,
volunteer, affiliate, board, alumni, unknown. A rule can also set a topic
(AI, bio, classic, general) when the section or title states it.

Run with:
    uv run python3 -m src.staff_counts
"""

import re
from pathlib import Path

import pandas as pd

MANUAL_DIR = Path("data/manual")
PROCESSED_DIR = Path("data/processed")


def match_role(person, rules):
    """
    Finds the first rule matching a person's section or title.

    Arguments:
        person (pandas.Series): row with org_id, section and title
        rules (pandas.DataFrame): role rules (org_id, field, pattern, role, topic)

    Returns:
        tuple: (role, topic), ("unknown", "") if no rule matches.
    """
    for rule in rules[rules["org_id"] == person["org_id"]].itertuples(index=False):
        text = str(person[rule.field] or "")
        if re.search(rule.pattern, text, flags=re.I):
            return rule.role, rule.topic
    return "unknown", ""


def carry_forward(people, rules):
    """
    Copies an organization's people from one year to a later year without a
    readable team page. Copied rows get source "assumed same as <year>", so
    later removals still apply to them.

    Arguments:
        people (pandas.DataFrame): people with org_id, year and source
        rules (pandas.DataFrame): org_id, from_year, to_year

    Returns:
        pandas.DataFrame: people plus the carried-forward rows.
    """
    copies = []
    for rule in rules.itertuples(index=False):
        org = people["org_id"] == rule.org_id
        if (org & (people["year"] == rule.to_year)).any():
            continue
        rows = people[org & (people["year"] == rule.from_year)]
        copies.append(
            rows.assign(year=rule.to_year, source=f"assumed same as {rule.from_year}")
        )
    return pd.concat([people, *copies], ignore_index=True)


def apply_removals(people, removals):
    """
    Drops people the author knows had left although the page still lists them.

    Arguments:
        people (pandas.DataFrame): people with org_id, name and year
        removals (pandas.DataFrame): org_id, name, from_year

    Returns:
        pandas.DataFrame: people without the removed person-years.
    """
    merged = people.merge(
        removals[["org_id", "name", "from_year"]], on=["org_id", "name"], how="left"
    )
    keep = merged["from_year"].isna() | (merged["year"] < merged["from_year"])
    return people[keep.to_numpy()]


def assign_roles(people, rules):
    """
    Adds role and topic columns to the people table.

    Arguments:
        people (pandas.DataFrame): output of src.team_pages
        rules (pandas.DataFrame): role rules

    Returns:
        pandas.DataFrame: people with role and topic.
    """
    roles = people.apply(lambda person: match_role(person, rules), axis=1)
    return people.assign(role=[r for r, _ in roles], topic=[t for _, t in roles])


def match_function(person, rules, default):
    """
    Finds a person's function (research, teaching, policy, operations).

    Organization-specific rules come first, then generic rules (org_id "*"),
    then the organization's default type.

    Arguments:
        person (pandas.Series): row with org_id and title
        rules (pandas.DataFrame): function rules (org_id, field, pattern, function)
        default (str): the organization's default type

    Returns:
        str: the function.
    """
    for org in (person["org_id"], "*"):
        for rule in rules[rules["org_id"] == org].itertuples(index=False):
            if re.search(rule.pattern, str(person[rule.field] or ""), flags=re.I):
                return rule.function
    return default


def assign_functions(people, rules, org_types):
    """
    Adds function and focus columns; only staff and scholars get a function.

    Arguments:
        people (pandas.DataFrame): people with role
        rules (pandas.DataFrame): function rules
        org_types (pandas.DataFrame): org_id, type, focus

    Returns:
        pandas.DataFrame: people with function and focus.
    """
    types = org_types.set_index("org_id")
    counted = people["role"].isin(["staff", "scholar"])
    functions = [
        match_function(person, rules, types["type"].get(person["org_id"], ""))
        if is_counted
        else ""
        for (_, person), is_counted in zip(people.iterrows(), counted)
    ]
    return people.assign(
        function=functions, focus=people["org_id"].map(types["focus"]).fillna("")
    )


def apply_person_focus(people, overrides):
    """
    Replaces the organization's focus for people who mainly work on another
    focus (e.g. CSER researchers working on AI or bio), in every year.

    Arguments:
        people (pandas.DataFrame): people with org_id, name and focus
        overrides (pandas.DataFrame): org_id, name, focus

    Returns:
        pandas.DataFrame: people with the corrected focus.
    """
    keys = ["org_id", "name"]
    merged = people[keys].merge(overrides[[*keys, "focus"]], on=keys, how="left")
    new = merged["focus"].to_numpy()
    return people.assign(
        focus=[n if isinstance(n, str) else o for n, o in zip(new, people["focus"])]
    )


def count_by_function(people):
    """
    Counts staff and scholars per organization, year and function.

    Arguments:
        people (pandas.DataFrame): people with function and focus

    Returns:
        pandas.DataFrame: org_id, year, focus, function, source, people.
    """
    counted = people[people["function"] != ""]
    keys = ["org_id", "year", "focus", "function", "source"]
    return counted.groupby(keys).size().rename("people").reset_index()


def count_by_year(people):
    """
    Counts people per organization, year and role.

    Arguments:
        people (pandas.DataFrame): people with role

    Returns:
        pandas.DataFrame: org_id, year, one column per role.
    """
    return (
        people.groupby(["org_id", "year", "role"])
        .size()
        .unstack("role", fill_value=0)
        .reset_index()
    )


def main():
    """
    Assigns roles, writes the person table and the yearly counts.

    Returns:
        None
    """
    people = pd.read_csv(PROCESSED_DIR / "team_people_raw.csv", keep_default_na=False)
    additions = pd.read_csv(MANUAL_DIR / "team_additions.csv", keep_default_na=False)
    people = pd.concat(
        [people, additions.drop(columns=["evidence"])], ignore_index=True
    )
    people = carry_forward(
        people.assign(source="team page"),
        pd.read_csv(MANUAL_DIR / "staff_carry_forward.csv"),
    )
    removals = pd.read_csv(MANUAL_DIR / "team_removals.csv", keep_default_na=False)
    people = apply_removals(people, removals)
    rules = pd.read_csv(MANUAL_DIR / "team_role_rules.csv", keep_default_na=False)
    coded = assign_roles(people, rules)
    coded = assign_functions(
        coded,
        pd.read_csv(MANUAL_DIR / "team_function_rules.csv", keep_default_na=False),
        pd.read_csv(MANUAL_DIR / "org_types.csv", keep_default_na=False),
    )
    coded = apply_person_focus(
        coded,
        pd.read_csv(MANUAL_DIR / "team_person_focus.csv", keep_default_na=False),
    )
    count_by_function(coded).to_csv(
        PROCESSED_DIR / "staff_by_function.csv", index=False
    )
    coded.to_csv(PROCESSED_DIR / "team_people.csv", index=False)
    counts = count_by_year(coded)
    counts.to_csv(PROCESSED_DIR / "staff_by_year.csv", index=False)
    print(counts.to_string(index=False))
    unknown = coded[coded["role"] == "unknown"]
    print(unknown.groupby(["org_id", "section", "title"]).size().to_string())


if __name__ == "__main__":
    main()
