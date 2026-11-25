"""
Find and download yearly Wayback Machine snapshots of web pages.

One snapshot per calendar year is chosen: the successful (HTTP 200) capture
closest to 1 July. Raw page HTML (the "id_" variant, without the Wayback
toolbar) is cached in data/raw/wayback/<org_id>/<timestamp>.html so repeated
runs do not hit the archive again. The archive is sometimes temporarily
offline, so requests are retried with a pause.
"""

import gzip
import time
import urllib.parse
import urllib.request
from pathlib import Path

CDX_URL = "https://web.archive.org/cdx/search/cdx"
SNAPSHOT_URL = "https://web.archive.org/web/{timestamp}id_/{url}"
VIEW_URL = "https://web.archive.org/web/{timestamp}/{url}"
CACHE_DIR = Path("data/raw/wayback")
OFFLINE_MARKER = "Temporarily Offline"


def http_get(url, retries=5, pause=20, timeout=90):
    """
    Downloads a URL as text, retrying when the archive is offline or slow.

    Arguments:
        url (str): the URL
        retries (int): number of attempts
        pause (int): seconds between attempts
        timeout (int): seconds per attempt

    Returns:
        str: the response body.
    """
    for attempt in range(retries):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(request, timeout=timeout) as response:
                body = decode_body(response.read())
            if OFFLINE_MARKER not in body[:2000]:
                return body
            print(f"  archive offline (attempt {attempt + 1})")
        except OSError as error:
            print(f"  {error} (attempt {attempt + 1})")
        time.sleep(pause)
    raise RuntimeError(f"Failed to download {url}")


def decode_body(raw):
    """
    Decodes a response body, decompressing it if it is gzip data.

    Arguments:
        raw (bytes): the raw response body

    Returns:
        str: the decoded text.
    """
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return raw.decode("utf-8", errors="replace")


def parse_cdx(text):
    """
    Parses CDX output lines "timestamp original statuscode".

    Arguments:
        text (str): CDX response body

    Returns:
        list: (timestamp, original url) tuples for HTTP 200 captures.
    """
    rows = []
    for line in text.strip().splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[2] == "200" and parts[0].isdigit():
            rows.append((parts[0], parts[1]))
    return rows


def list_captures(url):
    """
    Lists all successful captures of one exact URL.

    Arguments:
        url (str): the page URL (without scheme is fine)

    Returns:
        list: (timestamp, original url) tuples.
    """
    query = urllib.parse.urlencode(
        {"url": url, "fl": "timestamp,original,statuscode", "filter": "statuscode:200"}
    )
    return parse_cdx(http_get(f"{CDX_URL}?{query}"))


def closest_to_midyear(captures, year):
    """
    Picks the capture of a given year closest to 1 July.

    Arguments:
        captures (list): (timestamp, url) tuples
        year (int): the calendar year

    Returns:
        tuple or None: the chosen (timestamp, url), None if the year has none.
    """
    in_year = [c for c in captures if c[0].startswith(str(year))]
    if not in_year:
        return None
    target = int(f"{year}0701000000")
    return min(in_year, key=lambda capture: abs(int(capture[0][:14]) - target))


def yearly_snapshots(url, years):
    """
    Chooses one capture per year for a URL.

    Arguments:
        url (str): the page URL
        years (iterable): calendar years

    Returns:
        dict: year -> (timestamp, original url) for years with a capture.
    """
    captures = list_captures(url)
    chosen = {year: closest_to_midyear(captures, year) for year in years}
    return {year: capture for year, capture in chosen.items() if capture}


def fetch_snapshot(org_id, timestamp, url):
    """
    Downloads (or reads from cache) the raw HTML of one capture.

    Arguments:
        org_id (str): organization id, used as cache folder
        timestamp (str): Wayback timestamp
        url (str): original URL

    Returns:
        str: the page HTML.
    """
    path = CACHE_DIR / org_id / f"{timestamp}.html"
    if path.exists():
        return path.read_text()
    html = http_get(SNAPSHOT_URL.format(timestamp=timestamp, url=url))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html)
    time.sleep(6)
    return html
