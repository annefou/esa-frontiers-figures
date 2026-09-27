# Slide 7 (`space-answer`) — sphere vs WGS84 HEALPix (GRID4EARTH)

Share of points that land in a different depth-10 (~6 km) HEALPix cell when the sphere is used instead of the
WGS84 ellipsoid, by latitude (healpix-geo). Code extracted verbatim from GRID4EARTH/grid4earth.github.io
`scripts/figures/make_dggs_figures.py` (commit eb148fd).

    python make_sphere_vs_ellipsoid.py   # -> figure/healpix-sphere-vs-ellipsoid.png (env: ../environments/plot.yml)

Checked 2026-09-26: same curve (max 100% reassigned); PNG 1 px larger with a newer matplotlib.
The GRID4EARTH website repository declares no licence; this extract is by its author (A. Fouilloux) and released here under MIT.
