// Overview page: headline numbers computed from the same data as the other pages.

const GCR = ["Classic GCR", "AI", "Bio", "General x-risk", "Geoengineering", "Climate", "Forecasting", "Unknown"];

function setNumber(id, value, text) {
  const el = document.getElementById(id);
  el.querySelector(".octagon").textContent = value;
  el.querySelector("p").textContent = text;
}

// Plain bars on one scale, so the size difference between AI, bio and classic GCR shows.
function drawComparison(gcr) {
  const amount = (cat) => d3.sum(gcr.filter((g) => g.category === cat), (g) => g.amount);
  const rows = ["AI", "Bio", "Classic GCR"].map((cat) => ({ cat, value: amount(cat) }));
  const max = d3.max(rows, (r) => r.value);
  document.getElementById("compare").innerHTML = rows.map((r) =>
    `<div class="row"><span>${r.cat}</span><div class="bar">` +
    `<div class="fill" style="width:${(85 * r.value) / max}%;background:${ENTITY_COLORS.topic[r.cat]}"></div>` +
    `<span class="value">${fmtMoney(r.value)}</span></div></div>`).join("");
  const [ai, bio, classic] = rows.map((r) => r.value);
  document.getElementById("compare-intro").textContent = `The percentages hide how big the gap is in dollars. ` +
    `In 2015–2025 the four funders gave ${fmtMoney(ai)} to AI and ${fmtMoney(bio)} to bio, against ${fmtMoney(classic)} ` +
    `for classic GCR. AI got about ${Math.round(ai / classic)} times as much as classic GCR, bio about ${Math.round(bio / classic)} times.`;
  const years = d3.max(gcr, (g) => g.year) - d3.min(gcr, (g) => g.year) + 1;
  document.getElementById("compare-outro").textContent = `So it seems there's just very little money to be had for GCR research ` +
    `outside of AI and bio. All classic hazards together got about ${fmtMoney(classic / years)} a year on average.`;
}

async function init() {
  const [funding, pubs, staff] = await Promise.all([loadJSON("funding.json"), loadJSON("publications.json"), loadJSON("staff.json")]);
  const gcr = funding.filter((g) => GCR.includes(g.category) && g.year >= 2015 && g.year <= 2025);
  const total = d3.sum(gcr, (g) => g.amount);
  const classic = d3.sum(gcr.filter((g) => g.category === "Classic GCR"), (g) => g.amount);
  const y2025 = gcr.filter((g) => g.year === 2025);
  const ai2025 = d3.sum(y2025.filter((g) => g.category === "AI"), (g) => g.amount) / d3.sum(y2025, (g) => g.amount);
  setNumber("n-classic", fmtMoney(classic), `went to classic GCR (nuclear, volcanic, space weather, resilient food, ...) from the four funders in 2015–2025`);
  const share = (cat) => d3.sum(gcr.filter((g) => g.category === cat), (g) => g.amount) / total;
  setNumber("n-share", fmtPct(classic / total), `of their ${fmtMoney(total)} GCR funding in that period. AI got ${fmtPct(share("AI"))}, bio ${fmtPct(share("Bio"))}`);
  drawComparison(gcr);
  exportButton(document.getElementById("export-compare"), () => [document.getElementById("compare-figure")], "gcr-funding-comparison.png");
  setNumber("n-ai", fmtPct(ai2025), "of GCR funding in 2025 went to AI");
  const researchers = staff.functions.filter((r) => r.year === PARTIAL_YEAR && r.focus === "classic or multi-hazard" && r.function === "research");
  const nResearchers = d3.sum(researchers, (r) => r.people);
  setNumber("n-people", `~${Math.round(nResearchers / 5) * 5}`, `people do research at the main GCR organizations working on classic or several risks (my selection) in ${PARTIAL_YEAR}. A rough count, see the caveats below`);
  const works = pubs.by_year.find((r) => r.scope === "title_abstract" && r.year === 2025);
  setNumber("n-pubs", works ? fmtInt(works.works) : "–", `works in 2025 with "global catastrophic risk" in title or abstract (and ~${fmtInt((pubs.by_year.find((r) => r.scope === "fulltext" && r.year === 2025) || {}).works || 0)} mentioning it anywhere)`);
}

init();
