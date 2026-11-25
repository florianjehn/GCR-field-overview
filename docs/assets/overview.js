// Overview page: headline numbers computed from the same data as the other pages.

const GCR = ["Classic GCR", "AI", "Bio", "General x-risk", "Geoengineering", "Climate", "Forecasting", "Unknown"];

function setNumber(id, value, text) {
  const el = document.getElementById(id);
  el.querySelector(".octagon").textContent = value;
  el.querySelector("p").textContent = text;
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
  setNumber("n-ai", fmtPct(ai2025), "of GCR funding in 2025 went to AI");
  const researchers = staff.functions.filter((r) => r.year === PARTIAL_YEAR && r.focus === "classic or multi-hazard" && r.function === "research");
  const byOrg = d3.rollups(researchers, (v) => d3.sum(v, (r) => r.people), (r) => r.org_id).sort((a, b) => b[1] - a[1]);
  const SHORT = { allfed: "ALLFED", cser: "CSER", xlab: "XLab", beri: "BERI", gcri: "GCRI", fhi: "FHI" };
  const nResearchers = d3.sum(byOrg, ([, n]) => n);
  setNumber("n-people", `~${Math.round(nResearchers / 5) * 5}`, `people do research at classic or multi-hazard GCR organizations in ${PARTIAL_YEAR} ` +
    `(${byOrg.map(([id, n]) => `${SHORT[id] || id} ${n}`).join(", ")}). A generous count, see below`);
  const works = pubs.by_year.find((r) => r.scope === "title_abstract" && r.year === 2025);
  setNumber("n-pubs", works ? fmtInt(works.works) : "–", `works in 2025 with "global catastrophic risk" in title or abstract (and ~${fmtInt((pubs.by_year.find((r) => r.scope === "fulltext" && r.year === 2025) || {}).works || 0)} mentioning it anywhere)`);
}

init();
