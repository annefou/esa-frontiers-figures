"""Download BIOMASS L2A forest-height (FP_FH__L2A) products over the Beni box from ESA MAAP.

Needs a (free) ESA MAAP account. Credentials come only from the environment, never from this repository:
  MAAP_OFFLINE_TOKEN        your offline token (or MAAP_TOKEN_FILE = path to a file holding it)
  MAAP_CLIENT_ID / MAAP_CLIENT_SECRET   the public client id/secret given in ESA MAAP's BIOMASS
                            data-access example (https://portal.maap.eo.esa.int/biomass/)
Token exchange as documented in that example. The token is never printed.
"""
import json
import os
import sys
from pathlib import Path

import requests

HERE = Path(__file__).parent
OUT = HERE / "biomass_fh"
OUT.mkdir(exist_ok=True)
CATALOG = "https://catalog.maap.eo.esa.int/catalogue"
BBOX = "-67.5,-15.5,-64.5,-12.5"
CLIENT_ID = os.environ.get("MAAP_CLIENT_ID", "offline-token")
CLIENT_SECRET = os.environ.get("MAAP_CLIENT_SECRET", "")


def access_token() -> str:
    offline = os.environ.get("MAAP_OFFLINE_TOKEN")
    if not offline and os.environ.get("MAAP_TOKEN_FILE"):
        offline = Path(os.environ["MAAP_TOKEN_FILE"]).read_text()
    if not offline or not CLIENT_SECRET:
        sys.exit("set MAAP_OFFLINE_TOKEN (or MAAP_TOKEN_FILE) and MAAP_CLIENT_SECRET; see the docstring")
    offline = offline.strip().replace("\n", "")
    r = requests.post("https://iam.maap.eo.esa.int/realms/esa-maap/protocol/openid-connect/token",
                      data={"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET,
                            "grant_type": "refresh_token", "refresh_token": offline,
                            "scope": "offline_access openid"}, timeout=60)
    if r.status_code != 200:
        sys.exit(f"token exchange failed: HTTP {r.status_code} {r.json().get('error_description', '')}")
    return r.json()["access_token"]


def main():
    items = requests.get(f"{CATALOG}/collections/BiomassLevel2a/items",
                         params={"bbox": BBOX, "limit": 100, "filter": "product:type='FP_FH__L2A'"},
                         timeout=120).json()["features"]
    print(f"{len(items)} forest-height products", flush=True)
    tok = access_token()
    s = requests.Session()
    s.headers["Authorization"] = f"Bearer {tok}"
    meta = []
    for f in items:
        rec = {"id": f["id"], "datetime": f["properties"].get("datetime"),
               "geometry": f["geometry"], "files": {}}
        for key in ("enclosure_i_fh_tiff", "enclosure_i_quality_tiff", "enclosure_xml"):
            a = f["assets"].get(key)
            if not a:
                continue
            dest = OUT / Path(a["href"]).name
            if not dest.exists():
                r = s.get(a["href"], timeout=300)
                if r.status_code != 200:
                    print(f"  {key} {f['id'][:40]}: HTTP {r.status_code}", flush=True)
                    continue
                dest.write_bytes(r.content)
            rec["files"][key] = dest.name
        meta.append(rec)
        print(f"  {f['id'][15:31]} {list(rec['files'])}", flush=True)
    json.dump(meta, open(OUT / "items.json", "w"), indent=1)


if __name__ == "__main__":
    main()
