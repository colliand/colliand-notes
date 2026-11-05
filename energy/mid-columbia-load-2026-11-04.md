---
title: Grant County's load and the Columbia
subtitle: Grant PUD's load has grown enough since 2019 that an ordinary autumn now needs more power than its own dams make
date: 2026-11-04
description: Grant County PUD, home to the Quincy data centers, used about 26% more power in 2025 than in 2019. Its two Columbia River dams make the least power in the low-water months of September and October, and at today's load those are now the months when Grant uses more than its dams make.
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

Quincy, in Grant County, Washington, has become a data-center town. The servers came for cheap electricity from the
Columbia River. Grant County PUD, the public utility there, owns two dams on the river, Priest Rapids and Wanapum, and
supplies the county's homes, farms and data centers. I wanted to see how much the county's demand for power has grown
since 2019, and how it compares with what those two dams can make from the river month by month.

:::{tip} In short
- Grant PUD's customers used about 26% more power in 2025 than in 2019, an average of 769 MW compared with 612 MW.
- The dams turn more river into more power until the turbines are running flat out, at about 170,000 cubic feet per
  second. Water beyond that goes over the spillway, so a big spring runoff adds little, while a low autumn river costs
  a lot.
- Had Grant's load stayed at its 2019 level, its own dams would have covered it in every month since 2019 except
  September 2023, and then only by 5 MW. At the 2025 level they would have fallen short in 16 months, 12 of them in
  September or October.
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

Every utility or agency that keeps supply and demand matched on its own patch of the US grid, a balancing authority,
reports its load and generation to the Energy Information Administration each hour, on form EIA-930. Grant PUD
reports as `GCPD`, and its hydro generation is essentially the output of its two dams. For the river I use the USGS
gauge just below Priest Rapids Dam, the lower of Grant's two dams, which measures the water that has just run through
both of them.

## How Grant's load has grown

```{code-cell} python
:tags: [remove-input]
names = {"DOPD": "Douglas PUD", "GCPD": "Grant PUD", "BPAT": "Bonneville", "CHPD": "Chelan PUD"}
colors = {"DOPD": LINE, "GCPD": LOAD, "BPAT": LINE, "CHPD": LINE}
nudge = {"BPAT": 1.2, "CHPD": -1.2}  # keep the two labels apart
idx = annual.loc[2019:2025] / annual.loc[2019] * 100
fig, ax = plt.subplots(figsize=(7.5, 3.6))
for ba, label in names.items():
    ax.plot(idx.index, idx[ba], marker="o", ms=3, color=colors[ba], lw=2 if ba == "GCPD" else 1.2)
    ax.text(2025.1, idx.loc[2025, ba] + nudge.get(ba, 0), f"{label} {idx.loc[2025, ba] - 100:+.0f}%",
            va="center", fontsize=8, color=LOAD if ba == "GCPD" else MUTED)
ax.axhline(100, color=LINE, lw=0.8)
ax.set_xlim(2018.8, 2026.4); ax.set_xticks(range(2019, 2026)); ax.set_ylabel("average load, 2019 = 100")
plt.show()
```

Grant's average load, each year compared with 2019, rose every year from 2020 to 2025. To see whether that is
unusual I drew its neighbours in grey. Douglas PUD, across the river in East Wenatchee and also home to data centers,
grew even faster from a smaller base. Chelan PUD and the Bonneville Power Administration grew by less than 10%. I left
2026 out because December is not in yet.

## How the river makes power

The power a dam makes depends on how much water goes through its turbines and how far that water falls, which is
called the head. Turbine flow keeps pace with river flow only up to a point. When the river runs higher than the
turbines can take, the extra water goes over the spillway and makes no power, and high water backs up below the dam
and shortens the fall.

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

Each dot is one day from 2019 to October 2026. Up to about 150,000 cubic feet per second, each extra thousand adds
roughly 11 MW. Above about 170,000 the output levels off near 1,400 MW, however high the river runs.

At the same flow, days from November to March make more power than days from April to August, and reach 1,700 MW. My
guess is the spill for young salmon: in spring and summer the dams send some water over the spillway on purpose, to
help the fish downstream. I haven't yet checked this against Grant's operating rules. The September and October days
line up with the winter days, which fits the guess, since as I understand it the fish spill ends in late summer. Those
autumn days also sit at the low end of the curve, where every thousand cubic feet per second lost costs the most
power.

## Load growth or drought?

Grant's load first ran above its dams' output in 2023, a dry year, and I wanted to know whether the cause was the
growing load or the low river. To separate the two, I kept each month's actual hydro output and compared it with two
steady loads: the 2019 average of 612 MW and the 2025 average of 769 MW.

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

With the 2019 load, Grant's dams would have fallen short in only one month in nearly eight years, September 2023,
and then by just 5 MW. With the 2025 load they would have fallen short in 16 months, at least once in every year except
2020, and 12 of those months are in September or October. Even in ordinary years like 2019 and 2021, today's load
would have outrun the river in early autumn. The growth in load is what changed, and the low autumn river decides
which months feel it.

## Some caution

Grant sells a share of its dams' output to other utilities under long-term contracts and buys power on the wider
grid, so a month when its load tops its hydro output is a sign of pressure. The lights stay on, and Grant leans on
the wider grid at the time of year when the whole river is low.

EIA-930 counts all of Grant's load together and doesn't separate the data centers. The steady rise in the floor of
the load looks to me like servers running day and night, but that is my reading of the curve.

I used a steady load to keep the comparison simple. Real load peaks in July, so the months over in the table are a
first estimate.

## What I want to look at next

I'd like to check the two-curves guess against Grant's spill schedule, and look at the head at each dam from its
water levels above and below. I'm also curious about the snowpack and glacier melt that keep the late-summer river up.
Farther upstream, Grand Coulee and the Canadian dams under the Columbia River Treaty decide much of what reaches Grant
in the first place.

## Data

- US Energy Information Administration, Form EIA-930 hourly balancing-authority data, six-month bulk files
  ([eia.gov/electricity/gridmonitor](https://www.eia.gov/electricity/gridmonitor/)). Public domain.
- US Geological Survey, gauge 12472800, Columbia River below Priest Rapids Dam, daily mean discharge
  ([waterdata.usgs.gov](https://waterdata.usgs.gov/monitoring-location/12472800/)). Public domain.
- Derived files: [`data/grant-daily.csv`](data/grant-daily.csv) and [`data/annual-load.csv`](data/annual-load.csv),
  CC BY 4.0, rebuilt by `uv run python scripts/grant_pud_data.py`.
