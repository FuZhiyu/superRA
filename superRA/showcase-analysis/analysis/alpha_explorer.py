# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "pyarrow"]
# ///
"""Write the interactive CAPM-vs-FF3 alpha explorer from regression_estimates.parquet.

Only restyles and re-embeds the saved estimates; no re-estimation.
"""

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "02-analysis" / "attachments" / "alpha-explorer.html"

COLS = ["alpha", "alpha_t", "r2", "b_Mkt-RF", "t_Mkt-RF", "b_SMB", "t_SMB", "b_HML", "t_HML"]
est = pd.read_parquet(ROOT / "data" / "regression_estimates.parquet")
ports = list(dict.fromkeys(est["portfolio"]))
assert len(ports) == 25
rows = {
    m: [
        [None if pd.isna(v) else round(float(v), 4) for v in g.set_index("portfolio").loc[ports, COLS][c]]
        for c in COLS
    ]
    for m, g in est.groupby("model", sort=True)
}
data = {"portfolios": ports, "columns": COLS, "models": rows}

# The first view states the result; numbers come from the estimates, fixed formatting.
mean_abs = est.groupby("model")["alpha"].apply(lambda a: a.abs().mean())
sg = est[(est["model"] == "FF3") & (est["portfolio"] == ports[0])].iloc[0]
HEADLINE = f"FF3 cuts the mean |alpha| from {mean_abs['CAPM']:.3f} to {mean_abs['FF3']:.3f} % per month"
SUB = (f"Alphas of the 25 size and book-to-market portfolios, % per month. "
       f"Small-growth ({ports[0]}) keeps an FF3 alpha of {sg['alpha']:.2f} (t = {sg['alpha_t']:.2f}).")

TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Alpha Explorer</title>
<style>
:root { --bg:#f9f9f7; --fg:#1a1a1a; --muted:#6b6b66; --line:#d8d8d2; --pos:#c0392b; --neg:#2471a3; --focus:#1a1a1a }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --bg:#0d0d0d; --fg:#ececea; --muted:#9a9a94; --line:#333; --pos:#e8685a; --neg:#5aa3d6; --focus:#ececea; color-scheme: dark } }
:root[data-theme="dark"] { --bg:#0d0d0d; --fg:#ececea; --muted:#9a9a94; --line:#333; --pos:#e8685a; --neg:#5aa3d6; --focus:#ececea; color-scheme: dark }
body { background: var(--bg); color: var(--fg); font: 14px/1.4 system-ui, sans-serif; margin: 0; padding: 12px; max-width: 760px }
h1 { font-size: 17px; line-height: 1.3; margin: 0 0 4px }
p.sub { color: var(--muted); margin: 0 0 10px }
.ctl { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; margin-bottom: 8px }
.ctl button, .ctl select, .cell { font: inherit; color: var(--fg); background: var(--bg); border: 1px solid var(--line); border-radius: 6px; cursor: pointer }
.ctl button, .ctl select { padding: 3px 9px }
.ctl label { color: var(--muted); margin-left: 4px }
.ctl button[aria-pressed="true"] { border-color: var(--fg); font-weight: 600 }
.grid { display: grid; grid-template-columns: 3.4em repeat(5, minmax(0, 1fr)); gap: 3px; align-items: stretch }
#model { display: flex; gap: 4px }
.hd { color: var(--muted); font-size: 12px; text-align: center; align-self: center }
.cell { min-width: 0; padding: 7px 0; font-size: 12px; font-variant-numeric: tabular-nums; background: color-mix(in srgb, var(--c) calc(var(--m) * 85%), var(--bg)) }
.cell[aria-pressed="true"] { outline: 2px solid var(--focus); outline-offset: 1px }
.cell:disabled { cursor: default; color: var(--muted) }
.scroll { overflow-x: auto; margin-top: 14px }
table { border-collapse: collapse; width: 100%; font-variant-numeric: tabular-nums }
th, td { text-align: right; padding: 3px 8px; border-bottom: 1px solid var(--line); white-space: nowrap }
th:first-child, td:first-child { text-align: left }
h2 { font-size: 16px; margin: 16px 0 0 }
.note { color: var(--muted); font-size: 12px; margin: 6px 0 0 }
</style>
</head>
<body>
<h1>__HEADLINE__</h1>
<p class="sub">__SUB__</p>
<div class="ctl"><span id="model" role="group" aria-label="Model"></span><label for="metric">Show</label><select id="metric"></select></div>
<div class="grid" id="grid"></div>
<p class="note" id="scale"></p>
<p class="note" id="hint">Tap a cell to compare its CAPM and FF3 estimates.</p>
<section id="detailbox" hidden><h2 id="title"></h2>
<div class="scroll"><table id="detail"></table></div></section>
<script type="application/json" id="data">__DATA__</script>
<script>
const D = JSON.parse(document.getElementById("data").textContent);
const COL = Object.fromEntries(D.columns.map((c, i) => [c, i]));
const METRICS = [["alpha", "Alpha (%/mo)"], ["alpha_t", "t(alpha)"], ["b_Mkt-RF", "Mkt-RF loading"], ["b_SMB", "SMB loading"], ["b_HML", "HML loading"]];
const SIZE = ["Small", "ME2", "ME3", "ME4", "Big"], BM = ["Growth", "BM2", "BM3", "BM4", "Value"];
const models = Object.keys(D.models);
const S = { model: models.includes("FF3") ? "FF3" : models[0], metric: "alpha", cell: null };
const val = (m, c, i) => D.models[m][COL[c]][i];
const fmt = (v, d = 3) => v == null ? "–" : v.toFixed(d);

function buttons(id, items, key) {
  const box = document.getElementById(id);
  for (const [v, label] of items) {
    const b = document.createElement("button");
    b.textContent = label; b.dataset.v = v;
    b.addEventListener("click", () => { S[key] = v; render(); });
    box.append(b);
  }
}
buttons("model", models.map(m => [m, m]), "model");
const sel = document.getElementById("metric");
for (const [v, label] of METRICS) sel.append(new Option(label, v));
sel.addEventListener("change", () => { S.metric = sel.value; render(); });

const grid = document.getElementById("grid");
grid.append(document.createElement("div"));
for (const b of BM) { const h = document.createElement("div"); h.className = "hd"; h.textContent = b; grid.append(h); }
const cells = [];
SIZE.forEach((s, r) => {
  const h = document.createElement("div"); h.className = "hd"; h.textContent = s; grid.append(h);
  for (let k = 0; k < 5; k++) {
    const i = r * 5 + k, b = document.createElement("button");
    b.className = "cell"; b.title = D.portfolios[i];
    b.addEventListener("click", () => { S.cell = S.cell === i ? null : i; render(); });
    cells[i] = b; grid.append(b);
  }
});

function render() {
  for (const b of document.querySelectorAll("#model button")) b.setAttribute("aria-pressed", b.dataset.v === S.model);
  sel.value = S.metric;
  const all = models.flatMap(m => D.portfolios.map((_, i) => val(m, S.metric, i))).filter(v => v != null);
  const max = Math.max(...all.map(Math.abs)) || 1;
  cells.forEach((b, i) => {
    const v = val(S.model, S.metric, i);
    b.textContent = fmt(v, S.metric === "alpha_t" ? 2 : 3);
    b.disabled = v == null;
    b.style.setProperty("--m", v == null ? 0 : Math.abs(v) / max);
    b.style.setProperty("--c", v < 0 ? "var(--neg)" : "var(--pos)");
    b.setAttribute("aria-pressed", i === S.cell);
  });
  document.getElementById("scale").textContent =
    `Rows: size, small to big. Columns: book-to-market. Red positive, blue negative; full color at |value| = ${max.toFixed(2)} in both models.` +
    (S.model === "CAPM" && /SMB|HML/.test(S.metric) ? " CAPM has no SMB or HML loading." : "");
  document.getElementById("hint").hidden = S.cell !== null;
  document.getElementById("detailbox").hidden = S.cell === null;
  if (S.cell === null) return;
  document.getElementById("title").textContent = D.portfolios[S.cell];
  const rows = [["Alpha (%/mo)", "alpha"], ["t(alpha)", "alpha_t"], ["Mkt-RF loading", "b_Mkt-RF"], ["t(Mkt-RF)", "t_Mkt-RF"],
    ["SMB loading", "b_SMB"], ["t(SMB)", "t_SMB"], ["HML loading", "b_HML"], ["t(HML)", "t_HML"], ["R²", "r2"]];
  document.getElementById("detail").innerHTML =
    `<tr><th></th>${models.map(m => `<th>${m}</th>`).join("")}</tr>` +
    rows.map(([l, c]) => `<tr><td>${l}</td>${models.map(m => `<td>${fmt(val(m, c, S.cell))}</td>`).join("")}</tr>`).join("");
}
render();
</script>
</body>
</html>
"""

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(TEMPLATE.replace("__HEADLINE__", HEADLINE).replace("__SUB__", SUB)
               .replace("__DATA__", json.dumps(data, sort_keys=True, separators=(",", ":"))))
print(f"wrote {OUT.name}: {OUT.stat().st_size / 1024:.1f} KiB")
