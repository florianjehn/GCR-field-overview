import json

from src.fli_grants import (
    BLOCK_MARKER,
    parse_amount,
    parse_page,
    recipient_name,
)
from src.ltff_grants import extract_grants, grants_to_frame

GRANTS = [
    {
        "id": "a",
        "fund": "Long-Term Future Fund",
        "description": "AI safety research",
        "grantee": "X",
        "amount": 100,
        "round": "2024 Q1",
        "year": 2024,
    },
    {
        "id": "b",
        "fund": "Animal Welfare Fund",
        "description": "Cages",
        "grantee": "Y",
        "amount": 5,
        "round": "2024 Q1",
        "year": 2024,
    },
]


def test_extract_grants_from_next_data():
    """
    Tests that grants are read from the embedded __NEXT_DATA__ JSON.
    """
    payload = {"props": {"pageProps": {"grantsList": GRANTS}}}
    page = f'<script id="__NEXT_DATA__" type="application/json">{json.dumps(payload)}'
    page += "</script>"
    assert extract_grants(page) == GRANTS


def test_grants_to_frame_keeps_only_ltff():
    """
    Tests that only Long-Term Future Fund grants are kept.
    """
    frame = grants_to_frame(GRANTS)
    assert list(frame["grant_id"]) == ["ltff-a"]
    assert frame["amount_usd"].iloc[0] == 100


def fli_block(title, amount, investigator=""):
    """
    Builds a minimal FLI accordion block for tests.

    Arguments:
        title (str): project title
        amount (str): amount text
        investigator (str): investigator text, may be empty

    Returns:
        str: the HTML block.
    """
    pi = (
        f'<div data-id="text_block-340-45669">{investigator}</div>'
        if investigator
        else ""
    )
    return (
        f'<div {BLOCK_MARKER}><span data-id="span-254-45669">{title}</span>'
        f'<div data-id="code_block-48-45676">{amount}</div>{pi}'
        "Details Summary text</div><div id="
    )


def test_parse_amount():
    """
    Tests amount parsing and empty amounts.
    """
    assert parse_amount("$462,024.00") == 462024.0
    assert parse_amount("") is None


def test_parse_page_and_recipient():
    """
    Tests parsing of research-call and organization grants.
    """
    page = "header" + fli_block(
        "Nuclear winter", "$500,000.00", "<span>Alan Robock</span>, Rutgers"
    )
    page += fli_block("CSER", "$1,000.00")
    grants = parse_page(page)
    assert [g["amount_usd"] for g in grants] == [500000.0, 1000.0]
    assert recipient_name(grants[0]) == "Rutgers"
    assert recipient_name(grants[1]) == "CSER"
    assert "<div" not in grants[0]["summary"]
