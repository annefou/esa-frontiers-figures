# Slide 8 — a lat-lon grid manufactures a latitude gradient

One million uniform random points (seed 42) counted on a 5° lat-lon grid: up to ~23× more points per cell at the
equator than at 85°N (cell-area ratio 22.9×). From `annefou/dggs-biodiversity-bias` (MIT, doi:10.5281/zenodo.19848749),
`notebooks/01_synthetic_proof.py`, commit fc9ca6e. `./run_upstream.sh` clones and runs it.

Checked 2026-09-26: numbers identical (22.9×; 605 vs 27 points per cell); PNG 2 px taller with a newer matplotlib.
`reference/` holds the image used in the deck.
