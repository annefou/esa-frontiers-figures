# Beni lowlands pipeline (Bolivia, bbox -67.5,-15.5,-64.5,-12.5)

Everything on WGS84 HEALPix via healpix-connector (see `../environments/healpix-connector.md`, export HEALPIX_CONNECTOR).
Run in this order:

| Step | Script | Needs | Writes |
|---|---|---|---|
| 0a | `00_get_cci_biomass.sh` | — | `data/*.tif` (ESA CCI Biomass v7.0, 2023) |
| 0b | `00_get_biomass_fh.py` | MAAP_OFFLINE_TOKEN (or MAAP_TOKEN_FILE) + MAAP_CLIENT_SECRET in env | `biomass_fh/*.tiff` (BIOMASS L2A FP_FH) |
| 1 | `beni_biomass_gbif.py` | 0a, GBIF API | `results/cells.npz`, `summary.json`, `mammals.json` (not shipped) |
| 2 | `beni_biomass_fh.py` | 0b, 1 | `results/fh_cells.npz`, `fh_summary.json` (quality rule: drop product if median quality < 1.0) |
| 3 | `beni_genome_to_space.py` | 1, 2, GBIF API, CHELSA v2.1 | `results/g2s_cells.npz`, `g2s_summary.json` |
| 4 | `beni_where_next.py` | 3 | `results/where_next.npz|json` |
| 5 | `beni_fire.py` | 1, Fire CCI (streamed from CEDA) | `results/fire_cells.npz`, `fire_summary.json` |
| 6 | `beni_postfire_records.py` | 1, 5, GBIF API | `results/post_fire_counts.npy`, `postfire_summary.json` |
| 7 | `beni_fire_result.py` | 0a, 5, CHELSA | `results/fire_result.npz|json` |

`biomass_fh_items.json` lists the 18 BIOMASS products found by the MAAP catalogue query (2026-09-25); 16 used,
2 excluded by the quality rule (see `results/fh_summary.json`).

Shipped: per-cell results only. Not shipped: raw rasters (re-downloadable), `mammals.json` (record-level), and
`threatened_records.json` (locations of threatened species — deliberately excluded). Note `fh_cells.npz` contains
the coordinates of GBIF mammal records (`mlon`, `mlat`) for plotting, as published by GBIF.
Re-running steps 1, 3, 6 against the live GBIF API will give slightly different counts.
