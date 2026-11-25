// Staff page: people listed on archived team pages, one small chart per organization.

const DEFAULT_ORGS = ["cser", "gcri", "allfed", "fhi", "beri", "global_shield"];
const ROLES = ["staff", "scholar", "student", "volunteer", "affiliate", "board", "alumni"];
const NOTES = {
  allfed: "From 2021 the team page lists no job titles, so paid staff, part-timers and volunteers can't be told apart.",
  gcri: "Associates were listed until 2018 only; their removal in 2019 is a website change, not a cut.",
  fhi: "Closed 16 April 2024. Scholars are two-year paid research positions.",
  cltr: "No usable team page; line shows average employees from Companies House accounts.",
  beri: "BERI also employs staff embedded in university groups, mostly AI. 2025-26 page not yet parsed.",
  ero: "Team page does not separate paid, part-time and volunteer staff.",
};

const state = { orgs: [...DEFAULT_ORGS], roles: ["staff"], year: null };
let data;

function orgName(id) {
  const org = data.organizations.find((o) => o.org_id === id);
  return org ? org.name.replace(/\s*\(.*\)$/, "") : id;
}

function counts(orgId) {
  const rows = data.people.filter((p) => p.org_id === orgId && state.roles.includes(p.role));
  const years = [...new Set(data.people.filter((p) => p.org_id === orgId).map((p) => p.year))];
  return years.map((year) => ({ year, value: rows.filter((r) => r.year === year).length }));
}

function documented(orgId) {
  return data.headcounts.filter((h) => h.org_id === orgId && +h.year >= 2015)
    .map((h) => ({ year: +h.year, value: +h.staff, note: h.measure }));
}

function draw() {
  const container = document.getElementById("multiples");
  container.innerHTML = "";
  const all = state.orgs.map((id) => ({ id, team: counts(id), doc: documented(id) }));
  const ymax = d3.max(all, (o) => d3.max([...o.team, ...o.doc], (p) => p.value)) || 1;
  all.forEach((o) => {
    const box = document.createElement("div");
    box.innerHTML = `<p class="chart-title">${orgName(o.id)}</p>` +
      `<p class="chart-sub">${NOTES[o.id] || "&nbsp;"}</p><div class="chart"></div>`;
    container.appendChild(box);
    const series = [];
    if (o.team.length) series.push({ points: o.team, color: COLORS.aubergine, name: "team page" });
    if (o.doc.length) series.push({ points: o.doc, color: COLORS.slate, name: "filings / reports", line: o.id === "cltr" });
    smallLine(box.querySelector(".chart"), [], {
      yearFrom: 2015, yearTo: 2026, ymax, unit: "people", series,
      label: `People listed at ${orgName(o.id)}`,
    });
  });
  const years = [...new Set(data.people.map((p) => p.year))].sort();
  const select = document.getElementById("f-year");
  if (!state.year) state.year = Math.max(...years.filter((y) => y <= 2025));
  select.innerHTML = years.map((y) => `<option ${y === state.year ? "selected" : ""}>${y}</option>`).join("");
  const rows = data.people.filter((p) => state.orgs.includes(p.org_id) && state.roles.includes(p.role) && p.year === state.year)
    .map((p) => ({ ...p, org: orgName(p.org_id) }));
  renderTable(document.getElementById("table"), rows, [
    { key: "org", label: "Organization" },
    { key: "name", label: "Name", link: "snapshot" },
    { key: "section", label: "Listed under" },
    { key: "title", label: "Title" },
    { key: "role", label: "Role" },
  ], { sortKey: "org", desc: false, limit: 500 });
}

async function init() {
  data = await loadJSON("staff.json");
  const withData = [...new Set([...data.people.map((p) => p.org_id), ...data.headcounts.map((h) => h.org_id)])];
  const ids = data.organizations.map((o) => o.org_id).filter((id) => withData.includes(id));
  const box = document.getElementById("f-orgs");
  box.innerHTML = ids.map((id) =>
    `<label><input type="checkbox" value="${id}" ${state.orgs.includes(id) ? "checked" : ""}>${orgName(id)}</label>`).join("");
  box.querySelectorAll("input").forEach((i) => i.addEventListener("change", () => {
    state.orgs = [...box.querySelectorAll("input:checked")].map((x) => x.value);
    draw();
  }));
  checkboxes(document.getElementById("f-roles"), ROLES, state.roles, (v) => { state.roles = v; draw(); });
  document.getElementById("f-year").addEventListener("change", (e) => { state.year = +e.target.value; draw(); });
  draw();
}

init();
