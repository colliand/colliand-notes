---
title: "Mount Hood: how much bright ice is left?"
subtitle: Late-summer satellite images, 2013–2026, against Portland State University's glacier outlines
date: 2026-10-21
kernelspec:
  name: python3
  display_name: Python 3
---

:::{note} Machine-drafted, first results
Drafted with Claude (an AI assistant) from the code and outputs in
[colliand/glacier-change](https://github.com/colliand/glacier-change); see its
[methods note](https://github.com/colliand/glacier-change/blob/main/methods/hood.md). Not peer reviewed.
:::

Mount Hood's glaciers were mapped by Portland State University (PSU) from 1956 maps and from 2015–16 imagery. Those
outlines are in the [GLIMS](https://www.glims.org) inventory. This note asks what has happened since: in each late
summer, how much of the area inside PSU's 2015–16 outlines still shows bright snow or clean ice from space?

**The short answer:** about half to 60% of it, down from 70–85% before 2021. The 2021 heat dome made the first dip,
which recovered. The hot summer of 2023 made a deeper one, which has not.

**But that is not how much ice was lost.** Field crews mapped Hood's glaciers in September 2023
([Bakken-French et al. 2024](https://doi.org/10.5194/tc-18-4517-2024)) and found 17% less area than in 2015–16. Checked
against their outlines, only about half of the ice they mapped looks bright from space. The rest is under rock and
dirt, which the satellite test reads as bare ground. Most of the 2023 drop is the glaciers' surface going dark: the snow
and old firn that covered their dirty lower parts melted off and has not come back.

```{code-cell} python
:tags: [remove-cell]
import os
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

# Outputs of colliand/glacier-change, pinned to the commit that made them.
SRC = os.environ.get("GLACIER_CHANGE",
                     "https://raw.githubusercontent.com/colliand/glacier-change/d0a3947") + "/data/hood"
outlines = gpd.read_file(f"{SRC}/glims_outlines.geojson")
series = pd.read_csv(f"{SRC}/landsat-series.csv", parse_dates=["date"])
field = pd.read_csv(f"{SRC}/ogi-2023-check.csv")
ogi = gpd.read_file(f"{SRC}/external/ogi_2023_margins.geojson")
scenes = pd.read_csv(f"{SRC}/landsat-scenes.csv", parse_dates=["date"])
plt.rcParams.update({"figure.dpi": 120, "axes.spines.top": False, "axes.spines.right": False})
```

## The outlines

The 2023 field outlines use a different standard from Portland State's, counting more ice under rock and stagnant
ice, so their total is close to the 2015–16 one. Compare change within one inventory only.

```{code-cell} python
:tags: [hide-input]
named = outlines[~outlines.name.isna()]
fig, ax = plt.subplots(figsize=(6, 6))
named[named.era == "then"].to_crs(32610).plot(ax=ax, color="#c9d6e3", edgecolor="#8aa0b8", lw=0.5)
named[named.era == "now"].to_crs(32610).plot(ax=ax, color="#2b6cb0", edgecolor="#1a4480", lw=0.5)
ogi.to_crs(32610).boundary.plot(ax=ax, color="#d9480f", lw=0.8)
ax.set_axis_off()
ax.set_title("Named glaciers: 1956 (pale), 2015–16 (blue), 2023 field-mapped (orange line)", fontsize=9)
km2 = named.groupby("era").km2.sum()
print(f"Named glaciers, km²\n  1956     {km2['then']:5.1f}  Portland State\n  2015–16  {km2['now']:5.1f}  Portland State\n"
      f"  2023     {ogi.to_crs(32610).area.sum() / 1e6:5.1f}  Bakken-French et al.")
```

## Bright surface each late summer

For every Landsat 8 and 9 scene from 25 August to 30 September: the share of the 2015–16 outline area that is bright
(red reflectance more than twice shortwave infrared, the standard glacier-mapping test). Scenes with cloud, haze or
gaps over the glaciers are dropped; October is left out because low sun puts the north-side glaciers in deep shadow.
Each year's line value is the median of its scenes. Fresh snow pushes single scenes up and wildfire smoke pushes
them down, so the spread within a year matters.

```{code-cell} python
:tags: [hide-input]
usable = pd.read_csv(f"{SRC}/landsat-usable.csv", parse_dates=["date"])
fig, ax = plt.subplots(figsize=(7, 3.6))
ax.scatter(usable.date.dt.year + (usable.date.dt.dayofyear - 237) / 120, 100 * usable.bright_share,
           s=12, color="#9aa9b8", label="each usable scene", zorder=2)
ax.plot(series.year, 100 * series.bright_share, "o-", color="#2b6cb0", label="median for the year", zorder=3)
ax.set_ylim(0, 100)
ax.set_ylabel("% of 2015–16 outline area bright")
ax.set_xticks(range(2013, 2027))
ax.tick_params(axis="x", labelsize=8, rotation=45)
ax.grid(axis="y", alpha=0.3)
ax.legend(frameon=False, fontsize=8, loc="lower left")
plt.show()
```

```{code-cell} python
:tags: [hide-input]
t = series.assign(**{"bright (median)": (100 * series.bright_share).round().astype(int).astype(str) + "%",
                     "range": [f"{100 * a:.0f}–{100 * b:.0f}%" for a, b in zip(series.min_share, series.max_share)]})
t[["year", "bright (median)", "range", "scenes"]].style.hide(axis="index")
```

The pattern: from 2013 to 2020 the bright share sat between about 70% and 85%. It fell to 56% in 2021, the summer
of the Pacific Northwest heat dome, and came back in 2022. Then 2023 took it to 44%, and it has stayed between 50%
and 62% since. (2014 is missing: both of its September scenes had cloud over the mountain.)

For each year, the scene nearest the median, with PSU's outlines in red and the bright edge in cyan:

```{figure} https://raw.githubusercontent.com/colliand/glacier-change/d0a3947/methods/hood-landsat-series.jpg
:alt: Grid of late-summer Landsat images of Mount Hood, one per year, with glacier outlines in red and bright snow and ice outlined in cyan.
Landsat 8/9 true colour, the scene nearest each year's median. Red: PSU 2015–16 outlines. Cyan: edge of bright snow and clean ice.
```

## Glacier by glacier (Sentinel-2, 10 m)

Sentinel-2 is sharper, with fewer clear late-season scenes. Bright area within 100 m of each glacier's outline, on two
clear days nine years apart:

```{code-cell} python
:tags: [hide-input]
def bright(date):
    a = pd.read_csv(f"{SRC}/areas-{date}.csv")
    return a.dropna(subset=["name"]).groupby("name")["t2.0_km2"].sum()

g = pd.DataFrame({"1956 km²": named[named.era == "then"].groupby("name").km2.sum(),
                  "2015–16 km²": named[named.era == "now"].groupby("name").km2.sum(),
                  "bright 2016-09-25": bright("2016-09-25"),
                  "bright 2025-09-23": bright("2025-09-23")})
g.loc["Total"] = g.sum()
g["change"] = (100 * (g["bright 2025-09-23"] / g["bright 2016-09-25"] - 1)).round().astype(int).astype(str) + "%"
g.index = g.index.str.removesuffix(" Glacier")
g.index.name = None
g.round(2).style.format(precision=2)
```

## Checked against the field-mapped 2023 outlines

Bakken-French and colleagues mapped Hood's glaciers from 30 cm imagery taken on 8 September 2023 and walked about 60%
of the edges, counting ice under rock and stagnant ice
([data on Zenodo](https://doi.org/10.5281/zenodo.13356244)). The share of *their* 2023 ice that Sentinel-2 shows as
bright:

```{code-cell} python
:tags: [hide-input]
f = field.pivot(index="glacier", columns="date", values="bright_share")
f = f.loc[[*sorted(i for i in f.index if i != "All"), "All"]]
km2 = field[field.date == field.date.iloc[0]].set_index("glacier").ogi_2023_km2
f.insert(0, "2023 area km²", km2)
f.index.name = None
f.style.format({c: "{:.0%}" for c in f.columns[1:]} | {"2023 area km²": "{:.2f}"}).background_gradient(
    cmap="Blues", subset=f.columns[1:], vmin=0, vmax=1)
```

The same ice outline, unchanged across the columns, went from about 80% bright in 2016 to about 50% from 2023 on.
West-side glaciers went darkest: Sandy, Ladd and Zigzag. The test is precise: on 14 September 2023 only 0.19 km² it
called bright fell outside the field outlines. But in a low-snow year it misses about half the real ice.

## What this does and does not show

- **Shows:** a sharp, lasting change in the glaciers' surface in 2023, after a first dip in 2021 that recovered.
  About half of Hood's remaining ice now looks like rock from space, against a fifth in 2016. Two satellites,
  analysed separately, agree on the timing.
- **Where:** mostly at the edges and below about 2,300 m, and on the west-side glaciers.
- **Does not show:** area loss. Field mapping puts that at 17% from 2015–16 to 2023, about half the bright-surface
  drop. A satellite test of bright ice, used alone, would overstate Hood's glacier loss about twofold.
- **Why it matters:** dark, debris-covered ice melts differently. A thin dirt layer speeds melt; thick rock slows it.
  Hood's lower glaciers are turning into the kind that a bright-ice satellite inventory cannot track.
- **Next:** repeat the field-outline check each year the field team publishes, and measure thinning from repeat lidar
  elevation where it exists (thinning shows even under rock).

## Data and credits

- Glacier outlines: Portland State University, via [GLIMS](https://www.glims.org) (NSIDC), and the 2023 Mt. Hood glacier
  margins of Bakken-French et al. (2024), published by the Oregon Glaciers Institute on Zenodo under CC BY 4.0
  [](https://doi.org/10.5281/zenodo.13356244).
- Landsat 8/9 Collection 2 Level-2 (USGS) and Sentinel-2 Level-2A (ESA Copernicus), via
  [Microsoft Planetary Computer](https://planetarycomputer.microsoft.com).
- Copernicus DEM GLO-30 for elevations.
- Code and outputs: [colliand/glacier-change](https://github.com/colliand/glacier-change).
