import pandas as pd

from src.build_site import records


def test_records_replaces_nan_with_none():
    """
    Tests that missing values become None so the JSON is valid.
    """
    frame = pd.DataFrame({"a": [1.0, None], "b": ["x", None], "c": [1, 2]})
    assert records(frame, ["a", "b"]) == [{"a": 1.0, "b": "x"}, {"a": None, "b": None}]


def test_stamp_assets_versions_by_content(tmp_path):
    """
    Tests that asset links get a content hash that changes with the file.
    """
    from src.build_site import stamp_assets

    (tmp_path / "assets").mkdir()
    asset = tmp_path / "assets" / "a.js"
    asset.write_text("one")
    page = '<script src="assets/a.js?v=old"></script><link href="assets/a.js">'
    first = stamp_assets(page, tmp_path)
    asset.write_text("two")
    second = stamp_assets(page, tmp_path)
    assert first.count("assets/a.js?v=") == 2 and "v=old" not in first
    assert first != second
    assert stamp_assets(first, tmp_path) == second
