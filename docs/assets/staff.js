// Staff page: people on archived team pages, added up by function and focus,
// or shown per organization. No names are shown; they are in the repository.

const FUNCTIONS = ["Research", "Teaching", "Policy", "Operations"];
const ORG_TYPES = ["Research orgs", "Teaching orgs", "Policy orgs"];
const FOCI = ["Classic or multi-hazard", "AI or bio"];
const FOCUS_TITLE = {
  "Classic or multi-hazard": "GCR organizations working on classic or several risks",
  "AI or bio": "GCR organizations working mainly on AI or bio",
};
const YEARS = { from: 2015, to: PARTIAL_YEAR };
const TOTALS_TO = PARTIAL_YEAR;
const NOTES = {
  allfed: "The page shows names only (titles are on the profiles) and doesn't list volunteers. I took out people it still listed after they had left.",
  gcri: "Associates were listed until 2018. Dropping them in 2019 was a website change, not a cut.",
  fhi: "Closed on 16 April 2024, the 2024 count is from that day. Extra points are staff numbers from FHI's own reports.",
  cltr: "No usable team page, so these are average employees from the Companies House accounts.",
  beri: "The line is the core team. Extra points are staff BERI employs inside university groups, mostly on AI, as stated on its team page.",
  ero: "The page doesn't separate paid, part-time and volunteer staff.",
  cser: "Assistant professors for the MPhil and the postgraduate coordinator count as teaching.",
  xlab: "Director and deputy director count as teaching. Student associates aren't counted.",
  ceri_era: "Only one usable snapshot (2024). The research managers run the fellowship, so they count as teaching.",
  fernuni_erh: "Three funded positions in the new programme, from its website.",
};

const state = { view: "totals", types: [...ORG_TYPES], functions: [...FUNCTIONS], colour: "focus" };
let data, orgs;

const title = (s) => s.charAt(0).toUpperCase() + s.slice(1);
const typeLabel = (t) => `${title(t)} orgs`;
const shortName = (o) => o.name.replace(/\s*\(.*\)$/, "");

function selectedRows() {
  const allowed = new Set(orgs.filter((o) => state.types.includes(typeLabel(o.type))).map((o) => o.org_id));
  return data.functions.filter((r) => allowed.has(r.org_id) && state.functions.includes(r.function)
    && r.year >= YEARS.from && r.year <= YEARS.to);
}

function coverageText(rows) {
  const parts = FOCI.map((focus) => {
    const inFocus = orgs.filter((o) => o.focus === focus && rows.some((r) => r.org_id === o.org_id));
    const list = inFocus.map((o) => {
      const years = rows.filter((r) => r.org_id === o.org_id).map((r) => r.year);
      const from = d3.min(years), to = d3.max(years);
      return `${shortName(o)} (${from === to ? from : `${from}–${to}`})`;
    });
    return `${focus}: ${list.join(", ") || "none"}.`;
  });
  const assumed = [...new Set(rows.filter((r) => r.source.startsWith("assumed")).map((r) => r.org_id))]
    .map((id) => shortName(orgs.find((o) => o.org_id === id)));
  const end = assumed.length
    ? ` For ${assumed.join(", ")} I couldn't read a 2026 team page yet, so I assume their 2025 team stayed the same.`
    : "";
  return `Organizations counted and the years with a readable page. ${parts.join(" ")}${end}`;
}

function drawTotals(allRows) {
  const rows = allRows.filter((r) => r.year <= TOTALS_TO);
  const container = document.getElementById("multiples");
  container.innerHTML = "";
  container.className = "multiples two";
  const ymax = d3.max(d3.rollups(rows, (v) => d3.sum(v, (r) => r.people), (r) => r.focus, (r) => r.year)
    .flatMap(([, ys]) => ys.map(([, n]) => n))) || 1;
  FOCI.forEach((focus) => {
    const box = document.createElement("div");
    box.innerHTML = `<p class="chart-title">${FOCUS_TITLE[focus]}</p><div class="chart"></div>`;
    container.appendChild(box);
    const chartRows = rows.filter((r) => r.focus === focus)
      .map((r) => ({ year: r.year, key: r.function, value: r.people }));
    stackedBars(box.querySelector(".chart"), chartRows, state.functions,
      (k) => ENTITY_COLORS.function[k], {
        yearFrom: YEARS.from, yearTo: TOTALS_TO, format: fmtInt, width: 560, height: 320, right: 90,
        ymax, label: `People at ${focus.toLowerCase()} organizations by function`,
      });
  });
  legend(document.getElementById("legend"), state.functions, (k) => ENTITY_COLORS.function[k]);
}

function orgColour(o) {
  if (state.colour === "highlight") return o.focus === FOCI[0] ? COLORS.aubergine : COLORS.context;
  return ENTITY_COLORS.focus[o.focus];
}

function reportPoints(orgId) {
  return data.headcounts.filter((h) => h.org_id === orgId && ["fhi", "beri"].includes(orgId)
    && +h.year >= YEARS.from && +h.staff > 0)
    .map((h) => ({ year: +h.year, value: +h.staff, note: h.measure }));
}

function drawOrgs(rows) {
  const container = document.getElementById("multiples");
  container.innerHTML = "";
  container.className = "multiples";
  const perOrg = orgs.map((o) => {
    const points = d3.rollups(rows.filter((r) => r.org_id === o.org_id),
      (v) => ({ value: d3.sum(v, (r) => r.people), assumed: v.some((r) => r.source.startsWith("assumed")) }), (r) => r.year)
      .map(([year, p]) => ({ year, value: p.value, note: p.assumed ? "No readable page, assumed same as 2025" : "" }));
    return { org: o, points, reports: reportPoints(o.org_id) };
  }).filter((x) => x.points.length);
  perOrg.sort((a, b) => FOCI.indexOf(a.org.focus) - FOCI.indexOf(b.org.focus)
    || d3.max(b.points, (p) => p.value) - d3.max(a.points, (p) => p.value));
  const ymax = d3.max(perOrg, (x) => d3.max([...x.points, ...x.reports], (p) => p.value)) || 1;
  perOrg.forEach(({ org, points, reports }) => {
    const box = document.createElement("div");
    box.innerHTML = `<p class="chart-title">${shortName(org)}</p>` +
      `<p class="chart-sub">${org.focus} · ${org.type}. ${NOTES[org.org_id] || ""}</p><div class="chart"></div>`;
    container.appendChild(box);
    const fromFilings = rows.some((r) => r.org_id === org.org_id && r.source === "filings");
    const series = [{ points, color: orgColour(org), name: fromFilings ? "filings" : "team page", line: points.length > 1 }];
    if (reports.length) series.push({ points: reports, color: COLORS.berry, name: "own reports", line: false });
    smallLine(box.querySelector(".chart"), [], {
      yearFrom: YEARS.from, yearTo: YEARS.to, ymax, unit: "people", series,
      label: `People counted at ${shortName(org)}`,
    });
  });
  const keys = state.colour === "highlight" ? ["Classic or multi-hazard", "Other organizations"] : FOCI;
  const colourOf = (k) => (k === "Other organizations" ? COLORS.context : ENTITY_COLORS.focus[k]);
  legend(document.getElementById("legend"), [...keys, "Staff numbers from own reports"],
    (k) => (k.startsWith("Staff numbers") ? COLORS.berry : colourOf(k)));
}

function draw() {
  const rows = selectedRows();
  document.getElementById("c-colour-box").hidden = state.view !== "orgs";
  if (state.view === "totals") drawTotals(rows); else drawOrgs(rows);
  document.getElementById("coverage").textContent = coverageText(rows);
}

async function init() {
  data = await loadJSON("staff.json");
  data.functions = data.functions.map((r) => ({ ...r, function: title(r.function), focus: title(r.focus) }));
  orgs = data.organizations.filter((o) => o.type).map((o) => ({ ...o, focus: title(o.focus) }));
  segmented(document.getElementById("c-view"), [["totals", "Totals by function"], ["orgs", "Show all organizations"]],
    state.view, (v) => { state.view = v; draw(); });
  segmented(document.getElementById("c-colour"), [["focus", "By focus"], ["highlight", "Highlight classic"]],
    state.colour, (v) => { state.colour = v; draw(); });
  checkboxes(document.getElementById("f-types"), ORG_TYPES, state.types, (v) => { state.types = v; draw(); });
  checkboxes(document.getElementById("f-functions"), FUNCTIONS, state.functions, (v) => { state.functions = v; draw(); });
  draw();
}

init();
