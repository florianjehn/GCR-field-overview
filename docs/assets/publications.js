// Publications page: OpenAlex works mentioning "global catastrophic risk".

const SCOPES = { title_abstract: "In title or abstract", fulltext: "Anywhere incl. full text" };
const GROUPS = {
  classic: { label: "Classic hazards", tags: ["nuclear", "volcanic", "space", "food"], color: COLORS.aubergine },
  AI: { label: "AI", tags: ["AI"], color: COLORS.slate },
  bio: { label: "Bio", tags: ["bio"], color: COLORS.rose },
  climate: { label: "Climate", tags: ["climate"], color: COLORS.ochre },
};
const state = { topic: "classic", metric: "works", yearFrom: 2008, yearTo: 2026 };
let data;

function mentions(work, group) {
  const tags = (work.topics || "").split(";");
  return GROUPS[group].tags.some((t) => tags.includes(t));
}

function selected(scope) {
  return data.works.filter((w) => w.scope === scope && w.year >= state.yearFrom && w.year <= state.yearTo &&
    (state.topic === "all" || mentions(w, state.topic)));
}

function drawCounts() {
  const box = document.getElementById("counts");
  box.innerHTML = "";
  const useAuthors = state.metric === "authors" && state.topic === "all";
  document.getElementById("metric-note").textContent = state.metric === "authors" && state.topic !== "all"
    ? "Unique authors are only available for all works; showing works instead." : "";
  Object.entries(SCOPES).forEach(([scope, label]) => {
    const div = document.createElement("div");
    div.innerHTML = `<p class="chart-title">${label}</p><div class="chart"></div>`;
    box.appendChild(div);
    const rows = useAuthors
      ? data.by_year.filter((r) => r.scope === scope).map((r) => ({ year: r.year, key: "Unique authors", value: r.unique_authors }))
      : selected(scope).map((w) => ({ year: w.year, key: "Works", value: 1 }));
    stackedBars(div.querySelector(".chart"), rows, [useAuthors ? "Unique authors" : "Works"],
      () => (state.topic === "all" ? COLORS.aubergine : GROUPS[state.topic].color),
      { yearFrom: state.yearFrom, yearTo: state.yearTo, width: 520, height: 300, format: fmtInt, label: `${label} per year` });
  });
}

function drawShares() {
  const box = document.getElementById("shares");
  box.innerHTML = "";
  Object.entries(SCOPES).forEach(([scope, label]) => {
    const div = document.createElement("div");
    div.innerHTML = `<p class="chart-title">${label}</p><div class="chart"></div>`;
    box.appendChild(div);
    const works = data.works.filter((w) => w.scope === scope && w.year >= 2010 && w.year <= state.yearTo);
    const years = d3.range(2010, state.yearTo + 1);
    const series = Object.entries(GROUPS).map(([key, g]) => ({
      name: g.label, color: g.color,
      points: years.map((year) => {
        const inWindow = works.filter((w) => Math.abs(w.year - year) <= 1);
        return { year, value: inWindow.length ? Math.round(100 * inWindow.filter((w) => mentions(w, key)).length / inWindow.length) : null };
      }),
    }));
    smallLine(div.querySelector(".chart"), [], { yearFrom: 2010, yearTo: state.yearTo, ymax: 60, width: 520, height: 260, unit: "% of works", series, label: `Topic shares, ${label}` });
  });
}

function drawTable() {
  const rows = Object.keys(SCOPES).flatMap((s) => selected(s)).map((w) => ({ ...w, scopeLabel: SCOPES[w.scope] }));
  const seen = new Set();
  const unique = rows.filter((r) => (seen.has(r.url) ? false : seen.add(r.url)));
  renderTable(document.getElementById("table"), unique, [
    { key: "year", label: "Year", num: true },
    { key: "title", label: "Title", link: "url" },
    { key: "source", label: "Venue" },
    { key: "type", label: "Type" },
    { key: "n_authors", label: "Authors", num: true },
    { key: "cited_by", label: "Cited by", num: true },
    { key: "topics", label: "Mentions", format: (v) => (v || "").replaceAll(";", ", ") },
    { key: "scopeLabel", label: "Found" },
  ], { sortKey: "cited_by" });
}

function draw() { drawCounts(); drawShares(); drawTable(); }

async function init() {
  data = await loadJSON("publications.json");
  segmented(document.getElementById("c-topic"),
    [["classic", "Classic hazards"], ["all", "All works"], ["AI", "AI"], ["bio", "Bio"], ["climate", "Climate"]],
    state.topic, (v) => { state.topic = v; draw(); });
  segmented(document.getElementById("c-metric"), [["works", "Works"], ["authors", "Unique authors"]], state.metric,
    (v) => { state.metric = v; drawCounts(); });
  draw();
}

init();
