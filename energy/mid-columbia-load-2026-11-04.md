---
title: Grant County's load and the Columbia
subtitle: Since 2019, an ordinary autumn has come to need more power than Grant PUD's own dams make
date: 2026-11-04
description: Grant County PUD, home to the Quincy data centers, now uses about 25% more power than in 2019. Its dams make power roughly in step with river flow until the turbines fill up, so the pinch comes in low-water autumns, and at today's load most years now have a month or more when local load tops local hydro.
tags: [energy, hydropower, Columbia River, data centers, EIA-930]
draft: true
kernelspec:
  name: python3
  display_name: Python 3
---

:::{note} Machine-drafted
Drafted with help from AI language models, working from my exploration notebook and the data script
`scripts/grant_pud_data.py` in this site's repo. A dated snapshot (data through 31 October 2026), not peer reviewed.
:::

Data centers in Quincy and East Wenatchee sit beside the mid-Columbia dams. Grant County PUD runs Priest Rapids and
Wanapum; Douglas PUD runs Wells; Chelan PUD runs Rock Island and Rocky Reach. Cheap hydropower is a large part of why
the servers came. I wanted to know how fast local load is growing against what the river delivers, and whether a dry
year now matters more than it used to.

:::{tip} In short
- Grant PUD's average load rose from 612 MW in 2019 to 769 MW in 2025, about 26%. Douglas PUD rose about 35%.
- Grant's dams make power roughly in step with river flow up to about 150,000 cubic feet per second. Above about
  170,000 the turbines are full and the extra water spills, so a wet spring adds little.
- At the 2019 load, only one month from 2019 to 2026 has Grant's load above its own hydro output: September 2023,
  the driest. At the 2025 load, most years do, mostly in September and October, when the river is low.
:::

```{code-cell} python
:tags: [remove-cell]
import matplotlib.pyplot as plt
import pandas as pd

# Written by scripts/grant_pud_data.py from EIA-930 and USGS 12472800, data through 2026-10-31
daily = pd.read_csv("data/grant-daily.csv", parse_dates=["date"], index_col="date")
annual = pd.read_csv("data/annual-load.csv", index_col="year")

# whatcom.land colours (site/theme.js THEME)
INK, MUTED, LINE = "#1f2a24", "#5b6760", "#c9c5b9"
WATER, LOAD = "#2171b5", "#d94801"
plt.rcParams.update({"figure.dpi": 130, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
                     "font.size": 9})
```

## Where the data comes from

Every balancing authority in the US, the utility or agency that keeps supply and demand matched on its patch of grid,
reports its load and generation to the Energy Information Administration each hour (form EIA-930). Grant PUD reports as
`GCPD`. Its hydro generation is essentially the output of its two dams. For the river I use the USGS gauge just below
Priest Rapids Dam, the last of Grant's dams, so the gauge measures the water that has just run through them.

## How fast is load growing?

```{code-cell} python
:tags: [remove-input]
names = {"DOPD": "Douglas PUD", "GCPD": "Grant PUD", "BPAT": "Bonneville", "CHPD": "Chelan PUD"}
colors = {"DOPD": "#7a4a9e", "GCPD": LOAD, "BPAT": MUTED, "CHPD": "#5b86a8"}
nudge = {"BPAT": 1.2, "CHPD": -1.2}  # keep the two labels apart
idx = annual.loc[2019:2025] / annual.loc[2019] * 100
fig, ax = plt.subplots(figsize=(7.5, 3.6))
for ba, label in names.items():
    ax.plot(idx.index, idx[ba], marker="o", ms=3, color=colors[ba], lw=2 if ba == "GCPD" else 1.2)
    ax.text(2025.1, idx.loc[2025, ba] + nudge.get(ba, 0), f"{label} {idx.loc[2025, ba] - 100:+.0f}%",
            va="center", fontsize=8, color=colors[ba])
ax.axhline(100, color=LINE, lw=0.8)
ax.set_xlim(2018.8, 2026.4); ax.set_xticks(range(2019, 2026)); ax.set_ylabel("average load, 2019 = 100")
plt.show()
```

Average load, each year against 2019. Grant and Douglas, home to the Quincy and East Wenatchee campuses, grew far
faster than Bonneville's large federal footprint or Chelan next door. Puget Sound Energy, my own utility on the west
side, is left off: its load drops 20% between 2019 and 2020 and stays there, which looks like a change in what it
reports rather than a real fall. 2026 is left out because December is not in yet.

## Does more river mean more power?

Not simply. The power a dam makes is roughly efficiency × the weight of water × the flow **through the turbines** ×
the head, the drop in water level across the dam. River flow is not turbine flow. Once the turbines are full, the
extra water spills over the dam and makes nothing. High water also raises the river below the dam more than above it,
which shrinks the head.

```{code-cell} python
:tags: [remove-input]
d = daily[daily.hydro_mw > 0]
m = d.index.month
groups = [("November to March", m.isin([11, 12, 1, 2, 3]), WATER),
          ("April to August", m.isin([4, 5, 6, 7, 8]), LOAD),
          ("September and October", m.isin([9, 10]), "#2f6b4f")]
fig, ax = plt.subplots(figsize=(7.5, 4.4))
for label, sel, c in groups:
    ax.scatter(d.flow_kcfs[sel], d.hydro_mw[sel], s=5, color=c, alpha=0.5, lw=0, label=label)
ax.set(xlabel="Columbia River below Priest Rapids, thousand cubic feet per second (daily)",
       ylabel="Grant PUD hydro output, MW (daily)")
ax.legend(frameon=False, markerscale=3, fontsize=8, loc="lower right")
plt.show()
```

Each dot is one day from 2019 to October 2026. Three things show:

- **In step at low flow.** Up to about 150,000 cubic feet per second, each extra thousand adds roughly 11 MW.
- **A ceiling.** Above about 170,000, output stays near 1,400 MW however high the river runs.
- **Two curves.** At the same flow, winter days make more power than spring and summer days, up to 1,700 MW. My guess
  is the spill required for young salmon in spring and summer, water sent past the turbines on purpose. I have not yet
  checked that against Grant's operating rules.

The low-water days of September and October sit on the steep part of the curve, where every lost thousand cubic feet
per second costs the most power. They also sit on the winter curve, not the summer one, which fits the spill guess:
the fish spill season is over by then.

## Load growth or drought?

The dry years 2023 to 2025 came at the same time as the load growth, so either could explain months when Grant's load
ran above its own output. To separate them I hold the river fixed and change only the load: keep each year's real
monthly hydro output, and set it against a flat load at the 2019 average and at the 2025 average.

```{code-cell} python
:tags: [remove-input]
mon = daily.resample("MS").mean()
L19, L25 = annual.loc[2019, "GCPD"], annual.loc[2025, "GCPD"]
fig, ax = plt.subplots(figsize=(7.5, 3.6))
ax.plot(mon.index, mon.hydro_mw, color=WATER, lw=1.5, label="Grant hydro output (monthly)")
ax.plot(mon.index, mon.demand_mw, color=LOAD, lw=1.2, label="Grant load (actual)")
ax.axhline(L19, color=MUTED, ls="--", lw=1)
ax.axhline(L25, color=INK, ls="--", lw=1)
ax.text(1.01, L19, f"2019 load\n{L19:.0f} MW", transform=ax.get_yaxis_transform(), va="center", fontsize=8, color=MUTED)
ax.text(1.01, L25, f"2025 load\n{L25:.0f} MW", transform=ax.get_yaxis_transform(), va="center", fontsize=8, color=INK)
ax.set_ylim(450, 1700); ax.set_ylabel("MW")
ax.legend(frameon=False, fontsize=8, loc="upper left", ncol=2)
plt.show()
```

```{code-cell} python
:tags: [remove-input]
yr = mon.index.year
table = pd.DataFrame({
    "months over, at the 2019 load": (mon.hydro_mw < L19).groupby(yr).sum(),
    "months over, at the 2025 load": (mon.hydro_mw < L25).groupby(yr).sum(),
    "months over, actual load": (mon.demand_mw > mon.hydro_mw).groupby(yr).sum(),
})
table.index.name = None
table
```

- At the 2019 load, **one month in eight years** has load above output: September 2023, the driest, by 5 MW.
- At the 2025 load, **most years** have one to four such months, including ordinary years like 2019 and 2021. Twelve
  of those 16 months are September or October.

So the growth in load did it, and low water decides when.

## What this does not say

- **Over 100% is a pressure sign, not a shortage.** Grant sells part of its dams' output to other utilities under
  long-term contracts and buys power from the wider grid, so the lights stay on. What changes is that Grant leans on the
  wider grid in the months when the whole river is low.
- **Load is not all data centers.** EIA-930 does not meter them separately. The steady rise in the floor of Grant's
  load fits servers that run around the clock, but that is a reading, not a measurement.
- **A flat load is a simplification.** Real load peaks in July. The comparison is a first cut, not a forecast.

## What I want to look at next

Grant's spill schedule, to test the two-curves guess. The head at each dam, from forebay and tailwater levels. The
snowpack and glacier melt that keep the late-summer river up. And upstream: Grand Coulee and the Canadian dams under
the Columbia River Treaty decide much of what reaches Grant in the first place.

## Data

- US Energy Information Administration, Form EIA-930 hourly balancing-authority data, six-month bulk files
  ([eia.gov/electricity/gridmonitor](https://www.eia.gov/electricity/gridmonitor/)). Public domain.
- US Geological Survey, gauge 12472800, Columbia River below Priest Rapids Dam, daily mean discharge
  ([waterdata.usgs.gov](https://waterdata.usgs.gov/monitoring-location/12472800/)). Public domain.
- Derived files: [`data/grant-daily.csv`](data/grant-daily.csv) and [`data/annual-load.csv`](data/annual-load.csv),
  CC BY 4.0, rebuilt by `uv run python scripts/grant_pud_data.py`.
