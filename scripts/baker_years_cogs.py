"""Small COGs for the Mount Baker years map (maps/baker-years.html): red and SWIR for each summer, 16 km square.

    uv run python scripts/baker_years_cogs.py [path/to/whatcom-land]

Streaming the full Landsat scenes from Planetary Computer cost ~3 MB a summer and, on a slow day, minutes for all 42,
too slow to play. whatcom.land's glacier flipbook already holds the 16 km square around the summit for every scene it
considered (its .cache/flipbook, read from Planetary Computer, 1995 already shifted onto the ground). This cuts each
chosen scene's red and SWIR 1.6 µm bands from that cache into two Cloud-Optimized GeoTIFFs (uint16 Collection 2
digital numbers unchanged, deflate, 256 px blocks) in maps/data/years/ (gitignored), and points
maps/data/baker_years.json at them; scripts/baker_years_upload.py then puts them on R2.
Run scripts/baker_years_data.py first.
"""
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "maps" / "data" / "years"
WL = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT.parent / "whatcom-land"
CACHE = WL / ".cache" / "flipbook"
RES = 30

book = json.loads((WL / "site/data/whatcom/glacier_flipbook.json").read_text())
x0, y0, x1, y1 = book["bounds_utm"]
data_path = ROOT / "maps" / "data" / "baker_years.json"
data = json.loads(data_path.read_text())
OUT.mkdir(parents=True, exist_ok=True)
total = 0
for f in data["frames"]:
    shifted = CACHE / f"{f['scene']}-shifted.npz"
    z = np.load(shifted if shifted.exists() else CACHE / f"{f['scene']}.npz")
    for band, key in (("red", "red"), ("swir", "swir16")):
        a = z[key]
        path = OUT / f"{f['year']}-{band}.tif"
        with rasterio.open(path, "w", driver="COG", width=a.shape[1], height=a.shape[0], count=1, dtype="uint16",
                           crs=f"EPSG:{book['utm_epsg']}", transform=from_origin(x0, y1, RES, RES), nodata=0,
                           compress="DEFLATE", predictor=2, blocksize=256, overview_resampling="average") as dst:
            dst.write(a, 1)
        f[band] = f"data/years/{path.name}"
        total += path.stat().st_size
    f["shifted"] = shifted.exists()
data["source"] = ("USGS Landsat Collection 2 Level-2 (public domain), via Microsoft Planetary Computer; scenes chosen by "
                  "whatcom.land's glacier flipbook; red and SWIR cut to a 16 km square around the summit")
data_path.write_text(json.dumps(data, indent=1))
print(f"{len(data['frames'])} summers, {total / 1e6:.1f} MB in {OUT}")
