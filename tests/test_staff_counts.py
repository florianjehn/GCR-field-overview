import pandas as pd

from src.staff_counts import assign_functions, match_function

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
    from src.staff_counts import apply_removals

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
