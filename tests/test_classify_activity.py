import pandas as pd

from src.classify_activity import (
    classify_activity,
    code_grant,
    is_in_scope,
    match_rule,
)

RULES = pd.DataFrame(
    {
        "order": [1, 2, 3],
        "pattern": ["fellowship", "general support", "research"],
        "activity": ["Field-building & education", "Recipient default", "Research"],
        "rationale": ["training", "generic", "research"],
    }
)
CODE = {
    "activity": "Policy & advocacy",
    "activity_coding_source": "LLM-coded",
    "activity_confidence": "high",
    "activity_question_id": "",
    "activity_rationale": "think tank",
}


def grant(description, category="AI", recipient="Org", grant_id="1"):
    """
    Builds a one-grant Series for tests.

    Arguments:
        description (str): grant title or purpose
        category (str): hazard category
        recipient (str): recipient name
        grant_id (str): grant id

    Returns:
        pandas.Series: the grant.
    """
    return pd.Series(
        {
            "funder": "F",
            "grant_id": grant_id,
            "recipient": recipient,
            "description": description,
            "category": category,
        }
    )


def test_match_rule_first_match_wins():
    """
    Tests that the lowest-order matching rule is used.
    """
    activity, _ = match_rule("Research Fellowship", RULES)
    assert activity == "Field-building & education"


def test_match_rule_no_match():
    """
    Tests that unmatched text returns None.
    """
    assert match_rule("Something else", RULES) == (None, None)


def test_is_in_scope():
    """
    Tests that excluded categories are out of scope and splits are in scope.
    """
    assert not is_in_scope("EA & community")
    assert is_in_scope("AI=0.5;Bio=0.5")


def test_code_grant_out_of_scope_is_na():
    """
    Tests that out-of-scope grants get activity n/a.
    """
    assert (
        code_grant(grant("x", category="Not GCR"), RULES, {}, {})["activity"] == "n/a"
    )


def test_code_grant_generic_title_uses_recipient_default():
    """
    Tests that a generic title defers to the recipient code.
    """
    recipient_codes = {("F", "Org"): pd.Series(CODE)}
    code = code_grant(grant("General Support"), RULES, recipient_codes, {})
    assert code["activity"] == "Policy & advocacy"


def test_code_grant_override_beats_rule():
    """
    Tests that a grant override takes precedence over keyword rules.
    """
    overrides = {("F", "1"): pd.Series(CODE)}
    code = code_grant(grant("AI Research"), RULES, {}, overrides)
    assert code["activity"] == "Policy & advocacy"


def test_code_grant_unknown_without_sources():
    """
    Tests that a generic grant with no recipient code is Unknown.
    """
    assert code_grant(grant("General Support"), RULES, {}, {})["activity"] == "Unknown"


def test_classify_activity_adds_columns():
    """
    Tests that classify_activity adds the activity columns.
    """
    grants = pd.DataFrame([grant("AI Research"), grant("x", category="Regrant")])
    empty = pd.DataFrame(columns=["funder", "recipient", "grant_id"] + list(CODE))
    coded = classify_activity(grants, RULES, empty, empty)
    assert list(coded["activity"]) == ["Research", "n/a"]
