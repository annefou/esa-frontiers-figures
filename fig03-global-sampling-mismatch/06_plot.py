"""Slide-3 figure v2: GBIF records per km2 on equal-area WGS84 HEALPix (depth 6, ~110 km), ocean greyed,
biodiversity hotspots outlined; right: record density per hotspot vs the land average."""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import shapefile
import shapely
from matplotlib.collections import PolyCollection
from matplotlib.colors import LogNorm
from shapely.geometry import shape
from shapely.ops import unary_union

g6 = np.load("data/cells_d6.npz")
ph = json.load(open("data/per_hotspot.json"))
meta = json.load(open("data/gbif_bins.json"))
landf = g6["landf"]
cnt = np.load("data/counts_d6.npy")  # all records per depth-6 cell, land and ocean
dens = cnt / (4 * np.pi * 6371.0**2 / cnt.size)

plt.rcParams.update({"hatch.linewidth": 0.8, "font.size": 15, "font.family": "DejaVu Sans"})
fig = plt.figure(figsize=(19, 7.2))
ax = fig.add_axes([0.02, 0.15, 0.62, 0.78])
ax.set_facecolor("#FFFFFF")
keep = np.ones(cnt.size, bool)
polys, vals = [], []
for lo, la, v in zip(g6["vlon"][keep], g6["vlat"][keep], dens[keep]):
    if lo.max() - lo.min() > 180:
        continue
    polys.append(np.column_stack([lo, la])); vals.append(v)
vals = np.array(vals)
pc = PolyCollection(polys, array=np.where(vals > 0, vals, 1e-4), cmap="magma_r",
                    norm=LogNorm(vmin=0.001, vmax=1000), edgecolor="none")
ax.add_collection(pc)
r = shapefile.Reader("external/hotspots_2016_1.shp")
for sh, rec in zip(r.shapes(), r.records()):
    if rec[1] != "hotspot area":
        continue
    gg = shape(sh.__geo_interface__)
    for p in getattr(gg, "geoms", [gg]):
        x, y = p.exterior.xy
        ax.fill(x, y, facecolor="none", edgecolor="#00B0AD", hatch="//", linewidth=0, alpha=0.8)
        ax.plot(x, y, color="#00A09D", linewidth=2.0)
import json as _j
land = [shape(f["geometry"]) for f in _j.load(open("external/ne_50m_land.geojson"))["features"]]
for gg in land:
    for p in getattr(gg, "geoms", [gg]):
        x, y = p.exterior.xy
        ax.plot(x, y, color="#5A6670", linewidth=0.6)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(facecolor="none", edgecolor="#00A09D", hatch="///", linewidth=2, label="biodiversity hotspots (terrestrial)")],
          loc="lower left", fontsize=13, frameon=True)
ax.set_xlim(-170, 180); ax.set_ylim(-57, 78); ax.set_aspect(1.2)
ax.set_xticks([]); ax.set_yticks([])
cb = fig.colorbar(pc, ax=ax, orientation="horizontal", fraction=0.05, pad=0.02)
cb.set_label("GBIF records per km², land and ocean (equal-area HEALPix cells, ~110 km)")
ax.set_title(f"{meta['total'] / 1e9:.1f} billion GBIF records on one equal-area grid", fontsize=17,
             fontweight="bold", color="#004F8F")

bx = fig.add_axes([0.73, 0.13, 0.25, 0.78])
pick = ["California Floristic Province", "Forests of East Australia", "Mediterranean Basin", "Tropical Andes",
        "Atlantic Forest", "Madagascar and the Indian Ocean Islands", "Sundaland",
        "Guinean Forests of West Africa", "Cerrado", "Wallacea", "Horn of Africa"]
rows = {x["hotspot"]: x for x in ph["hotspots"]}
short = {"California Floristic Province": "California", "Forests of East Australia": "East Australia",
         "Mediterranean Basin": "Mediterranean", "Madagascar and the Indian Ocean Islands": "Madagascar",
         "Guinean Forests of West Africa": "Guinean Forests"}
names = [short.get(p, p) for p in pick][::-1]
v = [rows[p]["per_km2"] for p in pick][::-1]
cols = ["#004F8F" if x > ph["land_average_per_km2"] else "#F1592C" for x in v]
bx.barh(names, v, color=cols)
bx.set_xscale("log")
bx.axvline(ph["land_average_per_km2"], color="#333", linestyle="--", linewidth=1.5)
bx.text(ph["land_average_per_km2"] * 1.1, -0.9, "land average", fontsize=12, color="#333")
for i, x in enumerate(v):
    bx.text(x * 1.12, i, f"{x:.1f}" if x < 10 else f"{x:.0f}", va="center", fontsize=12)
bx.set_xlabel("GBIF records per km²")
bx.set_title("Same endemism criterion,\n~600× difference in records", fontsize=15, fontweight="bold", color="#004F8F")
bx.spines[["top", "right"]].set_visible(False); bx.tick_params(axis="y", labelsize=13)
bx.set_xlim(0.3, 2000)
fig.text(0.02, 0.01, f"GBIF.org occurrence density (Maps API v2, retrieved {meta['retrieved']}) summed into WGS84 HEALPix cells; "
         "hotspots: Hoffman et al. 2016, doi:10.5281/zenodo.3261807 (CC BY-SA 4.0); land: Natural Earth. Bars: land area only.", fontsize=10.5, color="#555")
fig.savefig("figure/global_mismatch_v3.png", dpi=110)
print("saved")
