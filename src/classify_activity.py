"""
Assign each GCR-relevant grant an activity type.

Activities: Research, Policy & advocacy, Field-building & education, Other
(operations, media, regranting), or Unknown. Grants outside GCR (categories
EA & community, Not GCR, Regrant) get "n/a".

Precedence, highest first:
1. data/manual/activity_grant_overrides.csv (funder + grant_id)
2. data/manual/activity_rules.csv: ordered regex rules on the grant
   title/purpose; a rule with activity "Recipient default" defers to step 3
3. data/manual/activity_recipient_codes.csv (funder + recipient)
4. otherwise "Unknown"

Called from src/classify_grants.py.
"""

import re
from pathlib import Path

import pandas as pd

MANUAL_DIR = Path("data/manual")
OUT_OF_SCOPE = ("EA & community", "Not GCR", "Regrant")
DEFER = "Recipient default"
ACTIVITY_COLUMNS = [
    "activity",
    "activity_coding_source",
    "activity_confidence",
    "activity_question_id",
    "activity_rationale",
]


def match_rule(text, rules):
    """
    Finds the first rule whose pattern matches the text (case-insensitive).

    Arguments:
        text (str): grant title or purpose
        rules (pandas.DataFrame): columns order, pattern, activity, rationale

    Returns:
        tuple: (activity, rationale), or (None, None) if nothing matches.
    """
    for rule in rules.sort_values("order").itertuples(index=False):
        if re.search(rule.pattern, str(text), flags=re.IGNORECASE):
            return rule.activity, rule.rationale
    return None, None


def is_in_scope(category):
    """
    Checks whether a (possibly split) category is GCR-relevant.

    Arguments:
        category (str): e.g. "AI" or "AI=0.5;Bio=0.5"

    Returns:
        bool: False for EA & community, Not GCR and Regrant.
    """
    return category not in OUT_OF_SCOPE


def code_from_rule(activity, rationale):
    """
    Builds the activity code record for a keyword-rule match.

    Arguments:
        activity (str): the matched activity
        rationale (str): the rule rationale

    Returns:
        dict: the activity code columns.
    """
    return {
        "activity": activity,
        "activity_coding_source": "LLM-coded",
        "activity_confidence": "high",
        "activity_question_id": "",
        "activity_rationale": f"Keyword rule: {rationale}",
    }


def code_from_record(record):
    """
    Builds the activity code record from a manual-code row.

    Arguments:
        record (pandas.Series): a row from a manual activity file

    Returns:
        dict: the activity code columns.
    """
    return {column: record[column] for column in ACTIVITY_COLUMNS}


def unknown_code():
    """
    Returns the code record for a grant no source could classify.

    Returns:
        dict: the activity code columns set to Unknown.
    """
    return {
        "activity": "Unknown",
        "activity_coding_source": "LLM-coded",
        "activity_confidence": "low",
        "activity_question_id": "",
        "activity_rationale": "No rule or recipient code",
    }


def code_grant(grant, rules, recipient_codes, overrides):
    """
    Determines the activity code for one grant following the precedence.

    Arguments:
        grant (pandas.Series): one grant with funder, grant_id, recipient,
            description and category
        rules (pandas.DataFrame): keyword rules
        recipient_codes (dict): (funder, recipient) -> manual row
        overrides (dict): (funder, grant_id) -> manual row

    Returns:
        dict: the activity code columns.
    """
    if not is_in_scope(grant["category"]):
        return {column: "" for column in ACTIVITY_COLUMNS} | {"activity": "n/a"}
    key = (grant["funder"], str(grant["grant_id"]))
    if key in overrides:
        return code_from_record(overrides[key])
    activity, rationale = match_rule(grant["description"], rules)
    if activity and activity != DEFER:
        return code_from_rule(activity, rationale)
    recipient_key = (grant["funder"], grant["recipient"])
    if recipient_key in recipient_codes:
        return code_from_record(recipient_codes[recipient_key])
    return unknown_code()


def index_by(frame, columns):
    """
    Indexes manual-code rows by a tuple of key columns (as strings).

    Arguments:
        frame (pandas.DataFrame): the manual file
        columns (list): key column names

    Returns:
        dict: key tuple -> row.
    """
    return {
        tuple(str(row[column]) for column in columns): row
        for _, row in frame.iterrows()
    }


def classify_activity(grants, rules, recipient_codes, overrides):
    """
    Adds activity code columns to all grants.

    Arguments:
        grants (pandas.DataFrame): classified grants
        rules (pandas.DataFrame): keyword rules
        recipient_codes (pandas.DataFrame): funder, recipient + codes
        overrides (pandas.DataFrame): funder, grant_id + codes

    Returns:
        pandas.DataFrame: grants with activity columns.
    """
    by_recipient = index_by(recipient_codes, ["funder", "recipient"])
    by_grant = index_by(overrides, ["funder", "grant_id"])
    codes = grants.apply(
        lambda grant: pd.Series(code_grant(grant, rules, by_recipient, by_grant)),
        axis=1,
    )
    return pd.concat(
        [grants.drop(columns=ACTIVITY_COLUMNS, errors="ignore"), codes], axis=1
    )


def load_activity_inputs():
    """
    Loads the keyword rules and manual activity codes.

    Returns:
        tuple: (rules, recipient codes, grant overrides) DataFrames.
    """
    rules = load_csv(MANUAL_DIR / "activity_rules.csv").astype({"order": int})
    recipient_codes = load_csv(MANUAL_DIR / "activity_recipient_codes.csv")
    overrides = load_csv(MANUAL_DIR / "activity_grant_overrides.csv")
    return rules, recipient_codes, overrides


def load_csv(path):
    """
    Reads a CSV keeping empty strings as empty strings.

    Arguments:
        path (pathlib.Path): the CSV path

    Returns:
        pandas.DataFrame: the table.
    """
    return pd.read_csv(path, keep_default_na=False, dtype=str)
