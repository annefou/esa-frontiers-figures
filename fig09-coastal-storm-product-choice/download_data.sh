#!/usr/bin/env bash
# Analysis-ready slices of the European coastal biodiversity replication (CMEMS WAVERYS + NWS regional waves,
# marine Natura 2000 sites), Zenodo doi:10.5281/zenodo.20465505, CC BY 4.0 (~70 MB).
set -euo pipefail
mkdir -p data && cd data
curl -sSL -o data_deposit.zip "https://zenodo.org/api/records/20465505/files/data_deposit.zip/content"
unzip -o -q data_deposit.zip
ls clean results
