"""Slide-14 figure: BIOMASS forest height + GBIF on WGS84 HEALPix; unevenness of the sample."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PolyCollection
from matplotlib.colors import LinearSegmentedColormap

HERE = Path(__file__).parent.parent / "beni-pipeline"  # derived per-cell results live there
FIG = Path(__file__).parent / "figure"
FIG.mkdir(exist_ok=True)
f = np.load(HERE / "results/fh_cells.npz")
c = np.load(HERE / "results/cells.npz")
g = json.load(open(HERE / "results/summary.json"))

well = f["frac9"] >= 0.8  # 12.7-km cells at least 80 % observed by BIOMASS
stats = {"n_cells": int(well.sum())}

plt.rcParams.update({"font.size": 15, "font.family": "DejaVu Sans"})
fig, axes = plt.subplots(1, 2, figsize=(16, 7.2), gridspec_kw={"width_ratios": [1.1, 1]})

ax = axes[0]
polys = [np.column_stack([lo, la]) for lo, la in zip(f["vlon"], f["vlat"])]
# colour-blind safe: light-to-mid greens for height, records as black dots with white edge (contrast by lightness, not hue)
forest = LinearSegmentedColormap.from_list("forest", plt.get_cmap("YlGn")(np.linspace(0.05, 0.7, 256)))
pc = PolyCollection(polys, array=f["fh"], cmap=forest, edgecolor="none", clim=(0, 30))
ax.add_collection(pc)
ax.scatter(f["mlon"], f["mlat"], s=9, c="#111111", edgecolors="#FFFFFF", linewidths=0.4, label="GBIF mammal records")
fig.colorbar(pc, ax=ax, fraction=0.046, pad=0.02, label="BIOMASS forest height (m)")
ax.set_xlim(-67.5, -64.5); ax.set_ylim(-15.5, -12.5); ax.set_aspect(1 / np.cos(np.radians(-14)))
ax.set_xlabel("Longitude"); ax.set_ylabel("Latitude")
ax.legend(loc="lower right", frameon=True, fontsize=12, markerscale=4)
for x, y in [(-66.02, -12.95), (-66.47, -15.05)]:
    ax.annotate("flagged by\nquality layer:\nexcluded", xy=(x, y), xytext=(x - 0.95, y + 0.05), fontsize=11,
                color="#333", arrowprops=dict(arrowstyle="->", color="#555", lw=1.2))
ax.set_title("BIOMASS L2A forest height, Apr–Aug 2026\nGBIF mammals · HEALPix WGS84 (~1.6 km)", fontsize=15)

ax = axes[1]
for key, label, col in [("counts", "all taxa", "#0072B2"), ("mammal_counts", "mammals", "#111111")]:
    v = np.sort(c[key][well])[::-1].astype(float)
    x = np.arange(1, v.size + 1) / v.size * 100
    y = np.cumsum(v) / v.sum() * 100
    ax.plot(np.r_[0, x], np.r_[0, y], color=col, linewidth=3, label=label)
    k5 = max(1, int(round(0.05 * v.size)))
    stats[key] = {"records": int(v.sum()), "top5pct_share": round(float(v[:k5].sum() / v.sum() * 100), 1),
                  "empty_cells_pct": round(float((v == 0).mean() * 100), 1)}
ax.plot([0, 100], [0, 100], color="#999", linestyle=":", linewidth=1.5, label="perfectly even sampling")
a, m = stats["counts"], stats["mammal_counts"]
ax.axvline(5, color="#555", linewidth=1, linestyle="--")
ax.text(6.5, 40, f"5% of cells hold\n{a['top5pct_share']:.0f}% of all records\n{m['top5pct_share']:.0f}% of mammal records",
        fontsize=14, color="#222")
ax.text(52, 12, f"no record at all:\n{a['empty_cells_pct']:.0f}% of cells (all taxa)\n{m['empty_cells_pct']:.0f}% of cells (mammals)",
        fontsize=14, color="#222")
ax.set_xlim(0, 100); ax.set_ylim(0, 102)
ax.set_xlabel("Share of cells, most-sampled first (%)"); ax.set_ylabel("Cumulative share of GBIF records (%)")
ax.set_title(f"How even is the sample?\n{stats['n_cells']} cells observed by BIOMASS (~12.7 km)", fontsize=15)
ax.legend(frameon=False, fontsize=13, loc="lower right", bbox_to_anchor=(1.0, 0.25))

fig.text(0.01, 0.005, "Data: ESA BIOMASS L2A FP_FH (ESA MAAP, BPS 4.4.4; 16 of 18 products, 2 excluded by quality flag); "
         f"GBIF.org occurrence search, retrieved {g['gbif_all_taxa']['retrieved_at'][:10]}. Grid: HEALPix on WGS84 via healpix-connector.",
         fontsize=10.5, color="#555")
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig(FIG / "beni_biomass_fh_gbif_v2.png", dpi=110)
json.dump(stats, open(HERE / "results/unevenness.json", "w"), indent=1)
print(json.dumps(stats, indent=1))
