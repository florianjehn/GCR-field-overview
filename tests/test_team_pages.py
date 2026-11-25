from src.team_pages import clean_name, extract_people, slug_to_name, slugify

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
