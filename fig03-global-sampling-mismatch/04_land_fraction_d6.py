"""Depth-6 WGS84 HEALPix cell outlines (~110 km) and land fraction per cell, from the depth-8 child centres
(data/cells_d4.npz, made by 02_prep_cells.py) tested against Natural Earth land -> data/cells_d6.npz.
`dens` (records per km² of land) is kept for the bar-chart era of the figure; 06_plot.py uses counts_d6.npy."""
import json

import numpy as np
import shapely
from healpix_geo import nested
from shapely.geometry import shape
from shapely.ops import unary_union

n6 = 12 * 4**6
cells = np.arange(n6, dtype=np.uint64)
vlon, vlat = nested.vertices(cells, np.uint8(6), ellipsoid="WGS84")
vlon = np.where(vlon > 180, vlon - 360, vlon)
d = np.load("data/cells_d4.npz")
land = unary_union([shape(f["geometry"]) for f in json.load(open("external/ne_50m_land.geojson"))["features"]])
shapely.prepare(land)
inside = shapely.contains_xy(land, d["klon"].astype(float), d["klat"].astype(float))
landf = inside.reshape(-1, 16).mean(1)  # 16 depth-8 children per depth-6 parent (NESTED order)
cnt = np.load("data/counts_d6.npy")
cell_km2 = 4 * np.pi * 6371.0**2 / n6
dens = cnt / (np.maximum(landf, 1e-9) * cell_km2)
np.savez("data/cells_d6.npz", dens=dens, landf=landf, vlon=vlon, vlat=vlat)
print("land cells (>=30%)", int((landf >= 0.3).sum()))
