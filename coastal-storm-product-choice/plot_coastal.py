"""Slide figure for the coastal Natura 2000 wave-product replication (data: zenodo.20465505).

Storm Xaver (North Sea, Dec 2013): peak significant wave height from global WAVERYS (0.2 deg)
and regional NWS (~1.5 km), marine Natura 2000 sites outlined; plus per-storm attribution
outcome (biodiversity-weighted, resolvable sites), reproducing the published 27/44/29 split.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon
from shapely import wkb

HERE = Path(__file__).parent / "data"  # unzipped Zenodo deposit (download_data.sh)
STORM = "xaver"
wv = xr.open_dataset(HERE / f"clean/{STORM}_waverys.nc")["waverys_hs"].max("time")
rg = xr.open_dataset(HERE / f"clean/{STORM}_regional.nc")["regional_hs"].max("time")
sites = pd.read_parquet(HERE / f"clean/{STORM}_n2000_sites.parquet")
d = pd.read_csv(HERE / "results/per_site_delta.csv")
tiers = d[d.storm == STORM].set_index("site_code")["tier"]


def patches(geoms):
    out = []
    for g in geoms:
        g = wkb.loads(g) if isinstance(g, (bytes, bytearray)) else g
        for poly in getattr(g, "geoms", [g]):
            out.append(Polygon(np.asarray(poly.exterior.coords)[:, :2], closed=True))
    return out


plt.rcParams.update({"font.size": 15, "font.family": "DejaVu Sans"})
fig = plt.figure(figsize=(19, 6.8))
gs = fig.add_gridspec(1, 3, width_ratios=[1, 1, 0.95], wspace=0.18)
vmax = float(np.nanpercentile(rg.values, 99.5))
for k, (da, title, blind_tier) in enumerate([
        (wv, "Global WAVERYS · 0.2° (~22 km)", "regional_only"),
        (rg, "Regional CMEMS (NWS) · ~1.5 km", "waverys_only")]):
    ax = fig.add_subplot(gs[0, k])
    ax.set_facecolor("#D9D4C7")  # land / no data
    lon, lat = da["longitude"].values, da["latitude"].values
    im = ax.pcolormesh(lon, lat, da.values, cmap="viridis", vmin=0, vmax=vmax, shading="nearest")
    blind = sites["SITECODE"].map(tiers).eq(blind_tier).values
    ax.add_collection(PatchCollection(patches(sites.geometry[~blind]), facecolor="none", edgecolor="white", linewidth=1.1))
    ax.add_collection(PatchCollection(patches(sites.geometry[blind]), facecolor="#F1592C", edgecolor="#8A2A0B",
                                      linewidth=1.0, alpha=0.85))
    ax.set_xlim(3.0, 9.3); ax.set_ylim(52.8, 56.2); ax.set_aspect(1 / np.cos(np.radians(54.5)))
    ax.set_title(title, fontsize=16, fontweight="bold", color="#004F8F")
    ax.tick_params(labelsize=11)
    ax.text(0.02, 0.03, f"orange: {int(blind.sum())} sites this product sees as land", transform=ax.transAxes,
            fontsize=13, color="#8A2A0B", bbox=dict(facecolor="white", alpha=0.85, edgecolor="none"))
cax = fig.add_axes([0.14, 0.14, 0.42, 0.03])
fig.colorbar(im, cax=cax, orientation="horizontal", label="storm peak wave height (m)")

ax = fig.add_subplot(gs[0, 2])
r = d[d.resolvable]
rows = []
for name, g in [("Xynthia\n2010", r[r.storm == "xynthia"]), ("Xaver\n2013", r[r.storm == "xaver"]),
                ("Gloria\n2020", r[r.storm == "gloria"]), ("All\n276 sites", r)]:
    w = g.weight.sum()
    rows.append((name, 100 * g[(g.tier == "both") & ~g.differs_headline].weight.sum() / w,
                 100 * g[(g.tier == "both") & g.differs_headline].weight.sum() / w,
                 100 * g[g.tier != "both"].weight.sum() / w))
x = np.arange(len(rows))
a = np.array([t[1] for t in rows]); m = np.array([t[2] for t in rows]); c = np.array([t[3] for t in rows])
ax.bar(x, c, color="#F1592C", label="decisive: water vs land")
ax.bar(x, m, bottom=c, color="#F79548", label="wave height differs")
ax.bar(x, a, bottom=c + m, color="#C9D3DC", label="agree")
for i in range(len(rows)):
    ax.text(i, c[i] + m[i] - 6, f"{c[i] + m[i]:.0f}%", ha="center", fontsize=15, fontweight="bold", color="#1F2A33")
ax.set_xticks(x, [t[0] for t in rows], fontsize=13); ax.set_ylim(0, 100); ax.set_ylabel("share of sites (biodiversity-weighted, %)")
ax.set_title("Does the product change the answer?", fontsize=16, fontweight="bold", color="#004F8F")
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2, frameon=False, fontsize=12)
ax.spines[["top", "right"]].set_visible(False)

fig.text(0.04, 0.005, "Storm Xaver, Dec 2013, German Bight and Wadden Sea. Copernicus Marine WAVERYS (doi:10.48670/moi-00022) vs NWS (doi:10.48670/moi-00060); "
         "EEA Natura 2000. Data: zenodo.20465505.", fontsize=10.5, color="#555")
fig.subplots_adjust(left=0.04, right=0.99, top=0.9, bottom=0.27)
fig.savefig(Path(__file__).parent / "figure" / "coastal_slide.png", dpi=110)
print("saved")
