"""Bright-ice area on Mount Baker for each summer, 1984-2026, from the years map's COGs (glaciers/data/baker-years-area.csv).

    uv run python scripts/baker_years_area.py

Same test as the map: surface reflectance red / SWIR 1.6 µm > threshold. Two areas per year and threshold: everything
in the 16 km square, and only inside Portland State's 2015 glacier outlines (which leaves out snow patches off the
glaciers, but not snow lying on them). Reads maps/data/years/ when it is there (scripts/baker_years_cogs.py), else the
copies on R2.
"""
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.features import geometry_mask

ROOT = Path(__file__).resolve().parent.parent
LOCAL = ROOT / "maps" / "data" / "years"
OUT = ROOT / "glaciers" / "data" / "baker-years-area.csv"
THRESHOLDS = (1.5, 2.0, 2.5)


def reflectance(path):
    with rasterio.open(path) as src:
        b = src.read(1).astype(float)
        return np.where(b > 0, ((b - 1) / 254) ** 2, np.nan), src.transform, src.shape


data = json.loads((ROOT / "maps" / "data" / "baker_years.json").read_text())
outlines = gpd.read_file(ROOT / "maps" / "data" / "baker_outlines.geojson")
outlines = outlines[outlines["set"] == "2015"].to_crs(32610)
rows, inside = [], None
for f in data["frames"]:
    y = f["year"]
    red, transform, shape = reflectance(LOCAL / f"{y}-red.tif" if LOCAL.exists() else f["red"])
    swir, _, _ = reflectance(LOCAL / f"{y}-swir.tif" if LOCAL.exists() else f["swir"])
    if inside is None:
        inside = ~geometry_mask(outlines.geometry, shape, transform)
    px = abs(transform.a * transform.e) / 1e6
    ratio = red / np.maximum(swir, 1e-4)
    row = {"year": y, "date": f["date"], "satellite": f["satellite"], "partly_cloudy": f["partly_cloudy"]}
    for t in THRESHOLDS:
        ice = np.isfinite(ratio) & (ratio > t)
        row[f"square_t{t}_km2"] = round(ice.sum() * px, 2)
        row[f"glaciers_t{t}_km2"] = round((ice & inside).sum() * px, 2)
    rows.append(row)
    print(y, row["square_t2.0_km2"], row["glaciers_t2.0_km2"])
OUT.parent.mkdir(exist_ok=True)
pd.DataFrame(rows).to_csv(OUT, index=False)
print(f"wrote {OUT.relative_to(ROOT)}; 2015 outlines {outlines.area.sum() / 1e6:.1f} km², in the square "
      f"{inside.sum() * px:.1f} km²")
