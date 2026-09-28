# Slide 9 (`biomass-fh`) — BIOMASS L2A forest height and GBIF on WGS84 HEALPix, with a zoom on the cells

Three panels:

- **Beni overview:** BIOMASS L2A forest height on WGS84 HEALPix depth 12 (~1.6 km cells), GBIF mammal records, the two
  products excluded by the declared quality rule, and the zoom window.
- **Zoom near Trinidad (~27 km):** every tile is one WGS84 HEALPix cell coloured by forest height; GBIF records are
  dots. One record with a stated uncertainty of 2.9 km is shown with its uncertainty circle and its footprint: the 20
  depth-12 cells it may fall in, computed exactly as healpix-connector v0.1.0 does (`cells.footprint_cells`:
  healpix-geo `cone_coverage` on WGS84 plus the record's own cell). The footprint lines up with the forest-height tiles:
  EO and GBIF are joined by cell ID. (The pipeline itself spreads records at depth 9, ~12.7 km, where this record
  covers 2 cells.)
- **How even is the sample:** cumulative share of GBIF records against share of the 427 well-observed 12.7 km cells.

    python plot_fh3.py     # env: ../environments/plot.yml -> figure/beni_biomass_fh_gbif_zoom.png

Reads `../beni-pipeline/results/`: `fh_cells.npz`, `cells.npz`, `summary.json` and `fh_zoom_records.npz` (the zoom
window's records: longitude, latitude and stated uncertainty only; written by `02b_zoom_records.py`).
`plot_fh2.py` is the earlier two-panel version.

Checked 2026-09-28: `reference/beni_biomass_fh_gbif_zoom.png` is the deck image, reproduced byte-identically.
