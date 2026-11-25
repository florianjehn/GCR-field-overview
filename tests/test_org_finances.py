from src.org_finances import filings_to_rows, filings_without_data

RECORD = {
    "filings_with_data": [
        {"tax_prd_yr": 2023, "totrevenue": 100, "totfuncexpns": 80},
        {"tax_prd_yr": 2022, "totrevenue": 50},
    ],
    "filings_without_data": [{"tax_prd_yr": 2024}, {"formtype_str": "990"}],
}


def test_filings_to_rows_extracts_revenue_and_expenses():
    """
    Tests that each filing becomes a row, with missing fields as None.
    """
    rows = filings_to_rows("x", 123, RECORD)
    assert [row["fiscal_year"] for row in rows] == [2023, 2022]
    assert rows[0]["expenses_usd"] == 80
    assert rows[1]["expenses_usd"] is None
    assert rows[0]["source_url"].endswith("/123")


def test_filings_without_data_skips_missing_years():
    """
    Tests that filings without a year are ignored.
    """
    assert filings_without_data(RECORD) == [2024]
    assert filings_without_data({}) == []
