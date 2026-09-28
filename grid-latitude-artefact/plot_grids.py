"""Slide 27 (models-geometry, backup) figure: same 1,000,000 uniform points on three grids (left) and true cell outlines at 0/60/80 N (right),
drawn to one km scale. Lat-lon 5 deg; Behrmann-type cylindrical equal-area (standard parallel 30 deg, ~309,000 km2 cells);
HEALPix depth 4 on WGS84 via healpix-geo (~166,000 km2). Colour-blind safe."""
from pathlib import Path
import healpix_geo.nested as hpx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from cells import latlon_cell, behrmann_cell, healpix_cell, shape

rng = np.random.default_rng(42); N = 1_000_000
lon = rng.uniform(-180, 180, N); lat = np.degrees(np.arcsin(rng.uniform(-1, 1, N)))
le, pe = np.arange(-180, 181, 5), np.arange(-90, 91, 5)
H_ll, _, _ = np.histogram2d(lon, lat, [le, pe])
se = np.linspace(-1, 1, 37); pe_b = np.degrees(np.arcsin(se))
H_b, _, _ = np.histogram2d(lon, np.sin(np.radians(lat)), [le, se])
D = np.uint8(4)  # HEALPix depth 4 (nside 16) on WGS84, via healpix-geo
cnt = np.bincount(hpx.lonlat_to_healpix(lon, lat, D, ellipsoid="WGS84").astype(np.int64), minlength=12 * 4**4)
glon, glat = np.meshgrid(np.linspace(-179.75, 179.75, 720), np.linspace(-89.75, 89.75, 360))
H_hp = cnt[hpx.lonlat_to_healpix(glon.ravel(), glat.ravel(), D, ellipsoid="WGS84").astype(np.int64)].reshape(glon.shape)

plt.rcParams.update({"font.size": 15, "font.family": "DejaVu Sans"})
fig = plt.figure(figsize=(19, 6.8))
cols = {"Lat-lon 5°": "#E69F00", "Behrmann": "#CC79A7", "HEALPix": "#0072B2"}
titles = [("Lat-lon 5°", "false equator–pole gradient"), ("Behrmann (equal-area)", "uniform counts"), ("HEALPix on WGS84", "uniform counts")]
for k, (t, sub) in enumerate(titles):
    ax = fig.add_axes([0.005 + k * 0.19, 0.3, 0.185, 0.52], projection="mollweide")
    if k == 0:
        m = ax.pcolormesh(np.radians(le), np.radians(pe), H_ll.T, cmap="viridis", vmin=0, vmax=650)
    elif k == 1:
        m = ax.pcolormesh(np.radians(le), np.radians(pe_b), H_b.T * (H_ll.sum() / H_b.sum()), cmap="viridis", vmin=0, vmax=650)
    else:
        m = ax.pcolormesh(np.radians(np.linspace(-180, 180, 721)), np.radians(np.linspace(-90, 90, 361)),
                          H_hp * (H_ll.mean() / cnt.mean()), cmap="viridis", vmin=0, vmax=650, rasterized=True)
    ax.set_xticklabels([]); ax.set_yticklabels([]); ax.grid(False)
    ax.set_title(t, fontsize=16, fontweight="bold", color=list(cols.values())[k], pad=8)
    ax.text(0.5, -0.1, sub, transform=ax.transAxes, ha="center", fontsize=14, color="#333", fontweight="bold" if k == 0 else "normal")
cax = fig.add_axes([0.1, 0.12, 0.38, 0.035]); cb = fig.colorbar(m, cax=cax, orientation="horizontal")
cb.set_label("points per cell (same 1,000,000 uniform points)", fontsize=13)

makers = {"Lat-lon 5°": lambda la: latlon_cell(la - 2.5), "Behrmann": behrmann_cell, "HEALPix": healpix_cell}
lats = [0, 60, 80]; L = 950
fig.text(0.775, 0.965, "HEALPix cells stay compact at every latitude", ha="center", fontsize=17, fontweight="bold", color="#004F8F")
for r, la in enumerate(lats):
    fig.text(0.585, 0.745 - r * 0.285, f"{la}°N", fontsize=15, fontweight="bold", va="center")
    for c, (name, f) in enumerate(makers.items()):
        ax = fig.add_axes([0.615 + c * 0.125, 0.625 - r * 0.285, 0.115, 0.255])
        lo, la_ = f(la)
        x, y, asp, area = shape(np.asarray(lo), np.asarray(la_))
        ax.fill(x, y, color=cols[name], alpha=0.85, clip_on=True)
        if y.max() > L or y.min() < -L: ax.text(0.5, 0.03, "continues ↑↓", transform=ax.transAxes, ha="center", fontsize=11, color="#333")
        ax.set_xlim(-L, L); ax.set_ylim(-L, L); ax.set_aspect("equal")
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values(): sp.set_color("#D5DBE2")
        ax.text(0.03, 0.97, f"{asp:.1f}×", transform=ax.transAxes, va="top", fontsize=13, fontweight="bold")
        if r == 0: ax.set_title(name, fontsize=14, color=cols[name], fontweight="bold")
fig.text(0.99, 0.005, "one km scale (boxes 1,900 km) · label = long ÷ short side · HEALPix: depth 4, WGS84 (healpix-geo)", ha="right", fontsize=11, color="#555")

(Path(__file__).parent / "figure").mkdir(exist_ok=True)
fig.savefig(Path(__file__).parent / "figure" / "grids_slide8.png", dpi=110)
