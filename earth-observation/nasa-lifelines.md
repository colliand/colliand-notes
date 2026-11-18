---
title: NASA Lifelines
subtitle: What it is, who it serves, and how it works
date: 2026-11-18
# thumbnail: img/share.jpg      (shown on the landing card and in share previews)
description: NASA Lifelines is a NASA-funded community, run by DevGlobal since October 2023, that connects humanitarians with Earth scientists. It hosts no data. It curates paths to data, guides for deciding whether satellite data fits a need, and programs that put the two groups in a room.
tags: [earth-observation, nasa, humanitarian]
draft: true
---

:::{note} Machine-drafted
Drafted with help from AI language models from the Lifelines website and a few NASA and conference pages, read on
18 November 2026. A quick experiment, not peer reviewed.
:::

I first heard about NASA Lifelines at SatSummit 2026 in St. Louis and wanted to learn more.

:::{tip} In short
- Lifelines is a **community, not a data system**. NASA funds it, the services firm DevGlobal runs it, and it
  launched in October 2023.
- Its users are **humanitarian organizations**. They use it to decide whether satellite data fits a need: early
  warning, preparedness, damage assessment, aid distribution.
- It **hosts no data**. Its "Data Studios" point to OCHA's Humanitarian Data Exchange, Source Cooperative and NASA
  Earthdata Search. Its "Decision-Making Guides" start with a question: is satellite data right for me?
:::

## What it is, and who runs it

Lifelines says it exists "to bring experts from different sectors, disciplines, countries, and backgrounds
together" to use space-based assets to improve life on Earth. It is "led by the services firm DevGlobal, in
partnership with NASA" ([about](https://nasalifelines.org/about/)). The NASA side is the Disasters program. Its
program manager, Shanna McClain, wrote one of the letters in the 2025 year in review.

A FOSS4G North America 2024 talk dates the launch to **October 2023** and calls it "NASA funded"
([talk](https://talks.osgeo.org/foss4g-na-2024/talk/9TQBYJ/)). NASA's own write-ups describe a six-year initiative
between NASA's Earth Science Division and DevGlobal. They also report 500+ practitioners and scientists from 143
countries in the first months. I saw those figures only in search summaries: the NASA pages now redirect, and I could
not open them to check. 2025 was "Year 2". The site claims a "community of 2000+ experts". The year in review says
"over 1,000 experts engaged" in 2025.

## Who uses it, and for which decisions

The users are humanitarian organizations, scientists, GIS practitioners and funders. Named partners and projects
include:

- the IOM's Climate Mobility Innovation Lab in Bangkok, where a Lifelines fellow worked;
- RED LabOT in Colombia, whose **Vigía** risk platform for municipalities builds on NASA's LHASA landslide model;
- Twilio.org, a new partner in 2025 for scaling work in Colombia;
- PAX for Peace, on tracking environmental damage in conflict zones.

The decisions are disaster-cycle decisions: early warning, preparedness, where to send aid, and damage assessment
after an event. The guides add disease risk, food security and human rights. The 2025 cohort of the Ready for
Impact accelerator had 12 teams, working on flood resilience, debris damage assessment and health service delivery.

## What it provides, and where it lives

Most of what Lifelines does is **convening**. Its programs:

| Program | What it does |
|---|---|
| Fellowship | Fellows build tools, research and convenings |
| Ready for Impact | Four-month accelerator for humanitarian teams, ending in a pitch to funders |
| Earth Science Review Board | Interdisciplinary panels that review program design, data choice and methods |
| Speed Dating, Supper Clubs | Introductions between scientists and humanitarians |
| Humanitarian Simulations | Exercises built around a crisis scenario |
| Past: Crisis Readiness Accelerator, Humanitarian Wayfinders | Earlier cohorts, one in Spanish |

The **community tools** are documents and pointers, not services:

- **[Data Studios](https://nasalifelines.org/data-studios/)**: a package for each use case, with case studies, tools,
  data and how-to guides. Active packages cover wildfires, flooding, landslides, disease risk, damage assessment,
  human rights and food security. Eleven more topics are asking for contributors. The page says plainly that
  Lifelines is "not building a master repository of geospatial data". The packages point to
  [HDX](https://data.humdata.org/), [Source Cooperative](https://source.coop/) and
  [Earthdata Search](https://search.earthdata.nasa.gov/).
- **[Decision-Making Guides](https://nasalifelines.org/decision-making-guides/)**: a main *Satellite Data
  Suitability Assessment* ("Is satellite data right for me?", "What's our approach?", "Communicating results",
  "Ethics and risk"). Five use-case guides follow: conflict damage, disease risk, food security, flood early
  warning, human rights.
- **Lifelines Data Series**: what data is useful and available, and how to get it, process it and turn it into
  insight.
- A **member portal** ([connect.nasalifelines.org](https://connect.nasalifelines.org/)) for tools and
  collaboration. The site says it is not launched yet.

## How it connects to the summit's themes

These are my readings, not claims Lifelines makes.

- **Karl Wuster: decision tools that get used.** The suitability guide is a guard against tools nobody uses. It asks
  whether satellite data is the right input before anyone builds anything. The simulations test tools under crisis
  conditions before a real crisis.
- **Katie Baynes: move the hard work from users to data providers.** Lifelines works from the other end. It does
  not change the data. It writes the map from a humanitarian question to an existing archive. The two fit together:
  every packaging step a provider takes on is a how-to guide a Data Studio no longer needs.
- **Hannah Kerner: an evaluation harness for geospatial models.** This is the gap. The Earth Science Review Board
  reviews methods case by case. I found nothing like a shared benchmark that says whether a flood or damage model
  works in a given place. A harness like Kerner's would give the review board something to measure against.

## Open questions

- What does the portal add when it launches? Is it a directory, or does it host anything?
- What is the budget, and what happens after year six (about 2029)?
- Source Cooperative appears as a data home. Is there a computing environment beside the data, or does every
  humanitarian team bring its own?

## Sources

- [nasalifelines.org](https://nasalifelines.org/), [About](https://nasalifelines.org/about/),
  [2025 year in review](https://nasalifelines.org/2025-year-in-review/),
  [Data Studios](https://nasalifelines.org/data-studios/),
  [Decision-Making Guides](https://nasalifelines.org/decision-making-guides/)
- N. Hunt, [Lifelines Data Series talk](https://talks.osgeo.org/foss4g-na-2024/talk/9TQBYJ/), FOSS4G North America
  2024
