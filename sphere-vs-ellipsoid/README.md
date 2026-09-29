# Slide 7 (`space-answer`) — the HEALPix grid on WGS84, and why the ellipsoid matters

The slide figure is `figure/slide7_globes.png` (since deck v211): the three globes below, on their own; the
sphere-vs-WGS84 point is made in the slide text (points shift by up to 14 km, the maximum geodetic–authalic latitude
difference, 0.128° at 45°). The earlier composite `figure/slide7_grid.png` (deck up to v210) has two parts, both
computed with healpix-geo:

- **Top — the grid itself:** three orthographic globes at depth 0, 2 and 4 (12, 192 and 3,072 cells). Every pixel is
  assigned its WGS84 HEALPix cell, so the (curved) cell edges are exact. The base cell containing the Beni (Bolivia) is
  shaded at every depth: the same area split into 16, then 256 cells whose IDs share its prefix.
- **Bottom — sphere vs ellipsoid:** share of points that land in a different depth-10 (~6 km) cell when the sphere is
  used instead of WGS84, by latitude: close to 100 % at mid-latitudes.

    python make_healpix_grid.py          # -> figure/slide7_globes.png (slide), figure/slide7_grid.png, figure/healpix_grid_globes.png
    python make_sphere_vs_ellipsoid.py   # -> figure/healpix-sphere-vs-ellipsoid.png (the curve on its own)

Env: ../environments/plot.yml. Coastlines: `data/ne_110m_land.geojson`, Natural Earth 1:110m land (public domain),
shipped here. Colours checked for colour-vision deficiency (orange #D06A14 vs blue, ΔE ≥ 22).

`make_sphere_vs_ellipsoid.py` is extracted verbatim from GRID4EARTH/grid4earth.github.io
`scripts/figures/make_dggs_figures.py` (commit eb148fd). That repository declares no licence; this extract is by its
author (A. Fouilloux) and released here under MIT.

Checked 2026-09-29: `reference/slide7_globes.png` is the deck image, reproduced byte-identically by `make_healpix_grid.py`.
