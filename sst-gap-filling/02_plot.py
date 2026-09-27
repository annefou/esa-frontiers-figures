"""Slide 33 (fill-gaps, backup) figure: SST cloud-gap filling with the scattering transform (FOSCAT) on HEALPix,
from the FIESTA replication run (01_sst_gap_filling.py, maps saved to results/sst_maps.npz)."""
import json

import healpy as hp
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap

m = np.load("results/sst_maps.npz")
r = json.load(open("results/sst_gap_filling_results.json"))
ocean, clouds = m["ocean"], m["clouds"]
nside = hp.npix2nside(ocean.size)
lon = np.linspace(-180, 180, 1440); lat = np.linspace(-80, 80, 640)
LO, LA = np.meshgrid(lon, lat)
pix = hp.ang2pix(nside, np.deg2rad(90 - LA), np.deg2rad(LO % 360), nest=True)

def grid(v, mask):
    out = np.where(mask, v, np.nan)[pix] - 273.15
    return out

vmin, vmax = -2, 30
cm = plt.get_cmap("RdYlBu_r")
plt.rcParams.update({"font.size": 15, "font.family": "DejaVu Sans"})
fig, axs = plt.subplots(1, 4, figsize=(20, 5.4))
err_h = np.sqrt(np.mean((m["l4"] - m["harm"])[clouds] ** 2))
err_f = np.sqrt(np.mean((m["l4"] - m["foscat"])[clouds] ** 2))
panels = [
    ("1 · What the satellite sees", grid(m["l3s"], ocean & m["observed"]), "grey: no data (between orbits, low quality)"),
    ("2 · Smooth fill", grid(m["harm"], ocean), f"error in gaps: {err_h:.1f} °C"),
    ("3 · Scattering fill (FOSCAT)", grid(m["foscat"], ocean), f"error in gaps: {err_f:.1f} °C"),
    ("4 · Reference (L4 analysis)", grid(m["l4"], ocean), "gap-free product, for checking"),
]
land = grid(np.ones(ocean.size), ~ocean)  # not NaN where land
for ax, (title, img, sub) in zip(axs, panels):
    ax.set_facecolor("#B9C1C8")  # clouds
    ax.imshow(np.where(np.isnan(land), np.nan, 1.0), extent=[-180, 180, -80, 80], origin="lower",
              cmap=ListedColormap(["#E8E2D6"]), aspect="auto")
    im = ax.imshow(img, extent=[-180, 180, -80, 80], origin="lower", cmap=cm, vmin=vmin, vmax=vmax, aspect="auto")
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_color("#C9D3DC")
    ax.set_title(title, fontsize=17, fontweight="bold", color="#004F8F", loc="left")
    good = "FOSCAT" in title
    ax.text(0.0, -0.05, sub, transform=ax.transAxes, fontsize=16, va="top",
            color="#008F4C" if good else ("#F1592C" if "Smooth" in title else "#555"),
            fontweight="bold" if ("error" in sub) else "normal")
cax = fig.add_axes([0.35, 0.16, 0.3, 0.035])
cb = fig.colorbar(im, cax=cax, orientation="horizontal"); cb.set_label("sea-surface temperature (°C)", fontsize=14)
fig.subplots_adjust(left=0.01, right=0.99, top=0.9, bottom=0.36, wspace=0.05)
fig.savefig("figure/sst_slide16.png", dpi=110)
print(err_h, err_f, clouds.sum() / ocean.sum())
