"""Data for the Mount Baker bright-ice map (maps/baker-s2.html): scene list and glacier outlines.

    uv run python scripts/baker_s2_data.py [path/to/whatcom-land]

Scenes: the late-season Sentinel-2 L2A scenes of tile 10UEV that whatcom.land's glacier method uses, from Element 84's
Collection 1 archive on AWS (public, no token, readable from a browser). Planetary Computer, which whatcom.land uses and
which alone has 2015, stores its bands as 15-bit COGs that deck.gl-raster 0.8.1 cannot decode, so 2015 appears only
as the Portland State outlines. Collection 1 is reprocessed with baseline 05.00+, so every scene carries the +1000
offset in its digital numbers; `offset` records it so the page can remove it before taking the ratio.

Outlines: PSU 2015 (GLIMS) and whatcom.land's 2025 estimate, within 10 km of the summit, from a whatcom-land checkout
(default ../whatcom-land).
"""
import json
import math
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "maps" / "data"
WL = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT.parent / "whatcom-land"
SUMMIT = (-121.8144, 48.7768)
RADIUS_KM = 10
STAC = "https://earth-search.aws.element84.com/v1/search"
# Clear late-season scenes vetted in whatcom-land methods/glacier-outlines.md. 2022-09-27 is left out (2022's big
# snowpack was still lying); 2024-09-06 too (smoke).
DATES = {
    "2021-09-24": "Before the hottest summers on record at South Cascade Glacier",
    "2023-09-14": "After the 2023 melt season",
    "2025-09-23": "The latest clear scene before autumn snow; whatcom.land's 2025 estimate",
}
BANDS = {"blue": "blue", "green": "green", "red": "red", "swir": "swir16"}  # page slot: Earth Search asset (B02, B03, B04, B11)


def search(date):
    body = {"collections": ["sentinel-2-c1-l2a"], "intersects": {"type": "Point", "coordinates": list(SUMMIT)},
            "datetime": f"{date}T00:00:00Z/{date}T23:59:59Z", "limit": 10,
            "query": {"mgrs:utm_zone": {"eq": 10}, "mgrs:latitude_band": {"eq": "U"}, "mgrs:grid_square": {"eq": "EV"}}}
    req = urllib.request.Request(STAC, json.dumps(body).encode(), {"Content-Type": "application/json"})
    feats = json.load(urllib.request.urlopen(req, timeout=60))["features"]
    if not feats:
        raise SystemExit(f"no 10UEV scene on {date}")
    # Two satellites can pass on one date (2025-09-23: S2A and S2B); keep the clearer
    return min(feats, key=lambda f: f["properties"]["eo:cloud_cover"])


def scenes():
    out = []
    for date, why in DATES.items():
        f = search(date)
        baseline = f["properties"]["s2:processing_baseline"]
        offset = -f["assets"]["red"]["raster:bands"][0]["offset"] / f["assets"]["red"]["raster:bands"][0]["scale"]
        out.append({"date": date, "note": why, "id": f["id"], "baseline": baseline, "offset": round(offset),
                    "bands": {k: f["assets"][b]["href"] for k, b in BANDS.items()}})
        print(date, f["id"], baseline)
    return out


def near(geom):
    lon, lat = SUMMIT
    ring = geom["coordinates"][0] if geom["type"] == "Polygon" else geom["coordinates"][0][0]
    x, y = ring[0]
    dx = (x - lon) * 111.32 * math.cos(math.radians(lat))
    dy = (y - lat) * 110.57
    return math.hypot(dx, dy) <= RADIUS_KM


def outlines():
    src = WL / "site" / "data" / "whatcom"
    psu = json.load(open(src / "snow_glaciers.geojson"))
    est = json.load(open(src / "snow_glaciers_2025.geojson"))
    feats = [{"type": "Feature", "geometry": f["geometry"], "properties": {"set": "2015", "name": f["properties"]["name"]}}
             for f in psu["features"] if f["properties"]["era"] == "now" and near(f["geometry"])]
    feats += [{"type": "Feature", "geometry": f["geometry"], "properties": {"set": "2025", "name": f["properties"]["name"]}}
              for f in est["features"] if near(f["geometry"])]
    return {"type": "FeatureCollection", "features": feats}


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "baker_s2_scenes.json").write_text(json.dumps(scenes(), indent=1) + "\n")
    o = outlines()
    (OUT / "baker_outlines.geojson").write_text(json.dumps(o, separators=(",", ":")) + "\n")
    print(f"outlines: {sum(f['properties']['set'] == '2015' for f in o['features'])} (2015), "
          f"{sum(f['properties']['set'] == '2025' for f in o['features'])} (2025)")
