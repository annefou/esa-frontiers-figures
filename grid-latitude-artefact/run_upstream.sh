#!/usr/bin/env bash
# Slide 27 (models-geometry, backup) figure comes from annefou/dggs-biodiversity-bias (MIT), doi:10.5281/zenodo.19848749.
set -euo pipefail
git clone https://github.com/annefou/dggs-biodiversity-bias upstream
cd upstream && git checkout fc9ca6ec402e0598ab58226747f95b92739a4a58
# Environment: upstream environment.yml (conda/mamba). The figure is written by notebooks/01_synthetic_proof.py:
cd notebooks && python 01_synthetic_proof.py   # -> ../images/raw_counts_by_latitude.png (seed 42)
