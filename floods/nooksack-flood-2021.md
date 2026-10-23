---
title: How much of Whatcom was under water on 16 November 2021?
subtitle: Mapping a flood from radar, through the clouds
date: 2026-10-23
thumbnail: img/share-nooksack-2021.jpg
description: Radar from Sentinel-1 caught the Nooksack flood at 6:20 am on 16 November 2021. Comparing that pass with six from before the flood finds about 8,600 acres of open water, nine-tenths of it inside FEMA's mapped flood zones.
tags: [Sentinel-1, radar, floods, Nooksack, whatcom.land]
draft: true
kernelspec:
  name: python3
  display_name: Python 3
---

:::{note} Machine-drafted
Drafted with help from AI language models, working from my analysis code and its outputs in
[colliand/flood-extent](https://github.com/colliand/flood-extent). First results, not peer reviewed.
:::

In mid-November 2021 an atmospheric river dropped days of heavy rain on the North Cascades. The Nooksack River broke
out near Everson, ran north through Sumas and across the border into British Columbia's Sumas Prairie, and rose to a
record height at Ferndale. The [Floods tab on whatcom.land](https://whatcom.land/floods) shows my estimate of the open
water that morning. This note explains how I made it and how far to trust it.

:::{tip} In short
- One radar pass came near the peak: Sentinel-1B, 6:20 am on 16 November 2021.
- Comparing it with six passes from before the flood finds about **8,600 acres** of open floodwater in Whatcom County
  (6,500 to 10,200, depending on how dark counts as water).
- 91% of that water lies inside FEMA's mapped flood zones. Radar cannot see water among buildings or under trees, so
  towns are undercounted.
:::

```{code-cell} python
:tags: [remove-cell]
import json
import os
import urllib.request

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

# Outputs of colliand/flood-extent, pinned to the commit that made them.
SRC = os.environ.get("FLOOD_EXTENT",
                     "https://raw.githubusercontent.com/colliand/flood-extent/b0624b0") + "/data/nooksack-2021-11"


def load(name):
    if SRC.startswith("http"):
        return json.load(urllib.request.urlopen(f"{SRC}/{name}"))
    return json.load(open(f"{SRC}/{name}"))


summary, check = load("summary.json"), load("check.json")
estimate = gpd.read_file(f"{SRC}/estimate.geojson")
zones = gpd.read_file(f"{SRC}/fema_zones.geojson")

# whatcom.land's flood palette (maps/theme.js): ColorBrewer Blues
BLUE = {"floodway": "#08306b", "high": "#2171b5", "coastal": "#4a6fa5", "moderate": "#9ecae1"}
INK, MUTED, LINE, PALE = "#1f2a24", "#5b6760", "#e2e0d8", "#c6dbef"
plt.rcParams.update({"figure.dpi": 130, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
                     "font.size": 9})
```

## Why radar?

The storm came with cloud, and cloud hides the ground from ordinary satellite cameras for days. Radar sends its own
pulse of microwaves and sees through cloud, day or night.

Calm open water acts like a mirror. It bounces the pulse away from the satellite, so water looks **dark** in a radar
image. Fields, forest and buildings scatter some of the pulse back and look grey or bright. A field that was grey on
every pass before the flood and is black on the flood pass has most likely gone under water.

Sentinel-1 passes over the same spot from the same angle every 12 days. The pass at 6:20 am on 16 November came the
morning after the river peaked at Everson, while it was near its peak downstream at Ferndale.

## What did the radar see?

Here is the area from Everson to Sumas, about 13 km across, north at the top. The Nooksack comes in at the bottom
and turns west at Everson, in the lower middle. Sumas is the bright town at the top right, on the border, and the
rough ground on the right is the foot of Sumas Mountain. First, "normal": the middle value of six passes from 5
September to 4 November 2021.

:::{figure} img/radar-normal.jpg
:label: fig-normal
:alt: Radar image of farmland between Everson and Sumas before the flood: grey fields, a dark river line.
Normal: the middle of six passes before the flood. Darker means less of the pulse came back. Grey scale from −25 dB
(black) to 0 dB (white).
:::

:::{figure} img/radar-flood.jpg
:label: fig-flood
:alt: The same area on 16 November 2021: large black areas where fields had been grey, running north from Everson to Sumas.
16 November 2021, 6:20 am. The black sheets are open floodwater.
:::

The dark band running north-east from Everson toward Sumas is the overflow: the path the Nooksack takes into the
Fraser basin when it tops its banks. The river channel itself is wider, and fields west of Everson are under water too.
The ponds at the bottom left were dark before the flood as well, so they do not count.

## From dark pixels to floodwater

Dark is not enough. Lakes and bays are always dark; so are hillsides facing away from the satellite, which sit in radar
shadow; and radar images are grainy ("speckle"), which makes scattered dark pixels everywhere. Each test below removes
one of these. The acres are what is left after each step:

```{code-cell} python
:tags: [remove-input]
steps = pd.Series(summary["steps_acres"], name="acres left").map("{:,.0f}".format)
steps.index.name = None
steps.to_frame()
```

- **Darker than normal.** At least 3 dB darker than the six-pass normal: the place changed.
- **Not permanent water.** Dark on any of the six earlier passes (a calm lake on a calm day), or water at least half the
  time since 1984 in the European Commission's Global Surface Water record. My first try let lakes and bays
  through; this fixed it.
- **Near a stream.** Less than 10 m above the nearest stream (height above nearest drainage, from a global elevation
  model). This removes the hillside shadows.
- **Big enough.** Patches of half a hectare (about 1.2 acres) or more. Smaller ones are mostly speckle.

:::{figure} img/radar-estimate.jpg
:label: fig-estimate
:alt: The 16 November radar image with the estimated floodwater in teal.
What is left, in teal, on the 16 November image.
:::

## How much water, and where?

```{code-cell} python
:tags: [remove-input]
lo, hi = summary["acres_range"]
print(f"Open floodwater, 16 Nov 2021, 06:20 PST\n"
      f"  {summary['acres']:,.0f} acres ({summary['km2']} km²)\n"
      f"  range {lo:,.0f} to {hi:,.0f} acres")
```

```{code-cell} python
:tags: [remove-input]
fig, ax = plt.subplots(figsize=(6.4, 4.4))
zones.plot(ax=ax, color=PALE, linewidth=0)
estimate.plot(ax=ax, color=BLUE["floodway"], linewidth=0)
ax.set_xlim(-122.72, -122.17)
ax.set_ylim(48.76, 49.015)
ax.set_aspect(1 / 0.657)  # cos(48.9°): metres the same both ways
ax.set_axis_off()
OFFSET = {"Everson": (-6, -10, "right"), "Nooksack": (5, -2, "left"), "Sumas": (-5, -9, "right"),
          "Lynden": (-5, 4, "right"), "Ferndale": (-5, 0, "right")}
for name, (lon, lat) in check["towns"].items():
    dx, dy, ha = OFFSET.get(name, (4, 4, "left"))
    ax.plot(lon, lat, "o", ms=3, color=INK)
    ax.annotate(name, (lon, lat), xytext=(dx, dy), textcoords="offset points", ha=ha, fontsize=8, color=INK)
ax.set_title("Open floodwater on 16 Nov 2021 (dark blue)\nover FEMA's mapped flood zones (pale)",
             fontsize=9, color=INK, loc="left")
plt.show()
```

Most of the water lay along the Nooksack between Lynden and Ferndale. The Everson–Sumas overflow in the radar
images above is the scattered patches at the top right.

The range comes from making the darkness test stricter (−19 dB) or looser (−17 dB). The other choices matter less.
Moving each one a step on its own:

```{code-cell} python
:tags: [remove-input]
names = {"water_db": ("how dark counts as water", "dB"), "change_db": ("how much darker than normal", "dB"),
         "hand_max_m": ("how far above a stream", "m"), "min_patch_px": ("smallest patch", "px")}
used = {"water_db": -18, "change_db": -3, "hand_max_m": 10, "min_patch_px": 50}
lines = [f"Acres, one setting moved at a time\n(all at their usual values: {summary['acres']:,.0f})"]
for k, v in summary["sensitivity_acres"].items():
    label, unit = names[k]
    lines.append(f"\n{label} (used {used[k]} {unit})")
    lines.append("   " + "   ".join(f"{float(x):g} {unit} → {a:,.0f}" for x, a in v.items()))
print("\n".join(lines))
```

## Is it believable?

No official map of the flooded area was published, and the high-water marks that would be the natural check were not
collected for this flood (the USGS flood event database has none). So I asked a weaker question: does the water fall
where floods are expected?

```{code-cell} python
:tags: [remove-input]
z = check["share_in_fema_zones_pct"]
print(f"Share of the estimate inside FEMA's flood zones\n"
      f"  floodway        {z.get('floodway', 0):5.1f}%\n"
      f"  high risk (1%)  {z.get('high', 0):5.1f}%\n"
      f"  moderate (0.2%) {z.get('moderate', 0):5.1f}%\n"
      f"  any zone        {check['share_in_any_studied_zone_pct']:5.1f}%")
```

Nine-tenths of the water lies where FEMA's maps say floods happen. That says the method is finding floodwater, not
shadows or lakes. It does not say how much it missed.

It misses towns. Within 2 km of each town centre, the share called open water:

```{code-cell} python
:tags: [remove-input]
t = pd.Series(check["open_water_within_2km_of_town_pct"]).map("{:.0f}%".format)
t.index.name = None
t.to_frame("open water")
```

Everson and Sumas were badly flooded, yet only a few percent of the land around them shows as water. Some of that is
real: by 6:20 am the water had begun to drain from Everson. Most of it is the method: among buildings, the radar pulse
bounces between walls and the water's surface and comes back bright, not dark. Water under trees is hidden the same way.
So read the estimate as **open water in fields and on the floodplain**, a lower bound on the flood.

## What don't I know?

- How much water was in the towns. Radar from a different angle, or the double bounce off flooded buildings, might show
  it; I have not tried.
- How the flood moved. Sentinel-1 passed again on 20 November, as the water drained, and a second storm flooded the
  valley on 28 November. Both are worth a look.
- How deep it was. This is extent only.

## What did I get wrong?

If you were there, or know this floodplain, I would like to hear what this misses. The code and outputs are on
[GitHub](https://github.com/colliand/flood-extent), with a longer
[methods note](https://github.com/colliand/flood-extent/blob/main/methods/nooksack-2021-11.md), and
[issues](https://github.com/colliand/flood-extent/issues) are open. This is not FEMA's or the county's map, and it is not
for decisions about a property.

## Sources

- Radar: Sentinel-1 radiometric terrain corrected backscatter (contains modified Copernicus Sentinel data, 2021;
  terrain correction by Catalyst), via Microsoft Planetary Computer, CC BY 4.0.
- Height above nearest drainage: ASF GLO-30 HAND, from the Copernicus DEM GLO-30.
- Permanent water: Pekel, J.-F. et al. (2016), Global Surface Water, EC Joint Research Centre.
- Flood zones: FEMA National Flood Hazard Layer (effective). County boundary: US Census TIGERweb.
- The flood map, gauges and flood history: [whatcom.land](https://whatcom.land/floods).
