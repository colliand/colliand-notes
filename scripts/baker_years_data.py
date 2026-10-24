"""Data for the Mount Baker years map (maps/baker-years.html): one late-summer Landsat scene per year since 1984.

    uv run python scripts/baker_years_data.py [path/to/whatcom-land]

The scenes are the ones whatcom.land's glacier flipbook chose and checked by eye (glacier_flipbook.json in a
whatcom-land checkout, default ../whatcom-land): Landsat 5, 7, 8 and 9 Collection 2 Level-2 surface reflectance, read
from Microsoft Planetary Computer, which gives any browser a short-lived token without an account. Only the red and
shortwave-infrared (SWIR 1.6 µm) bands are listed: the bright-ice test needs nothing else. Asset hrefs are stored
unsigned; the page signs them with a fresh token.
"""
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "maps" / "data"
WL = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT.parent / "whatcom-land"
PC = "https://planetarycomputer.microsoft.com/api/stac/v1/collections/landsat-c2-l2/items/"

book = json.loads((WL / "site/data/whatcom/glacier_flipbook.json").read_text())
frames = []
for f in book["frames"]:
    item = json.load(urllib.request.urlopen(PC + f["scene"], timeout=60))
    a = item["assets"]
    frames.append({"year": f["year"], "date": f["date"], "satellite": f["satellite"], "scene": f["scene"],
                   "partly_cloudy": f.get("partly_cloudy", False),
                   "red": a["red"]["href"], "swir": a["swir16"]["href"],
                   "epsg": item["properties"]["proj:epsg"] if "proj:epsg" in item["properties"]
                   else int(item["properties"]["proj:code"].split(":")[1])})
    print(f["year"], f["satellite"], frames[-1]["epsg"])
out = {"summit": book["summit"], "gaps": book["gaps"], "frames": frames,
       "source": "USGS Landsat Collection 2 Level-2 (public domain), via Microsoft Planetary Computer; scenes chosen "
                 "by whatcom.land's glacier flipbook"}
(OUT / "baker_years.json").write_text(json.dumps(out, indent=1))
print(len(frames), "frames →", OUT / "baker_years.json")
