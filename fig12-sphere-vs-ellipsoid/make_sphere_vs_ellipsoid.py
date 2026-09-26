"""Slide 12: how often the reference surface (sphere vs WGS84) changes a point's HEALPix cell, by latitude.

Extracted verbatim from GRID4EARTH/grid4earth.github.io scripts/figures/make_dggs_figures.py
(commit eb148fd, author Anne Fouilloux) so it runs standalone; writes figure/healpix-sphere-vs-ellipsoid.png.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import healpix_geo.nested as hpx

OUT = Path(__file__).resolve().parent / "figure"
OUT.mkdir(exist_ok=True)
NAVY = "#0a2540"
TEAL = "#2a9d8f"
plt.rcParams.update({"font.size": 13, "axes.titlesize": 15, "axes.labelsize": 13,
                     "xtick.labelsize": 12, "ytick.labelsize": 12})


def make_sphere_vs_ellipsoid(out="healpix-sphere-vs-ellipsoid.png", depth=10):
    """How often the reference surface (sphere vs WGS84) changes a point's HEALPix
    cell, as a function of latitude. A clean curve — no per-pixel map (which would
    alias into moiré near the poles where HEALPix cells fan out)."""
    lons = np.linspace(-180, 180, 1440)
    lats = np.linspace(-89.5, 89.5, 720)
    lon_g, lat_g = np.meshgrid(lons, lats)
    s = hpx.lonlat_to_healpix(lon_g.ravel(), lat_g.ravel(), depth, ellipsoid="sphere")
    e = hpx.lonlat_to_healpix(lon_g.ravel(), lat_g.ravel(), depth, ellipsoid="WGS84")
    frac = 100.0 * (s != e).reshape(lat_g.shape).mean(axis=1)

    fig, ax = plt.subplots(figsize=(11.0, 4.6), dpi=200)
    ax.fill_between(lats, 0, frac, color=TEAL, alpha=0.22)
    ax.plot(lats, frac, color=NAVY, lw=2.5)
    ax.set_title(f"Spherical vs WGS84 HEALPix: cell reassignment by latitude (depth {depth})")
    ax.set_xlabel("latitude (°)")
    ax.set_ylabel("% of points moved to a different cell")
    ax.set_xlim(-90, 90); ax.set_ylim(0, max(5, frac.max() * 1.08))
    ax.set_xticks([-90, -60, -30, 0, 30, 60, 90])
    ax.grid(alpha=0.3)
    ax.margins(x=0)
    fig.tight_layout()
    fig.savefig(OUT / out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", out, f"(max {frac.max():.1f}% reassigned)")


if __name__ == "__main__":
    make_sphere_vs_ellipsoid()
