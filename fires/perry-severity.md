---
title: How badly did the Perry fire burn?
subtitle: Four satellite maps of one fire in the North Cascades, and what they teach my own method
date: 2026-10-22
thumbnail: img/share-perry.jpg
description: Two official maps of the 2025 Perry fire, made from the same two satellite images, disagree on how much burned at high severity, 7% or 16%. My own estimate sits between them, and moves closer to the field-calibrated map when I tune it.
tags: [Sentinel-2, burn severity, North Cascades, whatcom.land]
kernelspec:
  name: python3
  display_name: Python 3
---

:::{note} Machine-drafted
Drafted with help from AI language models, working from my analysis code and its outputs in
[colliand/burn-severity](https://github.com/colliand/burn-severity). An exploration, not peer reviewed.
:::

The Perry fire started on 28 August 2025 in North Cascades National Park, in the east of Whatcom County, and burned
about 1,800 acres. On [whatcom.land](https://whatcom.land/fires) I show how badly recent fires burned, from my own
reading of satellite images, until the official maps arrive a year or two later. I wanted to know how my estimate
compares with the official maps, and whether putting them side by side could make my method better.

:::{tip} In short
- Two official maps of Perry, made from the **same two satellite images**, disagree: 7% or 16% of the fire burned at
  high severity. The difference is method and judgement, not data.
- My estimate, made independently from more images, agrees with the Forest Service map about as well as the USGS map
  does.
- Tuning where my method draws its lines brings it closer to the Forest Service map, which is calibrated against field
  measurements, and the gain holds on part of the fire the tuning never saw.
:::

```{code-cell} python
:tags: [remove-cell]
import json
import os
import urllib.request
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio
from rasterio import features

# Outputs of colliand/burn-severity, pinned to the commit that made them.
REPO = os.environ.get("BURN_SEVERITY", "https://raw.githubusercontent.com/colliand/burn-severity/868c466")
SRC, CHECK = f"{REPO}/data/perry-2025", f"{REPO}/methods/perry-photo-check"
getjson = lambda url: json.load(urllib.request.urlopen(url))
compare = pd.read_csv(f"{SRC}/compare.csv")
agree = getjson(f"{SRC}/agreement.json")
calib = getjson(f"{SRC}/calibration.json")
perimeter = gpd.read_file(f"{SRC}/perimeter.geojson")

def read(name):
    with rasterio.open(f"{SRC}/{name}.tif") as s:
        return s.read(1), s.transform, s.crs

# whatcom.land's fire severity colours (site/common.js THEME.fire.severity), with a pale grey for unburned to low
CLASSES = ["unburned to low", "low", "moderate", "high"]
COLORS = ["#e4e1d8", "#fcae91", "#fb6a4a", "#a50f15"]
INK, MUTED = "#1f2a24", "#5b6760"
plt.rcParams.update({"figure.dpi": 130, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
                     "font.size": 9})
LABEL = {"ravg-cbi4": "Forest Service (RAVG)", "baer-barc4": "USGS for the BAER team",
         "baer-keybenson": "USGS image, textbook lines", "ours-initial": "Mine, weeks after",
         "ours-extended": "Mine, a year after"}
```

## What is burn severity?

Satellites see fire through a ratio of two colours of light. Healthy plants reflect a lot of near-infrared light and
little shortwave infrared; burned ground does the opposite. Compare the ratio before and after a fire, and the size of
the change says how much the vegetation changed. That change is sorted into classes: unburned to low, low, moderate,
high. Every map below does some version of this. They differ in which images they use, how long after the fire, and
where they draw the lines between classes.

## Who made which map?

- The **USGS** made a map for the National Park Service's burned area emergency response team (BAER) three weeks after
  the fire, from one Sentinel-2 image before (24 August) and one after (18 September). An analyst chose the class lines.
- The **Forest Service** program RAVG made a map from the same two images. It uses a variant of the ratio that adjusts
  for how much vegetation was there before, and class lines calibrated against field measurements on other fires.
- I classed the USGS's own before-after change with the textbook lines (Key and Benson, 2006).
- I made two maps of my own, from the median of many Sentinel-2 images rather than one pair: one from the weeks after
  the fire, and one from the summer a year later, after the trees that would die had died.

```{code-cell} python
:tags: [remove-input]
names = ["ravg-cbi4", "baer-barc4", "ours-initial", "ours-extended"]
fig, axes = plt.subplots(2, 2, figsize=(8, 7))
for ax, n in zip(axes.flat, names):
    a, t, crs = read(n)
    h, w = a.shape
    inside = features.rasterize([(g, 1) for g in perimeter.to_crs(crs).geometry], out_shape=a.shape, transform=t)
    a = np.where(inside == 1, a, 0)  # inside the fire's perimeter only
    extent = (t.c, t.c + w * t.a, t.f + h * t.e, t.f)
    rgba = np.zeros((h, w, 4))
    for k, c in enumerate(COLORS, 1):
        rgba[a == k] = [*(int(c[i:i + 2], 16) / 255 for i in (1, 3, 5)), 1]
    ax.imshow(rgba, extent=extent, interpolation="nearest")
    per = perimeter.to_crs(crs)
    per.boundary.plot(ax=ax, color=INK, lw=0.6)
    x0, y0, x1, y1 = per.total_bounds
    ax.set_xlim(x0 - 150, x1 + 150); ax.set_ylim(y0 - 150, y1 + 150)
    ax.set_title(LABEL[n], fontsize=10, color=INK)
    ax.set_axis_off()
handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in COLORS]
fig.legend(handles, CLASSES, loc="lower center", ncol=4, frameon=False)
fig.tight_layout(rect=(0, 0.05, 1, 1))
plt.show()
```

Four maps of the Perry fire, inside the fire's perimeter. They agree on where it burned, and roughly on the hot core in
the middle. They differ at the edges between classes.

## How much burned at high severity?

```{code-cell} python
:tags: [remove-input]
order = ["ravg-cbi4", "baer-barc4", "baer-keybenson", "ours-initial", "ours-extended"]
c = compare.set_index("map").loc[order, CLASSES]
fig, ax = plt.subplots(figsize=(8, 2.9))
left = np.zeros(len(c))
for cls, col in zip(CLASSES, COLORS):
    ax.barh([LABEL[n] for n in order], c[cls], left=left, color=col, edgecolor="white", lw=0.5, label=cls)
    left += c[cls].to_numpy()
for i, n in enumerate(order):
    ax.text(101, i, f"{c.loc[n, 'high']:.0f}% high", va="center", fontsize=8, color=INK)
ax.invert_yaxis(); ax.set_xlim(0, 115); ax.set_xticks([0, 25, 50, 75, 100])
ax.set_xlabel("share of the fire (%)")
ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.45, -0.28), frameon=False)
plt.show()
```

The two official maps start from the same two images, yet the Forest Service calls 16% of the fire high severity and
the USGS map 7%. Using the textbook lines on the USGS image gives 8%. So most of the difference between the official
maps comes from how they turn the change into classes, not from the images.

My map from the weeks after the fire says 14% high. My map from a year later says 12% high, but much more moderate:
ground I called low in the autumn reads moderate a year later. That is what you expect as scorched trees die over the
following year, and why the official long-term maps (MTBS) wait a year.

## Do the maps agree spot by spot?

I put every map on the same 20 m grid and counted how often each puts a spot in the same class as the Forest Service
map, the one calibrated against measurements on the ground.

```{code-cell} python
:tags: [remove-input]
t = pd.DataFrame({LABEL[k]: {"same class": v["exact_pct"] / 100, "within one class": v["within_one_pct"] / 100}
                  for k, v in agree["maps"].items()}).T
t.loc[["USGS for the BAER team", "Mine, weeks after", "Mine, a year after"]].style.format(
    {"same class": "{:.0%}", "within one class": "{:.1%}"})
```

My map from the weeks after the fire agrees with the Forest Service map as well as the USGS map does, almost always
within one class. My map from a year later agrees less, as it should: it measures a later moment.

## What do the images show?

No aerial photos of the fire have been published since it burned (the latest for Washington are from 2023), so the
sharpest look is the satellite's own natural-colour image, at 10 m. I picked 30 spots, each 60 m across: where the maps
disagree, and where they all agree, as a check. Each spot was rated green, mixed or dead from the images before and
after, without knowing which group it came from. The rater was an AI model, not me; a second rater, or a walk through
the burn, would make this stronger.

```{code-cell} python
:tags: [remove-input]
key = getjson(f"{CHECK}/key.json")["spots"]
ratings = getjson(f"{CHECK}/ratings.json")
groups = {"D": "All three maps say high", "E": "All three maps say low", "B": "USGS moderate, Forest Service high",
          "A": "USGS low, Forest Service moderate", "C": "Mine moderate, Forest Service low"}
rows = {g: {"green": 0, "mixed": 0, "dead": 0, "can't tell": 0} for g in groups.values()}
for sp in key:
    rows[groups[sp["stratum"]]][{"G": "green", "P": "mixed", "D": "dead", "U": "can't tell"}[ratings[str(sp["n"])]]] += 1
pd.DataFrame(rows).T
```

Where all three maps say high, all six spots look dead. Where they all say low, the spots mostly look mixed: from space,
low severity often still looks brown, from scorched needles and late-summer drying. So this look cannot tell low from
moderate.

It can judge the line between moderate and high. Where the USGS map says moderate and the Forest Service says high, five
of six spots look like the spots every map calls high. On that line, the field-calibrated map looks right.

:::{figure} https://raw.githubusercontent.com/colliand/burn-severity/868c466/methods/perry-photo-check/sheet_01.jpg
:alt: Five spots in the Perry fire, each shown before, three weeks after and a year after the fire, in natural colour.
One page of the image check. Each row is a spot (the yellow square, 60 m across), before the fire, three weeks after,
and a year after (often cloudy). Contains modified Copernicus Sentinel data (2025, 2026).
:::

## Can my method learn from the Forest Service map?

My map uses the textbook lines between classes. If the Forest Service map is the best reference, which lines on my
measurements would reproduce it best? I searched for the three lines that give the most spots in the same class. To
check that this does not just memorise one fire, I also found the best lines using only the west half of the fire, and
tested them on the east half.

```{code-cell} python
:tags: [remove-input]
r = calib["runs"]
pd.DataFrame({
    "textbook lines": [r[k]["textbook_agreement"] for k in ("initial", "extended")],
    "tuned lines": [r[k]["fitted_agreement"] for k in ("initial", "extended")],
    "east half, textbook": [r[k]["holdout"]["east_agreement_textbook"] for k in ("initial", "extended")],
    "east half, tuned on west": [r[k]["holdout"]["east_agreement"] for k in ("initial", "extended")],
}, index=["Mine, weeks after", "Mine, a year after"]).style.format("{:.0%}")
```

Tuning raises my weeks-after map's agreement with the Forest Service from 72% to 80%. On the half of the fire the tuning
never saw, it still rises, from 70% to 75%. The main change is to raise the line between low and moderate: my medians
read a little hotter than the Forest Service in the low range. For the year-after map the gain is larger, as expected,
because the textbook lines were never meant for a map made a year later.

One fire is not enough to change what whatcom.land shows. The next step is to repeat this on many fires that have
Forest Service or MTBS maps, and see whether one set of lines works across them, and how sure we can be.

## What I take from this

Burn severity is a measurement with a date and a set of judgement calls. Two careful official maps of the same fire,
from the same images, differ by a factor of two in how much burned hard. That does not make them wrong. It means a
single number for "how badly it burned" should come with its method and its date.

For whatcom.land this is encouraging: my estimate sits among the official maps, not outside them, and laying the maps
side by side shows how to improve it.

Open questions I would like help with:
- Which map is closer to what is on the ground at Perry? The Forest Service lines are calibrated on field plots, but
  not in the North Cascades. A walk through the burn would help.
- Do tuned lines from fires elsewhere in the Cascades carry over to fires here?
- When MTBS maps Perry, does it side with my one-year-later map?

If you know burn severity mapping, or the Perry burn, better than I do, I would like to hear from you. The code, data
and a longer [methods note](https://github.com/colliand/burn-severity/blob/main/methods/perry-2025.md) are on GitHub,
and [issues](https://github.com/colliand/burn-severity/issues) are open.

## Sources

- Fire perimeter: NIFC Wildland Fire Interagency Geospatial Services (WFIGS), public domain.
- Official severity maps: USGS EROS (BAER imagery support) and USDA Forest Service RAVG, from the
  [Burn Severity Portal](https://burnseverity.cr.usgs.gov), public domain.
- Images: Sentinel-2 (ESA Copernicus), via Microsoft Planetary Computer. Contains modified Copernicus Sentinel data
  (2024–2026).
- Class lines: Key, C. H. and Benson, N. C. (2006), Landscape Assessment, in FIREMON, USDA Forest Service RMRS-GTR-164-CD.
- Colours: the same as on [whatcom.land](https://whatcom.land/fires).
