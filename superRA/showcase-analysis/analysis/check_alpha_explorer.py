# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "pyarrow"]
# ///
"""Fail if the numbers embedded in alpha-explorer.html differ from regression_estimates.parquet."""

import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
html = (ROOT / "02-analysis" / "attachments" / "alpha-explorer.html").read_text()
data = json.loads(re.search(r'<script type="application/json" id="data">(.*?)</script>', html, re.S).group(1))
est = pd.read_parquet(ROOT / "data" / "regression_estimates.parquet")

n = 0
for model, cols in data["models"].items():
    g = est[est["model"] == model].set_index("portfolio")
    assert list(g.index) == data["portfolios"] or set(g.index) == set(data["portfolios"]), model
    for c, vals in zip(data["columns"], cols):
        for p, v in zip(data["portfolios"], vals):
            ref = g.loc[p, c]
            assert (v is None) == pd.isna(ref), f"{model} {p} {c}: missing mismatch"
            if v is not None:
                assert abs(v - ref) <= 5e-5, f"{model} {p} {c}: {v} vs {ref}"
                n += 1
print(f"{n} embedded numbers match the parquet")
