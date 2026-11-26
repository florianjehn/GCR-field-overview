"""
Figure of what the funding categories cover and what is left out.

Shows GCR-framed work split into AI, Bio and "GCR outside AI and bio" (abrupt
sunlight reduction & infrastructure collapse, general x-risk, climate &
geoengineering), each with its 2015–2025 total from the four funders, and the
neighbouring fields that are not counted. Not used on the
website. Output: results/figures/scope_of_terms.png.

Run with:
    uv run python3 -m src.scope_figure
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Rectangle

PROCESSED_DIR = Path("data/processed")
FIGURE_PATH = Path("results/figures/scope_of_terms.png")
STYLE = "style/scientific_v2.mplstyle"
FIRST_YEAR, LAST_YEAR = 2015, 2025
ASRIC = "Abrupt sunlight reduction & infrastructure collapse"
# Figure group -> categories in data/processed/grants_by_category.csv.
GROUPS = {
    "AI": ["AI"],
    "Bio": ["Bio"],
    ASRIC: [ASRIC],
    "General x-risk": ["General x-risk"],
    "Climate & geoengineering": ["Climate", "Geoengineering"],
}
OUTSIDE = (ASRIC, "General x-risk", "Climate & geoengineering")
# Width of the "GCR outside AI and bio" box. Fixed rather than sized by
# funding: its parts carry the money, and they need room for their text.
OUTSIDE_WIDTH = 47.0
COLORS = {
    "AI": "#46708A",
    "Bio": "#CC8FA0",
    ASRIC: "#5D2A42",
    "General x-risk": "#627F64",
    "Climate & geoengineering": "#C9A55A",
    "outside": "#EFE7E9",
    "excluded": "#A29A97",
    "ink": "#2E2A2B",
    "muted": "#6E6668",
    "paper": "#F7F4EF",
}
EXAMPLES = {
    "AI": "AI safety, alignment and AI governance",
    "Bio": "Biosecurity and pandemic preparedness, incl. pandemics that "
    "disrupt infrastructure",
    ASRIC: "Nuclear winter, large volcanic eruptions, asteroid and comet "
    "impacts, severe space weather. Preventing them and keeping food and "
    "infrastructure running through them",
    "General x-risk": "Catastrophic or existential risk as a whole: "
    "multi-hazard institutes (FHI, CSER, GCRI), all-hazards policy "
    "(Global Shield), x-risk student programmes",
    "Climate & geoengineering": "Extreme climate change and solar "
    "geoengineering research and governance, when framed as GCR",
}
NOT_COUNTED = [
    "Mainstream climate science and policy",
    "Nuclear security and arms control outside a GCR framing",
    "Disaster risk reduction",
    "EA community building, longtermism and global priorities research",
    "Generic forecasting (platforms and research not tied to these risks)",
    "Everything else the funders support (e.g. global health, animal welfare)",
]


def group_totals(long, first=FIRST_YEAR, last=LAST_YEAR):
    """
    Sums the funding of each figure group in a year range.

    Arguments:
        long (pandas.DataFrame): grants_by_category rows with category,
            award_year and amount_usd_share
        first (int): first award year included
        last (int): last award year included

    Returns:
        dict: figure group -> USD.
    """
    in_years = long[long["award_year"].between(first, last)]
    by_category = in_years.groupby("category")["amount_usd_share"].sum()
    return {
        group: float(sum(by_category.get(c, 0.0) for c in categories))
        for group, categories in GROUPS.items()
    }


def format_usd(value):
    """
    Formats a dollar amount in short form, like the website.

    Arguments:
        value (float): amount in USD

    Returns:
        str: e.g. "$1.1B", "$330M", "$14M", "$5.6M".
    """
    if value >= 1e9:
        return f"${value / 1e9:.1f}B"
    if value >= 1e7:
        return f"${value / 1e6:.0f}M"
    return f"${value / 1e6:.1f}M"


def damped_sizes(values, total, exponent=0.5):
    """
    Splits a length so each part grows with its value, damped by an exponent
    (1 = proportional, 0.5 = square root, 0 = equal).

    Arguments:
        values (list of float): the amounts, e.g. USD
        total (float): the length to split
        exponent (float): damping exponent applied to the values

    Returns:
        list of float: the parts, in the order of values, summing to total.
    """
    weights = [max(v, 0.0) ** exponent for v in values]
    weight_sum = sum(weights)
    if weight_sum == 0:
        return [total / len(values)] * len(values)
    return [total * w / weight_sum for w in weights]


def wrap_to_width(ax, text, width, fontsize):
    """
    Wraps text so each line fits a width in data units, measured as rendered.
    Existing line breaks are kept.

    Arguments:
        ax (matplotlib.axes.Axes): axes the text will be drawn on
        text (str): the text
        width (float): available width in data units
        fontsize (float): font size in points

    Returns:
        str: the text with line breaks.
    """
    renderer = ax.figure.canvas.get_renderer()
    to_data = ax.transData.inverted()

    def fits(line):
        probe = ax.text(0, 0, line, fontsize=fontsize)
        box = probe.get_window_extent(renderer).transformed(to_data)
        probe.remove()
        return box.width <= width

    lines = []
    for paragraph in text.split("\n"):
        line = ""
        for word in paragraph.split():
            candidate = f"{line} {word}".strip()
            if line and not fits(candidate):
                lines.append(line)
                line = word
            else:
                line = candidate
        lines.append(line)
    return "\n".join(lines)


def draw_box(ax, x, y, w, h, color, title, body=None, dark=True):
    """
    Draws a filled box with a title and an optional description below it,
    both wrapped to the box width. Raises ValueError if the text runs out of
    the bottom of the box.

    Arguments:
        ax (matplotlib.axes.Axes): axes in data units 0-100
        x, y, w, h (float): lower left corner, width and height
        color (str): fill colour
        title (str): text at the top of the box
        body (str): optional text below the title
        dark (bool): light text on a dark fill if True

    Returns:
        None
    """
    ax.add_patch(Rectangle((x, y), w, h, facecolor=color, edgecolor="none"))
    ink = COLORS["paper"] if dark else COLORS["ink"]
    pad = 1.0
    head = ax.text(
        x + pad,
        y + h - 1.6,
        wrap_to_width(ax, title, w - 2 * pad, 10.5),
        color=ink,
        fontsize=10.5,
        va="top",
        ha="left",
        linespacing=1.2,
    )
    last = head
    if body:
        last = ax.text(
            x + pad,
            text_bottom(ax, head) - 1.8,
            wrap_to_width(ax, body, w - 2 * pad, 8),
            color=ink,
            fontsize=8,
            va="top",
            ha="left",
            linespacing=1.35,
        )
    if text_bottom(ax, last) < y + pad:
        raise ValueError(f"Text does not fit in the box {title.splitlines()[0]!r}")


def text_bottom(ax, text):
    """
    Measures the lower edge of a drawn text in data units.

    Arguments:
        ax (matplotlib.axes.Axes): axes the text is drawn on
        text (matplotlib.text.Text): the text

    Returns:
        float: y of the lower edge of the text.
    """
    renderer = ax.figure.canvas.get_renderer()
    return text.get_window_extent(renderer).transformed(ax.transData.inverted()).y0


def draw_outside_parts(ax, totals, x, y, w, h):
    """
    Draws the parts of GCR outside AI and bio: General x-risk in one column,
    the other two stacked in the second, all sized by their funding.

    Arguments:
        ax (matplotlib.axes.Axes): axes in data units 0-100
        totals (dict): figure group -> USD
        x, y, w, h (float): lower left corner, width and height of the area

    Returns:
        None
    """
    gap = 1.0
    stacked = [ASRIC, "Climate & geoengineering"]
    left_w, right_w = damped_sizes(
        [totals["General x-risk"], sum(totals[g] for g in stacked)],
        w - gap,
    )
    draw_box(
        ax,
        x,
        y,
        left_w,
        h,
        COLORS["General x-risk"],
        titled(totals, "General x-risk"),
        EXAMPLES["General x-risk"],
    )
    top_h, low_h = damped_sizes([totals[g] for g in stacked], h - gap)
    right_x = x + left_w + gap
    draw_box(
        ax,
        right_x,
        y + low_h + gap,
        right_w,
        top_h,
        COLORS[ASRIC],
        titled(totals, ASRIC),
        EXAMPLES[ASRIC],
    )
    draw_box(
        ax,
        right_x,
        y,
        right_w,
        low_h,
        COLORS["Climate & geoengineering"],
        titled(totals, "Climate & geoengineering"),
        EXAMPLES["Climate & geoengineering"],
        dark=False,
    )


def titled(totals, group):
    """
    Builds a box title from a group name and its funding.

    Arguments:
        totals (dict): figure group -> USD
        group (str): the figure group

    Returns:
        str: e.g. "AI\n$1.1B".
    """
    return f"{group}\n{format_usd(totals[group])}"


def scope_figure(totals):
    """
    Draws the scope figure.

    Arguments:
        totals (dict): figure group -> USD (from group_totals)

    Returns:
        matplotlib.figure.Figure: the figure.
    """
    plt.style.use(STYLE)
    # Fixed axes over the whole figure, so text measured while drawing keeps
    # its size (the style's constrained layout would resize the axes later).
    fig = plt.figure(figsize=(10, 6.6), layout=None)
    ax = fig.add_axes((0.01, 0.01, 0.98, 0.98))
    ax.set_xlim(0, 100)
    ax.set_ylim(5, 100)
    ax.set_axis_off()

    ax.text(
        0,
        99,
        "GCR-framed work: counted in the funding numbers (2015–2025, four funders)",
        fontsize=11,
        color=COLORS["muted"],
        va="top",
    )
    # Box sizes follow the money, damped (square root) so the small groups
    # still have room for their text.
    outside = sum(totals[g] for g in OUTSIDE)
    gap, bottom, height = 1.0, 32.0, 63.0
    out_w = OUTSIDE_WIDTH
    ai_w, bio_w = damped_sizes([totals["AI"], totals["Bio"]], 100 - 2 * gap - out_w)
    draw_box(
        ax, 0, bottom, ai_w, height, COLORS["AI"], titled(totals, "AI"), EXAMPLES["AI"]
    )
    bio_x = ai_w + gap
    draw_box(
        ax,
        bio_x,
        bottom,
        bio_w,
        height,
        COLORS["Bio"],
        titled(totals, "Bio"),
        EXAMPLES["Bio"],
    )
    out_x = bio_x + bio_w + gap
    draw_box(
        ax,
        out_x,
        bottom,
        out_w,
        height,
        COLORS["outside"],
        f"GCR outside AI and bio: {format_usd(outside)}",
        dark=False,
    )
    draw_outside_parts(
        ax, totals, out_x + gap, bottom + gap, out_w - 2 * gap, height - 9
    )
    ax.text(
        0,
        28,
        "Not counted: related work not framed as GCR, and everything else",
        fontsize=11,
        color=COLORS["muted"],
        va="top",
    )
    for i, item in enumerate(NOT_COUNTED):
        col, row = i % 2, i // 2
        y = 20 - row * 6.5
        ax.add_patch(Rectangle((col * 50, y), 1.4, 3, facecolor=COLORS["excluded"]))
        ax.text(
            col * 50 + 2.5, y + 1.5, item, fontsize=9, color=COLORS["ink"], va="center"
        )
    return fig


def main():
    """
    Builds the scope figure from the classified grants and saves it.

    Returns:
        None
    """
    long = pd.read_csv(PROCESSED_DIR / "grants_by_category.csv")
    totals = group_totals(long)
    for group, value in totals.items():
        print(f"{group}: {format_usd(value)}")
    FIGURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    scope_figure(totals).savefig(FIGURE_PATH)
    print(f"Wrote {FIGURE_PATH}")


if __name__ == "__main__":
    main()
