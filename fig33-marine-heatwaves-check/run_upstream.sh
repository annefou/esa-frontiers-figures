#!/usr/bin/env bash
# Slide 33 (backup): replication of Oliver et al. 2018 Fig. 2 with ESA SST CCI Analysis v3.0,
# annefou/marine-heatwave-replication (MIT), doi:10.5281/zenodo.21950032.
set -euo pipefail
git clone https://github.com/annefou/marine-heatwave-replication upstream
cd upstream && git checkout 665c325c320d2100b1693bcebe6ff0debaca47c1
pixi install
pixi run run                      # snakemake (~8 core-hours): downloads SST CCI; 07_figure2.py -> figures/figure2_replica.png
