from src.wayback import closest_to_midyear, parse_cdx

CDX = """20190105000000 https://a.org/team/ 200
20190702120000 https://a.org/team/ 200
20191230000000 https://a.org/team/ 200
20200301000000 https://a.org/team/ 404
bad line
"""


def test_parse_cdx_keeps_only_http_200():
    """
    Tests that only successful captures are kept and bad lines skipped.
    """
    rows = parse_cdx(CDX)
    assert len(rows) == 3
    assert rows[0] == ("20190105000000", "https://a.org/team/")


def test_closest_to_midyear():
    """
    Tests that the capture closest to 1 July is chosen, None for empty years.
    """
    rows = parse_cdx(CDX)
    assert closest_to_midyear(rows, 2019)[0] == "20190702120000"
    assert closest_to_midyear(rows, 2020) is None


def test_decode_body_handles_gzip_and_plain():
    """
    Tests that gzip bodies are decompressed and plain bodies decoded.
    """
    import gzip

    from src.wayback import decode_body

    assert decode_body(gzip.compress(b"<html>x</html>")) == "<html>x</html>"
    assert decode_body(b"<p>y</p>") == "<p>y</p>"
