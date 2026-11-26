import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
import pytest  # noqa: E402

from src.scope_figure import (  # noqa: E402
    ASRIC,
    GROUPS,
    damped_sizes,
    draw_box,
    format_usd,
    group_totals,
    scope_figure,
    wrap_to_width,
)

LONG = pd.DataFrame(
    {
        "category": ["AI", "Climate", "Geoengineering", ASRIC, ASRIC, "Not GCR"],
        "award_year": [2020, 2020, 2021, 2015, 2026, 2020],
        "amount_usd_share": [100.0, 3.0, 4.0, 10.0, 99.0, 50.0],
    }
)


def test_group_totals_combines_categories_and_respects_years():
    """
    Tests that climate and geoengineering are added up and 2026 is left out.
    """
    totals = group_totals(LONG)
    assert totals["Climate & geoengineering"] == 7.0
    assert totals[ASRIC] == 10.0
    assert totals["AI"] == 100.0
    assert totals["Bio"] == 0.0


def test_groups_use_known_categories():
    """
    Tests that every figure group maps to categories used in the grant data.
    """
    known = {
        "AI",
        "Bio",
        ASRIC,
        "General x-risk",
        "Climate",
        "Geoengineering",
    }
    assert {c for cats in GROUPS.values() for c in cats} <= known


def test_format_usd():
    """
    Tests the short dollar format at different sizes.
    """
    assert format_usd(1.1e9) == "$1.1B"
    assert format_usd(330e6) == "$330M"
    assert format_usd(5.56e6) == "$5.6M"


def test_wrap_to_width_keeps_lines_inside_width():
    """
    Tests that every wrapped line fits the width it was wrapped to.
    """
    fig = plt.figure(figsize=(10, 6), layout=None)
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    text = wrap_to_width(ax, "one two three four five six seven eight nine ten", 15, 10)
    renderer = fig.canvas.get_renderer()
    for line in text.split("\n"):
        probe = ax.text(0, 0, line, fontsize=10)
        box = probe.get_window_extent(renderer).transformed(ax.transData.inverted())
        assert box.width <= 15
    assert len(text.split("\n")) > 1
    plt.close(fig)


def test_scope_figure_shows_groups_and_amounts():
    """
    Tests that the figure names each group with its amount and the umbrella total.
    """
    totals = dict.fromkeys(GROUPS, 1e6) | {"AI": 1.1e9}
    fig = scope_figure(totals)
    texts = " ".join(t.get_text().replace("\n", " ") for t in fig.axes[0].texts)
    assert "$1.1B" in texts
    assert "GCR outside AI and bio: $3.0M" in texts
    assert "Not counted" in texts
    plt.close(fig)


def test_damped_sizes_follow_values_by_square_root():
    """
    Tests that parts grow with the square root of their value and fill the total.
    """
    assert damped_sizes([400.0, 100.0], 30) == [20.0, 10.0]
    assert damped_sizes([0.0, 0.0], 10) == [5.0, 5.0]
    assert damped_sizes([9.0, 1.0], 8, exponent=1) == [7.2, 0.8]


def test_draw_box_refuses_text_that_overflows():
    """
    Tests that a box too small for its text raises instead of drawing over its
    neighbours.
    """
    fig = plt.figure(figsize=(10, 6), layout=None)
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    draw_box(ax, 0, 0, 30, 30, "#000000", "Title", "Short body")
    with pytest.raises(ValueError, match="Long"):
        draw_box(ax, 50, 0, 10, 8, "#000000", "Long", "word " * 40)
    plt.close(fig)


def test_scope_figure_fits_text_with_real_proportions():
    """
    Tests that the text fits every box at the 2015-2025 funding totals.
    """
    totals = {
        "AI": 1.1e9,
        "Bio": 330e6,
        ASRIC: 14e6,
        "General x-risk": 39e6,
        "Climate & geoengineering": 16e6,
    }
    plt.close(scope_figure(totals))
