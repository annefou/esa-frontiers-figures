# esa-frontiers-figures

Code and data behind every figure in **"Rethinking Interoperability for AI-Driven Earth Intelligence —
What AI-ready means for biodiversity from space"** (Anne Fouilloux, LifeWatch ERIC; ESA Frontiers of Science,
30 September 2026). Organised as a reproducibility package: one folder per slide figure,
each with scripts, a README, and either the small derived data or a script that fetches the source data.

Code: MIT. Data: see [DATA_LICENSES.md](DATA_LICENSES.md). Credentials are never stored here (MAAP and
Copernicus Marine accounts are read from environment variables / their own login files).

| Slide | Figure | Folder | Code | Data here | Re-run check |
|---|---|---|---|---|---|
| 4 | GBIF records per km² on WGS84 HEALPix vs hotspots | `global-sampling-mismatch` | this repo | GBIF bins + per-cell counts; hotspots/NE by script | from saved GBIF bins: all intermediates and PNG **byte-identical** (2026-09-26) |
| 7 | Sphere vs WGS84 HEALPix: cells reassigned by latitude | `sphere-vs-ellipsoid` | extracted from GRID4EARTH website script | none needed | reproduced (100% max reassignment); PNG 1 px larger (matplotlib version) |
| **9** | **BIOMASS L2A forest height × GBIF, Beni** | `beni-biomass-forest-height` | `beni-pipeline` steps 0b, 1, 2 + plot | per-cell results | plot **byte-identical** from saved results (2026-09-27) |
| 10 | Storm Xaver: WAVERYS vs regional waves, Natura 2000 outcome | `coastal-storm-product-choice` | this repo (analysis upstream `european-coastal-biodiversity-replication`) | Zenodo 20465505 by script | PNG **byte-identical** |
| 12 | Weather radar: rain vs birds in one scan (FMI Korpo) | `radar-birds-two-communities` | this repo | FMI open data + aloft by script (CC BY 4.0) | PNG **byte-identical** from a fresh download (2026-09-27) |
| 13 | 2024 fires and threatened-species records, Beni | `beni-fire-threatened-species` | `beni-pipeline` steps 5, 8 + plot | aggregates only (record locations withheld) | analysis and PNG **byte-identical** from the 2026-09-26 GBIF extract |
| 14 | SDM hotspot misidentification vs sampling effort | `sdm-sampling-bias` | upstream `annefou/sdm-hotspot-spatial-effort` @37d682e | upstream downloads | not re-run here |
| 27 (backup) | Uniform points on a lat-lon grid: counts by latitude | `grid-latitude-artefact` | upstream `annefou/dggs-biodiversity-bias` @fc9ca6e | synthetic (seed 42) | numbers reproduced (22.9× area ratio, 605 vs 27 per cell); PNG differs by 2 px (matplotlib version) |
| 29 (backup) | Burned 2024 vs pre-fire biomass by rain tercile, Beni | `beni-fire-vs-biomass` | `beni-pipeline` step 7 + plot | per-cell results | plot **byte-identical**; full replication in [annefou/beni-fire-biomass-healpix](https://github.com/annefou/beni-fire-biomass-healpix) |
| 33 (backup) | SST gap filling: satellite / smooth / scattering / L4 | `sst-gap-filling` | this repo (from `annefou/fiesta-scattering-sst` @21f8f95) | HEALPix maps (`sst_maps.npz`) | plot **byte-identical**; full run re-done 2026-09-26: RMSE 0.985 K (published 0.989 K) |
| 34 (backup) | Fire CCI burned share and post-fire GBIF records, Beni | `beni-fire-where` | `beni-pipeline` steps 5, 6 + plot | per-cell results | plot **byte-identical** |
| 35 (backup) | Genome-to-space layers, Beni | `beni-genome-to-space` | `beni-pipeline` step 3 + plot | per-cell results | plot **byte-identical** |
| 36 (backup) | Where next: dissimilarity to sampled cells | `beni-where-next` | `beni-pipeline` step 4 + plot | per-cell results | plot **byte-identical** |
| 40 (backup) | Oliver et al. 2018 Fig. 2 and ESA SST CCI replication | `marine-heatwaves-check` | upstream `annefou/marine-heatwave-replication` @665c325 | original panel (CC BY 4.0) | not re-run here (~8 core-hours) |
| 41 (backup) | ESA CCI Biomass × GBIF, Beni | `beni-cci-biomass-gbif` | `beni-pipeline` step 1 + plot | per-cell results | plot **byte-identical** |

Slide numbers follow the deck as presented on 30 September 2026; each folder also names the slide by its id.

"Byte-identical" means re-running the plot script from the derived data shipped here reproduced the exact PNG
used in the deck. Re-running from source downloads is expected to drift where sources are live (GBIF grows daily).

## Environments
- `environments/plot.yml` — plotting, and the global-sampling, coastal-storm, sphere-vs-ellipsoid and radar figures.
- `environments/healpix-connector.md` — Beni analysis (healpix-connector pixi env).
- `environments/foscat.yml` — SST gap filling (FOSCAT).
These list the versions the figures were produced with; a fresh install from them has not been tested yet.

## Known limitations
1. GBIF counts were retrieved through the Maps and search APIs, which have no DOI; re-running against the live
   API gives slightly different counts. A GBIF download DOI would pin them.
2. The `sphere-vs-ellipsoid` code is extracted from the GRID4EARTH website repository.
3. healpix-connector is pinned to v0.1.0 (Zenodo [10.5281/zenodo.22904851](https://doi.org/10.5281/zenodo.22904851));
   every layer converted with it was validated against its source before use.
4. The BIOMASS L2A products were downloaded on 2026-09-25 from ESA MAAP (list in `beni-pipeline/README.md`). Two
   25 July products were excluded by the declared quality rule (median quality < 1.0).
5. Record-level locations of threatened species are not published here (see `beni-fire-threatened-species`).
