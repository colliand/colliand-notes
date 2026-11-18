---
title: Climate risk scores in court
subtitle: A running record of the lawsuits over First Street's property-level risk scores
date: 2026-11-18
# thumbnail: img/share.jpg      (shown on the landing card and in share previews)
description: Two state attorneys general and a New York homeowner are suing First Street over the flood and climate risk scores shown on home listings. This note tracks the cases and what they mean for anyone who publishes property-level model output.
tags: [law, climate-risk, flood, data-products]
draft: true
---

:::{note} Machine-drafted, and kept up to date
Drafted with help from AI language models from the sources linked below. Not legal advice.
**Last checked: 18 November 2026.** Statuses go stale, so check the dates before relying on one.
:::

I first heard about this at the Cloud-Native Geospatial Forum in October 2026. It matters beyond climate.
The legal theory is about how a model's output is presented, not about whether the model is right, so it
would apply to any producer that publishes confident numbers for individual properties.

## The cases

| Case | Court | Filed | Law | Status (last checked) |
|---|---|---|---|---|
| *State of Nebraska ex rel. Hilgers v. First Street Technology, Inc.* | District Court of Dakota County, Nebraska | 27 Aug 2026 | Nebraska Consumer Protection Act; Uniform Deceptive Trade Practices Act | Pending. Only the complaint is on record (18 Nov 2026) |
| Florida (AG Uthmeier) v. First Street Technology | State court, Polk County, Florida | 23 Oct 2026 | Florida Deceptive and Unfair Trade Practices Act | Pending. No response from First Street reported (18 Nov 2026) |
| *Uerkwitz v. First Street Technology and Zillow Group* | NY Supreme Court, New York County, Index No. 653631/2025 | June 2025 | Injurious falsehood (disparaging property) | Reported as pending (Oct 2026) |

## What the states object to

Both state suits make the same kind of argument. Nebraska's complaint says outright that it does not ask for
perfect accuracy. The objections are about presentation and handling:

- **Forecasts shown as facts.** A single 1 to 10 score next to bedrooms and price, with no uncertainty range.
- **"Peer-reviewed" and "validated" overclaimed.** The methods were reviewed, not the individual property scores.
- **Disagreement not disclosed.** Scores run well above FEMA flood maps and flood insurance claims history, and
  other vendors' scores differ. Florida points to properties FEMA rates as minimal flood hazard.
- **No way to correct a score.** Scores ignore mitigation homeowners have built, and First Street's stated
  policy is not to change scores in response to individual disputes.
- **"Transparent", but proprietary.** The underlying data is paywalled.

Both states want an injunction, civil penalties and money back for consumers, and both ask for a jury. Florida's
penalties run $10,000 to $15,000 per violation. Florida's complaint is also openly political: it calls the scores
"marketing fear to advance a climate activism agenda".

## The likely defence

In the New York case, Zillow argued that a risk score is a forecast, "not a statement of verifiable fact"
(as quoted in Nebraska's complaint, para. 141). Any producer of model output would reach for the same argument.
The state suits are built to get around it by attacking the marketing claims, not the forecast.

## Timeline

- **June 2025.** The Uerkwitz family sues First Street and Zillow over a 9/10 flood score on a Chappaqua, New York
  house outside any FEMA flood zone. They seek $500,000.
- **Nov to Dec 2025.** Zillow removes the scores from its listings after California Regional MLS questions the
  flood model, and now only links to First Street. Redfin and Realtor.com keep showing them.
- **24 June 2026.** MSCI announces it will buy First Street for $120 million plus earn-outs.
- **July 2026.** Consumers' Research and the American Energy Institute call for a federal investigation of
  First Street.
- **27 Aug 2026.** Nebraska sues.
- **23 Oct 2026.** Florida sues.

## Sources

Nebraska
- [Complaint (PDF, 63 pages)](https://ago.nebraska.gov/sites/default/files/doc/Court%20filing.pdf)
- [Nebraska AG press release](https://ago.nebraska.gov/news/attorney-general-hilgers-files-lawsuit-against-first-street-harming-nebraska-homeowners)
- [Climate Litigation Database (Sabin Center)](https://www.climatecasechart.com/document/state-of-nebraska-v-first-street-technology-inc_0912)

Florida
- [ESG Dive](https://www.esgdive.com/news/florida-ag-sues-climate-analytics-provider-first-street-over-home-risk-scor/873473/)
- [Insurance Journal (Bloomberg)](https://www.insurancejournal.com/news/southeast/2026/10/27/890449.htm)
- [Florida Phoenix](https://floridaphoenix.com/2026/10/26/uthmeier-property-risk-assessment-company-is-marketing-fear-to-advance-a-climate-activism-agenda/)
- [HousingWire, on both state suits](https://www.housingwire.com/articles/first-street-climate-risk-lawsuit/)

New York and context
- [HousingWire, on Uerkwitz](https://www.housingwire.com/articles/ny-couple-claims-zillows-climate-risk-data-harmed-home-sale/)
- [Trellis docket, Uerkwitz](https://trellis.law/case/36061/653631-2025/uerkwitz-andrew-et-al-v-first-street-technology-inc-et-al)
- [Inside Climate News, on Zillow removing the scores](https://insideclimatenews.org/news/20012026/climate-expert-works-to-restore-zillow-climate-risk-scores/)
- [MSCI announcement](https://ir.msci.com/node/22796)

## To check next time

- Has First Street answered either state, moved a case to federal court, or moved to dismiss?
- Florida's complaint itself and its case number. I found news coverage but not the filing.
- Did the MSCI acquisition close?
- Other states following Nebraska and Florida.
