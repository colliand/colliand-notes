---
title: The Earth observation sensor design space
subtitle: Radar bands, optical sensors, and what each one can see
date: 2026-11-18
# thumbnail: img/share.jpg      (shown on the landing card and in share previews)
description: A map of the choices behind Earth observation satellites, from X-band and C-band radar to multispectral and hyperspectral optical sensors. Wavelength sets what a sensor can see through and what it can identify; band count trades against pixel size.
tags: [earth-observation, sar, remote-sensing]
draft: true
kernelspec:
  name: python3
  display_name: Python 3
---

:::{note} Machine-drafted
Drafted with help from AI language models from the references listed at the end, read on 18 November 2026. Mission
figures are nominal specifications, not measured performance. A quick experiment, not peer reviewed.
:::

I started this at SatSummit 2026 in St. Louis. Most of the talks assumed you already knew why one satellite carries a
C-band radar and another a 22-band optical camera. I wanted a map of that design space.

:::{tip} In short
- **Wavelength decides what a sensor sees through.** Radar wavelengths run from about 1 cm to 1 m. All of them see
  through cloud and work at night. Longer waves go deeper: X-band bounces off the top of a forest, L-band reaches
  the trunks.
- **Optical sensors see what things are made of.** They trade spectral detail for sharpness. A panchromatic camera
  takes one wide band and gets the sharpest pixels. Hyperspectral sensors split the light into hundreds of narrow
  bands, so each band gets less light and the pixels are coarser.
- **Radar sees shape, roughness, moisture and motion.** Comparing the phase of two passes (InSAR) measures ground
  movement to about a centimetre. Optical sees colour and chemistry. The two complement each other.
:::

```{code-cell} python
:tags: [remove-cell]
import matplotlib.pyplot as plt

INK, MUTED, LINE = "#1f2a24", "#5b6760", "#c9c5b9"
OPTICAL, THERMAL, RADAR = "#b8862b", "#c2552a", "#1b5f7a"
plt.rcParams.update({"figure.dpi": 130, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
                     "font.size": 9})
```

## Where the sensors sit in the spectrum

Earth observation uses two windows where the atmosphere lets energy through. The **optical** window runs from visible
light into the shortwave infrared, roughly 0.4 to 2.5 µm. A **thermal** window sits near 8 to 14 µm. Past it is the
**microwave** window, where radar works. Radar wavelengths are 10,000 to 100,000 times longer than visible light.

```{code-cell} python
:tags: [remove-input]
# Wavelengths in metres. Radar edges from IEEE Std 521 (as tabulated by NASA Earthdata).
optical = [("VNIR", 0.4e-6, 1.0e-6, OPTICAL), ("SWIR", 1.0e-6, 2.5e-6, OPTICAL), ("Thermal IR", 8e-6, 14e-6, THERMAL)]
radar = [("Ka", 0.0075, 0.011), ("K", 0.011, 0.017), ("Ku", 0.017, 0.025), ("X", 0.025, 0.0375),
         ("C", 0.0375, 0.075), ("S", 0.075, 0.15), ("L", 0.15, 0.30), ("P", 0.30, 1.0)]
used = {"X", "C", "S", "L", "P"}

fig, ax = plt.subplots(figsize=(7.5, 1.9))
for name, lo, hi, c in optical:
    ax.barh(1, hi - lo, left=lo, height=0.6, color=c)
    ax.text((lo * hi) ** 0.5, 1.45, name, ha="center", color=INK)
for name, lo, hi in radar:
    ax.barh(0, hi - lo, left=lo, height=0.6, color=RADAR if name in used else LINE, edgecolor="white")
    ax.text((lo * hi) ** 0.5, 0, name, ha="center", va="center", color="white" if name in used else MUTED,
            fontsize=8)
ax.set_xscale("log")
ax.set_xlim(2e-7, 2)
ax.set_ylim(-0.6, 1.9)
ax.set_yticks([0, 1], ["Radar\n(active)", "Optical\n(passive)"])
ax.set_xticks([1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1], ["1 µm", "10 µm", "100 µm", "1 mm", "1 cm", "10 cm", "1 m"])
ax.set_xlabel("Wavelength (log scale)")
ax.spines["left"].set_visible(False)
ax.tick_params(axis="y", length=0)
ax.set_title("Optical and radar sensors use different windows", loc="left", color=INK)
plt.tight_layout()
plt.show()
```

The radar letters are not physics. They are naming conventions from the Second World War, now fixed by
**IEEE Std 521**, *Standard Letter Designations for Radar-Frequency Bands*. The blue bands are the ones Earth
observation radars use. The shorter bands (Ku, K, Ka) are mostly used for altimetry and weather radar, not imaging.

| Band | Frequency | Wavelength | What it is good at | Examples |
|---|---|---|---|---|
| X | 8–12 GHz | 2.4–3.8 cm | Fine detail; cities, ships, ice. Sees only the top of a canopy | TerraSAR-X, ICEYE, Capella, Umbra |
| C | 4–8 GHz | 3.8–7.5 cm | The workhorse for global mapping and change detection; sea ice, oceans, floods | Sentinel-1, RADARSAT |
| S | 2–4 GHz | 7.5–15 cm | Agriculture, a growing middle ground | NISAR (ISRO's channel) |
| L | 1–2 GHz | 15–30 cm | Reaches branches and trunks; biomass, ground movement (InSAR) under vegetation | NISAR (NASA's channel), ALOS-2 |
| P | 0.3–1 GHz | 0.3–1 m | Forest biomass through the whole canopy; experimental | ESA Biomass |

## What the radar bands trade off

**Penetration.** A radar wave interacts with things about its own size. X-band (about 3 cm) bounces off leaves at the
top of a forest. C-band gets into the upper canopy. L-band (about 23 cm) reaches large branches and trunks. P-band
sees the whole forest structure. That is why the biomass missions are L- and P-band. Longer waves also reach a little
way into dry soil and sand.

**Cloud and rain.** All the imaging bands see through cloud, smoke and darkness. Heavy rain can attenuate X-band and
the shorter bands. At L-band it barely matters.

**Resolution.** A radar's fine detail comes from processing, not from a big antenna. A C-band radar would need an
antenna about 4 km long to see 10 m detail directly. The satellite instead synthesizes that aperture as it moves.
Across-track detail comes from the signal's bandwidth. Wider bandwidths are easier at higher frequencies, and the
antenna can be smaller. This is why commercial small-satellite radar (ICEYE, Capella, Umbra) is mostly X-band and
reaches below a metre.

**Stability over time (coherence).** Interferometry compares the phase of two passes to measure ground movement to
about a centimetre. That works only if the surface scatters the same way both times. Leaves move between passes, so
X- and C-band lose coherence over vegetation quickly. L-band sees the stable trunks and ground. This is a large part
of NISAR's case.

**Polarization** is a separate choice from band. A radar can send and receive horizontally or vertically polarized
waves. Bare soil and water show up most in VV. Leaves and branches scatter into the cross-polarized channels (VH or
HV). Buildings, trunks and flooded forest bounce twice and show up in HH.

**Revisit** is not a property of the band. It comes from the orbit and the number of satellites. Sentinel-1 repeats
every 12 days with one satellite, and every 6 with two (1C and 1D since late 2025).

## Panchromatic, multispectral, hyperspectral

An optical sensor counts reflected sunlight. The design question is how to split it.

- **Panchromatic**: one wide band across the visible spectrum. All the light lands in one channel, so it gives the
  sharpest pixels. It is black and white.
- **Multispectral**: about 4 to 20 broad bands, each placed for a purpose. Red and near-infrared show vegetation.
  The *red edge* between them tracks plant stress. The shortwave infrared shows moisture and burn scars. A cirrus
  band catches high cloud.
- **Hyperspectral**: hundreds of narrow, adjacent bands (5–10 nm wide) from 0.4 to 2.5 µm. Each pixel is a
  continuous spectrum, so materials can be identified by their absorption features: minerals, plant pigments,
  methane plumes, water quality.
- **Thermal infrared** (8–14 µm) measures emitted heat, not reflected light. It works at night. It gives surface
  temperature, which shows evaporation, fires and urban heat.

Band count matters because each new band is a question you can ask. But the light is shared. Split it into 200
bands and each one gets a two-hundredth of the photons. The sensor needs bigger pixels, a bigger telescope or a
longer look to get the same signal-to-noise. More bands also mean more data to send down. The chart shows the
trade-off. The sharp sensors sit at the bottom left, the hyperspectral ones at the top right, and the top left (sharp
and hyperspectral) is empty.

```{code-cell} python
:tags: [remove-input]
# Nominal specs: finest ground sample distance (m) and number of spectral bands, incl. panchromatic and thermal.
missions = [
    ("WorldView-3", 0.31, 17, "commercial"), ("SkySat", 0.5, 5, "commercial"),
    ("PlanetScope\nSuperDove", 3, 8, "commercial"), ("EarthDaily", 5, 22, "commercial"),
    ("Sentinel-2", 10, 13, "public"), ("Landsat 8/9", 15, 11, "public"), ("MODIS", 250, 36, "public"),
    ("EnMAP", 30, 228, "public"), ("PRISMA", 30, 239, "public"), ("Tanager-1", 30, 424, "commercial"),
    ("EMIT", 60, 285, "public"),
]
offset = {"PRISMA": (6, 8), "EnMAP": (6, -10), "Tanager-1": (6, 0), "EMIT": (6, 0)}
fig, ax = plt.subplots(figsize=(7.5, 3.6))
for name, gsd, bands, owner in missions:
    c = OPTICAL if owner == "commercial" else RADAR
    ax.scatter(gsd, bands, s=30, color=c, zorder=3)
    ax.annotate(name, (gsd, bands), xytext=offset.get(name, (6, 2)), textcoords="offset points", fontsize=8,
                color=INK, va="center")
ax.axhspan(100, 600, color=LINE, alpha=0.35, lw=0)
ax.text(0.22, 140, "hyperspectral", color=MUTED, fontsize=8)
ax.text(0.22, 40, "multispectral", color=MUTED, fontsize=8)
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlim(0.2, 1500)
ax.set_ylim(3, 600)
ax.set_xticks([0.3, 1, 3, 10, 30, 100, 300, 1000], ["0.3", "1", "3", "10", "30", "100", "300", "1000"])
ax.set_yticks([5, 10, 20, 50, 100, 200, 400], ["5", "10", "20", "50", "100", "200", "400"])
ax.minorticks_off()
ax.set_xlabel("Finest pixel size (m, log scale)")
ax.set_ylabel("Spectral bands (log scale)")
ax.scatter([], [], color=RADAR, label="public mission")
ax.scatter([], [], color=OPTICAL, label="commercial")
ax.legend(frameon=False, loc="lower right")
ax.set_title("Optical sensors trade sharpness for spectral detail", loc="left", color=INK)
plt.tight_layout()
plt.show()
```

The pixel size is each sensor's finest band. Most have coarser bands too. WorldView-3's panchromatic band is 0.31 m,
but its shortwave infrared bands are 3.7 m. EarthDaily's 5 m applies to its visible and near-infrared bands. Its
shortwave bands are 95 m and its thermal bands 120 m.

## Active versus passive

| | Radar (active) | Optical (passive) |
|---|---|---|
| Light source | Its own pulse | The sun, or the surface's own heat for thermal |
| Night, cloud, smoke | Sees through | Blocked (thermal works at night, not through cloud) |
| Measures | Geometry, roughness, moisture, structure; phase (motion to about 1 cm) | Colour and chemistry: pigments, minerals, water, temperature |
| Hard parts | Speckle; side-looking geometry (layover, shadow); takes training to read | Cloud cover (much of the tropics, much of the time); needs daylight |
| Good for | Floods under cloud, ground deformation, ships, sea ice, forest structure | Crop health, land cover, burn severity, water quality, methane |

Radar cannot tell a green field from a brown one. Optical cannot measure a centimetre of subsidence, or see through a
monsoon. Most serious monitoring uses both.

## Where the big constellations sit

| Mission | Who | Sensor | Detail | Revisit |
|---|---|---|---|---|
| Sentinel-1 | ESA / Copernicus | C-band SAR | 5 × 20 m, 250 km swath (main mode) | 12 days per satellite, 6 with two |
| Sentinel-2 | ESA / Copernicus | Multispectral, 13 bands (0.44–2.19 µm) | 10, 20 and 60 m | 5 days with two satellites |
| Landsat 8 and 9 | NASA / USGS | 9 optical bands and 2 thermal | 15 m pan, 30 m, 100 m thermal | 16 days each, 8 together |
| NISAR | NASA / ISRO | L-band and S-band SAR | swath about 240 km | 12 days |
| Planet | Planet Labs | PlanetScope (8 bands), SkySat, Pelican, Tanager (hyperspectral) | about 3 m to below 1 m | near-daily (PlanetScope) |
| EarthDaily | EarthDaily Analytics | 22 bands: 11 VNIR, 6 SWIR, 5 thermal | 5 m, 95 m, 120 m; 240 km swath | daily (planned) |

Three notes on the table.

- **NISAR** launched on 30 July 2025. NASA's L-band data became public on 20 July 2026 through the Alaska Satellite
  Facility, free. ISRO distributes the S-band data through its Bhoonidhi portal. It is the first mission to fly
  two radar bands. It is the reference case for L-band interferometry under vegetation.
- **"About 700 Planet satellites"** is the number launched over the company's history: one tracker counts 672
  launched. Far fewer are flying now. Trackers count about 130 in orbit, and Planet says more than 200. The fleet
  mixes sharp but narrow SkySat and Pelican satellites, the PlanetScope flock that images most land daily, and its
  first hyperspectral satellite, Tanager-1.
- **EarthDaily** is not chasing sharpness. Its 22 bands cover much of Sentinel-2's and Landsat's range, including
  thermal. It is cross-calibrated against both, so it can serve as a daily version of the public missions. Eight
  of its nine satellites plus a spare were in orbit by July 2026. Commercial operations were expected late in 2026.

## Non-Earth imaging

Non-Earth imaging (NEI) means satellites photographing other objects in orbit: other satellites, rocket bodies,
debris. The customers are satellite operators checking on their own spacecraft (did the solar array deploy? what hit
it?), insurers, and governments doing space domain awareness.

The sensors are mostly ordinary optical cameras pointed sideways rather than down. That makes existing Earth imaging
fleets a ready-made NEI network. The company I found most of is [HEO](https://www.heospace.com/). It flies its own
"Holmes" cameras as hosted payloads, and it buys time on other operators' satellites. In 2026 it signed agreements
to use Planet's SkySats (August) and Satellogic's satellites (through 2029). HEO also reports a contract with the
US National Reconnaissance Office.

In the US, NOAA licenses NEI as commercial remote sensing. HEO reports the first NOAA-licensed NEI payload cleared to
image above 800 km (November 2025). Most of what I found comes from HEO's own press releases. I found no independent
estimate of the market's size.

## References

Standard and survey references, then the sources for specific figures.

- IEEE, *IEEE Standard Letter Designations for Radar-Frequency Bands*, IEEE Std 521-2019,
  [doi:10.1109/IEEESTD.2020.8999849](https://doi.org/10.1109/IEEESTD.2020.8999849). The band letters.
- A. Moreira, P. Prats-Iraola, M. Younis, G. Krieger, I. Hajnsek, K. P. Papathanassiou, "A tutorial on synthetic
  aperture radar," *IEEE Geoscience and Remote Sensing Magazine* 1(1), 6–43 (2013),
  [doi:10.1109/MGRS.2013.2248301](https://doi.org/10.1109/MGRS.2013.2248301).
  ([open copy via IEEE GRSS](https://www.grss-ieee.org/resources/tutorials/dlr-tutorial-on-synthetic-aperture-radar-pdf/))
- J. M. Bioucas-Dias, A. Plaza, G. Camps-Valls, P. Scheunders, N. M. Nasrabadi, J. Chanussot, "Hyperspectral remote
  sensing data analysis and future challenges," *IEEE Geoscience and Remote Sensing Magazine* 1(2), 6–36 (2013),
  [doi:10.1109/MGRS.2013.2244672](https://doi.org/10.1109/MGRS.2013.2244672).
- A. Flores-Anderson et al. (eds.), *The SAR Handbook: Comprehensive Methodologies for Forest Monitoring and Biomass
  Estimation*, NASA SERVIR and SilvaCarbon (2019), [NASA NTRS](https://ntrs.nasa.gov/citations/20190002563).
  Free, with exercises.
- NASA Earthdata, [What is SAR?](https://www.earthdata.nasa.gov/learn/earth-observation-data-basics/sar). Band table,
  penetration, polarization, the 4 km antenna example.
- NISAR data release: [NASA Earthdata](https://www.earthdata.nasa.gov/news/nisar-l-band-data-released-expanding-record-surface-changes),
  [ASF](https://asf.alaska.edu/notices/nisar-l-band-data-now-publicly-available/),
  [ISRO S-band](https://www.isro.gov.in/NISARS_Band_SAR_Data_Products_Release.html).
- Sentinel-1D: [ESA](https://www.esa.int/Applications/Observing_the_Earth/Copernicus/Sentinel-1/Sentinel-1D_reaches_orbit_on_Ariane_6).
- EarthDaily: [constellation documentation](https://docs.earthdaily.com/data/edc-product-introduction/),
  [Launch III](https://earthdaily.com/blog/earthdaily-constellation-entering-commercial-operations-with-successful-launch-iii).
- Tanager: [USGS system characterization report](https://pubs.usgs.gov/publication/ofr20211030W/full).
  EnMAP: [eoPortal](https://eoportal.org/satellite-missions/enmap).
- HEO: [NOAA license above 800 km](https://www.heospace.com/resources/stories/heo-launches-first-noaa-licensed-non-earth-imaging-payload-authorized-above-800-kilometres),
  [Planet SkySat integration](https://satnews.com/2026/08/19/heo-expands-non-earth-imaging-network-via-planet-labs-skysat-constellation-integration/),
  [Satellogic through 2029](https://newspaceeconomy.ca/2026/10/30/satellogic-and-heo-extend-satellite-inspection-through-2029/).
