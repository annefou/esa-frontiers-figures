#!/usr/bin/env bash
# Reference layers (not redistributed here; fetched from their publishers).
set -euo pipefail
mkdir -p external && cd external
# Biodiversity hotspots 2016.1 (Hoffman et al. 2016), CC BY-SA 4.0, doi:10.5281/zenodo.3261807
curl -sSL -o hotspots.zip "https://zenodo.org/api/records/3261807/files/hotspots_2016_1.zip/content"
unzip -o -q hotspots.zip
# Natural Earth 1:50m land, public domain
curl -sSL -o ne_50m_land.geojson "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_land.geojson"
ls
