#!/usr/bin/env bash
# Slide 17 figure comes from annefou/sdm-hotspot-spatial-effort (MIT), doi:10.5281/zenodo.20465140
# (FORRT replication of Phillips et al. 2009, doi:10.1890/07-2153.1).
set -euo pipefail
git clone https://github.com/annefou/sdm-hotspot-spatial-effort upstream
cd upstream && git checkout 37d682e6bc4ad9ffb6019cbe06410024f59358fa
pixi install                      # upstream pixi.toml / pixi.lock
pixi run run                      # snakemake: 01_data_download -> 04_figures; writes figures/main_result.png
