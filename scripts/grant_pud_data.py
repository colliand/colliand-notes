"""Data for energy/mid-columbia-load-2026-11-04: Grant PUD load and hydro against the Columbia's flow.

    uv run python scripts/grant_pud_data.py

Downloads EIA-930 hourly balancing-authority data (the six-month bulk CSVs, ~50 MB each, no API key) and USGS daily
flow at 12472800, Columbia River below Priest Rapids Dam, and writes two small files the note reads:

- energy/data/grant-daily.csv: GCPD daily mean demand and hydro (MW) with flow (kcfs), 2019-01-01 to END.
- energy/data/annual-load.csv: mean demand (MW) by year for the PNW balancing authorities.

The bulk files are cached in ~/.cache/colliand-notes/eia930/; past half-years are fixed, so only missing ones download.
Both sources are US federal data (public domain). The exploration behind this lives in a private lab notebook.
"""
import io
import json
import urllib.request
from pathlib import Path

import pandas as pd

END = "2026-10-31"
OUT = Path(__file__).resolve().parent.parent / "energy" / "data"
CACHE = Path.home() / ".cache" / "colliand-notes" / "eia930"
EIA = "https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/EIA930_BALANCE_{y}_{h}.csv"
BAS = ["BPAT", "GCPD", "CHPD", "DOPD", "PSEI", "SCL", "TPWR", "AVA"]
COLS = {
    "Balancing Authority": "ba",
    "UTC Time at End of Hour": "utc",
    "Demand (MW) (Adjusted)": "demand_mw",
    "Net Generation (MW) from Hydropower Excluding Pumped Storage (Adjusted)": "hydro_mw",
    # files before mid-2025 lump pumped storage in; the PNW has almost none
    "Net Generation (MW) from Hydropower and Pumped Storage (Adjusted)": "hydro_mw",
}


def get(url):
    with urllib.request.urlopen(url, timeout=300) as r:
        return r.read()


def eia930():
    CACHE.mkdir(parents=True, exist_ok=True)
    end = pd.Timestamp(END)
    parts = []
    for y in range(2019, end.year + 1):
        for h, m in (("Jan_Jun", 1), ("Jul_Dec", 7)):
            if pd.Timestamp(y, m, 1) > end:
                continue
            cache = CACHE / f"{y}_{h}.csv.gz"
            if not cache.exists():
                df = pd.read_csv(io.BytesIO(get(EIA.format(y=y, h=h))), usecols=lambda c: c in COLS,
                                 thousands=",", low_memory=False).rename(columns=COLS)
                df = df[df.ba.isin(BAS)]
                df["utc"] = pd.to_datetime(df.utc, format="%m/%d/%Y %I:%M:%S %p")
                df.to_csv(cache, index=False)
            parts.append(pd.read_csv(cache, parse_dates=["utc"]))
    e = pd.concat(parts, ignore_index=True)
    # local days for a Pacific utility; drop anything after END
    e["date"] = e.utc.dt.tz_localize("UTC").dt.tz_convert("America/Los_Angeles").dt.tz_localize(None).dt.normalize()
    return e[(e.date >= "2019-01-01") & (e.date <= END)]


def usgs(site="12472800"):
    q = f"https://waterservices.usgs.gov/nwis/dv/?sites={site}&parameterCd=00060&startDT=2019-01-01&endDT={END}&format=json"
    vals = json.loads(get(q))["value"]["timeSeries"][0]["values"][0]["value"]
    return pd.Series({pd.Timestamp(v["dateTime"][:10]): float(v["value"]) / 1000 for v in vals}, name="flow_kcfs")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    e = eia930()
    g = e[e.ba == "GCPD"].groupby("date")[["demand_mw", "hydro_mw"]].mean()
    daily = g.join(usgs(), how="inner").round(1)
    daily.index.name = "date"
    daily.to_csv(OUT / "grant-daily.csv")
    annual = e.groupby([e.date.dt.year.rename("year"), "ba"]).demand_mw.mean().unstack().round(0)
    annual.to_csv(OUT / "annual-load.csv")
    print(f"{len(daily)} days, {daily.index.min():%F} to {daily.index.max():%F}")
    print(annual)
