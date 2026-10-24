---
title: Mount Baker's bright ice, computed in your browser
subtitle: An experiment with deck.gl-raster and Sentinel-2
date: 2026-10-22
description: The band-ratio test behind whatcom.land's glacier estimate, run live on Sentinel-2 images streamed from the public archive. Drag the threshold and switch years.
tags: [Sentinel-2, deck.gl-raster, Mount Baker, cloud-native]
thumbnail: img/baker-s2.jpg
---

:::{note} Machine-drafted
Drafted with help from AI language models. A quick experiment, not peer reviewed.
:::

At the Cloud-Native Geospatial Forum this month, Kyle Barron of Development Seed showed
[deck.gl-raster](https://github.com/developmentseed/deck.gl-raster): satellite images read straight from cloud storage
into the browser and coloured on the graphics card, with no tile server in between. I wanted to try it on something I
know, so I gave it the test I use for glaciers on [whatcom.land](https://whatcom.land/glaciers).

The test is simple. Ice and snow are bright in red light and dark in shortwave infrared; rock is not. Where red divided
by shortwave infrared is above 2, call it ice. Here the graphics card does that division for every pixel, so you can
drag the threshold and watch the answer change.

:::{iframe} /maps/baker-s2.html
:label: fig-baker-s2
:title: Mount Baker bright ice, live
:width: 100%
:class: live-map
White: pixels where red / shortwave infrared is above the threshold, on the chosen date. Purple lines: the glaciers as
Portland State mapped them in 2015. Images: Sentinel-2, read from the public archive on AWS as you look.
:::

## What I noticed

- At a threshold of 2, the white matches the 2015 outlines on the upper mountain, and pulls back from them at the
  low snouts. That is where whatcom.land found most of the loss.
- Anywhere from 1.3 to 3.5, the white barely moves; only its edges shift by a pixel or two. Lost ice is not a close
  call. When I measured it for whatcom.land, pixels that were ice in 2015 and are not now had a median ratio of 8.6 in
  2015 and 1.2 in 2025: rock, nowhere near the threshold.

## What did not work

The 2015 image, the baseline, is not here. The only public copy that a browser can read is on Microsoft's Planetary
Computer, which stores Sentinel-2 bands as 15-bit numbers. deck.gl-raster reads 16-bit, so for now 2015 shows only as
the outlines.

The first version was slow: each view streamed about 22 MB and took half a minute on my connection. Two fixes brought
it to about 7 MB. The page now fetches only the two bands the test uses, red and shortwave infrared, so the background
is the red band in grey rather than natural colour. And deck.gl-raster 0.8.1 fetched each shortwave-infrared block
up to four times over: where two bands share a grid, a tile's edge lands exactly on the next block's edge, and the
library counted that block too. The patch is one line
([maps-src/baker-s2/patch-tile-range.mjs](https://github.com/colliand/colliand-notes/blob/main/maps-src/baker-s2/patch-tile-range.mjs)).
After the first year, the others load in the background and switching is instant.

## Sources

- Images: Copernicus Sentinel-2 Level-2A, Collection 1, via [Element 84 on AWS](https://registry.opendata.aws/sentinel-2-l2a-cogs/).
- 2015 outlines: Portland State University, via [GLIMS](https://www.glims.org).
- The method and its checks against Portland State and the USGS: [whatcom.land, Glaciers](https://whatcom.land/glaciers).
- Code: `maps/baker-s2.html` and `maps-src/baker-s2/` in [colliand/colliand-notes](https://github.com/colliand/colliand-notes).
