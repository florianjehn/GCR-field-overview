// Staff page: people on archived team pages of the GCR organizations that work
// on classic or several risks, added up by function or by organization, or shown per organization.
// No names are shown; they are in the repository.

const FUNCTIONS = ["Research", "Teaching", "Policy", "Operations"];
const ORG_TYPES = ["Research orgs", "Teaching orgs", "Policy orgs"];
const FOCUS = "Classic or multi-hazard";
const YEARS = { from: 2015, to: PARTIAL_YEAR };
const NOTES = {
  allfed: "The page shows names only (titles are on the profiles) and doesn't list volunteers. I took out people it still listed after they had left.",
  gcri: "Associates were listed until 2018. Dropping them in 2019 was a website change, not a cut.",
  fhi: "Closed on 16 April 2024, the 2024 count is from that day. Extra points are staff numbers from FHI's own reports.",
  beri: "The line is the core team. Extra points are staff BERI employs inside university groups, mostly on AI, as stated on its team page.",
  cser: "Assistant professors for the MPhil and the postgraduate coordinator count as teaching. Researchers who mainly work on AI or bio aren't counted.",
  xlab: "Director and deputy director count as teaching. Student associates aren't counted.",
  fernuni_erh: "Three funded positions in the new programme, from its website.",
  gpi: "Closed at the end of July 2025. Board, affiliates and DPhil scholars aren't counted.",
  odyssean: "People who mainly work on AI (the AI safety lead) aren't counted.",
  adapt: "A one-person research consultancy (Matt Boyd). Counted from 2020, when the About page starts naming global catastrophic risk.",
  seri: "Only one archived staff page (2026): the faculty director, who teaches the course on preventing human extinction, and an operations manager.",
  rcg: "Now called ORCG. Archived team pages only exist for 2023 and 2026, so 2024 and 2025 assume the 2023 team.",
};

const state = { view: "totals", types: [...ORG_TYPES], functions: [...FUNCTIONS] };
let data, orgs;

const title = (s) => s.charAt(0).toUpperCase() + s.slice(1);
const typeLabel = (t) => `${title(t)} orgs`;
const shortName = (o) => o.name.replace(/\s*\(.*\)$/, "");
const colourOf = (k) => ENTITY_COLORS.function[k];

function selectedRows() {
  const allowed = new Set(orgs.filter((o) => state.types.includes(typeLabel(o.type))).map((o) => o.org_id));
  return data.functions.filter((r) => allowed.has(r.org_id) && r.focus === FOCUS
    && state.functions.includes(r.function) && r.year >= YEARS.from && r.year <= YEARS.to);
}

function coverageText(rows) {
  const list = orgs.filter((o) => rows.some((r) => r.org_id === o.org_id)).map((o) => {
    const years = rows.filter((r) => r.org_id === o.org_id).map((r) => r.year);
    const from = d3.min(years), to = d3.max(years);
    return `${shortName(o)} (${from === to ? from : `${from}–${to}`})`;
  });
  const assumed = [...new Set(rows.filter((r) => r.source.startsWith("assumed")).map((r) => r.org_id))]
    .map((id) => shortName(orgs.find((o) => o.org_id === id)));
  const end = assumed.length
    ? ` For ${assumed.join(", ")} some years have no readable team page, so I assume the team stayed the same as in the last readable year.`
    : "";
  return `Organizations counted and the years with data: ${list.join(", ")}.${end}`;
}

function drawTotals(rows) {
  const container = document.getElementById("multiples");
  container.innerHTML = "";
  container.className = "chart";
  const chartRows = rows.map((r) => ({ year: r.year, key: r.function, value: r.people }));
  stackedBars(container, chartRows, state.functions, colourOf, {
    yearFrom: YEARS.from, yearTo: YEARS.to, format: fmtInt, height: 340,
    label: "People at GCR organizations working on classic or several risks, by function",
  });
  legend(document.getElementById("legend"), keysWithData(state.functions, chartRows), colourOf);
}

// Fixed colour per organization for the biggest ones; the rest share one grey.
const ORG_COLORS = {
  fhi: COLORS.aubergine, cser: COLORS.slate, allfed: COLORS.sage, gpi: COLORS.ochre, global_shield: COLORS.rose,
};
const OTHER_ORGS = "Other organizations";
const orgKey = (id) => (ORG_COLORS[id] ? shortName(orgs.find((o) => o.org_id === id)) : OTHER_ORGS);

function drawOrgTotals(rows) {
  const container = document.getElementById("multiples");
  container.innerHTML = "";
  container.className = "chart";
  const chartRows = rows.map((r) => ({ year: r.year, key: orgKey(r.org_id), value: r.people }));
  const keys = keysWithData([...Object.keys(ORG_COLORS).map(orgKey), OTHER_ORGS], chartRows);
  const colourOfOrg = (k) => {
    const id = Object.keys(ORG_COLORS).find((i) => orgKey(i) === k);
    return id ? ORG_COLORS[id] : COLORS.context;
  };
  stackedBars(container, chartRows, keys, colourOfOrg, {
    yearFrom: YEARS.from, yearTo: YEARS.to, format: fmtInt, height: 340,
    label: "People at GCR organizations working on classic or several risks, by organization",
  });
  const small = orgs.filter((o) => !ORG_COLORS[o.org_id] && rows.some((r) => r.org_id === o.org_id)).map(shortName);
  legend(document.getElementById("legend"), keys, colourOfOrg);
  document.getElementById("org-note").textContent = small.length
    ? `${OTHER_ORGS}: ${small.join(", ")}.` : "";
}

function reportPoints(orgId) {
  return data.headcounts.filter((h) => h.org_id === orgId && ["fhi", "beri"].includes(orgId)
    && +h.year >= YEARS.from && +h.staff > 0)
    .map((h) => ({ year: +h.year, value: +h.staff, note: h.measure }));
}

function orgPoints(rows, orgId) {
  return d3.rollups(rows.filter((r) => r.org_id === orgId),
    (v) => ({ value: d3.sum(v, (r) => r.people), assumed: v.some((r) => r.source.startsWith("assumed")) }), (r) => r.year)
    .map(([year, p]) => ({ year, value: p.value, note: p.assumed ? "No readable page, assumed same as the last readable year" : "" }));
}

function drawOrgs(rows) {
  const container = document.getElementById("multiples");
  container.innerHTML = "";
  container.className = "multiples";
  const perOrg = orgs.map((o) => ({ org: o, points: orgPoints(rows, o.org_id), reports: reportPoints(o.org_id) }))
    .filter((x) => x.points.length)
    .sort((a, b) => d3.max(b.points, (p) => p.value) - d3.max(a.points, (p) => p.value));
  const ymax = d3.max(perOrg, (x) => d3.max([...x.points, ...x.reports], (p) => p.value)) || 1;
  perOrg.forEach(({ org, points, reports }) => {
    const box = document.createElement("div");
    box.innerHTML = `<p class="chart-title">${shortName(org)}</p>` +
      `<p class="chart-sub">${title(org.type)}. ${NOTES[org.org_id] || ""}</p><div class="chart"></div>`;
    container.appendChild(box);
    const fromFilings = rows.some((r) => r.org_id === org.org_id && r.source === "filings");
    const series = [{ points, color: COLORS.aubergine, name: fromFilings ? "website" : "team page", line: points.length > 1 }];
    if (reports.length) series.push({ points: reports, color: COLORS.berry, name: "own reports", line: false });
    smallLine(box.querySelector(".chart"), [], {
      yearFrom: YEARS.from, yearTo: YEARS.to, ymax, unit: "people", series,
      label: `People counted at ${shortName(org)}`,
    });
  });
  const keys = perOrg.some((x) => x.reports.length) ? ["People counted", "Staff numbers from own reports"] : ["People counted"];
  legend(document.getElementById("legend"), keys, (k) => (k === "People counted" ? COLORS.aubergine : COLORS.berry));
}

function draw() {
  const rows = selectedRows();
  document.getElementById("org-note").textContent = "";
  ({ totals: drawTotals, orgTotals: drawOrgTotals, orgs: drawOrgs })[state.view](rows);
  document.getElementById("coverage").textContent = coverageText(rows);
}

async function init() {
  data = await loadJSON("staff.json");
  data.functions = data.functions.map((r) => ({ ...r, function: title(r.function), focus: title(r.focus) }));
  orgs = data.organizations.filter((o) => o.type && title(o.focus) === FOCUS);
  segmented(document.getElementById("c-view"), [["totals", "Totals by function"], ["orgTotals", "Totals by organization"], ["orgs", "Show all organizations"]],
    state.view, (v) => { state.view = v; draw(); });
  checkboxes(document.getElementById("f-types"), ORG_TYPES, state.types, (v) => { state.types = v; draw(); });
  checkboxes(document.getElementById("f-functions"), FUNCTIONS, state.functions, (v) => { state.functions = v; draw(); });
  exportButton(document.getElementById("export-chart"),
    () => [document.getElementById("legend"), document.getElementById("multiples"), document.getElementById("org-note")], "gcr-staff.png");
  draw();
}

init();
