"""ESA Fire CCI (Sentinel-3 SYN v1.1, 300 m) burned area 2024 on WGS84 HEALPix, Beni.

Pixel codes (JD layer): day of year = burned that month; 0 = not burned; -1 = not observed;
-2 = not burnable (codes confirmed on the data; meaning per the Fire_cci Product User Guide,
not declared in the GeoTIFF itself). CL = confidence level (0-100).
Dataset: ESA Fire_cci SYN burned area pixel v1.1, doi:10.5285/d441079fc77f49fabeb41330612b252f
"""
import json
import os
import sys
from pathlib import Path

import numpy as np

# healpix-connector: pip-install it, or point HEALPIX_CONNECTOR at a checkout (see ../README.md)
if os.environ.get("HEALPIX_CONNECTOR"):
    sys.path.insert(0, str(Path(os.environ["HEALPIX_CONNECTOR"]) / "src"))
from healpix_connector.binning import bin_to_cells  # noqa: E402
from healpix_connector.sources.geotiff import read_window  # noqa: E402

HERE = Path(__file__).parent
OUT = HERE / "results"
BBOX = (-67.5, -15.5, -64.5, -12.5)
URL = ("https://dap.ceda.ac.uk/neodc/esacci/fire/data/burned_area/Sentinel3_SYN/pixel/v1.1/uncompressed/"
       "2024/{m:02d}/2024{m:02d}01-ESACCI-L3S_FIRE-BA-SYN-AREA_2-fv1.1-{v}.tif")
os.environ["GDAL_DISABLE_READDIR_ON_OPEN"] = "EMPTY_DIR"


def main():
    burned = observed = unburnable = None
    conf_sum = conf_n = None
    month_burned = {}
    for m in range(1, 13):
        jd = read_window(URL.format(m=m, v="JD"), BBOX)
        cl = read_window(URL.format(m=m, v="CL"), BBOX)
        j, c = jd.values, cl.values
        if burned is None:
            burned = np.zeros(j.shape, bool); observed = np.zeros(j.shape, bool)
            unburnable = np.ones(j.shape, bool); conf_sum = np.zeros(j.shape); conf_n = np.zeros(j.shape)
            lon, lat, res = jd.lon, jd.lat, jd.res_deg
        b = j > 0
        burned |= b; observed |= j >= 0; unburnable &= j == -2
        conf_sum[b] += c[b]; conf_n[b] += 1
        month_burned[m] = int(b.sum())
        print(f"2024-{m:02d}: burned pixels {b.sum()}", flush=True)
    frac = np.where(observed & ~unburnable, burned.astype(float), np.nan)
    conf = np.where(conf_n > 0, conf_sum / np.maximum(conf_n, 1), np.nan)
    c9 = np.load(OUT / "cells.npz")["cells"]
    res_d = {}
    for depth in (9, 11):
        st = bin_to_cells(frac, lon, lat, depth, res)
        sc = bin_to_cells(conf, lon, lat, depth, res)
        res_d[depth] = (st, sc)
    st9, sc9 = res_d[9]
    j = np.searchsorted(st9.cell_ids, c9); j[j >= st9.cell_ids.size] = 0
    ok = st9.cell_ids[j] == c9
    bf9 = np.full(c9.size, np.nan); bf9[ok] = st9.mean[j[ok]]
    jc = np.searchsorted(sc9.cell_ids, c9); jc[jc >= sc9.cell_ids.size] = 0
    okc = sc9.cell_ids[jc] == c9
    cf9 = np.full(c9.size, np.nan); cf9[okc] = sc9.mean[jc[okc]]
    st11 = res_d[11][0]
    from healpix_geo import nested
    vlon, vlat = nested.vertices(st11.cell_ids, np.uint8(11), ellipsoid="WGS84")
    vlon = np.where(vlon > 180, vlon - 360, vlon)
    np.savez(OUT / "fire_cells.npz", cells9=c9, burned_frac9=bf9, conf9=cf9,
             cells11=st11.cell_ids, burned_frac11=st11.mean, vlon11=vlon, vlat11=vlat)
    pix_total = frac.size
    summary = {"dataset": "ESA Fire_cci SYN burned area pixel v1.1 (Sentinel-3 OLCI+SLSTR, 300 m), 2024",
               "doi": "10.5285/d441079fc77f49fabeb41330612b252f",
               "burned_share_of_observed_burnable_pct": round(100 * float(np.nanmean(frac)), 1),
               "never_observed_pct": round(100 * float((~observed).mean()), 2),
               "unburnable_pct": round(100 * float(unburnable.mean()), 2),
               "burned_pixels_by_month": month_burned,
               "cells9_with_any_burn_pct": round(100 * float((bf9 > 0).mean()), 1),
               "cells9_burned_over_25pct": int((bf9 > 0.25).sum()),
               "mean_confidence_of_burned_pixels": round(float(np.nanmean(conf)), 1),
               "pixels": pix_total}
    json.dump(summary, open(OUT / "fire_summary.json", "w"), indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
