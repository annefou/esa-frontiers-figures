"""Depth-4 WGS84 HEALPix cell outlines (for GBIF counts) and depth-8 child centres (for hotspot fractions)."""
import numpy as np
from healpix_geo import nested

D, F = 4, 8
cells = np.arange(12 * 4**D, dtype=np.uint64)
vlon, vlat = nested.vertices(cells, np.uint8(D), ellipsoid="WGS84", step=4)
vlon = np.where(vlon > 180, vlon - 360, vlon)
kids = np.arange(12 * 4**F, dtype=np.uint64)
klon, klat = nested.healpix_to_lonlat(kids, np.uint8(F), ellipsoid="WGS84")
klon = np.where(klon > 180, klon - 360, klon)
np.savez("data/cells_d4.npz", cells=cells, vlon=vlon, vlat=vlat, klon=klon.astype("f4"), klat=klat.astype("f4"))
print(vlon.shape, klon.shape)
