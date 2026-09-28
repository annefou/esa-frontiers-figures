# Data sources and licences

Code in this repository is MIT (see LICENSE). Data and figures carry the licence of their sources.
"Included" = small derived files shipped here; "script" = fetched from the publisher by a script in the folder.

| Source | Slides | Licence / terms (checked 2026-09-26) | Here |
|---|---|---|---|
| GBIF occurrence density, Maps API v2 (GBIF.org, retrieved 2026-09-26) | 4 | Records are published under CC0, CC BY 4.0 or CC BY-NC 4.0 per dataset; cite GBIF.org. **The Maps API has no DOI.** | included: binned totals (`gbif_bins.npz`), per-cell counts |
| GBIF occurrence search API via healpix-connector (Beni box) | slides 9, 13, 29, 34, 35, 36, 41 | as above; **no download DOI yet** | included: per-cell counts only. Record-level files (`mammals.json`, `threatened_records.json`, `fire_action_points.npz`) are **not** shipped — the last two hold locations of threatened species |
| Biodiversity hotspots 2016.1, Hoffman et al. 2016, doi:10.5281/zenodo.3261807 | 4 | CC BY-SA 4.0 (derived `per_hotspot.json` is therefore CC BY-SA 4.0) | script |
| Natural Earth 1:50m land | 4 | Public domain | script |
| Natural Earth 1:110m land | 7 | Public domain | included (`sphere-vs-ellipsoid/data/`) |
| ESA CCI Biomass v7.0 (2023 AGB, AGB_SD), doi:10.5285/6429d1aafe1e43b9b414e4a5a7f8b903 | 29, 41 | ESA CCI terms: any use; acknowledge ESA CCI and Biomass_cci; cite DOI | script; per-cell means included |
| ESA Fire CCI SYN burned area v1.1 (2024), doi:10.5285/d441079fc77f49fabeb41330612b252f | 13, 29, 34 | ESA CCI terms (as above, Fire_cci) | streamed by script; per-cell fractions included |
| ESA BIOMASS L2A forest height FP_FH__L2A, ESA MAAP | 9, 35, 36 | ESA/NASA MAAP open data policy (free, open; attribution in metadata). Needs free MAAP registration | script (`00_get_biomass_fh.py`, credentials from env only); per-cell means included |
| CHELSA v2.1 climatologies (bio1, bio12, monthly pr), doi:10.16904/envidat.228 | 29, 35, 36 | CC0 1.0 (EnviDat) | streamed by script; per-cell values included |
| Copernicus Marine SST L3S PMW + L4 (cmems_obs-sst_glo_phy_l3s_pmw_P1D-m, cmems_obs-sst_glo_phy-temp_nrt_P1D-m), 2026-04-01 | 33 | Copernicus Marine licence: redistribution and derived products allowed; credit "Generated using E.U. Copernicus Marine Service Information" + DOIs | included: HEALPix nside-32 maps (`sst_maps.npz`) |
| Coastal replication deposit (CMEMS WAVERYS/NWS waves, Natura 2000), doi:10.5281/zenodo.20465505 | 10 | CC BY 4.0 | script |
| FMI open radar data, Korpo (fikor) polar volume 2023-09-13 20:15 UTC | 12 | CC BY 4.0 (Finnish Meteorological Institute) | script |
| aloft vertical bird profiles (vol2bird), fikor 2023-09-13/14, Desmet et al. 2025 | 12 | CC BY 4.0 | script |
| Oliver et al. 2018, Nat Commun 9:1324, Fig. 2, doi:10.1038/s41467-018-03732-9 | 40 (original panel) | CC BY 4.0 | included (reference copy) |
| ESA SST CCI Analysis v3.0 | 40 (replication) | ESA CCI terms | via upstream repo |
| GRID4EARTH website figure code (grid4earth.github.io) | 7 | code by A. Fouilloux, redistributed here under MIT | included (extracted script) |
| annefou/dggs-biodiversity-bias, sdm-hotspot-spatial-effort, marine-heatwave-replication, fiesta-scattering-sst | 27, 14, 40, 33 | MIT | pinned commits, run upstream |

GBIF-derived counts come from the Maps and search APIs (no DOI); a GBIF derived dataset or a download DOI would
make them citable. See Known limitations in README.md.
