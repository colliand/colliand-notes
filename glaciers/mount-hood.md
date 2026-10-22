---
title: What is happening to Mount Hood's glaciers?
subtitle: Satellite images from 2013 to 2026, checked against maps made on the ground
date: 2026-10-21
thumbnail: img/share-hood-3d.jpg
description: Hood's glaciers lost another 17% of their area between 2015–16 and 2023. From space the loss looks twice as big, because much of the remaining ice is covered in rock and dirt.
tags: [Landsat, Mount Hood, Oregon]
kernelspec:
  name: python3
  display_name: Python 3
---

:::{note} Machine-drafted
Drafted with help from AI language models, working from my analysis code and its outputs in
[colliand/glacier-change](https://github.com/colliand/glacier-change). First results, not peer reviewed.
:::

On [whatcom.land](https://whatcom.land/glaciers) I mapped how Mount Baker's glaciers have changed since the 1970s. I
wondered whether the same approach would work on other mountains, so I tried it on Mount Hood in Oregon.

:::{tip} In short
- Between 1956 and 2015–16, Hood's named glaciers shrank by almost two thirds, from 15.6 to 5.8 km².
- They kept shrinking. A team that mapped them on the ground found they lost another 17% of their area by 2023.
- From space the recent loss looks twice as big. Since 2023 about a third less of the glacier area is bright, but much
  of the dark part is still ice, covered in rock and dirt.
:::

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
named = outlines[~outlines.name.isna()]
ogi = gpd.read_file(f"{SRC}/external/ogi_2023_margins.geojson")
series = pd.read_csv(f"{SRC}/landsat-series.csv")
usable = pd.read_csv(f"{SRC}/landsat-usable.csv", parse_dates=["date"])
field = pd.read_csv(f"{SRC}/ogi-2023-check.csv")

# whatcom.land's snow palette (maps/theme.js): ColorBrewer Purples, light to dark, and the teal of the newest outline
SNOW = ["#f2f0f7", "#cbc9e2", "#9e9ac8", "#756bb1", "#54278f", "#3f007d"]
TEAL, INK, MUTED, LINE = "#0e8a9e", "#1f2a24", "#5b6760", "#e2e0d8"
plt.rcParams.update({"figure.dpi": 130, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
                     "font.size": 9})
```

## What do the maps show?

Portland State University mapped Hood's glaciers twice: from 1956 maps, and from 2015–16 images. Their outlines are in
[GLIMS](https://www.glims.org), the global glacier inventory. In 2023 a team from the Oregon Glaciers Institute mapped
the glaciers again, walking much of the ice edge
([Bakken-French et al. 2024](https://doi.org/10.5194/tc-18-4517-2024)).

:::{iframe} https://notes.colliand.com/maps/hood-3d.html
:label: fig-hood-3d
:title: Mount Hood's glaciers in 3D
:width: 100%
:class: hood-map
:placeholder: img/hood-3d-north.jpg
:alt: Mount Hood in 3D from the north. Glaciers on the 1956 map in purple, 2015–16 in pale purple, and 2023 in white with a teal edge.
Mount Hood from the north. Purple: ice on the 1956 map. Pale purple: 2015–16. White, with a teal edge: 2023, mapped in
the field. The purple band is ice that is gone. Tap a glacier to see its numbers. Drag with two fingers to turn the
mountain.
:::

```{code-cell} python
:tags: [remove-input]
km2 = named.groupby("era").km2.sum()
print(f"Named glaciers, Portland State outlines (same method both times)\n"
      f"     1956  {km2['then']:4.1f} km²\n"
      f"  2015–16  {km2['now']:4.1f} km²   {100 * (km2['now'] / km2['then'] - 1):.0f}%\n\n"
      f"Field team's outlines (a different method: they include ice under rock)\n"
      f"     2023  {ogi.to_crs(32610).area.sum() / 1e6:4.1f} km²   -17% since 2015–16, by their own comparison")
```

Hood's named glaciers lost almost two thirds of their area between 1956 and 2015–16. Don't compare the 2023 total with
those two: it is not a sign that the shrinking stopped. The field team drew the edges differently and counted ice buried
under rock, which is hard to see on images. Comparing their own outlines over time, they found that Hood's glaciers lost
another 17% of their area from 2015–16 to 2023.

## What do satellites see each summer?

Landsat satellites photograph Hood every week or two. Clean snow and ice are bright in red light and dark in shortwave
infrared, so a simple ratio of the two finds them. For every clear image from late August through September, I
measured how much of the 2015–16 glacier area was bright.

```{code-cell} python
:tags: [remove-input]
fig, ax = plt.subplots(figsize=(6.4, 3.2))
ax.scatter(usable.date.dt.year + (usable.date.dt.dayofyear - 255) / 140, 100 * usable.bright_share,
           s=10, color=SNOW[2], label="one image", zorder=2)
ax.plot(series.year, 100 * series.bright_share, "o-", color=SNOW[4], lw=1.8, ms=5, label="middle value for the year", zorder=3)
ax.annotate("heat dome", (2021, 56), xytext=(0, -16), textcoords="offset points", ha="center", color=TEAL, fontsize=8)
ax.annotate("2023", (2023, 44), xytext=(0, -16), textcoords="offset points", ha="center", color=TEAL, fontsize=8)
ax.set_ylim(0, 100)
ax.set_ylabel("% of 2015–16 glacier area that is bright")
ax.set_xticks(range(2013, 2027), [str(y) if y in (2013, 2026) else f"’{y % 100:02d}" for y in range(2013, 2027)])
ax.grid(axis="y", color=LINE)
ax.legend(frameon=False, loc="lower left", fontsize=8)
plt.show()
```

From 2013 to 2020 about three quarters of the glacier area was bright each September. In 2021, the summer of the heat
dome, that fell to 56%, then came back the next year. In 2023 it fell to 44%, and it has not come back: it has been
between 50% and 62% since. (2014 is missing because clouds covered the mountain in every September image.)

## Is the ice gone, or just hidden?

The satellites say Hood lost about a third of its bright surface. The field team says Hood lost 17% of its area. Why
the difference?

I checked the satellite images against the field team's 2023 outlines. This is the share of *their* 2023 ice that
looks bright from space:

```{code-cell} python
:tags: [remove-input]
f = field.pivot(index="glacier", columns="date", values="bright_share")
f = f.loc[[*sorted(i for i in f.index if i != "All"), "All"]].rename(index={"All": "All glaciers"})
f.columns = [c[:4] for c in f.columns]
f.index.name = None
f.style.format("{:.0%}").background_gradient(cmap="Purples", vmin=0, vmax=1.4)
```

The outline is the same in every column; only the year of the image changes. In 2016 about 80% of the ice was bright.
Since 2023 it has been about half. On the west side it is much less: Sandy and Ladd glaciers have been mostly dark since 2023.

So much of the change since 2023 is ice going dark, not ice going away. My best guess is that the snow and old firn that
used to cover the lower glaciers melted off in 2023, uncovering ice mixed with rock and dirt. From space that looks like
bare ground.

If you measured Hood's glaciers by their bright ice alone, you would conclude they lost about a third of their area
since 2015–16. Counting the dark ice too, the field team found 17%. Bright ice alone doubles the loss.

## What don't I understand?

- How much of the dark ice is under a thin layer of dirt, and how much under thick rock? A thin layer makes ice melt
  faster; thick rock slows it down.
- Will the dark lower glaciers keep their area while they thin? Repeat lidar would show thinning, even under rock. I
  have not yet looked for repeat lidar of Hood.
- The same method gave a much better match on Mount Baker, where the glaciers carry less rock. How many Cascade
  glaciers look more like Hood than Baker?

## What did I get wrong?

If you know Hood's glaciers, or this kind of data, better than I do, I would like to hear from you. The code, data and
a longer [methods note](https://github.com/colliand/glacier-change/blob/main/methods/hood.md) are on GitHub, and
[issues](https://github.com/colliand/glacier-change/issues) are open.

## Sources

- Glacier outlines for 1956 and 2015–16: Portland State University, via GLIMS (NSIDC).
- Glacier outlines for 2023: Oregon Glaciers Institute,
  [doi:10.5281/zenodo.13356244](https://doi.org/10.5281/zenodo.13356244), CC BY 4.0. The study: Bakken-French et al.
  (2024), *Unprecedented 21st century glacier loss on Mt. Hood, Oregon, USA*, The Cryosphere 18, 4517–4530.
- Images: Landsat 8 and 9 (USGS) and Sentinel-2 (ESA Copernicus), via Microsoft Planetary Computer.
- 3D terrain: AWS Terrain Tiles (Mapzen), from USGS 3DEP. Map colours and 3D view: the same as
  [whatcom.land](https://whatcom.land/glaciers).
