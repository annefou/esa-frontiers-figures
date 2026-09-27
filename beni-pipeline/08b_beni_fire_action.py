"""Enable action: in the 2024 Beni fires (ESA Fire CCI), which threatened species had open GBIF records in cells
that burned, and how many records are too blurred (generalised to protect the taxon) to tell?
Cells: WGS84 HEALPix depth 11 (~3.2 km). Burned = >25 % of the cell burned in 2024."""
import json
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from healpix_geo import nested

S = OUT = Path(__file__).parent / "results"
f = np.load(S / "fire_cells.npz")
cells, burned = f["cells11"].astype(np.int64), f["burned_frac11"]
heavy = set(cells[burned > 0.25].tolist())
recs = json.load(open(S / "threatened_records.json"))
lon = np.array([r["decimalLongitude"] for r in recs]); lat = np.array([r["decimalLatitude"] for r in recs])
unc = np.array([r.get("coordinateUncertaintyInMeters") or np.nan for r in recs], float)
blurred = np.array([bool(r.get("informationWithheld") or r.get("dataGeneralizations")) for r in recs])
c = nested.lonlat_to_healpix(lon, lat, np.uint8(11), ellipsoid="WGS84").astype(np.int64)
in_heavy = np.array([x in heavy for x in c.tolist()])
precise = (~blurred) & (np.nan_to_num(unc, nan=np.inf) <= 3200)
unknown = (~blurred) & ~np.isfinite(unc)
cat = np.array([r["_cat"] for r in recs]); sp = np.array([r["species"] for r in recs])
out = {"records": len(recs), "heavy_cells": len(heavy), "cells": int(cells.size),
       "blurred_records": int(blurred.sum()), "precise_le_3km_records": int(precise.sum()),
       "no_uncertainty_records": int(unknown.sum()),
       "records_in_heavily_burned_cells": int(in_heavy.sum()),
       "precise_records_in_heavily_burned_cells": int((in_heavy & precise).sum()),
       "blurred_records_whose_point_is_in_burned_cell": int((in_heavy & blurred).sum())}
by = defaultdict(lambda: Counter())
for s_, k_, h, b in zip(sp, cat, in_heavy, blurred):
    by[(s_, k_)]["records"] += 1; by[(s_, k_)]["in_burned"] += int(h); by[(s_, k_)]["blurred"] += int(b)
species_burned = sorted([(k[0], k[1], v["in_burned"], v["records"], v["blurred"]) for k, v in by.items() if v["in_burned"] > 0],
                        key=lambda x: ({"CR": 0, "EN": 1, "VU": 2}.get(x[1], 3), -x[2]))
out["threatened_species_total"] = len(by)
out["threatened_species_with_records_in_burned_cells"] = len(species_burned)
out["by_category_in_burned"] = dict(Counter(x[1] for x in species_burned))
out["species_in_burned"] = [{"species": a, "iucn": b, "records_in_burned": c_, "records": d, "blurred": e} for a, b, c_, d, e in species_burned]
# a blurred record: what share of the cells within its declared radius burned?
lonc, latc = nested.healpix_to_lonlat(cells.astype(np.uint64), np.uint8(11), ellipsoid="WGS84")
lonc, latc = np.asarray(lonc, float), np.asarray(latc, float)
lonc = np.where(lonc > 180, lonc - 360, lonc)
shares = []
for i in np.where(blurred & np.isfinite(unc))[0]:
    dx = (lonc - lon[i]) * 111.32 * np.cos(np.radians(lat[i])); dy = (latc - lat[i]) * 110.57
    m = (dx**2 + dy**2) <= (unc[i] / 1000) ** 2
    if m.sum() > 20:
        shares.append(float((burned[m] > 0.25).mean()))
out["blurred_records_radius_km_median"] = float(np.nanmedian(unc[blurred]) / 1000) if blurred.any() else None
out["blurred_share_of_disc_heavily_burned_median"] = float(np.median(shares)) if shares else None
out["blurred_share_of_disc_heavily_burned_range"] = [float(np.min(shares)), float(np.max(shares))] if shares else None
json.dump(out, open(OUT / "fire_action.json", "w"), indent=1)
np.savez(OUT / "fire_action_points.npz", lon=lon, lat=lat, unc=unc, blurred=blurred, precise=precise, in_heavy=in_heavy, cat=cat, sp=sp)
print(json.dumps({k: v for k, v in out.items() if k != "species_in_burned"}, indent=1))
for x in out["species_in_burned"][:12]: print(x)
