# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib"]
# ///
"""Generate the size-decile average-return bar chart for the showcase demo.

The numbers are illustrative figures for a documentation demo, consistent with
the planted size premium in the simulated panel — not real market data.
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

deciles = list(range(1, 11))
# Average monthly value-weighted return (%) per size decile.
# Small firms (decile 1) earn more; the spread is the planted size premium.
avg_ret = [1.05, 0.98, 0.94, 0.91, 0.88, 0.85, 0.83, 0.80, 0.78, 0.74]

fig, ax = plt.subplots(figsize=(6.4, 3.6))
ax.bar(deciles, avg_ret, color="#4C72B0", edgecolor="white")
ax.set_xlabel("Size decile  (1 = smallest, 10 = largest)")
ax.set_ylabel("Avg. monthly return (%)")
ax.set_title("Average return falls monotonically with firm size")
ax.set_xticks(deciles)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
fig.tight_layout()
fig.savefig("attachments/size_decile_returns.png", dpi=130)
print("wrote attachments/size_decile_returns.png")
