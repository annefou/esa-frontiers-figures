"""Slide 9 (biomass-fh) figure: BIOMASS forest height + GBIF on WGS84 HEALPix, with a zoom on the cells.

Left: the Beni at depth 12 (~1.6 km cells), GBIF mammal records, the zoom window.
Middle: zoom near Trinidad (~27 km): every cell is a WGS84 HEALPix cell (healpix-geo, via healpix-connector),
coloured by BIOMASS forest height; GBIF records as dots; a record's stated uncertainty as a dashed circle,
and its footprint outlined: the cells healpix-connector spreads it over (cone_coverage on WGS84), shown at depth 12.
The pipeline itself spreads records at depth 9 (~12.7 km), where this record covers 2 cells.
Right: how even the sample is (12.7 km cells, depth 9).
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import healpix_geo.nested as hpx
import numpy as np
from matplotlib.collections import PolyCollection
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle

HERE = Path(__file__).parent.parent / "beni-pipeline"  # derived per-cell results live there
FIG = Path(__file__).parent / "figure"
FIG.mkdir(exist_ok=True)
f = np.load(HERE / "results/fh_cells.npz")
c = np.load(HERE / "results/cells.npz")
z = np.load(HERE / "results/fh_zoom_records.npz")
g = json.load(open(HERE / "results/summary.json"))
W = z["window"]  # lon_min, lat_min, lon_max, lat_max
INK, SPREAD = "#1F2A33", "#D06A14"
KM_LAT, KM_LON = 110.57, 111.32 * np.cos(np.radians(-14.8))

well = f["frac9"] >= 0.8  # 12.7-km cells at least 80 % observed by BIOMASS
stats = {"n_cells": int(well.sum())}
forest = LinearSegmentedColormap.from_list("forest", plt.get_cmap("YlGn")(np.linspace(0.05, 0.7, 256)))
polys = [np.column_stack([lo, la]) for lo, la in zip(f["vlon"], f["vlat"])]

plt.rcParams.update({"font.size": 15, "font.family": "DejaVu Sans"})
fig = plt.figure(figsize=(17.8, 8.0))

# --- overview --------------------------------------------------------------------------------------
ax = fig.add_axes([0.035, 0.19, 0.30, 0.69])
pc = PolyCollection(polys, array=f["fh"], cmap=forest, edgecolor="none", clim=(0, 30))
ax.add_collection(pc)
ax.scatter(f["mlon"], f["mlat"], s=7, c="#111111", edgecolors="#FFFFFF", linewidths=0.3)
ax.add_patch(Rectangle((W[0], W[1]), W[2] - W[0], W[3] - W[1], fill=False, ec=SPREAD, lw=2.5))
ax.text(W[0] - 0.02, W[3] + 0.05, "zoom", ha="right", color=INK, fontsize=17, fontweight="bold")
for x, y in [(-66.02, -12.95), (-66.47, -15.05)]:
    ax.annotate("quality flag:\nexcluded", xy=(x, y), xytext=(x - 0.95, y + 0.1), fontsize=14,
                color="#333", arrowprops=dict(arrowstyle="->", color="#555", lw=1.1))
ax.set_xlim(-67.5, -64.5); ax.set_ylim(-15.5, -12.5); ax.set_aspect(1 / np.cos(np.radians(-14)))
ax.set_xticks([-67, -66, -65]); ax.set_yticks([-15, -14, -13]); ax.tick_params(labelsize=13)
ax.set_title("BIOMASS forest height\n+ GBIF mammals, Beni", fontsize=18)
cax = fig.add_axes([0.06, 0.095, 0.25, 0.025])
fig.colorbar(pc, cax=cax, orientation="horizontal").set_label("BIOMASS L2A forest height (m)", fontsize=15)
cax.tick_params(labelsize=13)

# --- zoom ------------------------------------------------------------------------------------------
ax = fig.add_axes([0.37, 0.19, 0.32, 0.69])
clon, clat = f["vlon"].mean(1), f["vlat"].mean(1)
pad = 0.02
inz = (clon > W[0] - pad) & (clon < W[2] + pad) & (clat > W[1] - pad) & (clat < W[3] + pad)
zp = [polys[i] for i in np.where(inz)[0]]
ax.add_collection(PolyCollection(zp, array=f["fh"][inz], cmap=forest, clim=(0, 30), edgecolor="#FFFFFF", linewidth=0.8))
# one example record: its stated uncertainty (dashed circle) and the cells it is spread over (outlined)
EX = (-64.901, -14.7355)  # a mammal record stating 2.9 km, north of the Trinidad cluster
i = int(np.argmin((z["lon"] - EX[0]) ** 2 + (z["lat"] - EX[1]) ** 2))
lo, la, rk = z["lon"][i], z["lat"][i], z["unc"][i] / 1000
# footprint exactly as healpix-connector v0.1.0 computes it (cells.footprint_cells): every WGS84 cell the
# uncertainty disc touches (healpix-geo cone_coverage), plus the record's own cell -- here at depth 12
M_PER_DEG = 6_371_008.8 * np.pi / 180.0
cov = hpx.cone_coverage((float(lo), float(la)), float(rk * 1000) / M_PER_DEG, np.uint8(12), ellipsoid="WGS84", flat=True)
own = hpx.lonlat_to_healpix(np.array([lo]), np.array([la]), np.uint8(12), ellipsoid="WGS84")
fp = np.union1d(np.asarray(cov[0], dtype=np.uint64), own)
vlo, vla = hpx.vertices(fp, np.uint8(12), ellipsoid="WGS84", step=8)
vlo = (np.asarray(vlo) + 180) % 360 - 180  # vertices come back in 0-360°
ax.add_collection(PolyCollection([np.column_stack([a, b]) for a, b in zip(vlo, np.asarray(vla))],
                                 facecolor="none", edgecolor=SPREAD, linewidth=2.6, zorder=4))
covered = fp
tt = np.linspace(0, 2 * np.pi, 160)
ax.plot(lo + rk / KM_LON * np.cos(tt), la + rk / KM_LAT * np.sin(tt), color=SPREAD, lw=2.2, ls=(0, (5, 3)), zorder=4)
ax.scatter(z["lon"], z["lat"], s=20, c="#111111", edgecolors="#FFFFFF", linewidths=0.6, zorder=5)
ax.scatter([lo], [la], s=90, c=SPREAD, edgecolors=INK, linewidths=1.5, zorder=6)
ax.annotate(f"one record, uncertainty {rk:.1f} km\n→ spread over the {int(covered.size)}\n    cells it may fall in",
            xy=(lo + rk / KM_LON * 0.72, la + rk / KM_LAT * 0.72), xytext=(W[2] - 0.008, W[3] - 0.012),
            fontsize=17, color=INK, va="top", ha="right", bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="none", alpha=0.9),
            arrowprops=dict(arrowstyle="-", color=INK, lw=1.2), zorder=7)
ax.set_xlim(W[0], W[2]); ax.set_ylim(W[1], W[3]); ax.set_aspect(1 / np.cos(np.radians(-14.8)))
ax.set_xticks([]); ax.set_yticks([])
for s_ in ax.spines.values():
    s_.set_color(SPREAD); s_.set_linewidth(2.5)
ax.plot([W[0] + 0.012, W[0] + 0.012 + 5 / KM_LON], [W[1] + 0.012] * 2, color=INK, lw=3, zorder=7)
ax.text(W[0] + 0.012 + 2.5 / KM_LON, W[1] + 0.017, "5 km", ha="center", fontsize=16, color=INK, zorder=7,
        bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))
ax.set_title("Zoom near Trinidad: each tile is\none WGS84 HEALPix cell (~1.6 km)", fontsize=18)
ax.text(0.5, -0.03, "tiles: BIOMASS forest height · dots: GBIF mammal records\nEO and GBIF joined by cell ID (depth 12)", transform=ax.transAxes,
        ha="center", va="top", fontsize=15, color="#333")
stats["zoom"] = {"records": int(z["lon"].size), "example_uncertainty_km": round(float(rk), 2),
                 "example_footprint_cells_depth12": int(covered.size), "cells_in_view": int(inz.sum())}

# --- unevenness ------------------------------------------------------------------------------------
ax = fig.add_axes([0.775, 0.22, 0.215, 0.60])
for key, label, col in [("counts", "all taxa", "#0072B2"), ("mammal_counts", "mammals", "#111111")]:
    v = np.sort(c[key][well])[::-1].astype(float)
    x = np.arange(1, v.size + 1) / v.size * 100
    y = np.cumsum(v) / v.sum() * 100
    ax.plot(np.r_[0, x], np.r_[0, y], color=col, linewidth=2.5, label=label)
    k5 = max(1, int(round(0.05 * v.size)))
    stats[key] = {"records": int(v.sum()), "top5pct_share": round(float(v[:k5].sum() / v.sum() * 100), 1),
                  "empty_cells_pct": round(float((v == 0).mean() * 100), 1)}
ax.plot([0, 100], [0, 100], color="#999", linestyle=":", linewidth=1.5, label="even sampling")
a, m = stats["counts"], stats["mammal_counts"]
ax.axvline(5, color="#555", linewidth=1, linestyle="--")
ax.text(8, 38, f"5% of cells hold\n{a['top5pct_share']:.0f}% of records\n({m['top5pct_share']:.0f}% mammals)", fontsize=16, color="#222")
ax.set_xlim(0, 100); ax.set_ylim(0, 102)
ax.tick_params(labelsize=13)
ax.set_xlabel("cells, most-sampled first (%)", fontsize=15); ax.set_ylabel("cumulative GBIF records (%)", fontsize=15)
ax.set_title(f"How even is the sample?\n{stats['n_cells']} cells of ~12.7 km", fontsize=18)
ax.legend(frameon=False, fontsize=14, loc="lower right")

fig.savefig(FIG / "beni_biomass_fh_gbif_zoom.png", dpi=110)
json.dump(stats, open(HERE / "results/unevenness_zoom.json", "w"), indent=1)
print(json.dumps(stats["zoom"]))
