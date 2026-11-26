// Shared helpers for the GCR field overview site: colours, formatting,
// tooltip, legend, stacked bar chart, small line chart and sortable table.

const COLORS = {
  aubergine: "#5D2A42", slate: "#46708A", rose: "#CC8FA0", sage: "#627F64",
  ochre: "#C9A55A", context: "#A29A97", mauve: "#C9B1BD", ink: "#2E2A2B",
  paper: "#F7F4EF", hairline: "#D9D2CF", muted: "#6E6668", berry: "#8E5A74",
  deep: "#3E1C2C",
};

// The last year in the data is still running; it gets an asterisk on axes.
const PARTIAL_YEAR = 2026;
const yearLabel = (y) => (+y === PARTIAL_YEAR ? `${y}*` : `${y}`);

// Fixed colour per entity (never by rank). Abrupt sunlight reduction & infrastructure collapse is the focus colour.
const ENTITY_COLORS = {
  topic: {
    "Abrupt sunlight reduction & infrastructure collapse": COLORS.aubergine, "AI": COLORS.slate, "Bio": COLORS.rose,
    "General x-risk": COLORS.sage, "Climate & geoengineering": COLORS.ochre,
    "Forecasting": COLORS.berry, "EA & community": COLORS.deep, "Other": COLORS.context,
  },
  funder: {
    "Coefficient Giving": COLORS.aubergine, "SFF": COLORS.slate,
    "LTFF": COLORS.rose, "FLI": COLORS.sage,
  },
  activity: {
    "Research": COLORS.aubergine, "Policy & advocacy": COLORS.slate,
    "Field-building & education": COLORS.rose, "Other": COLORS.sage,
    "Unknown/not assessed": COLORS.context,
  },
  function: {
    "Research": COLORS.aubergine, "Teaching": COLORS.ochre,
    "Policy": COLORS.slate, "Operations": COLORS.context,
  },
};

const fmtMoney = (v) => {
  const a = Math.abs(v);
  if (a >= 1e9) return `$${(v / 1e9).toFixed(1)}B`;
  if (a >= 1e6) return `$${(v / 1e6).toFixed(a >= 1e7 ? 0 : 1)}M`;
  if (a >= 1e3) return `$${(v / 1e3).toFixed(0)}k`;
  return `$${Math.round(v)}`;
};
const fmtInt = (v) => d3.format(",")(Math.round(v));
const fmtPct = (v) => `${(100 * v).toFixed(v < 0.1 ? 1 : 0)} %`;

async function loadJSON(name) {
  // no-cache: revalidate with the server so updated data is never mixed with old code.
  const response = await fetch(`data/${name}`, { cache: "no-cache" });
  return response.json();
}

function tooltip() {
  let el = document.querySelector(".tooltip");
  if (!el) {
    el = document.createElement("div");
    el.className = "tooltip";
    document.body.appendChild(el);
  }
  return {
    show(event, html) {
      el.innerHTML = html;
      el.style.display = "block";
      const pad = 14;
      const w = el.offsetWidth, h = el.offsetHeight;
      let x = event.clientX + pad, y = event.clientY + pad;
      if (x + w > window.innerWidth) x = event.clientX - w - pad;
      if (y + h > window.innerHeight) y = event.clientY - h - pad;
      el.style.left = `${x}px`;
      el.style.top = `${y}px`;
    },
    hide() { el.style.display = "none"; },
  };
}

// Keys that have a non-zero value in rows ([{key, value}]), in their original order,
// so legends only list what is in the chart.
const keysWithData = (keys, rows) => keys.filter((k) => rows.some((r) => r.key === k && r.value > 0));

function legend(container, keys, colorOf) {
  container.innerHTML = keys
    .map((k) => `<span><i style="background:${colorOf(k)}"></i>${k}</span>`)
    .join("");
}

// Stacked bars per year. rows: [{year, key, value}]; keys in stacking order.
function stackedBars(container, rows, keys, colorOf, opts = {}) {
  const width = opts.width || 900, height = opts.height || 360;
  const m = { top: 12, right: opts.right ?? 110, bottom: 28, left: 64 };
  const years = d3.range(opts.yearFrom, opts.yearTo + 1);
  const table = years.map((year) => {
    const entry = { year };
    keys.forEach((k) => { entry[k] = 0; });
    rows.filter((r) => r.year === year).forEach((r) => { entry[r.key] += r.value; });
    return entry;
  });
  if (opts.percent) {
    table.forEach((e) => {
      const total = d3.sum(keys, (k) => e[k]);
      keys.forEach((k) => { e[k] = total ? e[k] / total : 0; });
    });
  }
  const series = d3.stack().keys(keys)(table);
  const x = d3.scaleBand().domain(years).range([m.left, width - m.right]).padding(0.25);
  const ymax = Math.max(opts.ymax || 0, d3.max(series, (s) => d3.max(s, (d) => d[1])) || 1);
  const y = d3.scaleLinear().domain([0, opts.percent ? 1 : ymax]).nice().range([height - m.bottom, m.top]);
  const fmt = opts.percent ? fmtPct : (opts.format || fmtMoney);

  container.innerHTML = "";
  const svg = d3.select(container).append("svg").attr("viewBox", `0 0 ${width} ${height}`)
    .attr("role", "img").attr("aria-label", opts.label || "Stacked bar chart");
  svg.append("g").attr("class", "grid").selectAll("line").data(y.ticks(5)).join("line")
    .attr("x1", m.left).attr("x2", width - m.right).attr("y1", (d) => y(d)).attr("y2", (d) => y(d));
  svg.append("g").attr("class", "axis").attr("transform", `translate(${m.left - 6},0)`)
    .call(d3.axisLeft(y).ticks(5).tickSize(0).tickFormat(fmt));
  const every = years.length > 14 ? 2 : 1;
  svg.append("g").attr("class", "axis").attr("transform", `translate(0,${height - m.bottom + 6})`)
    .call(d3.axisBottom(x).tickSize(0).tickValues(years.filter((_, i) => i % every === 0)).tickFormat(yearLabel));
  svg.append("line").attr("class", "baseline").attr("x1", m.left).attr("x2", width - m.right)
    .attr("y1", y(0)).attr("y2", y(0));

  const tip = tooltip();
  svg.append("g").selectAll("g").data(series).join("g").attr("fill", (s) => colorOf(s.key))
    .selectAll("rect").data((s) => s.map((d) => ({ ...d, key: s.key }))).join("rect")
    .attr("x", (d) => x(d.data.year)).attr("width", x.bandwidth())
    .attr("y", (d) => y(d[1]))
    .attr("height", (d) => Math.max(0, y(d[0]) - y(d[1])))
    .on("mousemove", (event, d) => {
      const total = d3.sum(keys, (k) => d.data[k]);
      tip.show(event, `<div class="t-head">${yearLabel(d.data.year)} · ${d.key}</div>` +
        `${fmt(d[1] - d[0])}<br><span class="note">Year total ${fmt(total)}</span>`);
    })
    .on("mouseleave", () => tip.hide());

  // Direct labels at the end of the last year for up to 4 series.
  const last = table[table.length - 1];
  if (keys.length > 1 && keys.length <= 4 && last) {
    const lastSeries = series.map((s) => ({ key: s.key, d: s[s.length - 1] }))
      .filter((s) => y(s.d[0]) - y(s.d[1]) >= 12);
    svg.append("g").selectAll("text").data(lastSeries).join("text")
      .attr("class", "direct-label").attr("x", x(last.year) + x.bandwidth() + 6)
      .attr("y", (s) => y((s.d[0] + s.d[1]) / 2) + 4).text((s) => s.key);
  }
  return table;
}

// Small line chart for small multiples. points: [{year, value}].
function smallLine(container, points, opts) {
  const width = opts.width || 360, height = opts.height || 190;
  const m = { top: 10, right: 16, bottom: 24, left: 34 };
  const x = d3.scaleLinear().domain([opts.yearFrom, opts.yearTo]).range([m.left, width - m.right]);
  const y = d3.scaleLinear().domain([0, Math.max(opts.ymax || 0, d3.max(points, (p) => p.value) || 1)])
    .nice().range([height - m.bottom, m.top]);
  container.innerHTML = "";
  const svg = d3.select(container).append("svg").attr("viewBox", `0 0 ${width} ${height}`)
    .attr("role", "img").attr("aria-label", opts.label || "Line chart");
  svg.append("g").attr("class", "grid").selectAll("line").data(y.ticks(4)).join("line")
    .attr("x1", m.left).attr("x2", width - m.right).attr("y1", (d) => y(d)).attr("y2", (d) => y(d));
  svg.append("g").attr("class", "axis").attr("transform", `translate(${m.left - 4},0)`)
    .call(d3.axisLeft(y).ticks(4).tickSize(0).tickFormat(d3.format("d")));
  svg.append("g").attr("class", "axis").attr("transform", `translate(0,${height - m.bottom + 4})`)
    .call(d3.axisBottom(x).ticks(5).tickSize(0).tickFormat(yearLabel));
  svg.append("line").attr("class", "baseline").attr("x1", m.left).attr("x2", width - m.right)
    .attr("y1", y(0)).attr("y2", y(0));
  const tip = tooltip();
  (opts.series || [{ points, color: COLORS.aubergine, name: "" }]).forEach((s) => {
    const data = s.points.filter((p) => p.value !== null).sort((a, b) => a.year - b.year);
    if (s.line !== false) svg.append("path").datum(data).attr("fill", "none").attr("stroke", s.color)
      .attr("stroke-width", 2).attr("stroke-linecap", "square").attr("stroke-linejoin", "miter")
      .attr("d", d3.line().x((p) => x(p.year)).y((p) => y(p.value)));
    svg.append("g").selectAll("rect").data(data).join("rect")
      .attr("x", (p) => x(p.year) - 4).attr("y", (p) => y(p.value) - 4)
      .attr("width", 8).attr("height", 8).attr("fill", s.color)
      .on("mousemove", (event, p) => tip.show(event,
        `<div class="t-head">${p.year}${s.name ? " · " + s.name : ""}</div>${fmtInt(p.value)} ${opts.unit || ""}` +
        (p.note ? `<br><span class="note">${p.note}</span>` : "")))
      .on("mouseleave", () => tip.hide());
  });
}

// Sortable table. columns: [{key, label, num, format, link}]
function renderTable(container, rows, columns, opts = {}) {
  // Sort state lives on the container so it survives redraws after filter changes.
  let sortKey = container.dataset.sortKey || opts.sortKey || columns[0].key;
  let desc = container.dataset.desc ? container.dataset.desc === "true" : opts.desc !== false;
  const limit = opts.limit || 300;
  function draw() {
    const sorted = [...rows].sort((a, b) => {
      const va = a[sortKey], vb = b[sortKey];
      const c = typeof va === "number" ? va - vb : String(va ?? "").localeCompare(String(vb ?? ""));
      return desc ? -c : c;
    }).slice(0, limit);
    const head = columns.map((c) =>
      `<th class="${c.num ? "num" : ""}" data-key="${c.key}">${c.label}${c.key === sortKey ? (desc ? " ↓" : " ↑") : ""}</th>`).join("");
    const body = sorted.map((r) => "<tr>" + columns.map((c) => {
      let v = r[c.key];
      v = c.format ? c.format(v, r) : (v ?? "");
      if (c.link && r[c.link]) v = `<a href="${r[c.link]}" target="_blank" rel="noopener">${v}</a>`;
      return `<td class="${c.num ? "num" : ""}">${v}</td>`;
    }).join("") + "</tr>").join("");
    container.innerHTML = `<div class="table-wrap"><table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table></div>` +
      `<p class="note">${rows.length > limit ? `Showing the top ${limit} of ${fmtInt(rows.length)} rows.` : `${fmtInt(rows.length)} rows.`}</p>`;
    container.querySelectorAll("th").forEach((th) => th.addEventListener("click", () => {
      const k = th.dataset.key;
      desc = k === sortKey ? !desc : true;
      sortKey = k;
      container.dataset.sortKey = sortKey;
      container.dataset.desc = desc;
      draw();
    }));
  }
  draw();
}

function checkboxes(container, values, checked, onChange) {
  container.innerHTML = values.map((v) =>
    `<label><input type="checkbox" value="${v}" ${checked.includes(v) ? "checked" : ""}>${v}</label>`).join("");
  container.querySelectorAll("input").forEach((i) => i.addEventListener("change", () => {
    onChange([...container.querySelectorAll("input:checked")].map((x) => x.value));
  }));
}

function segmented(container, values, current, onChange) {
  container.innerHTML = values.map(([v, label]) =>
    `<button type="button" data-v="${v}" aria-pressed="${v === current}">${label}</button>`).join("");
  container.querySelectorAll("button").forEach((b) => b.addEventListener("click", () => {
    container.querySelectorAll("button").forEach((x) => x.setAttribute("aria-pressed", x === b));
    onChange(b.dataset.v);
  }));
}

// PNG export of what is on screen. The chart parts (legend, titles, SVG charts,
// HTML bars) are redrawn on a canvas at the positions they have on the page,
// with a source line below.
const EXPORT_SCALE = 2;
const SVG_STYLE_PROPS = ["fill", "stroke", "stroke-width", "font-family", "font-size", "opacity", "text-anchor"];

function inlineSvg(svg) {
  const copy = svg.cloneNode(true);
  const from = [svg, ...svg.querySelectorAll("*")], to = [copy, ...copy.querySelectorAll("*")];
  from.forEach((el, i) => {
    const cs = getComputedStyle(el);
    SVG_STYLE_PROPS.forEach((p) => to[i].style.setProperty(p, cs.getPropertyValue(p)));
  });
  const box = svg.getBoundingClientRect();
  copy.setAttribute("width", box.width);
  copy.setAttribute("height", box.height);
  copy.setAttribute("xmlns", "http://www.w3.org/2000/svg");
  return new XMLSerializer().serializeToString(copy);
}

function svgImage(svg) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = reject;
    img.src = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(inlineSvg(svg))}`;
  });
}

// Splits a text node into its rendered lines: [{text, rect}], measured word by word.
function textLines(node) {
  const lines = [];
  const range = document.createRange();
  for (const match of node.textContent.matchAll(/\S+/g)) {
    range.setStart(node, match.index);
    range.setEnd(node, match.index + match[0].length);
    const rect = range.getClientRects()[0];
    if (!rect) continue;
    const line = lines[lines.length - 1];
    if (line && Math.abs(line.top - rect.top) < 2) {
      line.words.push(match[0]);
      line.right = rect.right;
    } else {
      lines.push({ words: [match[0]], left: rect.left, top: rect.top, right: rect.right, height: rect.height });
    }
  }
  return lines.map((l) => ({ text: l.words.join(" "), rect: { left: l.left, top: l.top, width: l.right - l.left, height: l.height } }));
}

// Text lines outside SVGs, with their position and style.
function textBoxes(root) {
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  const boxes = [];
  for (let node = walker.nextNode(); node; node = walker.nextNode()) {
    const el = node.parentElement;
    if (!node.textContent.trim() || el.closest("svg")) continue;
    const cs = getComputedStyle(el);
    const style = { font: `${cs.fontSize} ${cs.fontFamily}`, color: cs.color, transform: cs.textTransform, spacing: cs.letterSpacing };
    textLines(node).forEach((line) => boxes.push({ ...style, ...line }));
  }
  return boxes;
}

function swatches(root) {
  return [...root.querySelectorAll(".legend i, .compare .fill")].map((el) => ({
    rect: el.getBoundingClientRect(), color: getComputedStyle(el).backgroundColor,
  }));
}

async function exportPng(elements, filename) {
  const shown = elements.filter((el) => el && el.getBoundingClientRect().height > 0);
  const rects = shown.map((el) => el.getBoundingClientRect());
  const pad = 20, footer = 30;
  const left = d3.min(rects, (r) => r.left), top = d3.min(rects, (r) => r.top);
  const width = d3.max(rects, (r) => r.right) - left + 2 * pad;
  const height = d3.max(rects, (r) => r.bottom) - top + 2 * pad + footer;
  const canvas = document.createElement("canvas");
  canvas.width = width * EXPORT_SCALE;
  canvas.height = height * EXPORT_SCALE;
  const ctx = canvas.getContext("2d");
  ctx.scale(EXPORT_SCALE, EXPORT_SCALE);
  ctx.fillStyle = COLORS.paper;
  ctx.fillRect(0, 0, width, height);
  const at = (r) => ({ x: r.left - left + pad, y: r.top - top + pad, w: r.width, h: r.height });
  for (const el of shown) {
    swatches(el).forEach((s) => {
      const p = at(s.rect);
      ctx.fillStyle = s.color;
      ctx.fillRect(p.x, p.y, p.w, p.h);
    });
    ctx.textBaseline = "middle";
    textBoxes(el).forEach((b) => {
      const p = at(b.rect);
      ctx.font = b.font;
      ctx.fillStyle = b.color;
      ctx.letterSpacing = b.spacing === "normal" ? "0px" : b.spacing;
      ctx.fillText(b.transform === "uppercase" ? b.text.toUpperCase() : b.text, p.x, p.y + p.h / 2);
    });
    ctx.letterSpacing = "0px";
    const svgs = el.tagName === "svg" ? [el] : [...el.querySelectorAll("svg")];
    for (const svg of svgs) {
      const p = at(svg.getBoundingClientRect());
      ctx.drawImage(await svgImage(svg), p.x, p.y, p.w, p.h);
    }
  }
  const built = document.getElementById("built");
  ctx.font = `12px ${getComputedStyle(document.body).fontFamily}`;
  ctx.fillStyle = COLORS.muted;
  ctx.fillText(`GCR field overview · ${location.href.split(/[?#]/)[0]}${built && built.textContent ? " · " + built.textContent : ""}`,
    pad, height - pad);
  const link = document.createElement("a");
  link.download = filename;
  link.href = canvas.toDataURL("image/png");
  link.click();
}

// Adds a "Download PNG" button that exports the elements returned by getElements().
function exportButton(host, getElements, filename) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "export";
  button.textContent = "Download PNG";
  button.addEventListener("click", () => exportPng(getElements(), filename));
  host.appendChild(button);
}
