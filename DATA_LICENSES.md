# Data sources and licences

Code in this repository is MIT (see LICENSE). Data and figures carry the licence of their sources.
"Included" = small derived files shipped here; "script" = fetched from the publisher by a script in the folder.

| Source | Used in | Licence / terms (checked 2026-09-26) | Here |
|---|---|---|---|
| GBIF occurrence density, Maps API v2 (GBIF.org, retrieved 2026-09-26) | fig03 | Records are published under CC0, CC BY 4.0 or CC BY-NC 4.0 per dataset; cite GBIF.org. **The Maps API has no DOI.** | included: binned totals (`gbif_bins.npz`), per-cell counts |
| GBIF occurrence search API via healpix-connector (Beni box) | fig14/15/18/28/29/34 | as above; **no download DOI yet** | included: per-cell counts only. Record-level files (`mammals.json`, `threatened_records.json`) are **not** shipped — the second holds (generalised) locations of threatened species |
| Biodiversity hotspots 2016.1, Hoffman et al. 2016, doi:10.5281/zenodo.3261807 | fig03 | CC BY-SA 4.0 (derived `per_hotspot.json` is therefore CC BY-SA 4.0) | script |
| Natural Earth 1:50m land | fig03 | Public domain | script |
| ESA CCI Biomass v7.0 (2023 AGB, AGB_SD), doi:10.5285/6429d1aafe1e43b9b414e4a5a7f8b903 | fig15, fig34 | ESA CCI terms: any use; acknowledge ESA CCI and Biomass_cci; cite DOI | script; per-cell means included |
| ESA Fire CCI SYN burned area v1.1 (2024), doi:10.5285/d441079fc77f49fabeb41330612b252f | fig15, fig18 | ESA CCI terms (as above, Fire_cci) | streamed by script; per-cell fractions included |
| ESA BIOMASS L2A forest height FP_FH__L2A, ESA MAAP | fig14, fig28, fig29 | ESA/NASA MAAP open data policy (free, open; attribution in metadata). Needs free MAAP registration | script (`00_get_biomass_fh.py`, credentials from env only); per-cell means included |
| CHELSA v2.1 climatologies (bio1, bio12, monthly pr), doi:10.16904/envidat.228 | fig15, fig28, fig29 | CC0 1.0 (EnviDat) | streamed by script; per-cell values included |
| Copernicus Marine SST L3S PMW + L4 (cmems_obs-sst_glo_phy_l3s_pmw_P1D-m, cmems_obs-sst_glo_phy-temp_nrt_P1D-m), 2026-04-01 | fig16 | Copernicus Marine licence: redistribution and derived products allowed; credit "Generated using E.U. Copernicus Marine Service Information" + DOIs | included: HEALPix nside-32 maps (`sst_maps.npz`) |
| Coastal replication deposit (CMEMS WAVERYS/NWS waves, Natura 2000), doi:10.5281/zenodo.20465505 | fig09 | CC BY 4.0 | script |
| Oliver et al. 2018, Nat Commun 9:1324, Fig. 2, doi:10.1038/s41467-018-03732-9 | fig33 (original panel) | CC BY 4.0 | included (reference copy) |
| ESA SST CCI Analysis v3.0 | fig33 (replication) | ESA CCI terms | via upstream repo |
| GRID4EARTH website figure code (grid4earth.github.io) | fig12 | **No licence declared in that repository** (code by A. Fouilloux) — add one upstream before public release | included (extracted script) |
| annefou/dggs-biodiversity-bias, sdm-hotspot-spatial-effort, marine-heatwave-replication, fiesta-scattering-sst | fig08, fig17, fig33, fig16 | MIT | pinned commits, run upstream |

Before public release: register the GBIF-derived counts as a **GBIF derived dataset** (gives a citable DOI
listing the contributing datasets) or re-run from a GBIF download with a DOI.
