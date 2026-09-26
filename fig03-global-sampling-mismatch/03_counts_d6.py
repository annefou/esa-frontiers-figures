"""Sum all GBIF Maps API density bins (0.35°, land and ocean) into WGS84 HEALPix depth-6 cells."""
import numpy as np
from healpix_geo import nested

b = np.load("data/gbif_bins.npz")
lon = np.where(b["lon"] < 0, b["lon"] + 360, b["lon"])
c = nested.lonlat_to_healpix(lon, b["lat"], np.uint8(6), ellipsoid="WGS84")
np.save("data/counts_d6.npy", np.bincount(c.astype(np.int64), weights=b["total"], minlength=12 * 4**6))
