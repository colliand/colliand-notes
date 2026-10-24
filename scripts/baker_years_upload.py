"""Upload the Mount Baker years COGs (maps/data/years/, from scripts/baker_years_cogs.py) to R2 and point
maps/data/baker_years.json at them.

    uv run --with boto3 python scripts/baker_years_upload.py

They go to whatcom.land's bucket (`whatcom-land-data`, served at https://data.whatcom.land) under notes/baker-years/,
using its upload keys on dayhoff (~/Library/Application Support/whatcom-land-r2; never printed). The bucket's CORS
admits notes.colliand.com and its previews. Keeping the 44 MB out of this repo is the point.
"""
import json
import urllib.request
from pathlib import Path

import boto3

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "maps" / "data" / "years"
DATA = ROOT / "maps" / "data" / "baker_years.json"
BUCKET, PREFIX, PUBLIC = "whatcom-land-data", "notes/baker-years/", "https://data.whatcom.land/"
APP = Path.home() / "Library/Application Support"

keys = dict(l.split("=", 1) for l in (APP / "whatcom-land-r2").read_text().split())
req = urllib.request.Request("https://api.cloudflare.com/client/v4/accounts",
                             headers={"Authorization": f"Bearer {(APP / 'cloudflare-token').read_text().strip()}"})
acct = json.load(urllib.request.urlopen(req, timeout=60))["result"][0]["id"]
s3 = boto3.client("s3", endpoint_url=f"https://{acct}.r2.cloudflarestorage.com", region_name="auto",
                  aws_access_key_id=keys["R2_ACCESS_KEY_ID"], aws_secret_access_key=keys["R2_SECRET_ACCESS_KEY"])
files = sorted(SRC.glob("*.tif"))
for f in files:
    s3.upload_file(str(f), BUCKET, PREFIX + f.name,
                   ExtraArgs={"ContentType": "image/tiff", "CacheControl": "public, max-age=604800"})
data = json.loads(DATA.read_text())
for fr in data["frames"]:
    for band in ("red", "swir"):
        fr[band] = PUBLIC + PREFIX + Path(fr[band]).name
DATA.write_text(json.dumps(data, indent=1))
print(f"uploaded {len(files)} files to {PUBLIC}{PREFIX}")
