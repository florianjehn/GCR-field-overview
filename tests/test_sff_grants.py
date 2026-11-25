from src.sff_grants import clean_cell, parse_amount, parse_table, round_to_year

SAMPLE_HTML = """
<table><tbody>
<tr><td class="in-grid">SFF-2026</td><td class="in-grid">Jaan Tallinn</td>
<td class="in-grid">AI &amp; Democracy Foundation</td>
<td class="in-grid">$338,000 +$16,000‡</td>
<td class="in-grid">Thoughtful Tech Project, Inc.</td>
<td class="in-grid">General support</td></tr>
<tr><th>Header row is ignored</th></tr>
</tbody></table>
"""


def test_parse_amount_single():
    """
    Tests a plain single amount.
    """
    assert parse_amount("$1,305,000") == (1305000, 0)


def test_parse_amount_two_funders():
    """
    Tests that amounts from two funders are summed.
    """
    assert parse_amount("$4,000 and $26,000") == (30000, 0)


def test_parse_amount_matching_pledge():
    """
    Tests that dagger-marked amounts are counted as matching pledges.
    """
    assert parse_amount("$29,000 +$277,000‡ and $1,541,000") == (1570000, 277000)


def test_parse_amount_matching_only():
    """
    Tests an amount that is only a matching pledge.
    """
    assert parse_amount("$1,607,000‡") == (0, 1607000)


def test_round_to_year():
    """
    Tests year extraction from both round name formats.
    """
    assert round_to_year("SFF-2023-H2") == 2023
    assert round_to_year("Initiative Committee 2024") == 2024


def test_clean_cell():
    """
    Tests that tags and entities are removed.
    """
    assert clean_cell("<b>AI &amp; Democracy</b> ") == "AI & Democracy"


def test_parse_table():
    """
    Tests that only complete data rows are parsed.
    """
    rows = parse_table(SAMPLE_HTML)
    assert len(rows) == 1
    assert rows[0]["organization"] == "AI & Democracy Foundation"
    assert rows[0]["amount"] == "$338,000 +$16,000‡"
