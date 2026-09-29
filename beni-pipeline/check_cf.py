"""Check the step-9 Zarr stores with the CF checker (cfchecker reads netCDF, so each store is copied to a
temporary netCDF file first). Needs cfchecker + udunits2 (conda-forge) and the CF standard name table v95:

    curl -sSLO https://cfconventions.org/Data/cf-standard-names/current/src/cf-standard-name-table.xml
    python check_cf.py cf-standard-name-table.xml
"""
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import xarray as xr

table = sys.argv[1]
for zarr in sorted((Path(__file__).parent / "results").glob("beni_healpix_d*.zarr")):
    ds = xr.open_zarr(zarr).load()
    for v in ds.variables.values():  # Zarr stores attributes as JSON; restore flag_values to the variable's type
        if "flag_values" in v.attrs:
            v.attrs["flag_values"] = np.asarray(v.attrs["flag_values"], dtype=v.dtype)
    with tempfile.TemporaryDirectory() as tmp:
        nc = Path(tmp) / (zarr.stem + ".nc")
        ds.to_netcdf(nc)
        out = subprocess.run(["cfchecks", "-v", "1.8", "-s", table, str(nc)], capture_output=True, text=True).stdout
    print(zarr.name, [l for l in out.splitlines() if l.startswith(("ERRORS", "WARNINGS"))])
