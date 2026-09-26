"""Figure for the Beni ESA CCI Biomass x GBIF demo (reads results/cells.npz, summary.json)."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PolyCollection
from matplotlib.colors import LogNorm

HERE = Path(__file__).parent.parent / "beni-pipeline"  # derived per-cell results live there
FIG = Path(__file__).parent / "figure"
FIG.mkdir(exist_ok=True)
d = np.load(HERE / "results/cells.npz")
s = json.load(open(HERE / "results/summary.json"))
polys = [np.column_stack([lo, la]) for lo, la in zip(d["vlon"], d["vlat"])]
agb, cnt = d["agb_mean"], d["counts"]

plt.rcParams.update({"font.size": 14, "font.family": "DejaVu Sans"})
fig, axes = plt.subplots(1, 3, figsize=(16, 6.9), gridspec_kw={"width_ratios": [1, 1, 1.05]})

ax = axes[0]
pc = PolyCollection(polys, array=agb, cmap="YlGn", edgecolor="none")
ax.add_collection(pc)
fig.colorbar(pc, ax=ax, fraction=0.046, pad=0.02, label="Above-ground biomass (Mg/ha)")
ax.set_title("ESA CCI Biomass v7.0 (2023)\nmean per HEALPix cell, WGS84, depth 9", fontsize=14)

ax = axes[1]
zero = cnt == 0
ax.add_collection(PolyCollection([p for p, z in zip(polys, zero) if z], facecolor="#E9ECEF",
                                 edgecolor="#C9CED4", linewidth=0.3, hatch="///"))
pc2 = PolyCollection([p for p, z in zip(polys, zero) if not z], array=cnt[~zero], cmap="OrRd",
                     norm=LogNorm(vmin=1, vmax=max(10, cnt.max())), edgecolor="none")
ax.add_collection(pc2)
fig.colorbar(pc2, ax=ax, fraction=0.046, pad=0.02, label="GBIF records per cell (log)")
g = s["gbif_all_taxa"]
ax.set_title(f"GBIF occurrences, all taxa\nhatched: no record ({g['cells_without_records']} of "
             f"{s['grid']['n_cells']} cells)", fontsize=14)

for ax in axes[:2]:
    ax.set_xlim(s["region"]["bbox_lonlat"][0], s["region"]["bbox_lonlat"][2])
    ax.set_ylim(s["region"]["bbox_lonlat"][1], s["region"]["bbox_lonlat"][3])
    ax.set_aspect(1 / np.cos(np.radians(-14)))
    ax.set_xlabel("Longitude"); ax.set_ylabel("Latitude")

ax = axes[2]
bins = np.linspace(0, np.percentile(agb, 99.5), 30)
ax.hist(agb, bins=bins, density=True, color="#4C9A6A", alpha=0.55, label="all cells (the region)")
ax.hist(agb, bins=bins, weights=cnt, density=True, histtype="step", linewidth=2.5,
        color="#D2461E", label="weighted by GBIF records\n(where people looked)")
ax.set_xlabel("Above-ground biomass per cell (Mg/ha)"); ax.set_ylabel("Density")
ax.set_title("Is the biodiversity sample representative\nof the biomass landscape?", fontsize=14)
ax.legend(frameon=False, fontsize=12)

fig.text(0.01, 0.005, "Data: ESA CCI Biomass v7.0 (Santoro & Cartus 2026, doi:10.5285/6429d1aafe1e43b9b414e4a5a7f8b903); "
         f"GBIF.org occurrence search, retrieved {g['retrieved_at'][:10]}. Grid: HEALPix on WGS84 via healpix-connector.",
         fontsize=10, color="#555")
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig(FIG / "beni_biomass_gbif.png", dpi=110)
print("saved")
