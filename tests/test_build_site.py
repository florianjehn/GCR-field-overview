import pandas as pd

from src.build_site import records


def test_records_replaces_nan_with_none():
    """
    Tests that missing values become None so the JSON is valid.
    """
    frame = pd.DataFrame({"a": [1.0, None], "b": ["x", None], "c": [1, 2]})
    assert records(frame, ["a", "b"]) == [{"a": 1.0, "b": "x"}, {"a": None, "b": None}]


def test_carry_forward_copies_only_missing_years():
    """
    Tests that counts are copied to a missing year and existing years are kept.
    """
    from src.build_site import carry_forward

    functions = pd.DataFrame(
        {
            "org_id": ["cser", "cser", "gcri", "gcri"],
            "year": [2025, 2025, 2025, 2026],
            "function": ["research", "teaching", "research", "research"],
            "people": [15, 4, 2, 3],
            "source": ["team page"] * 4,
        }
    )
    rules = pd.DataFrame(
        {"org_id": ["cser", "gcri"], "from_year": [2025, 2025], "to_year": [2026, 2026]}
    )
    out = carry_forward(functions, rules)
    added = out[out["source"] == "assumed same as 2025"]
    assert list(zip(added["org_id"], added["year"], added["people"])) == [
        ("cser", 2026, 15),
        ("cser", 2026, 4),
    ]
    assert len(out) == 6
