# Slide 27 (`models-geometry`, backup) — the grid shapes the answer

Left: the same 1,000,000 uniform random points (seed 42) counted on a 5° lat-lon grid, a Behrmann-type cylindrical
equal-area grid, and HEALPix depth 4 on WGS84 (healpix-geo). Only the lat-lon grid shows a gradient: equator cells hold
up to ~23× more points than polar ones. Right: true cell outlines at 0°, 60° and 80°N drawn to one km scale, labelled with
their elongation (long ÷ short side): lat-lon cells narrow (1.0, 1.9, 4.6), Behrmann cells become slivers (1.3, 2.7, 10.1),
HEALPix cells stay compact (1.2, 1.4, 1.3).

    python plot_grids.py     # env: ../environments/plot.yml -> figure/grids_slide8.png

`cells.py` builds the cell outlines (HEALPix via `healpix_geo.nested.vertices`, WGS84). The original synthetic proof
(22.9× cell-area ratio; 605 vs 27 points per cell) is `annefou/dggs-biodiversity-bias` (MIT, doi:10.5281/zenodo.19848749),
`notebooks/01_synthetic_proof.py` at commit fc9ca6e; `./run_upstream.sh` clones and runs it.

Checked 2026-09-28: `reference/grids_slide8.png` is the deck image and is reproduced byte-identically by `plot_grids.py`.
