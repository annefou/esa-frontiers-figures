# esa-frontiers-figures

Code and data behind every figure in **"Rethinking Interoperability for AI-Driven Earth Intelligence —
What AI-ready means for biodiversity from space"** (Anne Fouilloux, LifeWatch ERIC; ESA Frontiers of Science,
ACEO, 30 September 2026). Organised as a FORRT-style reproducibility package: one folder per slide figure,
each with scripts, a README, and either the small derived data or a script that fetches the source data.

Code: MIT. Data: see [DATA_LICENSES.md](DATA_LICENSES.md). Credentials are never stored here (MAAP and
Copernicus Marine accounts are read from environment variables / their own login files).

| Slide | Figure | Folder | Code | Data here | Re-run check (2026-09-26) |
|---|---|---|---|---|---|
| 3 | GBIF records per km² on WGS84 HEALPix vs hotspots | `fig03-global-sampling-mismatch` | this repo | GBIF bins + per-cell counts; hotspots/NE by script | from saved GBIF bins: all intermediates and PNG **byte-identical** |
| 8 | Uniform points on a lat-lon grid: counts by latitude | `fig08-grid-latitude-artefact` | upstream `annefou/dggs-biodiversity-bias` @fc9ca6e | synthetic (seed 42) | numbers reproduced (22.9× area ratio, 605 vs 27 per cell); PNG differs by 2 px (matplotlib version) |
| 9 | Storm Xaver: WAVERYS vs regional waves, Natura 2000 outcome | `fig09-coastal-storm-product-choice` | this repo (analysis upstream `european-coastal-biodiversity-replication`) | Zenodo 20465505 by script | PNG **byte-identical** |
| 12 | Sphere vs WGS84 HEALPix: cells reassigned by latitude | `fig12-sphere-vs-ellipsoid` | extracted from GRID4EARTH website script | none needed | reproduced (100% max reassignment); PNG 1 px larger (matplotlib version) |
| 14 | BIOMASS L2A forest height × GBIF, Beni | `fig14-beni-biomass-forest-height` | `beni-pipeline` + plot | per-cell results | plot **byte-identical** from saved results |
| 15 | Burned 2024 vs pre-fire biomass by rain tercile, Beni | `fig15-beni-fire-vs-biomass` | `beni-pipeline` + plot | per-cell results | plot **byte-identical** |
| 16 | SST gap filling: satellite / smooth / scattering / L4 | `fig16-sst-gap-filling` | this repo (from `annefou/fiesta-scattering-sst` @21f8f95) | HEALPix maps (`sst_maps.npz`) | plot **byte-identical**; full run re-done 2026-09-26: RMSE 0.985 K (published 0.989 K) |
| 17 | SDM hotspot misidentification vs sampling effort | `fig17-sdm-sampling-bias` | upstream `annefou/sdm-hotspot-spatial-effort` @37d682e | upstream downloads | not re-run here |
| 18 | Fire CCI burned share and post-fire GBIF records, Beni | `fig18-beni-fire-where` | `beni-pipeline` + plot | per-cell results | plot **byte-identical** |
| 28 (backup) | Genome-to-space layers, Beni | `fig28-beni-genome-to-space` | `beni-pipeline` + plot | per-cell results | plot **byte-identical** |
| 29 (backup) | Where next: dissimilarity to sampled cells | `fig29-beni-where-next` | `beni-pipeline` + plot | per-cell results | plot **byte-identical** |
| 33 (backup) | Oliver et al. 2018 Fig. 2 and ESA SST CCI replication | `fig33-marine-heatwaves-check` | upstream `annefou/marine-heatwave-replication` @665c325 | original panel (CC BY 4.0) | not re-run here (~8 core-hours) |
| 34 (backup) | ESA CCI Biomass × GBIF, Beni | `fig34-beni-cci-biomass-gbif` | `beni-pipeline` + plot | per-cell results | plot **byte-identical** |

"Byte-identical" means re-running the plot script from the derived data shipped here reproduced the exact PNG
used in the deck. Re-running from source downloads is expected to drift where sources are live (GBIF grows daily).

## Environments
- `environments/plot.yml` — plotting and fig03/fig09/fig12.
- `environments/healpix-connector.md` — Beni analysis (healpix-connector pixi env).
- `environments/foscat.yml` — fig16.
These list the versions the figures were produced with; a fresh install from them has not been tested yet.

## Open issues before public release
1. GBIF: no DOI for the Maps API or the search-API counts → register a GBIF derived dataset (or use a download DOI).
2. GRID4EARTH website repo has no licence → add one (fig12 code is extracted from it).
3. healpix-connector `read_window` bbox bug (worked around in `beni_biomass_fh.py`); `__version__` reports 0.0.1.
4. The BIOMASS L2A products were downloaded on 2026-09-25; list in `beni-pipeline/README.md`. Two 25 July products were
   excluded by the declared quality rule (median quality < 1.0).
