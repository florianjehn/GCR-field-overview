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
    both wrapped to the box width.

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
    if body:
        renderer = ax.figure.canvas.get_renderer()
        bottom = (
            head.get_window_extent(renderer).transformed(ax.transData.inverted()).y0
        )
        ax.text(
            x + pad,
            bottom - 1.8,
            wrap_to_width(ax, body, w - 2 * pad, 8),
            color=ink,
            fontsize=8,
            va="top",
            ha="left",
            linespacing=1.35,
        )


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
    fig = plt.figure(figsize=(10, 6.0), layout=None)
    ax = fig.add_axes((0.01, 0.01, 0.98, 0.98))
    ax.set_xlim(0, 100)
    ax.set_ylim(8, 100)
    ax.set_axis_off()

    def titled(group):
        return f"{group}\n{format_usd(totals[group])}"

    ax.text(
        0,
        99,
        "GCR-framed work: counted in the funding numbers (2015–2025, four funders)",
        fontsize=11,
        color=COLORS["muted"],
        va="top",
    )
    draw_box(ax, 0, 36, 21, 59, COLORS["AI"], titled("AI"), EXAMPLES["AI"])
    draw_box(ax, 22, 36, 21, 59, COLORS["Bio"], titled("Bio"), EXAMPLES["Bio"])
    outside = sum(
        totals[g] for g in (ASRIC, "General x-risk", "Climate & geoengineering")
    )
    draw_box(
        ax,
        44,
        36,
        56,
        59,
        COLORS["outside"],
        f"GCR outside AI and bio: {format_usd(outside)}",
        dark=False,
    )
    draw_box(ax, 45, 37, 26.5, 50, COLORS[ASRIC], titled(ASRIC), EXAMPLES[ASRIC])
    draw_box(
        ax,
        72.5,
        62.5,
        26.5,
        24.5,
        COLORS["General x-risk"],
        titled("General x-risk"),
        EXAMPLES["General x-risk"],
    )
    draw_box(
        ax,
        72.5,
        37,
        26.5,
        24.5,
        COLORS["Climate & geoengineering"],
        titled("Climate & geoengineering"),
        EXAMPLES["Climate & geoengineering"],
        dark=False,
    )

    ax.text(
        0,
        31,
        "Not counted: related work not framed as GCR, and everything else",
        fontsize=11,
        color=COLORS["muted"],
        va="top",
    )
    for i, item in enumerate(NOT_COUNTED):
        col, row = i % 2, i // 2
        y = 23 - row * 6.5
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
