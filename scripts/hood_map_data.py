"""Per-glacier facts for the Mount Hood 3D map (maps/data/hood_glaciers.json), from glacier-change outputs.

    uv run python scripts/hood_map_data.py            # from GitHub, pinned like the notebook
    GLACIER_CHANGE=../glacier-change uv run python scripts/hood_map_data.py
"""
import json
import os

import geopandas as gpd
import pandas as pd

SRC = os.environ.get("GLACIER_CHANGE",
                     "https://raw.githubusercontent.com/colliand/glacier-change/d0a3947") + "/data/hood"
psu = gpd.read_file(f"{SRC}/glims_outlines.geojson")
psu = psu[~psu.name.isna()]
check = pd.read_csv(f"{SRC}/ogi-2023-check.csv")

out = {}
for name, g in psu.groupby("name"):
    short = name.removesuffix(" Glacier").replace("Newton Clark", "Newton-Clark")
    c = check[check.glacier == short].sort_values("date")
    out[short] = {
        "name": name,
        "km2_1956": round(g[g.era == "then"].km2.sum(), 3),
        "km2_2015": round(g[g.era == "now"].km2.sum(), 3),
        "year_2015": int(g[g.era == "now"].year.max()),
        "km2_2023": round(float(c.ogi_2023_km2.iloc[0]), 3) if len(c) else None,
        # share of the field-mapped 2023 outline that is bright on one September Sentinel-2 image per year
        "bright": [{"date": d, "share": round(s, 3)} for d, s in zip(c.date, c.bright_share)],
    }
with open("maps/data/hood_glaciers.json", "w") as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
print(len(out), "glaciers")
