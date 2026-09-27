"""Fetch open GBIF records of threatened species (IUCN CR, EN, VU) in the Beni bbox.

Writes results/threatened_records.json. NOT shipped in this repository: it holds the locations of
threatened species, and the point of the talk's legal-layer slide is that exact sites should reach
the right hands, not a public file. Re-running queries the live GBIF API, so counts drift.
"""
import collections
import json
import time
from pathlib import Path

import requests

OUT = Path(__file__).parent / "results" / "threatened_records.json"
G = "https://api.gbif.org/v1/occurrence/search"
GEOM = "POLYGON((-67.5 -15.5,-64.5 -15.5,-64.5 -12.5,-67.5 -12.5,-67.5 -15.5))"
KEEP = ["gbifID", "species", "_cat", "decimalLatitude", "decimalLongitude", "coordinateUncertaintyInMeters",
        "dataGeneralizations", "informationWithheld", "datasetKey", "basisOfRecord", "year"]

s = requests.Session()
s.headers["User-Agent"] = "esa-frontiers-figures (LifeWatch ERIC)"
recs = []
for cat in ["CR", "EN", "VU"]:
    off = 0
    while True:
        r = s.get(G, params={"geometry": GEOM, "hasCoordinate": "true", "iucnRedListCategory": cat,
                             "limit": 300, "offset": off}, timeout=120)
        if r.status_code == 429:
            time.sleep(20)
            continue
        j = r.json()
        recs += [dict(x, _cat=cat) for x in j["results"]]
        off += 300
        time.sleep(1.0)
        if j["endOfRecords"]:
            break
print("threatened records", len(recs))
print("by category", collections.Counter(x["_cat"] for x in recs))
json.dump([{k: x.get(k) for k in KEEP} for x in recs], open(OUT, "w"))
