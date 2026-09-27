#!/usr/bin/env bash
# Open data, CC BY 4.0, no credentials.
set -euo pipefail
cd "$(dirname "$0")" && mkdir -p data
curl -fsS -o data/202309132015_fikor_PVOL.h5 https://fmi-opendata-radar-volume-hdf5.s3-eu-west-1.amazonaws.com/2023/09/13/fikor/202309132015_fikor_PVOL.h5
for d in 20230913 20230914; do
  curl -fsS -o data/fikor_vpts_$d.csv https://aloftdata.s3-eu-west-1.amazonaws.com/baltrad/daily/fikor/2023/fikor_vpts_$d.csv
done
