---
title: Wildlife by month in Whatcom County
subtitle: How the data behind whatcom.land's Wildlife page was put together, from sightings, bird checklists and a salmon calendar
date: 2026-11-17
thumbnail: img/share-wildlife.png
description: Building a month-by-month view of Whatcom County's wildlife from eBird, iNaturalist and the salmon co-managers' run-timing table. Sightings follow people, so each animal is measured as a share of all reports that month. Eagles turn up with the chum, not with the summer salmon.
tags: [wildlife, salmon, eBird, iNaturalist, Nooksack, whatcom.land]
draft: true
kernelspec:
  name: python3
  display_name: Python 3
---

:::{note} Machine-drafted
Drafted with help from AI language models, working from my exploration notebook and the data script
`scripts/wildlife_data.py` in this site's repo. A dated snapshot (17 November 2026), not peer reviewed.
:::

A friend told me he saw a river otter in the Nooksack. This autumn I saw a pine grosbeak and a harlequin duck, and
logged the grosbeak as my first eBird record. I wanted to know which animals are around in which months, and whether
the public records could show it fairly. This note is how the data for the
[Wildlife page on whatcom.land](https://whatcom.land/wildlife) was put together.

:::{tip} In short
- Sightings follow people. More people are outdoors in summer, so raw counts rise in summer for almost everything.
  Dividing by all reports that month fixes most of that.
- For birds, eBird's share of checklists and iNaturalist's share of sightings agree on the shape of the year
  (a correlation of about 0.8 to 0.9 for the well-reported birds), two independent sources.
- Bald eagles are on about a third of all birding checklists in the county from November to March and 4% in
  September. They are scarce in late summer, when Chinook, pink and sockeye spawn, and arrive with the chum.
:::

```{code-cell} python
:tags: [remove-cell]
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Written by scripts/wildlife_data.py from whatcom.land's Wildlife summary (eBird shares), iNaturalist and WDFW
m = pd.read_csv("data/monthly.csv")
runs = pd.read_csv("data/salmon-timing.csv", dtype=str).fillna("")
chum = pd.read_csv("data/chum-spawners.csv")
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# whatcom.land colours (site/theme.js THEME)
INK, MUTED, LINE = "#1f2a24", "#5b6760", "#c9c5b9"
LEVEL = ["#f3f1e8", "#d3e4d6", "#98c4a5", "#559c78", "#1d5e44"]
FISH = {"chinook": "#1b5f7a", "coho": "#d27a1f", "chum": "#5b8a2a", "pink": "#d0628e", "sockeye": "#c22f2a",
        "steelhead": "#6c79b0"}
NOW = "#b8862b"
plt.rcParams.update({"figure.dpi": 130, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
                     "font.size": 9})
from matplotlib.colors import LinearSegmentedColormap
LEVEL_CMAP = LinearSegmentedColormap.from_list("level", LEVEL)

effort = m.drop_duplicates("month").set_index("month")["all"]
m["inat_share"] = m.inat_count / m["all"]
```

## Where the records come from

Three public sources, each counting something different:

- **eBird**, run by the Cornell Lab of Ornithology. Birders submit checklists of what they saw on an outing. Its bar
  charts give, for each species and each quarter of a month, the share of complete checklists that reported it.
  Because a checklist is one outing, that share already allows for how many people went out.
- **iNaturalist**, where people post photos and others confirm the species. I used research-grade observations
  only: at least two people agreed on what it is. It covers mammals as well as birds, but it counts sightings, not
  outings.
- **The salmon co-managers' calendar.** The Lummi Nation, the Nooksack Tribe and the state manage the Nooksack's salmon
  together. Their shared table, *Anadromous Fish Periodicity in WRIA 1* (a January 2003 draft), shades each month in
  which each run enters the river, holds and spawns. The shading is in spreadsheet cells, not text, so I read it from
  an image of the page by colour, and checked it against the salmon recovery program's species sheets.

## Sightings follow people

```{code-cell} python
:tags: [remove-input]
fig, ax = plt.subplots(figsize=(7.5, 2.6))
ax.bar(MONTHS, effort.values / 1000, color=LINE)
ax.set_ylabel("thousand sightings")
ax.set_title("All research-grade iNaturalist sightings in Whatcom County, by month (all years)", fontsize=9, loc="left")
plt.show()
```

People post nearly seven times as many sightings in July as in December. A raw count makes almost any
animal look like a summer animal. So for iNaturalist I divided each animal's sightings in a month by all sightings
that month: its share of what people reported. For eBird, the checklist share does the same job.

Neither fixes where people go. Mountain birds will look like summer birds partly because summer is when people hike.

## The year, animal by animal

```{code-cell} python
:tags: [remove-input]
order = list(dict.fromkeys(m.animal))
val = {}
for a in order:
    d = m[m.animal == a].sort_values("month")
    v = d.ebird_share if d.ebird_share.notna().all() else d.inat_share
    val[a] = (v / v.max()).values
grid = np.array([val[a] for a in order])
src = {a: ("eBird" if m[m.animal == a].ebird_share.notna().all() else "iNaturalist") for a in order}
fig, ax = plt.subplots(figsize=(7.5, 6))
ax.imshow(grid, cmap=LEVEL_CMAP, vmin=0, vmax=1, aspect="auto")
ax.set_xticks(range(12), [x[0] for x in MONTHS])
ax.set_yticks(range(len(order)), [f"{a}  ({src[a]})" for a in order])
ax.tick_params(length=0)
for s in ax.spines.values():
    s.set_visible(False)
ax.set_title("How often each animal is reported, against its own best month (darkest)", fontsize=9, loc="left")
plt.show()
```

The winter visitors are the clearest: trumpeter swans and both goldeneyes from October or November to March, and
next to nothing in summer. Bald eagles peak in January. Black bears peak in September. Harlequin ducks are seen most
in October and November and least in June and July, when they are up on mountain streams to nest.

Some rows rest on few records. Pine grosbeaks are on fewer than 1% of checklists in any month. River otters have 73
iNaturalist records in all and beavers 131, so their rows are a rough guide.

## Do the two sources agree?

eBird and iNaturalist are collected in different ways by mostly different people. If both show the same shape of
year for a bird, I trust that shape more.

```{code-cell} python
:tags: [remove-input]
birds = [a for a in order if src[a] == "eBird"]
r = {}
for a in birds:
    d = m[m.animal == a].sort_values("month")
    r[a] = np.corrcoef(d.ebird_share, d.inat_share)[0, 1]
fig, axes = plt.subplots(1, 2, figsize=(7.5, 2.8), sharey=True)
for ax, a in zip(axes, ["Bald eagle", "Harlequin duck"]):
    d = m[m.animal == a].sort_values("month")
    ax.plot(MONTHS, d.ebird_share / d.ebird_share.mean(), marker="o", ms=3, color=LEVEL[4], label="eBird checklists")
    ax.plot(MONTHS, d.inat_share / d.inat_share.mean(), marker="o", ms=3, color=MUTED, label="iNaturalist sightings")
    ax.axhline(1, color=LINE, lw=0.8)
    ax.set_title(f"{a} (r = {r[a]:.2f})", fontsize=9, loc="left")
    ax.set_xticks(range(12), [x[0] for x in MONTHS])
axes[0].set_ylabel("times its average month")
axes[0].legend(frameon=False, fontsize=8)
plt.show()
table = pd.DataFrame({"agreement (r)": pd.Series(r).round(2),
                      "iNaturalist records": m.groupby("animal").inat_count.sum()[birds]}).sort_values("agreement (r)")
table
```

For the well-reported birds the two sources agree closely. The great blue heron does not, but it is around all year
with little seasonal swing, so there is little shape to agree on. The pine grosbeak has only four iNaturalist
records.

## Eagles and the salmon calendar

```{code-cell} python
:tags: [remove-input]
def months(s):
    return [int(x) for x in s.split()] if s else []

label = {"spring native": "spring", "fall hatchery-origin": "fall", "odd years only": "odd years",
         "Nooksack small runs": "Nooksack", "Baker Lake via Skagit": "Baker Lake"}
fig, (ax, ax2) = plt.subplots(2, 1, figsize=(7.5, 5.8), sharex=True, gridspec_kw={"height_ratios": [3, 1.4]})
for i, r_ in enumerate(runs.itertuples()):
    c = FISH[r_.species]
    for mo in months(r_.in_river):
        ax.barh(i, 1, left=mo - 1.5, height=0.7, color=c, alpha=0.28, edgecolor="white", lw=0.5)
    for mo in months(r_.spawning):
        ax.barh(i, 1, left=mo - 1.5, height=0.36, color=c, edgecolor="white", lw=0.5)
ax.set_yticks(range(len(runs)), [f"{r_.species.capitalize()}{', ' + label.get(r_.run, r_.run) if r_.run else ''}"
                                  for r_ in runs.itertuples()])
ax.invert_yaxis()
ax.tick_params(length=0)
ax.set_title("Nooksack runs: in the river (pale) and spawning (dark)", fontsize=9, loc="left")
e = m[m.animal == "Bald eagle"].sort_values("month")
ax2.plot(range(12), e.ebird_share * 100, marker="o", ms=3, color=INK)
ax2.set_ylabel("% of checklists")
ax2.set_title("Bald eagle, share of eBird checklists", fontsize=9, loc="left")
ax2.set_xticks(range(12), MONTHS)
ax.set_xlim(-0.5, 11.5)
plt.show()
```

I expected eagles to follow the salmon all through the year. They don't. In August and September, when spring
Chinook, pink and sockeye are spawning, eagles are on 4 to 7% of checklists. They climb from October, as the chum
and coho start to spawn, and peak in January, about a month after the chum. My guess is that many of our winter
eagles spend late summer on salmon runs farther north and come here for the chum. That fits what I've read, but I
haven't checked it against tagging studies yet.

## How many chum come back

The calendar says when. How many is a separate measurement. WDFW publishes a yearly spawner estimate for Nooksack
fall chum, counted in the North Fork, side channels and Maple Creek: an index of the run, not the whole run.

```{code-cell} python
:tags: [remove-input]
fig, ax = plt.subplots(figsize=(7.5, 2.8))
ax.plot(chum.year, chum.spawners / 1000, marker="o", ms=2.5, color=FISH["chum"])
ax.set_ylabel("thousand spawners")
ax.set_title("Nooksack fall chum spawners, North Fork index (WDFW)", fontsize=9, loc="left")
plt.show()
```

It swings from under 5,000 to over 90,000 from year to year, with big years in 1994, 2003 and 2011. I'd like to see
whether the eagles follow those swings too.

## Keeping it quiet

The Wildlife page never puts an animal on the map. The map shows streams where spawning is recorded, which is public
habitat data. Animals appear only as county-wide numbers by month. The list of birds reported in the last 30 days
gives species and dates, not places, because many birding spots are people's homes. Rare and sensitive species,
such as nesting owls, murrelets and raptors at their nests, are left out, and eBird and iNaturalist hide them too.

## What's next

- Skagit County. Its runs are timed differently, and there is no single shared table like the Nooksack's.
- Asking the Lummi Nation, the Nooksack Tribe and the Skagit River System Cooperative whether there is a newer
  periodicity table than the 2003 draft.
- Correcting the maps for where people go, not only how many go, so sightings could be shown on a coarse grid.

## Data

- eBird. 2026. eBird: An online database of bird distribution and abundance. Cornell Lab of Ornithology, Ithaca,
  New York. [ebird.org](https://ebird.org). Monthly checklist shares for Whatcom County, used for noncommercial
  education; no records are republished.
- [iNaturalist](https://www.inaturalist.org), research-grade observations per month for Whatcom County (place 1730),
  through its public API.
- WRIA 1 Co-Managers, 2003, *Anadromous Fish Periodicity in WRIA 1*, January 2003 draft, from the
  [WRIA 1 Watershed Management Project](https://wria1project.whatcomcounty.org/resources/technical-documents/historic-habitatandisf).
- Washington Department of Fish and Wildlife, Salmonid Population Indicators, escapement
  ([data.wa.gov](https://data.wa.gov/d/fgyz-n3uk)).
- Derived files: [`data/monthly.csv`](data/monthly.csv), [`data/salmon-timing.csv`](data/salmon-timing.csv) and
  [`data/chum-spawners.csv`](data/chum-spawners.csv), rebuilt by `uv run python scripts/wildlife_data.py`.
