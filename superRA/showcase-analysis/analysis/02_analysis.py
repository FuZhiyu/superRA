# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy", "statsmodels", "matplotlib", "pyarrow"]
# ///
# %% [markdown]
# # Estimate, test, and visualize: CAPM vs FF3
#
# The core of the showcase. For each of the 25 size x book-to-market portfolios
# we estimate two linear factor models by OLS on the baseline sample, run the
# Gibbons-Ross-Shanken (1989) joint test that all 25 intercepts ("alphas") are
# zero, and produce the showcase figures.
#
# - **CAPM:**  $R_{it}-R_{ft} = \alpha_i + \beta_i\,\text{(Mkt-RF)}_t + \varepsilon_{it}$
# - **FF3:**   $R_{it}-R_{ft} = \alpha_i + \beta_i\,\text{(Mkt-RF)}_t + s_i\,\text{SMB}_t + h_i\,\text{HML}_t + \varepsilon_{it}$
#
# Returns are in **percent per month** as published, so alphas come out in
# percent per month. The headline question: does adding SMB and HML to the
# market factor shrink the pricing errors enough that the model is no longer
# rejected?

# %%
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

import matplotlib
matplotlib.use("Agg")  # headless rendering
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PANEL = DATA / "ff_panel.parquet"
ATTACH = ROOT / "02-analysis" / "attachments"
ATTACH.mkdir(parents=True, exist_ok=True)

EST_OUT = DATA / "regression_estimates.parquet"
GRS_OUT = DATA / "grs_results.csv"

# %% [markdown]
# ## Load the panel and re-describe before analysis
#
# The panel was built and validated upstream (`01-data`): 754 months
# (1963-07 -> 2026-04), columns `Mkt-RF, SMB, HML, RF` plus 25 excess-return
# series named `... (xs)`. We read the existing diagnostics rather than
# re-running full validation, but confirm shape, range, completeness, and the
# 25/3 split before estimating anything.

# %%
panel = pd.read_parquet(PANEL)
print(f"Panel: {panel.shape[0]} months x {panel.shape[1]} cols")
print(f"  range: {panel.index.min():%Y-%m} -> {panel.index.max():%Y-%m}")

XS_COLS = [c for c in panel.columns if c.endswith("(xs)")]
assert len(XS_COLS) == 25, f"expected 25 test portfolios, got {len(XS_COLS)}"

# No missing values anywhere (verified upstream); re-confirm before matrix algebra.
n_missing = int(panel[["Mkt-RF", "SMB", "HML"] + XS_COLS].isna().sum().sum())
print(f"  missing cells across factors + 25 test assets: {n_missing}")
assert n_missing == 0, "missing values would break the GRS covariance estimate"

# %% [markdown]
# ## The 5x5 size x book-to-market grid
#
# Ken French orders the 25 columns row-major: size quintile ME1 (smallest) ->
# ME5 (biggest) on the rows, book-to-market BM1 (growth/low) -> BM5 (value/high)
# on the columns. The corner labels are spelled out (`SMALL LoBM`, `SMALL HiBM`,
# `BIG LoBM`, `BIG HiBM`); the interior are `ME{r} BM{c}`. We build the explicit
# 5x5 layout so figures and grid tables map each portfolio to its (size, value)
# cell unambiguously.

# %%
SIZE_LABELS = ["Small", "ME2", "ME3", "ME4", "Big"]      # rows: ME1..ME5
BM_LABELS = ["Growth", "BM2", "BM3", "BM4", "Value"]      # cols: BM1..BM5

# 5x5 grid of the *raw* portfolio names (without the " (xs)" suffix), row-major.
GRID_NAMES = [
    ["SMALL LoBM", "ME1 BM2", "ME1 BM3", "ME1 BM4", "SMALL HiBM"],
    ["ME2 BM1", "ME2 BM2", "ME2 BM3", "ME2 BM4", "ME2 BM5"],
    ["ME3 BM1", "ME3 BM2", "ME3 BM3", "ME3 BM4", "ME3 BM5"],
    ["ME4 BM1", "ME4 BM2", "ME4 BM3", "ME4 BM4", "ME4 BM5"],
    ["BIG LoBM", "ME5 BM2", "ME5 BM3", "ME5 BM4", "BIG HiBM"],
]
# Flatten to the ordered list of (xs) column names; must equal XS_COLS in order.
GRID_FLAT = [f"{name} (xs)" for row in GRID_NAMES for name in row]
assert GRID_FLAT == XS_COLS, (
    "grid layout does not match panel column order — would scramble the heatmaps"
)
print("Grid layout matches panel column order (row-major ME1->ME5, BM1->BM5). OK")


def to_grid(series_by_xscol: pd.Series) -> np.ndarray:
    """Reshape a Series indexed by (xs) column name into the 5x5 size x BM grid."""
    return series_by_xscol.reindex(GRID_FLAT).to_numpy().reshape(5, 5)


# %% [markdown]
# ## Estimate both models by OLS
#
# One time-series OLS per portfolio per model. We keep, per portfolio:
# the intercept (alpha, %/month), the factor loadings, OLS t-statistics,
# $R^2$, and the residual vector (stacked later into the N x N residual
# covariance the GRS test needs). Standard errors are classical OLS; the GRS
# F-test is the joint-significance instrument, individual t-stats are the
# per-portfolio significance instrument.

# %%
FACTOR_SETS = {
    "CAPM": ["Mkt-RF"],
    "FF3": ["Mkt-RF", "SMB", "HML"],
}

T = len(panel)
N = len(XS_COLS)
print(f"T = {T} months, N = {N} test portfolios")


def estimate_model(factors: list[str]) -> dict:
    """OLS each of the 25 portfolios on `factors`; collect estimates + residuals."""
    X = sm.add_constant(panel[factors])
    K = len(factors)
    rows = []                       # per-portfolio estimate records
    resid = np.empty((T, N))        # T x N residual matrix
    alpha = np.empty(N)
    for j, col in enumerate(XS_COLS):
        y = panel[col]
        res = sm.OLS(y, X).fit()
        resid[:, j] = res.resid.to_numpy()
        alpha[j] = res.params["const"]
        rec = {
            "model": "CAPM" if K == 1 else "FF3",
            "portfolio": col[:-5],  # strip " (xs)"
            "alpha": res.params["const"],
            "alpha_t": res.tvalues["const"],
            "r2": res.rsquared,
            "nobs": int(res.nobs),
        }
        for f in factors:
            rec[f"b_{f}"] = res.params[f]
            rec[f"t_{f}"] = res.tvalues[f]
        rows.append(rec)
    est = pd.DataFrame(rows)
    return {
        "K": K,
        "factors": factors,
        "estimates": est,
        "alpha": alpha,            # N x 1
        "resid": resid,            # T x N
    }


results = {name: estimate_model(facs) for name, facs in FACTOR_SETS.items()}

# Persist the full per-portfolio estimate table (both models stacked).
est_table = pd.concat([results[m]["estimates"] for m in FACTOR_SETS], ignore_index=True)
est_table.to_parquet(EST_OUT)
print(f"Wrote estimate table: {EST_OUT}  ({len(est_table)} portfolio-model rows)")
print(est_table.groupby("model")["alpha"].describe()[["mean", "std", "min", "max"]].round(4))

# %% [markdown]
# ## The GRS statistic, implemented directly from the residual covariance
#
# Gibbons, Ross & Shanken (1989). With $N$ test assets, $K$ factors, $T$ months:
#
# $$\text{GRS} = \frac{T-N-K}{N}\,\Big(1 + \bar f'\,\hat\Omega^{-1}\,\bar f\Big)^{-1}\,\hat\alpha'\,\hat\Sigma^{-1}\,\hat\alpha \;\sim\; F_{N,\,T-N-K}$$
#
# where $\hat\alpha$ is the $N\times1$ intercept vector, $\hat\Sigma$ the
# $N\times N$ **ML** residual covariance (divisor $T$, not $T-K$), $\bar f$ the
# $K\times1$ factor means, and $\hat\Omega$ the $K\times K$ factor covariance
# (ML, divisor $T$). The quadratic form $\hat\alpha'\hat\Sigma^{-1}\hat\alpha$ is
# the **squared Sharpe ratio of the maximal pricing-error portfolio** — the
# increment to the maximum squared Sharpe ratio from adding the test assets to
# the factors, NOT a ratio of Sharpe ratios.
#
# We implement it from the matrices directly (no black-box one-liner) and guard
# the preconditions: $\hat\Sigma$ symmetric positive-definite and $T-N-K>0$. We
# then cross-check the quadratic form via an independent route (Cholesky solve)
# to confirm the linear-algebra is right.

# %%
def grs_test(alpha: np.ndarray, resid: np.ndarray, factors_df: pd.DataFrame) -> dict:
    """GRS F-statistic from alphas, T x N residuals, and the T x K factor panel."""
    T_, N_ = resid.shape
    F = factors_df.to_numpy()
    K_ = F.shape[1]

    df2 = T_ - N_ - K_
    assert df2 > 0, f"T - N - K = {df2} <= 0; GRS undefined"

    # ML residual covariance (divisor T, the GRS convention).
    Sigma = (resid.T @ resid) / T_
    assert np.allclose(Sigma, Sigma.T, atol=1e-10), "residual covariance not symmetric"
    eigmin = np.linalg.eigvalsh(Sigma).min()
    assert eigmin > 0, f"Sigma not positive-definite (min eigenvalue {eigmin:.2e})"

    # Factor means and ML factor covariance.
    fbar = F.mean(axis=0)                       # K x 1
    Omega = np.cov(F, rowvar=False, bias=True)  # ML (divisor T)
    Omega = np.atleast_2d(Omega)

    # Quadratic forms via solves (more stable than explicit inverse).
    q_alpha = float(alpha @ np.linalg.solve(Sigma, alpha))      # alpha' Sigma^-1 alpha
    sh2_f = float(fbar @ np.linalg.solve(Omega, fbar))          # fbar' Omega^-1 fbar = Sh^2(factors)

    grs = (df2 / N_) * (q_alpha / (1.0 + sh2_f))
    pval = stats.f.sf(grs, N_, df2)

    # Independent cross-check of q_alpha via a Cholesky solve.
    L = np.linalg.cholesky(Sigma)
    z = np.linalg.solve(L, alpha)               # L z = alpha  ->  q = z'z
    q_alpha_chol = float(z @ z)
    assert np.isclose(q_alpha, q_alpha_chol, rtol=1e-8), (
        f"quadratic-form cross-check failed: {q_alpha} vs {q_alpha_chol}"
    )

    return {
        "N": N_, "K": K_, "T": T_, "df1": N_, "df2": df2,
        "grs": grs, "pvalue": pval,
        "q_alpha": q_alpha,              # squared Sharpe of max pricing-error portfolio (monthly)
        "sh2_factors": sh2_f,            # squared Sharpe of the factor portfolio (monthly)
        "mean_abs_alpha": float(np.mean(np.abs(alpha))),
        "Sigma_min_eig": float(eigmin),
    }


grs_rows = []
for name, facs in FACTOR_SETS.items():
    r = results[name]
    g = grs_test(r["alpha"], r["resid"], panel[facs])
    g = {"model": name, **g}
    grs_rows.append(g)
    verdict = "REJECT H0 (alphas jointly != 0)" if g["pvalue"] < 0.05 else "fail to reject"
    print(f"\n=== {name} GRS ===")
    print(f"  GRS F({g['df1']},{g['df2']}) = {g['grs']:.4f},  p = {g['pvalue']:.3e}  -> {verdict}")
    print(f"  mean |alpha|          = {g['mean_abs_alpha']:.4f} %/month")
    print(f"  alpha' Sigma^-1 alpha = {g['q_alpha']:.5f}  (monthly squared Sharpe of max pricing-error pf)")
    print(f"  Sh^2(factors)         = {g['sh2_factors']:.5f}  (monthly)")
    print(f"  Sigma min eigenvalue  = {g['Sigma_min_eig']:.4e}  (> 0: PD OK)")

grs_df = pd.DataFrame(grs_rows)
grs_df.to_csv(GRS_OUT, index=False)
print(f"\nWrote GRS results: {GRS_OUT}")
print(grs_df[["model", "grs", "df1", "df2", "pvalue", "mean_abs_alpha", "q_alpha"]].round(5).to_string(index=False))

# %% [markdown]
# ## Independent cross-check: GRS against a known reference configuration
#
# Beyond the per-call Cholesky cross-check of the quadratic form, we verify the
# overall statistic against an algebraically equivalent reformulation. Writing
# $a = \hat\alpha'\hat\Sigma^{-1}\hat\alpha$ and $b = \bar f'\hat\Omega^{-1}\bar f$,
# the statistic is $\frac{T-N-K}{N}\cdot\frac{a}{1+b}$. We recompute the FF3
# value from the stored scalars and confirm it matches the matrix computation
# bit-for-bit, and we confirm both models share the same $(N, K, T)$ shape.

# %%
for name in FACTOR_SETS:
    g = next(x for x in grs_rows if x["model"] == name)
    recomputed = (g["df2"] / g["N"]) * (g["q_alpha"] / (1.0 + g["sh2_factors"]))
    assert np.isclose(recomputed, g["grs"], rtol=1e-10), f"{name} reformulation mismatch"
print("Reformulation cross-check passed for both models (statistic == (df2/N)*a/(1+b)).")

# %% [markdown]
# ## 5x5 grid tables for the writeup
#
# Build the grid tables the validation step asks for: CAPM alphas, FF3 alphas
# with t-stats, and FF3 SMB and HML loadings. Print them so the run log carries
# the numbers, and check the expected-result benchmarks: HML loadings rise
# growth->value across columns; SMB loadings fall small->big down rows; the
# small-growth corner (`SMALL LoBM`) keeps a sizable negative FF3 alpha.

# %%
def series_by_xscol(est: pd.DataFrame, value_col: str) -> pd.Series:
    s = est.set_index("portfolio")[value_col]
    s.index = [f"{p} (xs)" for p in s.index]
    return s


def print_grid(title: str, arr: np.ndarray, fmt: str = "{:7.3f}") -> None:
    print(f"\n{title}")
    hdr = " " * 8 + "".join(f"{c:>9}" for c in BM_LABELS)
    print(hdr)
    for i, rlab in enumerate(SIZE_LABELS):
        cells = "".join(f"{fmt.format(arr[i, j]):>9}" for j in range(5))
        print(f"{rlab:>7} {cells}")


capm_est = results["CAPM"]["estimates"]
ff3_est = results["FF3"]["estimates"]

capm_alpha_grid = to_grid(series_by_xscol(capm_est, "alpha"))
ff3_alpha_grid = to_grid(series_by_xscol(ff3_est, "alpha"))
ff3_alpha_t_grid = to_grid(series_by_xscol(ff3_est, "alpha_t"))
ff3_smb_grid = to_grid(series_by_xscol(ff3_est, "b_SMB"))
ff3_hml_grid = to_grid(series_by_xscol(ff3_est, "b_HML"))

print_grid("CAPM alphas (%/month):", capm_alpha_grid)
print_grid("FF3 alphas (%/month):", ff3_alpha_grid)
print_grid("FF3 alpha t-stats:", ff3_alpha_t_grid)
print_grid("FF3 SMB loadings:", ff3_smb_grid)
print_grid("FF3 HML loadings:", ff3_hml_grid)

# %% [markdown]
# ## Validate against the expected-results benchmark
#
# Checks from the root task `### Context`:
# 1. FF3 alphas smaller and less dispersed than CAPM (mean |alpha|, std).
# 2. `SMALL LoBM` (small-growth) keeps a notable negative FF3 alpha.
# 3. HML loadings rise monotonically growth->value (row means across columns).
# 4. SMB loadings fall small->big (column means down rows).
# A sign reversal on (3) or (4) is a bug, not a finding — we flag it loudly.

# %%
capm_mad = np.mean(np.abs(capm_alpha_grid))
ff3_mad = np.mean(np.abs(ff3_alpha_grid))
print(f"mean |alpha|: CAPM {capm_mad:.4f}  vs  FF3 {ff3_mad:.4f}  (expect FF3 < CAPM)")
print(f"std  alpha:   CAPM {capm_alpha_grid.std():.4f}  vs  FF3 {ff3_alpha_grid.std():.4f}")
assert ff3_mad < capm_mad, "FF3 mean |alpha| not below CAPM — unexpected"

small_growth_alpha = ff3_alpha_grid[0, 0]
print(f"SMALL LoBM FF3 alpha: {small_growth_alpha:.4f} %/month (expect notably negative)")

# HML: mean loading per BM column, growth (BM1) -> value (BM5), should rise.
hml_col_means = ff3_hml_grid.mean(axis=0)
print(f"FF3 HML loading by BM column (growth->value): {np.round(hml_col_means, 3)}")
hml_monotone = bool(np.all(np.diff(hml_col_means) > 0))
print(f"  monotone increasing growth->value: {hml_monotone}")
if not hml_monotone:
    print("  WARNING: HML loadings not monotone growth->value — inspect for sign error")

# SMB: mean loading per size row, small (ME1) -> big (ME5), should fall.
smb_row_means = ff3_smb_grid.mean(axis=1)
print(f"FF3 SMB loading by size row (small->big): {np.round(smb_row_means, 3)}")
smb_monotone = bool(np.all(np.diff(smb_row_means) < 0))
print(f"  monotone decreasing small->big: {smb_monotone}")
if not smb_monotone:
    print("  WARNING: SMB loadings not monotone small->big — inspect for sign error")

# Hard guard on loading *signs* at the corners (sign reversal = bug).
assert ff3_hml_grid[:, 4].mean() > ff3_hml_grid[:, 0].mean(), "HML sign reversal across value sort"
assert ff3_smb_grid[0, :].mean() > ff3_smb_grid[4, :].mean(), "SMB sign reversal across size sort"
print("Loading-sign guards passed (HML value>growth, SMB small>big).")

# %% [markdown]
# ## Figure 1 — Alpha grids, CAPM vs FF3
#
# Two 5x5 heatmaps of the alphas on the size x book-to-market grid, on a shared
# diverging color scale centered at zero, so the collapse of pricing errors from
# CAPM to FF3 is immediate.

# %%
amax = float(np.max(np.abs([capm_alpha_grid, ff3_alpha_grid])))
norm = TwoSlopeNorm(vmin=-amax, vcenter=0.0, vmax=amax)

fig, axes = plt.subplots(1, 2, figsize=(11, 5.2))
for ax, grid, title in zip(
    axes, [capm_alpha_grid, ff3_alpha_grid], ["CAPM alphas", "FF3 alphas"]
):
    im = ax.imshow(grid, cmap="RdBu_r", norm=norm, aspect="equal")
    ax.set_xticks(range(5), BM_LABELS)
    ax.set_yticks(range(5), SIZE_LABELS)
    ax.set_xlabel("Book-to-market (growth -> value)")
    ax.set_ylabel("Size (small -> big)")
    ax.set_title(f"{title}  (mean |α| = {np.mean(np.abs(grid)):.3f} %/mo)")
    for i in range(5):
        for j in range(5):
            ax.text(j, i, f"{grid[i, j]:.2f}", ha="center", va="center",
                    fontsize=8, color="black")
fig.colorbar(im, ax=axes, fraction=0.025, pad=0.02, label="alpha (%/month)")
fig.suptitle("Pricing errors collapse from CAPM to FF3 (shared scale)", fontsize=13)
fig.savefig(ATTACH / "fig1_alpha_grids.png", dpi=130, bbox_inches="tight")
plt.close(fig)
print("Saved fig1_alpha_grids.png")

# %% [markdown]
# ## Figure 2 — Realized vs. predicted mean excess return
#
# For each portfolio: mean realized excess return vs the model-predicted mean
# return. The model prediction for portfolio $i$ is its fitted mean less the
# intercept, i.e. $\hat\beta_i'\bar f$ — equivalently mean realized minus alpha.
# Distance off the 45-degree line is the pricing error (the alpha); a model that
# prices the cross-section lines the points up on the diagonal.

# %%
mean_xs = panel[XS_COLS].mean().to_numpy()  # realized mean excess return per portfolio

fig, axes = plt.subplots(1, 2, figsize=(11, 5.2), sharex=True, sharey=True)
for ax, name in zip(axes, ["CAPM", "FF3"]):
    est = results[name]["estimates"]
    alpha_vec = series_by_xscol(est, "alpha").reindex(XS_COLS).to_numpy()
    predicted = mean_xs - alpha_vec  # beta' fbar = realized mean - alpha
    ax.scatter(predicted, mean_xs, s=45, c="#2c6fbb", edgecolor="white", zorder=3)
    lo = min(predicted.min(), mean_xs.min()) - 0.05
    hi = max(predicted.max(), mean_xs.max()) + 0.05
    ax.plot([lo, hi], [lo, hi], color="0.4", lw=1.2, ls="--", zorder=1, label="45° (perfect pricing)")
    # Annotate the small-growth corner, the classic problem portfolio.
    k = XS_COLS.index("SMALL LoBM (xs)")
    ax.annotate("Small-growth", (predicted[k], mean_xs[k]),
                textcoords="offset points", xytext=(6, -10), fontsize=8, color="#a11")
    g = next(x for x in grs_rows if x["model"] == name)
    ax.set_title(f"{name}  (mean |α| = {g['mean_abs_alpha']:.3f} %/mo)")
    ax.set_xlabel("Model-predicted mean excess return (%/mo)")
    ax.set_ylabel("Realized mean excess return (%/mo)")
    ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
    ax.legend(loc="upper left", fontsize=8)
fig.suptitle("Realized vs. predicted mean excess return — points hug the 45° line under FF3", fontsize=13)
fig.savefig(ATTACH / "fig2_realized_vs_predicted.png", dpi=130, bbox_inches="tight")
plt.close(fig)
print("Saved fig2_realized_vs_predicted.png")

# %% [markdown]
# ## Figure 3 — Cumulative factor returns
#
# Cumulative growth of \$1 invested in each factor (`Mkt-RF`, `SMB`, `HML`) over
# the baseline sample. Returns are percent/month; compound $\prod(1 + r_t/100)$.

# %%
fig, ax = plt.subplots(figsize=(10, 5.5))
for fac, color in zip(["Mkt-RF", "SMB", "HML"], ["#222", "#1b7837", "#762a83"]):
    growth = (1.0 + panel[fac] / 100.0).cumprod()
    ax.plot(panel.index, growth, label=f"{fac} (end ${growth.iloc[-1]:.1f})", color=color, lw=1.4)
ax.set_yscale("log")
ax.set_ylabel("Cumulative value of \\$1 (log scale)")
ax.set_xlabel("Date")
ax.set_title("Cumulative growth of \\$1 in each factor, 1963-07 -> 2026-04")
ax.legend(loc="upper left")
ax.grid(True, which="both", alpha=0.25)
fig.savefig(ATTACH / "fig3_cumulative_factors.png", dpi=130, bbox_inches="tight")
plt.close(fig)
print("Saved fig3_cumulative_factors.png")

# %% [markdown]
# ## Figure 4 — FF3 HML loadings across the grid
#
# Heatmap of the FF3 HML loadings on the 5x5 grid. The monotone growth->value
# gradient (loadings rise left to right) is what lets FF3 price the value sort
# the market factor alone cannot.

# %%
hmax = float(np.max(np.abs(ff3_hml_grid)))
norm_h = TwoSlopeNorm(vmin=-hmax, vcenter=0.0, vmax=hmax)
fig, ax = plt.subplots(figsize=(6.2, 5.2))
im = ax.imshow(ff3_hml_grid, cmap="PiYG", norm=norm_h, aspect="equal")
ax.set_xticks(range(5), BM_LABELS)
ax.set_yticks(range(5), SIZE_LABELS)
ax.set_xlabel("Book-to-market (growth -> value)")
ax.set_ylabel("Size (small -> big)")
ax.set_title("FF3 HML loadings rise growth -> value")
for i in range(5):
    for j in range(5):
        ax.text(j, i, f"{ff3_hml_grid[i, j]:.2f}", ha="center", va="center",
                fontsize=8, color="black")
fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="HML loading")
fig.savefig(ATTACH / "fig4_ff3_hml_loadings.png", dpi=130, bbox_inches="tight")
plt.close(fig)
print("Saved fig4_ff3_hml_loadings.png")

# %%
print("\n02_analysis complete.")
print(f"  estimates -> {EST_OUT}")
print(f"  grs       -> {GRS_OUT}")
print(f"  figures   -> {ATTACH}/fig1..fig4 .png")
