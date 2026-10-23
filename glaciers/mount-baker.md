---
title: What is happening to Mount Baker's glaciers?
subtitle: Maps from 1975 and 2015, and satellite images every late summer since
date: 2026-10-23
thumbnail: img/share-baker.jpg
description: Mount Baker's glaciers covered 48 km² on the 1970s maps and 40 km² in 2015. Satellite images say about another seventh of that bright ice was gone by 2025, mostly from the edges, and 2026 brought no recovery.
tags: [Sentinel-2, Landsat, Mount Baker, whatcom.land]
draft: true
kernelspec:
  name: python3
  display_name: Python 3
---

:::{note} Machine-drafted
Drafted with help from AI language models, working from my analysis code and its outputs in
[colliand/glacier-change](https://github.com/colliand/glacier-change). First results, not peer reviewed.
:::

The [Glaciers tab on whatcom.land](https://whatcom.land/glaciers) shows Mount Baker's glaciers in 1974–75, 2015 and
2025. The first two are maps made by glaciologists. The third is my own estimate from satellite images. This note
explains how I made it, how I checked it, and what it says.

:::{tip} In short
- On the 1970s maps Mount Baker's glaciers covered 48.0 km². By 2015 they covered 40.2 km², 16% less.
- A simple test on satellite images finds the 2015 ice to within 1%, so I trust it on Baker.
- By September 2025 about 14% of the 2015 bright ice was gone, mostly from a band about 30 m wide around every
  edge. 2026 was no better.
:::

```{code-cell} python
:tags: [remove-cell]
import os
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

# Outputs of colliand/glacier-change, pinned to the commit that made them.
SRC = os.environ.get("GLACIER_CHANGE",
                     "https://raw.githubusercontent.com/colliand/glacier-change/ed6f2d1") + "/data/baker"
outlines = gpd.read_file(f"{SRC}/glims_outlines.geojson")
DATES = ["2015-10-04", "2022-09-27", "2023-09-14", "2025-09-03", "2025-09-23", "2026-09-16"]
areas = {d: pd.read_csv(f"{SRC}/areas-{d}.csv") for d in DATES}
series = pd.read_csv(f"{SRC}/landsat-series.csv")
usable = pd.read_csv(f"{SRC}/landsat-usable.csv", parse_dates=["date"])

# whatcom.land's snow palette (maps/theme.js): ColorBrewer Purples, light to dark, and the teal of the newest outline
SNOW = ["#f2f0f7", "#cbc9e2", "#9e9ac8", "#756bb1", "#54278f", "#3f007d"]
TEAL, INK, MUTED, LINE = "#0e8a9e", "#1f2a24", "#5b6760", "#e2e0d8"
plt.rcParams.update({"figure.dpi": 130, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
                     "font.size": 9})
```

## What do the maps show?

Portland State University mapped the glaciers of the North Cascades twice: from USGS maps made from 1974–75 air
photos, and from 2015 images. Their outlines are in [GLIMS](https://www.glims.org), the global glacier inventory.
Counting everything within 10 km of Baker's summit:

```{code-cell} python
:tags: [remove-input]
km2 = outlines.groupby("era").km2.sum()
print(f"Baker's glaciers (Portland State)\n"
      f"  1974–75  {km2['then']:4.1f} km²\n"
      f"     2015  {km2['now']:4.1f} km²   {100 * (km2['now'] / km2['then'] - 1):.0f}%")
```

That is 16% in forty years. You can see the two outlines in 3D on [whatcom.land](https://whatcom.land/glaciers).

## Can a satellite find the ice?

Clean snow and ice are bright in red light and dark in shortwave infrared; rock is not. Where red divided by shortwave
infrared is above 2, I call it ice. This is the standard test glacier inventories use. (You can try it yourself, and
drag the threshold, in [an earlier note](baker-bright-ice.md).)

The test only means something if it agrees with the maps. Only one clear Sentinel-2 image exists from 2015, taken on 4
October, so I compared it with Portland State's 2015 outlines:

```{code-cell} python
:tags: [remove-input]
a = areas["2015-10-04"]
print(f"Portland State 2015  {a.ref_km2.sum():4.1f} km²\n"
      f"Satellite, Oct 2015  {a['t2.0_km2'].sum():4.1f} km²  "
      f"{100 * (a['t2.0_km2'].sum() / a.ref_km2.sum() - 1):+.0f}%\n"
      f"  stricter / looser  {a['t2.5_km2'].sum():.1f} / {a['t1.5_km2'].sum():.1f}")
```

The totals agree to within 1%, and 93% of the pixels agree too. The misses are where you would expect them: the lowest
tongues of Deming, Easton, Coleman and Boulder glaciers, which are covered in rock. On [Mount Hood](mount-hood.md),
where the glaciers carry much more rock, the same test did much worse. On Baker I trust it.

## How much has gone since 2015?

I ran the same test on every clear late-summer image I could find, checking each one by eye for cloud, smoke and
early snow.

```{code-cell} python
:tags: [remove-input]
base = areas["2015-10-04"]["t2.0_km2"].sum()
rows = []
for d, a in areas.items():
    t = a["t2.0_km2"].sum()
    rows.append({"image": d, "bright ice, km²": round(t, 1),
                 "range, km²": f"{a['t2.5_km2'].sum():.1f}–{a['t1.5_km2'].sum():.1f}",
                 "since 2015": "" if d == "2015-10-04" else f"{100 * (t / base - 1):.0f}%"})
pd.DataFrame(rows).set_index("image").rename_axis(None)
```

The best image is 23 September 2025: the end of the melt season, before the first autumn snow. Against 2015, about 14%
of the bright ice was gone. The range comes from making the test stricter or looser, and it is small. The date of the
image matters more than the threshold: in September 2022 a lot of the big winter's snow was still lying at the edges.

:::{figure} img/baker-change-2015-2025.jpg
:label: fig-baker-change
:alt: Mount Baker from above on 23 September 2025. An orange band rings every glacier: bright ice in 2015 that is gone by 2025.
Mount Baker on 23 September 2025, north at the top. Orange: bright ice in October 2015 that is not there in September
2025. Thin white lines: Portland State's 2015 outlines.
:::

The loss is a ring around every glacier. Half of the lost ice lies within 30 m of the 2015 edge, and 90% within 94 m.
It is widest at the low tongues. Inside the ring nothing much has changed: the glaciers are shrinking from the edges,
not breaking up.

```{code-cell} python
:tags: [remove-input]
a0, a1 = areas["2015-10-04"], areas["2025-09-23"]
g = pd.DataFrame({"name": a0.name, "y2015": a0["t2.0_km2"], "y2025": a1["t2.0_km2"]}).dropna()
g = g.groupby("name").sum()
g = g[g.y2015 > 0.5].sort_values("y2015")
chg = 100 * (g.y2025 / g.y2015 - 1)
fig, ax = plt.subplots(figsize=(4.2, 3.8))
ax.barh([n.replace(" Glacier", "") for n in g.index], chg, color=SNOW[3])
for i, v in enumerate(chg):
    ax.text(v - 0.6, i, f"{v:.0f}%", va="center", ha="right", fontsize=8, color=INK)
ax.set_title("Bright ice lost, 2015 to 2025\n(largest glacier at the top)", fontsize=9, color=INK, loc="left")
ax.set_xlim(min(chg) - 8, 0)
ax.grid(axis="x", color=LINE)
plt.show()
```

The big glaciers on the mountain lost about a tenth. The small ones lost a larger share: a ring of the same width is a
bigger part of a small glacier.

## What do satellites see each summer?

Sentinel-2 only began in 2015. Landsat 8 and 9 go back to 2013, at a coarser 30 m. For every clear Landsat image from
late August through September, I measured how much of the 2015 glacier area was bright.

```{code-cell} python
:tags: [remove-input]
fig, ax = plt.subplots(figsize=(6.4, 3.2))
ax.scatter(usable.date.dt.year + (usable.date.dt.dayofyear - 255) / 140, 100 * usable.bright_share,
           s=10, color=SNOW[2], label="one image", zorder=2)
ax.plot(series.year, 100 * series.bright_share, "o-", color=SNOW[4], lw=1.8, ms=5, label="middle value for the year", zorder=3)
ax.set_ylim(0, 100)
ax.set_ylabel("% of 2015 glacier area that is bright")
ax.set_xticks(range(2013, 2027), [str(y) if y in (2013, 2026) else f"’{y % 100:02d}" for y in range(2013, 2027)])
ax.grid(axis="y", color=LINE)
ax.legend(frameon=False, loc="lower left", fontsize=8)
plt.show()
```

Through 2020 more than 90% of the 2015 glacier area was bright every September. Since 2023 it has fallen each year I
can measure: 87% in 2023, 85% in 2025, 82% in 2026. In 2021 and 2024 smoke or cloud spoiled every late-summer image, so
those years are missing, and the 2015 and 2017 values come from hazy images. The drop is smaller than on
[Mount Hood](mount-hood.md), where about half the glacier area went dark after 2023, but it points the same way.

## Was 2026 any better?

No. The clearest image of late summer 2026, on 16 September, shows 33.9 km² of bright ice, a little less than in
September 2025. The ice was slightly brighter than in 2025, perhaps from a light dusting of snow, so if anything that
number is too high. By 3 October fresh snow covered the mountain, which ends the season for this method.

## What don't I understand?

- How much the glaciers have thinned. A glacier can lose much of its ice while keeping its outline. Repeat lidar of
  Baker would show it; I have not yet looked for it.
- How far to trust a single image a year. Leftover or early snow moves a single image by about 5% either way, which is
  why I compare several.
- Whether the rock-covered tongues are still ice. On Baker they are a small part of the total, but they are where the
  glaciers end.

## What did I get wrong?

If you know Baker's glaciers better than I do, I would like to hear from you. The code, data and a longer
[methods note](https://github.com/colliand/glacier-change/blob/main/methods/baker.md) are on GitHub, and
[issues](https://github.com/colliand/glacier-change/issues) are open.

## Sources

- Glacier outlines for 1974–75 and 2015: Portland State University, via GLIMS (NSIDC),
  [doi:10.15760/geology-data.03](https://doi.org/10.15760/geology-data.03), CC0.
- Images: Sentinel-2 (ESA Copernicus; contains modified Copernicus Sentinel data) and Landsat 8 and 9 (USGS), via
  Microsoft Planetary Computer.
- The glacier maps and 3D view: [whatcom.land](https://whatcom.land/glaciers).
