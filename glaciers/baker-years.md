---
title: Mount Baker, 42 summers
subtitle: One Landsat image a late summer since 1984, played in your browser
date: 2026-10-24
thumbnail: img/baker-years.jpg
description: A playable film of Mount Baker's bright ice from 1984 to 2026, computed on your graphics card from Landsat. Inside the 2015 glacier outlines the ice held near 40 km² for thirty years; since 2021 every summer has been under 35.
tags: [Landsat, deck.gl-raster, Mount Baker, whatcom.land]
kernelspec:
  name: python3
  display_name: Python 3
---

:::{note} Machine-drafted
Drafted with help from AI language models, working from my code and its outputs. A quick experiment, not peer
reviewed.
:::

My [first try with deck.gl-raster](baker-bright-ice.md) compared a few Sentinel-2 dates. A before and after is not where
the library shines. A time series is. Landsat has looked at Mount Baker since 1984, so here is one image for every late
summer, 42 in all, with the same ice test run live on each.

Press play, or drag along the strip of years. The threshold slider works while it plays.

:::{iframe} /maps/baker-years.html
:label: fig-baker-years
:title: Mount Baker, 42 summers
:width: 100%
:class: live-map
White: pixels where red / shortwave infrared is above the threshold. Purple lines: the glaciers as Portland State
mapped them in 2015. One clear late-summer Landsat image a year; none for 2012, when no working Landsat was flying.
:::

## How the images were chosen

The pictures are the ones in the [summer by summer flipbook](https://whatcom.land/glaciers#flipbook) on whatcom.land.
For each year, from every Landsat scene between 1 August and 20 October, it keeps the clear one with the least bright
snow: the end of the melt season, when the glacier edges are least hidden. In seven years no scene was clear, and a
partly cloudy one stands in. The 1995 scene sat 3.5 km off and was shifted back; every frame lines up with the others
to the pixel.

## What I noticed

```{code-cell} python
:tags: [remove-cell]
import matplotlib.pyplot as plt
import pandas as pd

# scripts/baker_years_area.py: the map's own test on its own images, counted on the 30 m Landsat pixels
d = pd.read_csv("data/baker-years-area.csv")
SNOW = ["#f2f0f7", "#cbc9e2", "#9e9ac8", "#756bb1", "#54278f", "#3f007d"]
INK, MUTED, LINE = "#1f2a24", "#5b6760", "#e2e0d8"
plt.rcParams.update({"figure.dpi": 130, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
                     "font.size": 9})
```

```{code-cell} python
:tags: [remove-input]
fig, ax = plt.subplots(figsize=(6.4, 3.2))
ax.fill_between(d.year, d["glaciers_t2.5_km2"], d["glaciers_t1.5_km2"], color=SNOW[1], lw=0, label="threshold 1.5 to 2.5")
clear, cloudy = d[~d.partly_cloudy], d[d.partly_cloudy]
ax.plot(d.year, d["glaciers_t2.0_km2"], color=SNOW[4], lw=1.2, zorder=2)
ax.scatter(clear.year, clear["glaciers_t2.0_km2"], s=14, color=SNOW[4], zorder=3, label="threshold 2")
ax.scatter(cloudy.year, cloudy["glaciers_t2.0_km2"], s=14, facecolor="white", edgecolor=SNOW[4], zorder=3,
           label="partly cloudy image")
ax.axhline(40.2, color=MUTED, lw=0.8, ls="--")
ax.text(1984, 40.4, "all of the 2015 outlines, 40.2 km²", fontsize=8, color=MUTED, va="bottom")
ax.set_ylim(30, 42)
ax.set_ylabel("bright ice inside the\n2015 outlines, km²")
ax.grid(axis="y", color=LINE)
ax.legend(frameon=False, loc="lower left", fontsize=8)
plt.show()
```

```{code-cell} python
:tags: [remove-input]
early, late = d[d.year <= 2014], d[d.year >= 2021]
print(f"1984–2014  {early['glaciers_t2.0_km2'].min():.1f} to {early['glaciers_t2.0_km2'].max():.1f} km²\n"
      f"2021–2026  {late['glaciers_t2.0_km2'].min():.1f} to {late['glaciers_t2.0_km2'].max():.1f} km²")
```

- For thirty years nearly all of the 2015 glacier area was bright every late summer. Since 2021 every summer
  has been under 35 km², and none has come back. The threshold barely matters; the shaded band is narrow.
- 2015 is the first real dip, and the summers after it bounced back only part of the way. 2021, the summer of the heat
  dome, is the step down, and it held.
- Before 2015 the glaciers reached past their 2015 outlines, so this chart cannot show how much they shrank in those
  years. It only says that the 2015 area was still full of bright ice. Play the film to see the edges move.
- A big winter, or early snow, makes a year look icier than it was. 1999 came after the record snowfall winter at the
  Mt. Baker Ski Area, and 2011's only clear image is from 18 October; in both the white spills far past the glaciers.

The level is not the point. On Landsat's 30 m pixels the test finds 36.9 km² on 4 October 2015, 8% less than Portland
State's outlines; on Sentinel-2's finer pixels the same test agreed to within 1% (see the
[Mount Baker note](mount-baker.md)). The 30 m test misses the thin edges, so read the change, not the total.

## What did not work

Streaming the full Landsat scenes from Microsoft's Planetary Computer cost about 3 MB a summer and, on a slow day,
minutes for all 42. Too slow to play. So I cut red and shortwave infrared for a 16 km square around the summit into small
files and put them on Cloudflare, about half a megabyte a summer.

The first version stored 16-bit numbers and worked on every computer I tried, but not on my iPhone: "The images did
not load." Storing 8-bit numbers fixed it. I do not know why; the Sentinel-2 page uses 16-bit and works on the same
phone. Holding all 42 summers on the graphics card at once may be too much for a phone at 16 bits. To keep 8 bits
honest, each number is the square root of the reflectance, which keeps detail in the dark shortwave infrared where ice
is decided. The ice area moves by at most 0.5% against the 16-bit files in any year.

## Sources

- Images: USGS Landsat 5, 7, 8 and 9, Collection 2 Level-2 surface reflectance, public domain, via
  [Microsoft Planetary Computer](https://planetarycomputer.microsoft.com/dataset/landsat-c2-l2). Landsat 7 after its
  2003 scan-line failure is left out.
- 2015 outlines: Portland State University, via GLIMS (NSIDC),
  [doi:10.15760/geology-data.03](https://doi.org/10.15760/geology-data.03), CC0.
- Scene choice: the whatcom.land flipbook, [Glaciers › Mount Baker, summer by summer](https://whatcom.land/glaciers#flipbook).
- Code: `maps/baker-years.html`, `maps-src/baker-s2/years.js` and `scripts/baker_years_*.py` in
  [colliand/colliand-notes](https://github.com/colliand/colliand-notes).
