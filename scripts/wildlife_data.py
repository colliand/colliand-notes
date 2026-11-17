"""Data for wildlife/whatcom-wildlife-by-month: animals by month in Whatcom County, and the salmon calendar.

    uv run python scripts/wildlife_data.py
    WL_BASE=https://wildlife.whatcom-land.pages.dev uv run python scripts/wildlife_data.py   # a whatcom.land preview

Writes small files the note reads, in wildlife/data/:

- monthly.csv: for each animal on whatcom.land's Wildlife page and each month, the eBird checklist share (birds,
  copied from whatcom.land's published wildlife_summary.json, which is all eBird data that leaves that build) and the
  iNaturalist research-grade count (every animal), plus all research-grade observations that month (`all`).
- salmon-timing.csv: whatcom.land's run-timing table for the Nooksack (pipeline/salmon_run_timing.csv), as published
  in the same summary.
- chum-spawners.csv: WDFW's yearly spawner estimate for Nooksack fall chum (North Fork index), from the SPI
  escapement dataset on data.wa.gov.

iNaturalist responses are cached in ~/.cache/colliand-notes/inat/ (one request a second, as iNaturalist asks).
eBird data: eBird.org, Cornell Lab of Ornithology, used for noncommercial education; no records are republished here.
"""
import json
import os
import ssl
import time
import urllib.parse
import urllib.request
from pathlib import Path

import certifi
import pandas as pd

BASE = os.environ.get("WL_BASE", "https://whatcom.land")
OUT = Path(__file__).resolve().parent.parent / "wildlife" / "data"
CACHE = Path.home() / ".cache" / "colliand-notes" / "inat"
INAT = "https://api.inaturalist.org/v1"
PLACE = 1730  # Whatcom County
SPI = "https://data.wa.gov/resource/fgyz-n3uk.json"
# iNaturalist taxon ids for the animals on the page (birds by eBird name)
TAXA = {"Bald eagle": 5305, "Glaucous-winged gull": 4399, "Common merganser": 7004, "River otter": 41777,
        "Black bear": 41638, "Harlequin duck": 7111, "American dipper": 7643, "Belted kingfisher": 2548,
        "Great blue heron": 4956, "Beaver": 43794, "Trumpeter swan": 6915, "Snow goose": 558426,
        "Common goldeneye": 6990, "Barrow's goldeneye": 6994, "Pine grosbeak": 9771}
UA = {"User-Agent": "notes.colliand.com data script (noncommercial)"}


def get(url: str) -> bytes:
    ctx = ssl.create_default_context(cafile=certifi.where())
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60, context=ctx) as r:
        return r.read()


def inat_month(taxon: int | None) -> list[int]:
    q = {"place_id": PLACE, "interval": "month_of_year", "quality_grade": "research", "date_field": "observed"}
    if taxon:
        q["taxon_id"] = taxon
    f = CACHE / f"hist_{PLACE}_{taxon or 'all'}.json"
    if not f.exists():
        time.sleep(1.0)
        CACHE.mkdir(parents=True, exist_ok=True)
        f.write_bytes(get(f"{INAT}/observations/histogram?{urllib.parse.urlencode(q)}"))
    m = json.loads(f.read_text())["results"]["month_of_year"]
    return [int(m[str(i)]) for i in range(1, 13)]


def check_taxa():
    """Make sure each id is the species we mean (iNaturalist ids are easy to mistype)."""
    ids = ",".join(str(v) for v in TAXA.values())
    got = {t["id"]: t for t in json.loads(get(f"{INAT}/taxa/{ids}"))["results"]}
    for name, tid in TAXA.items():
        common = (got[tid].get("preferred_common_name") or "").lower()
        if name.split()[-1].lower() not in common:
            raise SystemExit(f"{name}: iNaturalist {tid} is {got[tid]['name']} ({common})")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    s = json.loads(get(f"{BASE}/data/whatcom/wildlife_summary.json"))
    check_taxa()
    effort = inat_month(None)
    rows = []
    for sp in s["species"]:
        counts = inat_month(TAXA[sp["name"]])
        for i in range(12):
            rows.append({"animal": sp["name"], "group": sp["group"], "month": i + 1,
                         "ebird_share": sp["share"][i] if sp["source"] == "ebird" else None,
                         "inat_count": counts[i], "all": effort[i]})
    pd.DataFrame(rows).to_csv(OUT / "monthly.csv", index=False)

    t = [{"species": r["species"], "run": r["run"], "in_river": " ".join(map(str, r["in_river"])),
          "spawning": " ".join(map(str, r["spawning"])), "uncertain": " ".join(map(str, r["uncertain"]))}
         for r in s["runs"]]
    pd.DataFrame(t).to_csv(OUT / "salmon-timing.csv", index=False)

    q = urllib.parse.urlencode({"$limit": 500, "population_name": "Nooksack Fall Chum", "data_type": "Spawner Fish"})
    spi = pd.DataFrame(json.loads(get(f"{SPI}?{q}")))
    spi = spi.assign(year=spi.year.astype(int), spawners=pd.to_numeric(spi.abundance_qty))
    spi.groupby("year").spawners.sum().reset_index().to_csv(OUT / "chum-spawners.csv", index=False)
    print(f"wrote {len(rows)} monthly rows, {len(t)} runs, {len(spi)} chum years (summary built {s['generated']})")


if __name__ == "__main__":
    main()
