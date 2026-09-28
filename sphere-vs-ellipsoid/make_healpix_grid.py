"""Slide 7 (space-answer) figure: what the HEALPix grid looks like on WGS84, and why the ellipsoid matters.

Top: three orthographic globes at depth 0, 2 and 4. Every pixel is assigned its WGS84 HEALPix cell with
healpix-geo, so cell edges are exact (they are curves, not great circles). The base cell containing the
Beni (Bolivia) is shaded at every depth: the same area, split into 16 at depth 2 and 256 at depth 4, with
nested IDs (parent = child >> 2 bits per level).
Bottom: share of points that land in a different depth-10 cell on the sphere instead of WGS84, by
latitude (same computation as make_sphere_vs_ellipsoid.py).
Coastlines: Natural Earth 110m land (public domain), fetched by download.sh.

Writes figure/healpix_grid_globes.png (globes only) and figure/slide7_grid.png (the slide composite).
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import healpix_geo.nested as hpx
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import to_rgb
from matplotlib.path import Path as MplPath

HERE = Path(__file__).parent
FIG = HERE / "figure"
FIG.mkdir(exist_ok=True)

LON0, LAT0 = -45.0, 5.0            # view centre: Atlantic; South America and Africa visible
BENI = (-65.5, -14.0)
INK, EDGE, HILITE, LAND, SEA, COAST, MARK = "#1F2A33", "#004F8F", "#D06A14", "#D5DBE1", "#FFFFFF", "#6B7780", "#5B8FC9"


def inverse_ortho(n):
    """Pixel grid -> lon/lat on the visible hemisphere (NaN outside the disc)."""
    y, x = np.mgrid[1:-1:n * 1j, -1:1:n * 1j]
    r2 = x**2 + y**2
    inside = r2 <= 1
    z = np.sqrt(np.clip(1 - r2, 0, None))
    p0, l0 = np.radians(LAT0), np.radians(LON0)
    lat = np.degrees(np.arcsin(np.clip(z * np.sin(p0) + y * np.cos(p0), -1, 1)))
    lon = (np.degrees(l0 + np.arctan2(x, z * np.cos(p0) - y * np.sin(p0))) + 180) % 360 - 180
    lon[~inside] = np.nan
    lat[~inside] = np.nan
    return lon, lat, inside


def ortho(lon, lat):
    l, p, p0 = np.radians(lon - LON0), np.radians(lat), np.radians(LAT0)
    return np.cos(p) * np.sin(l), np.cos(p0) * np.sin(p) - np.sin(p0) * np.cos(p) * np.cos(l)


def land_mask(lon, lat, inside):
    """Rasterise Natural Earth land on the pixel grid: exact clipping at the limb."""
    ok = inside.ravel()
    pts = np.column_stack([lon.ravel()[ok], lat.ravel()[ok]])
    hit = np.zeros(len(pts), bool)
    for feat in json.load(open(HERE / "data" / "ne_110m_land.geojson"))["features"]:
        g = feat["geometry"]
        for poly in (g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]):
            ring = np.asarray(poly[0])
            box = ((pts[:, 0] >= ring[:, 0].min()) & (pts[:, 0] <= ring[:, 0].max())
                   & (pts[:, 1] >= ring[:, 1].min()) & (pts[:, 1] <= ring[:, 1].max()))
            if box.any():
                hit[np.where(box)[0][MplPath(ring).contains_points(pts[box])]] = True
    m = np.zeros(inside.size, bool)
    m[ok] = hit
    return m.reshape(inside.shape)


def boundary(a, inside):
    e = np.zeros(a.shape, bool)
    e[:, :-1] |= a[:, :-1] != a[:, 1:]
    e[:-1, :] |= a[:-1, :] != a[1:, :]
    return e & inside


def blend(c, a, alpha=0.62):
    return (1 - alpha) * np.asarray(to_rgb(c)) + alpha * np.asarray(to_rgb(a))


class Globes:
    def __init__(self, n):
        self.n = n
        self.lon, self.lat, self.inside = inverse_ortho(n)
        self.land = land_mask(self.lon, self.lat, self.inside)
        self.coast = boundary(self.land, self.inside)
        self.beni0 = int(hpx.lonlat_to_healpix(np.array([BENI[0]]), np.array([BENI[1]]), np.uint8(0), ellipsoid="WGS84")[0])

    def draw(self, ax, depth, title_size=20, marker=9, label=False):
        n, ok, inside, land = self.n, self.inside.ravel(), self.inside, self.land
        cell = np.full(n * n, -1, dtype=np.int64)
        cell[ok] = hpx.lonlat_to_healpix(self.lon.ravel()[ok], self.lat.ravel()[ok], np.uint8(depth), ellipsoid="WGS84").astype(np.int64)
        cell = cell.reshape(n, n)
        fam = inside & ((cell >> (2 * depth)) == self.beni0)
        img = np.ones((n, n, 3))
        img[inside & ~land] = to_rgb(SEA)
        img[inside & land] = to_rgb(LAND)
        img[fam & ~land] = blend(SEA, HILITE)
        img[fam & land] = blend(LAND, HILITE)
        img[self.coast] = to_rgb(COAST)
        img[boundary(cell, inside)] = to_rgb(EDGE)
        ax.imshow(img, extent=(-1, 1, -1, 1), interpolation="antialiased")
        ax.add_patch(plt.Circle((0, 0), 1, fill=False, color=EDGE, lw=1.2))
        bx, by = ortho(*BENI)
        ax.plot(bx, by, "o", ms=marker, mfc=MARK, mec=INK, mew=1.3)
        if label:
            ax.annotate("Beni", xy=(bx, by), xytext=(-0.98, -0.78), fontsize=title_size * 0.8, color=INK,
                        arrowprops=dict(arrowstyle="-", color=INK, lw=1))
        ax.set_title(f"depth {depth} · {12 * 4**depth:,} cells", fontsize=title_size, color=INK, pad=6)
        ax.set_xlim(-1.03, 1.03); ax.set_ylim(-1.03, 1.03); ax.set_aspect(1); ax.axis("off")


def sphere_vs_wgs84(depth=10):
    lons, lats = np.linspace(-180, 180, 1440), np.linspace(-89.5, 89.5, 720)
    lon_g, lat_g = np.meshgrid(lons, lats)
    s = hpx.lonlat_to_healpix(lon_g.ravel(), lat_g.ravel(), depth, ellipsoid="sphere")
    e = hpx.lonlat_to_healpix(lon_g.ravel(), lat_g.ravel(), depth, ellipsoid="WGS84")
    return lats, 100.0 * (s != e).reshape(lat_g.shape).mean(axis=1)


def globes_only(g):
    plt.rcParams.update({"font.family": "DejaVu Sans"})
    fig, axes = plt.subplots(1, 3, figsize=(18, 6.9))
    for i, (ax, d) in enumerate(zip(axes, (0, 2, 4))):
        g.draw(ax, d, label=(i == 0))
    fig.text(0.5, 0.035, "Every cell has the same area and splits into 4 at the next depth; the shaded base cell keeps one ID prefix.\n"
             "Depth 10 ≈ 6 km (12.6 million cells) · depth 11 ≈ 3 km, the Beni analyses · on the WGS84 ellipsoid",
             ha="center", fontsize=15, color="#333F48")
    fig.subplots_adjust(left=0.01, right=0.99, top=0.92, bottom=0.14, wspace=0.03)
    fig.savefig(FIG / "healpix_grid_globes.png", dpi=110)
    plt.close(fig)


def slide_composite(g):
    """980 x 514 px slot on the slide, rendered at 2x."""
    plt.rcParams.update({"font.family": "DejaVu Sans"})
    fig = plt.figure(figsize=(9.8, 5.14), dpi=200)
    for i, d in enumerate((0, 2, 4)):
        ax = fig.add_axes([0.02 + i * 0.327, 0.365, 0.31, 0.565])
        g.draw(ax, d, title_size=15, marker=6.5, label=(i == 0))
    lats, frac = sphere_vs_wgs84()
    ax = fig.add_axes([0.075, 0.075, 0.885, 0.20])
    ax.fill_between(lats, 0, frac, color=EDGE, alpha=0.18, lw=0)
    ax.plot(lats, frac, color=EDGE, lw=1.4)
    ax.set_xlim(-90, 90); ax.set_ylim(0, 105)
    ax.set_xticks([-90, -60, -30, 0, 30, 60, 90]); ax.set_xticklabels(["90°S", "60°S", "30°S", "0°", "30°N", "60°N", "90°N"])
    ax.set_yticks([0, 50, 100]); ax.set_yticklabels(["0", "50", "100%"])
    ax.tick_params(labelsize=11.5, colors="#4A5560", length=2)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#9AA4AD")
    ax.grid(axis="y", color="#E3E7EB", lw=0.6)
    ax.text(0.0, 1.16, "Sphere instead of WGS84 (depth 10): share of points that land in a different cell",
            transform=ax.transAxes, fontsize=13, color=INK, fontweight="bold")
    fig.savefig(FIG / "slide7_grid.png", dpi=200, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    globes_only(Globes(1100))
    slide_composite(Globes(900))
    print("saved figure/healpix_grid_globes.png and figure/slide7_grid.png")
