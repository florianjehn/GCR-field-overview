// Overview page: headline numbers computed from the same data as the other pages.

const ASRIC = "Abrupt sunlight reduction & infrastructure collapse";
const GCR = [ASRIC, "AI", "Bio", "General x-risk", "Geoengineering", "Climate", "Unknown"];
// "GCR outside AI and bio" and its parts, as on the funding page.
const OUTSIDE_PARTS = [
  { label: ASRIC, categories: [ASRIC] },
  { label: "General x-risk", categories: ["General x-risk"] },
  { label: "Climate & geoengineering", categories: ["Climate", "Geoengineering"] },
];
const OUTSIDE_AI_BIO = OUTSIDE_PARTS.flatMap((p) => p.categories);

function setNumber(id, value, text) {
  const el = document.getElementById(id);
  el.querySelector(".octagon").textContent = value;
  el.querySelector("p").textContent = text;
}

const sumOf = (grants, categories) => d3.sum(grants.filter((g) => categories.includes(g.category)), (g) => g.amount);

// Plain bars on one scale, so the size difference between AI, bio and the rest shows.
function drawComparison(gcr) {
  const parts = OUTSIDE_PARTS.map((p) => ({ label: p.label, value: sumOf(gcr, p.categories) }));
  const rows = [
    { label: "AI", parts: [{ label: "AI", value: sumOf(gcr, ["AI"]) }] },
    { label: "Bio", parts: [{ label: "Bio", value: sumOf(gcr, ["Bio"]) }] },
    { label: "Outside AI and bio", parts },
  ].map((r) => ({ ...r, value: d3.sum(r.parts, (p) => p.value) }));
  const max = d3.max(rows, (r) => r.value);
  document.getElementById("compare").innerHTML = rows.map((r) =>
    `<div class="row"><span>${r.label}</span><div class="bar">` +
    r.parts.map((p) => `<div class="fill" title="${p.label}: ${fmtMoney(p.value)}" ` +
      `style="width:${(85 * p.value) / max}%;background:${ENTITY_COLORS.topic[p.label]}"></div>`).join("") +
    `<span class="value">${fmtMoney(r.value)}</span></div></div>`).join("");
  legend(document.getElementById("compare-legend"), parts.map((p) => p.label), (k) => ENTITY_COLORS.topic[k]);
  const [ai, bio, outside] = rows.map((r) => r.value);
  const asric = parts[0].value;
  document.getElementById("compare-intro").textContent = `The percentages hide how big the gap is in dollars. ` +
    `In 2015–2025 the four funders gave ${fmtMoney(ai)} to AI and ${fmtMoney(bio)} to bio, against ${fmtMoney(outside)} ` +
    `for all GCR work outside AI and bio together. AI got about ${Math.round(ai / outside)} times as much.`;
  const years = d3.max(gcr, (g) => g.year) - d3.min(gcr, (g) => g.year) + 1;
  document.getElementById("compare-outro").textContent = `So it seems there's just very little money to be had for GCR research ` +
    `outside of AI and bio. That's about ${fmtMoney(outside / years)} a year for everything else, and about ` +
    `${fmtMoney(asric / years)} a year for abrupt sunlight reduction and infrastructure collapse.`;
}

async function init() {
  const [funding, staff] = await Promise.all([loadJSON("funding.json"), loadJSON("staff.json")]);
  const gcr = funding.filter((g) => GCR.includes(g.category) && g.year >= 2015 && g.year <= 2025);
  const total = d3.sum(gcr, (g) => g.amount);
  const outside = sumOf(gcr, OUTSIDE_AI_BIO);
  const y2025 = gcr.filter((g) => g.year === 2025);
  const ai2025 = sumOf(y2025, ["AI"]) / d3.sum(y2025, (g) => g.amount);
  const asric = sumOf(gcr, [ASRIC]);
  setNumber("n-outside", fmtMoney(outside), `went to GCR outside AI and bio from the four funders in 2015–2025, ` +
    `${fmtMoney(asric)} of it to abrupt sunlight reduction and infrastructure collapse`);
  const share = (cat) => sumOf(gcr, [cat]) / total;
  setNumber("n-share", fmtPct(outside / total), `of the four funders' ${fmtMoney(total)} GCR funding in 2015–2025 went to GCR outside AI and bio. ` +
    `AI got ${fmtPct(share("AI"))}, bio ${fmtPct(share("Bio"))}`);
  setNumber("n-asric-share", fmtPct(asric / total), "of that GCR funding went to abrupt sunlight reduction and infrastructure collapse");
  drawComparison(gcr);
  exportButton(document.getElementById("export-compare"), () => [document.getElementById("compare-figure")], "gcr-funding-comparison.png");
  setNumber("n-ai", fmtPct(ai2025), "of GCR funding in 2025 went to AI");
  const researchers = staff.functions.filter((r) => r.year === PARTIAL_YEAR && r.focus === "beyond AI and bio" && r.function === "research");
  const nResearchers = d3.sum(researchers, (r) => r.people);
  setNumber("n-people", `~${Math.round(nResearchers / 5) * 5}`, `people do research at the main GCR organizations working beyond AI and bio (my selection) in ${PARTIAL_YEAR}. A rough count, see the caveats below`);
}

init();
