"""Slide-15 figure: a result from co-located layers — 2024 burning vs pre-fire biomass and rainfall."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PolyCollection

HERE = Path(__file__).parent.parent / "beni-pipeline"  # derived per-cell results live there
FIG = Path(__file__).parent / "figure"
FIG.mkdir(exist_ok=True)
r = np.load(HERE / "results/fire_result.npz")
f = np.load(HERE / "results/fire_cells.npz")
s = json.load(open(HERE / "results/fire_result.json"))
burned, agb, rain, m = r["burned"], r["agb"], r["rain"], r["m"]

plt.rcParams.update({"font.size": 15, "font.family": "DejaVu Sans"})
fig, axes = plt.subplots(1, 2, figsize=(17, 7.0), gridspec_kw={"width_ratios": [1, 1.15]})

ax = axes[0]
polys = [np.column_stack([lo, la]) for lo, la in zip(f["vlon11"], f["vlat11"])]
ok = np.isfinite(burned)
pc = PolyCollection([p for p, k in zip(polys, ok) if k], array=100 * burned[ok], cmap="YlOrRd", clim=(0, 100), edgecolor="none")
ax.add_collection(pc)
forest = m & (agb >= 100)
ax.add_collection(PolyCollection([p for p, k in zip(polys, forest) if k], facecolor="#006B3A", alpha=0.45, edgecolor="none"))
ax.fill_between([], [], color="#006B3A", alpha=0.45, label="dense forest before the fires\n(≥100 Mg/ha, CCI 2023)")
fig.colorbar(pc, ax=ax, fraction=0.046, pad=0.02, label="area burned in 2024 (%)")
ax.set_xlim(-67.5, -64.5); ax.set_ylim(-15.5, -12.5); ax.set_aspect(1 / np.cos(np.radians(-14)))
ax.legend(loc="lower right", fontsize=12, frameon=True)
ax.set_title("2024 fires (Fire CCI) over pre-fire forest (CCI Biomass)\n~3.2 km equal-area cells, WGS84", fontsize=15)

ax = axes[1]
edges = [0, 10, 25, 50, 100, 150, 400]
labels = ["<10", "10–25", "25–50", "50–100", "100–150", "≥150"]
rt = np.nanpercentile(rain[m], [33.3, 66.7])
groups = [("drier third", rain < rt[0], "#F1592C"), ("middle", (rain >= rt[0]) & (rain < rt[1]), "#F79548"),
          ("wetter third", rain >= rt[1], "#00B0AD")]
x = np.arange(len(labels)); wdt = 0.27
for gi, (name, gk, col) in enumerate(groups):
    vals = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        k = m & gk & (agb >= lo) & (agb < hi)
        vals.append(100 * burned[k].mean() if k.sum() >= 30 else np.nan)
    ax.bar(x + (gi - 1) * wdt, vals, wdt, color=col, label=f"{name} (rain)")
ax.set_xticks(x, labels); ax.set_xlabel("pre-fire above-ground biomass, 2023 (Mg/ha)")
ax.set_ylabel("area burned in 2024 (%)")
ax.set_title(f"Burning falls with pre-fire biomass — in every rainfall band\n{s['n_cells']:,} cells · fire × biomass × rain on one grid", fontsize=15)
ax.legend(frameon=False, fontsize=13)
ax.spines[["top", "right"]].set_visible(False)

fig.text(0.01, 0.005, "ESA Fire_cci SYN v1.1 (doi:10.5285/d441079fc77f49fabeb41330612b252f); ESA CCI Biomass v7.0 2023 (doi:10.5285/6429d1aafe1e43b9b414e4a5a7f8b903); "
         "CHELSA v2.1. Bars: ≥30 cells. Association, not causation.", fontsize=10.5, color="#555")
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig(FIG / "beni_fire_result.png", dpi=110)
print("saved")
