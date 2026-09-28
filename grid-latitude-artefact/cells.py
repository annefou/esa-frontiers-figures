import healpix_geo.nested as hpx
import numpy as np
R = 6371.0
def local_km(lon, lat, lon0, lat0):  # local equal-area-ish plane (sinusoidal around centre)
    x = R * np.radians(lon - lon0) * np.cos(np.radians(lat)); y = R * np.radians(lat - lat0)
    return x, y
def latlon_cell(lat_lo, d=5.0):
    lo = np.r_[np.linspace(0, d, 30), np.full(30, d), np.linspace(d, 0, 30), np.zeros(30)]
    la = np.r_[np.full(30, lat_lo), np.linspace(lat_lo, lat_lo + d, 30), np.full(30, lat_lo + d), np.linspace(lat_lo + d, lat_lo, 30)]
    return lo, la
def behrmann_cell(lat_c, area=309e3, phis=30.0):
    s = np.sqrt(area); cs = np.cos(np.radians(phis))
    y0 = R * np.sin(np.radians(lat_c)) / cs
    ya, yb = y0 - s / 2, y0 + s / 2
    la_a = np.degrees(np.arcsin(np.clip(ya * cs / R, -1, 1))); la_b = np.degrees(np.arcsin(np.clip(yb * cs / R, -1, 1)))
    dlon = np.degrees(s / (R * cs))
    lo = np.r_[np.linspace(0, dlon, 30), np.full(30, dlon), np.linspace(dlon, 0, 30), np.zeros(30)]
    la = np.r_[np.full(30, la_a), np.linspace(la_a, la_b, 30), np.full(30, la_b), np.linspace(la_b, la_a, 30)]
    return lo, la
def healpix_cell(lat_c, depth=4):
    """Outline of the WGS84 HEALPix cell (healpix-geo) containing (10°E, lat_c), 30 points per edge."""
    p = hpx.lonlat_to_healpix(np.array([10.0]), np.array([float(lat_c)]), np.uint8(depth), ellipsoid="WGS84")
    lo, la = hpx.vertices(p, np.uint8(depth), ellipsoid="WGS84", step=30)
    return np.asarray(lo)[0], np.asarray(la)[0]
def shape(lo, la):
    lo0 = (lo.max() + lo.min()) / 2; la0 = (la.max() + la.min()) / 2
    x, y = local_km(lo, la, lo0, la0)
    w, h = x.max() - x.min(), y.max() - y.min()
    area = 0.5 * abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))
    return x - x.mean(), y - y.mean(), max(w, h) / min(w, h), area
