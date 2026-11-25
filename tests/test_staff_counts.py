import pandas as pd

from src.staff_counts import (
    apply_person_focus,
    apply_removals,
    assign_functions,
    assign_roles,
    carry_forward,
    count_by_function,
    count_by_year,
    match_function,
    match_role,
)

RULES = pd.DataFrame(
    [
        {
            "org_id": "cser",
            "field": "title",
            "pattern": "Assistant Professor",
            "function": "teaching",
        },
        {
            "org_id": "*",
            "field": "title",
            "pattern": "Administrator",
            "function": "operations",
        },
    ]
)
TYPES = pd.DataFrame([{"org_id": "cser", "type": "research", "focus": "classic"}])


def test_match_function_order():
    """
    Tests org rule, then generic rule, then org default.
    """

    def person(title):
        """
        Builds a CSER person with the given title.

        Arguments:
            title (str): job title

        Returns:
            pandas.Series: the person.
        """
        return pd.Series({"org_id": "cser", "title": title})

    assert (
        match_function(person("Assistant Professor in X"), RULES, "research")
        == "teaching"
    )
    assert (
        match_function(person("Centre Administrator"), RULES, "research")
        == "operations"
    )
    assert match_function(person("Research Associate"), RULES, "research") == "research"


def test_assign_functions_only_for_staff():
    """
    Tests that affiliates get no function and focus comes from org types.
    """
    people = pd.DataFrame(
        {
            "org_id": ["cser", "cser"],
            "title": ["Research Associate", "X"],
            "role": ["staff", "affiliate"],
        }
    )
    out = assign_functions(people, RULES, TYPES)
    assert list(out["function"]) == ["research", ""]
    assert list(out["focus"]) == ["classic", "classic"]


def test_apply_removals_drops_years_from_cutoff():
    """
    Tests that a removal drops the person from from_year on and nobody else.
    """
    people = pd.DataFrame(
        {
            "org_id": ["allfed"] * 3 + ["cser"],
            "name": ["A", "A", "B", "A"],
            "year": [2024, 2025, 2025, 2025],
        }
    )
    removals = pd.DataFrame([{"org_id": "allfed", "name": "A", "from_year": 2025}])
    out = apply_removals(people, removals)
    assert list(zip(out["org_id"], out["name"], out["year"])) == [
        ("allfed", "A", 2024),
        ("allfed", "B", 2025),
        ("cser", "A", 2025),
    ]


def test_apply_person_focus_overrides_named_people_only():
    """
    Tests that only the listed person gets the new focus.
    """
    people = pd.DataFrame(
        {
            "org_id": ["cser", "cser"],
            "name": ["A", "B"],
            "focus": ["classic", "classic"],
        }
    )
    overrides = pd.DataFrame([{"org_id": "cser", "name": "A", "focus": "AI or bio"}])
    assert list(apply_person_focus(people, overrides)["focus"]) == [
        "AI or bio",
        "classic",
    ]


def test_carry_forward_copies_people_only_into_missing_years():
    """
    Tests that people are copied to a missing year and existing years are kept.
    """
    people = pd.DataFrame(
        {
            "org_id": ["cser", "cser", "gcri", "gcri"],
            "year": [2025, 2025, 2025, 2026],
            "name": ["A", "B", "C", "D"],
            "source": ["team page"] * 4,
        }
    )
    rules = pd.DataFrame(
        {"org_id": ["cser", "gcri"], "from_year": [2025, 2025], "to_year": [2026, 2026]}
    )
    out = carry_forward(people, rules)
    added = out[out["source"] == "assumed same as 2025"]
    assert list(zip(added["org_id"], added["year"], added["name"])) == [
        ("cser", 2026, "A"),
        ("cser", 2026, "B"),
    ]
    assert len(out) == 6


ROLE_RULES = pd.DataFrame(
    [
        {
            "org_id": "gpi",
            "field": "section",
            "pattern": "Board",
            "role": "board",
            "topic": "",
        },
        {
            "org_id": "gpi",
            "field": "title",
            "pattern": "AI",
            "role": "staff",
            "topic": "AI",
        },
        {
            "org_id": "gpi",
            "field": "section",
            "pattern": ".*",
            "role": "staff",
            "topic": "",
        },
    ]
)


def test_match_role_first_rule_wins_and_unknown_fallback():
    """
    Tests rule order, topic passing and the fallback for unmatched people.
    """
    board = pd.Series({"org_id": "gpi", "section": "Board", "title": "AI lead"})
    ai = pd.Series({"org_id": "gpi", "section": "Team", "title": "AI lead"})
    other = pd.Series({"org_id": "cser", "section": "Team", "title": "X"})
    assert match_role(board, ROLE_RULES) == ("board", "")
    assert match_role(ai, ROLE_RULES) == ("staff", "AI")
    assert match_role(other, ROLE_RULES) == ("unknown", "")


def test_assign_roles_adds_role_and_topic():
    """
    Tests that assign_roles adds both columns row by row.
    """
    people = pd.DataFrame(
        {"org_id": ["gpi", "gpi"], "section": ["Board", "Team"], "title": ["", ""]}
    )
    out = assign_roles(people, ROLE_RULES)
    assert list(out["role"]) == ["board", "staff"]
    assert list(out["topic"]) == ["", ""]


def test_count_by_function_skips_people_without_function():
    """
    Tests grouping by organization, year, focus, function and source.
    """
    people = pd.DataFrame(
        {
            "org_id": ["cser"] * 3,
            "year": [2025] * 3,
            "focus": ["classic"] * 3,
            "function": ["research", "research", ""],
            "source": ["team page"] * 3,
        }
    )
    out = count_by_function(people)
    assert out.to_dict("records") == [
        {
            "org_id": "cser",
            "year": 2025,
            "focus": "classic",
            "function": "research",
            "source": "team page",
            "people": 2,
        }
    ]


def test_count_by_year_one_column_per_role():
    """
    Tests the wide table of people per organization, year and role.
    """
    people = pd.DataFrame(
        {
            "org_id": ["cser"] * 3,
            "year": [2025] * 3,
            "role": ["staff", "staff", "board"],
        }
    )
    out = count_by_year(people)
    assert out.loc[0, "staff"] == 2 and out.loc[0, "board"] == 1
