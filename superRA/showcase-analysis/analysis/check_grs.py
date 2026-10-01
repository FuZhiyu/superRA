# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Guard the headline GRS result in data/grs_results.csv.

Fails if either model is no longer rejected at 1%, if FF3's GRS statistic is not
below CAPM's, or if FF3 no longer at least halves CAPM's mean absolute alpha.
"""

import csv
from pathlib import Path

GRS = Path(__file__).resolve().parents[1] / "data" / "grs_results.csv"

rows = {r["model"]: r for r in csv.DictReader(GRS.open())}
capm, ff3 = rows["CAPM"], rows["FF3"]

for name, r in rows.items():
    n, k, t = int(r["N"]), int(r["K"]), int(r["T"])
    assert int(r["df2"]) == t - n - k > 0, f"{name}: df2 != T-N-K"
    assert float(r["pvalue"]) < 0.01, f"{name}: GRS no longer rejects at 1% (p={r['pvalue']})"
    print(f"{name}: GRS F({r['df1']},{r['df2']}) = {float(r['grs']):.3f}, p = {float(r['pvalue']):.2e}, "
          f"mean|alpha| = {float(r['mean_abs_alpha']):.3f}")

assert float(ff3["grs"]) < float(capm["grs"]), "FF3 GRS not below CAPM GRS"
ratio = float(ff3["mean_abs_alpha"]) / float(capm["mean_abs_alpha"])
assert ratio <= 0.5, f"FF3 mean|alpha| is {ratio:.2f} of CAPM's, no longer halved"
print(f"Headline holds: both rejected; FF3/CAPM mean|alpha| = {ratio:.2f}")
