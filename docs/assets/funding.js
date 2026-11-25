// Funding page: stacked bars by year, split and filtered by funder, topic and kind.

const TOPIC_OF = {
  "Classic GCR": "Classic GCR", "AI": "AI", "Bio": "Bio", "General x-risk": "General x-risk",
  "Geoengineering": "Climate & geoengineering", "Climate": "Climate & geoengineering",
  "Forecasting": "Forecasting", "EA & community": "EA & community",
  "Unknown": "Other", "Not GCR": "Other",
};
const GCR_CATEGORIES = ["Classic GCR", "AI", "Bio", "General x-risk", "Geoengineering", "Climate", "Forecasting", "Unknown"];
const TOPICS = ["Classic GCR", "AI", "Bio", "General x-risk", "Climate & geoengineering", "Forecasting", "EA & community", "Other"];
const GCR_TOPICS = TOPICS.filter((t) => t !== "EA & community");
const FUNDERS = ["Coefficient Giving", "SFF", "LTFF", "FLI"];
const KINDS = ["Research", "Policy & advocacy", "Field-building & education", "Other", "Unknown/not assessed"];
const PRESETS = {
  classic: { label: "Classic GCR", topics: ["Classic GCR"], wider: false },
  classicGeneral: { label: "Classic + general x-risk", topics: ["Classic GCR", "General x-risk"], wider: false },
  gcr: { label: "All GCR topics (incl. AI + bio)", topics: GCR_TOPICS, wider: false },
  all: { label: "Everything incl. EA & not GCR", topics: TOPICS, wider: true },
};

const state = {
  split: "funder", display: "amount", funders: [...FUNDERS], topics: ["Classic GCR"],
  kinds: [...KINDS], yearFrom: 2015, yearTo: PARTIAL_YEAR, wider: false,
};
let grants = [];

function kindOf(g) { return g.activity === "n/a" || g.activity === "Unknown" ? "Unknown/not assessed" : g.activity; }
function splitKey(g) {
  if (state.split === "funder") return g.funder;
  if (state.split === "topic") return g.topic;
  return g.kind;
}
function splitKeys() {
  if (state.split === "funder") return FUNDERS;
  if (state.split === "topic") return TOPICS;
  return KINDS;
}
function colorOf(k) {
  const map = state.split === "funder" ? ENTITY_COLORS.funder
    : state.split === "topic" ? ENTITY_COLORS.topic : ENTITY_COLORS.activity;
  return map[k] || COLORS.context;
}

function filtered() {
  return grants.filter((g) =>
    (state.wider || GCR_CATEGORIES.includes(g.category)) &&
    state.funders.includes(g.funder) && state.topics.includes(g.topic) &&
    state.kinds.includes(g.kind) && g.year >= state.yearFrom && g.year <= state.yearTo);
}

function gcrTotals(yearTo) {
  const inYears = grants.filter((g) => g.year >= state.yearFrom && g.year <= yearTo && GCR_CATEGORIES.includes(g.category));
  return {
    all: d3.sum(inYears, (g) => g.amount),
    classic: d3.sum(inYears.filter((g) => g.topic === "Classic GCR"), (g) => g.amount),
  };
}

function summary(rows) {
  const total = d3.sum(rows, (g) => g.amount);
  const t = gcrTotals(state.yearTo);
  const years = `${state.yearFrom}–${state.yearTo}`;
  let text = `What you selected adds up to <span class="figure">${fmtMoney(total)}</span> in ${years}. ` +
    `For comparison, classic GCR got ${fmtMoney(t.classic)} of the ${fmtMoney(t.all)} that went ` +
    `to GCR topics in these years (${fmtPct(t.classic / t.all)}).`;
  if (state.yearTo >= PARTIAL_YEAR && state.yearFrom < PARTIAL_YEAR) {
    const full = gcrTotals(PARTIAL_YEAR - 1);
    const partial = d3.sum(rows.filter((g) => g.year === PARTIAL_YEAR), (g) => g.amount);
    text += ` 2026 isn't over yet. Up to ${PARTIAL_YEAR - 1} only, your selection is ${fmtMoney(total - partial)}, ` +
      `and classic GCR got ${fmtMoney(full.classic)} of ${fmtMoney(full.all)} (${fmtPct(full.classic / full.all)})` +
      (state.yearFrom === 2015 ? ", the numbers on the overview page." : ".");
  }
  document.getElementById("summary").innerHTML = text;
}

function draw() {
  const rows = filtered();
  const keys = splitKeys();
  const chartRows = rows.map((g) => ({ year: g.year, key: splitKey(g), value: g.amount }));
  stackedBars(document.getElementById("chart"), chartRows, keys, colorOf, {
    yearFrom: state.yearFrom, yearTo: state.yearTo, percent: state.display === "share",
    label: "Funding per year",
  });
  legend(document.getElementById("legend"), keys, colorOf);
  summary(rows);
  renderTable(document.getElementById("table"), rows, [
    { key: "year", label: "Year", num: true },
    { key: "funder", label: "Funder" },
    { key: "recipient", label: "Recipient", link: "source_url" },
    { key: "description", label: "Grant" },
    { key: "category", label: "Topic" },
    { key: "kind", label: "Kind" },
    { key: "amount", label: "Amount", num: true, format: (v, r) => fmtMoney(v) + (r.split ? "*" : "") },
    { key: "coding_source", label: "Topic coded by" },
  ], { sortKey: "amount" });
}

function syncControls() {
  checkboxes(document.getElementById("f-funders"), FUNDERS, state.funders, (v) => { state.funders = v; draw(); });
  checkboxes(document.getElementById("f-topics"), TOPICS, state.topics, (v) => { state.topics = v; draw(); });
  checkboxes(document.getElementById("f-kinds"), KINDS, state.kinds, (v) => { state.kinds = v; draw(); });
}

async function init() {
  const raw = await loadJSON("funding.json");
  grants = raw.map((g) => ({ ...g, topic: TOPIC_OF[g.category] || "Other", kind: kindOf(g) }))
    .filter((g) => g.category !== "Regrant" && g.category !== "Duplicate");
  segmented(document.getElementById("c-preset"), Object.entries(PRESETS).map(([k, p]) => [k, p.label]), "classic", (k) => {
    state.topics = [...PRESETS[k].topics];
    state.wider = PRESETS[k].wider;
    if (k !== "classic" && state.split === "funder") state.split = "topic";
    segmented(document.getElementById("c-split"), [["funder", "Funder"], ["topic", "Topic"], ["activity", "Kind"]], state.split, onSplit);
    syncControls();
    draw();
  });
  const onSplit = (v) => { state.split = v; draw(); };
  segmented(document.getElementById("c-split"), [["funder", "Funder"], ["topic", "Topic"], ["activity", "Kind"]], state.split, onSplit);
  segmented(document.getElementById("c-display"), [["amount", "USD"], ["share", "Share"]], state.display, (v) => { state.display = v; draw(); });
  const from = document.getElementById("f-from"), to = document.getElementById("f-to");
  from.value = state.yearFrom; to.value = state.yearTo;
  from.addEventListener("change", () => { state.yearFrom = +from.value; draw(); });
  to.addEventListener("change", () => { state.yearTo = +to.value; draw(); });
  syncControls();
  draw();
}

init();
