"""Read ODIM HDF5 polar volumes (FMI open data) without extra dependencies."""
import h5py, numpy as np

def read_scan(path, elangle, quantities):
    f = h5py.File(path, "r")
    for k in f:
        if not k.startswith("dataset"):
            continue
        w = f[k]["where"].attrs
        if abs(float(w["elangle"]) - elangle) > 0.05:
            continue
        out = {"rscale": float(w["rscale"]), "nbins": int(w["nbins"]), "rstart": float(w.get("rstart", 0)) * 1000}
        for d in f[k]:
            if not d.startswith("data"):
                continue
            wa = f[k][d]["what"].attrs
            q = wa["quantity"].decode()
            if q in quantities:
                raw = f[k][d]["data"][()].astype(float)
                v = raw * wa["gain"] + wa["offset"]
                v[(raw == wa["nodata"]) | (raw == wa["undetect"])] = np.nan
                out[q] = v
        out["lat"] = float(f["where"].attrs["lat"]); out["lon"] = float(f["where"].attrs["lon"])
        return out
    raise KeyError(elangle)

def xy(scan):
    nrays = next(v for k, v in scan.items() if isinstance(v, np.ndarray)).shape[0]
    az = np.deg2rad((np.arange(nrays + 1) - 0.5) * 360 / nrays)
    r = (scan["rstart"] + np.arange(scan["nbins"] + 1) * scan["rscale"]) / 1000
    R, A = np.meshgrid(r, az)
    return R * np.sin(A), R * np.cos(A)
