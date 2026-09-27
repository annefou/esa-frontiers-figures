# Slide 4 (`esa-questions`) — GBIF sampling effort vs biodiversity hotspots

All 3.6 billion GBIF occurrence records (Maps API density, retrieved 2026-09-26) summed into equal-area
WGS84 HEALPix depth-6 cells (~110 km), land and ocean; terrestrial hotspots (Hoffman et al. 2016) hatched;
right: records per km² of land for 11 hotspots vs the land average.

Environment: `../environments/plot.yml`. Run from this folder:

    python 01_download_gbif_density.py   # optional: refreshes data/gbif_bins.* from the live GBIF index
    ./download_external.sh               # hotspots (CC BY-SA 4.0) + Natural Earth land -> external/
    python 02_prep_cells.py              # depth-8 WGS84 cell centres -> data/cells_d4.npz (not shipped, 6.8 MB)
    python 03_counts_d6.py               # data/counts_d6.npy
    python 04_land_fraction_d6.py        # data/cells_d6.npz
    python 05_per_hotspot.py             # data/per_hotspot.json
    python 06_plot.py                    # figure/global_mismatch_v3.png

Shipped: `data/gbif_bins.npz|json` (the 2026-09-26 retrieval), `counts_d6.npy`, `cells_d6.npz`, `per_hotspot.json`.
Skip step 1 to reproduce the deck figure exactly (checked: byte-identical). Caveats: records measure sampling effort;
bins are attributed to a hotspot by bin centre (0.35°), approximate for small hotspots; cell areas use a 6371 km
authalic radius.
