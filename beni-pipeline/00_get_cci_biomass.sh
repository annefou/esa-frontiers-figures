#!/usr/bin/env bash
# ESA CCI Biomass v7.0, 2023 AGB and AGB_SD tile S10W070 (100 m), via CEDA.
# doi:10.5285/6429d1aafe1e43b9b414e4a5a7f8b903 — ESA CCI terms: any use, acknowledge ESA CCI + Biomass_cci, cite DOI.
set -euo pipefail
mkdir -p data
B=https://dap.ceda.ac.uk/neodc/esacci/biomass/data/agb/maps/v7.0/geotiff/2023
curl -sSL -o data/S10W070_AGB_2023_v7.tif    "$B/S10W070_ESACCI-BIOMASS-L4-AGB-MERGED-100m-2023-fv7.0.tif"
curl -sSL -o data/S10W070_AGB_SD_2023_v7.tif "$B/S10W070_ESACCI-BIOMASS-L4-AGB_SD-MERGED-100m-2023-fv7.0.tif"
ls -l data
