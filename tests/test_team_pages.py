from src.team_pages import (
    clean_name,
    clean_text,
    extract_people,
    looks_like_name,
    slug_to_name,
    slugify,
)

LINK_PAGE = """
<h2>Research Staff</h2>
<h2><a href="/team/anders-sandberg/">Anders Sandberg</a></h2>
<p><a href="/team/toby-ord/">Show More &gt;</a></p>
<h2>Research Associates</h2>
<a href="/team/carl-shulman/"><h4>Carl Shulman</h4><p>Associate</p></a>
<a href="/team/anders-sandberg/">Anders Sandberg</a>
<a href="/about/">About</a>
"""

ELEMENT_PAGE = """
<p><strong>Leadership Team</strong></p>
<p><strong><a href="x">Seth Baum, Ph.D.</a></strong><br /><em>Director</em></p>
<p><strong>Staff</strong></p>
<p><a href="y"><strong>Andrea Owe, M.Phil.</strong></a><br /></p>
"""


def test_clean_name_removes_degrees_and_notes():
    """
    Tests removal of degrees, titles and bracketed notes.
    """
    assert clean_name("Seth Baum, Ph.D.") == "Seth Baum"
    assert clean_name("Andrew Critch (~1 hour/week)") == "Andrew Critch"
    assert clean_name("Dr. Jane Doe") == "Jane Doe"
    assert clean_name("Assoc Prof William MacAskill") == "William MacAskill"
    assert clean_name("Mr Luke Muehlhauser") == "Luke Muehlhauser"


def test_slug_helpers():
    """
    Tests slug creation and slug-to-name conversion.
    """
    assert slugify("Seán Ó hÉigeartaigh") == "se-n-h-igeartaigh"
    assert slug_to_name("anders-sandberg-2") == "Anders Sandberg"


def test_extract_people_link_mode():
    """
    Tests sections, name headings, generic links and de-duplication.
    """
    people = extract_people(LINK_PAGE, r"/team/([a-z0-9\-]+)/?$")
    names = [(p["section"], p["name"]) for p in people]
    assert names == [
        ("Research Staff", "Anders Sandberg"),
        ("Research Staff", "Toby Ord"),
        ("Research Associates", "Carl Shulman"),
    ]
    assert people[2]["title"] == "Associate"


def test_extract_people_element_mode_skips_section_labels():
    """
    Tests that bold section labels are not counted as people.
    """
    people = extract_people(
        ELEMENT_PAGE,
        r"<strong>((?:(?!</strong>).)*?)</strong>",
        "element",
        r"<p>\s*<strong>([^<]*)</strong>\s*</p>",
    )
    assert [(p["section"], p["name"]) for p in people] == [
        ("Leadership Team", "Seth Baum"),
        ("Staff", "Andrea Owe"),
    ]


def test_extract_people_skips_vacant_positions():
    """
    Tests that a vacant position listed like a person is skipped.
    """
    page = '<h3>Staff</h3><a href="/team/director-vacant/">Director (Vacant)</a>'
    assert extract_people(page, r"/team/([a-z\-]+)/?$") == []


def test_extract_people_optional_title_group():
    """
    Tests that an optional title group that does not match gives an empty title.
    """
    page = (
        "<h2>Core</h2><b><a href='x'>Max Tegmark</a>, Professor, MIT</b>"
        "<b>Lucas Perry</b>"
    )
    pattern = (
        r"<b>\s*(?:<a [^>]*>)?\s*([^<,]{3,40}?)\s*(?:</a>)?\s*"
        r"(?:,\s*([^<]*))?</b>"
    )
    people = extract_people(page, pattern, "element", r"<h2>(.*?)</h2>")
    assert [(p["name"], p["title"]) for p in people] == [
        ("Max Tegmark", "Professor, MIT"),
        ("Lucas Perry", ""),
    ]


def test_clean_text_strips_tags_and_entities():
    """
    Tests tag and entity removal and whitespace collapsing.
    """
    assert clean_text("<b>Jane</b>&nbsp;&amp;\n  Doe") == "Jane & Doe"


def test_looks_like_name():
    """
    Tests the loose name check used by the name filter.
    """
    assert looks_like_name("Jane Doe")
    assert not looks_like_name("Jane")
    assert not looks_like_name("Room 101 Main")
