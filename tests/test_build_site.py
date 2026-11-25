import pandas as pd

from src.build_site import records


def test_records_replaces_nan_with_none():
    """
    Tests that missing values become None so the JSON is valid.
    """
    frame = pd.DataFrame({"a": [1.0, None], "b": ["x", None], "c": [1, 2]})
    assert records(frame, ["a", "b"]) == [{"a": 1.0, "b": "x"}, {"a": None, "b": None}]
