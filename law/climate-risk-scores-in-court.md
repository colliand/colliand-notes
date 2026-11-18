---
title: Climate risk scores in court
subtitle: A running record of the lawsuits over First Street's property-level risk scores
date: 2026-11-18
# thumbnail: img/share.jpg      (shown on the landing card and in share previews)
description: Two state attorneys general and a New York homeowner are suing First Street over the flood and climate risk scores shown on home listings. This note tracks the cases and what they mean for anyone who publishes property-level model output.
tags: [law, climate-risk, flood, data-products]
draft: false
---

:::{note} Machine-drafted, and kept up to date
Drafted with help from AI language models from the sources linked below. Not legal advice.
**Last checked: 18 November 2026.** I am tracking these cases and update this note as they move.
Statuses go stale, so check the dates before relying on one.
:::

I first heard about this at the Cloud-Native Geospatial Forum in October 2026. It matters beyond climate.
The legal theory is about how a model's output is presented, not about whether the model is right, so it
would apply to any producer that publishes confident numbers for individual properties.

I read it as a crucible. A startup whose data product could displace an incumbent's numbers (here, FEMA flood
maps and the insurance and real estate practices built on them) can be attacked on the validity of its data.
The attack does not have to prove the model wrong. It only has to show the product claimed more than it could
back up. That makes the defences mostly a matter of design and disclosure, which a startup controls.

## The cases

| Case | Court | Filed | Law | Status (last checked) |
|---|---|---|---|---|
| *State of Nebraska ex rel. Hilgers v. First Street Technology, Inc.* | District Court of Dakota County, Nebraska | 27 Aug 2026 | Nebraska Consumer Protection Act; Uniform Deceptive Trade Practices Act | Pending. Only the complaint is on record (18 Nov 2026) |
| *Office of the Attorney General v. First Street Technology, Inc.*, Case No. 2026CA005207A000BA | Circuit Court, Tenth Judicial Circuit, Polk County, Florida | 23 Oct 2026 | Florida Deceptive and Unfair Trade Practices Act | Pending. No response from First Street reported (18 Nov 2026) |
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

## Defensive moves for a data-product startup

Each objection in the state complaints maps to something a producer can do before anyone sues.

- **Show the uncertainty.** Publish a range or a confidence band with every property-level number, not a bare
  score. The "forecast, not fact" defence is only as strong as the presentation behind it.
- **Claim exactly what was validated.** Say which part was peer reviewed (the method) and which was not (each
  property's score). Publish validation against observed outcomes, such as past claims and hindcasts.
- **Disclose disagreement on the page.** Where your number differs from the authoritative one (FEMA, the
  incumbent vendor), say so next to the number and explain why. Silence about it is what the states call deceptive.
- **Run a correction channel.** Accept disputes, take in local evidence such as mitigation work, and keep a
  versioned score history with a change log. A stated policy of never revising a score is the opposite.
- **Match the word "transparent" to reality.** If the data is paywalled, say "documented", or open enough of
  it that outsiders can check the model.
- **Control how distributors show it.** License terms with listing sites can require the caveats, the range and a
  link to the method, so a partner's display does not become your misrepresentation.
- **Assume the paper trail will be read.** Model cards, validation reports and internal messages are discoverable.
  Write them as if a state attorney general will quote them, because two have.
- **Expect politics.** A number that moves prices has losers with allies. Don't depend on one channel or one
  jurisdiction.

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
- [Complaint (PDF)](https://www.myfloridalegal.com/sites/default/files/first-street-complaint.pdf)
- [Climate Litigation Database (Sabin Center)](https://www.climatecasechart.com/document/office-of-the-attorney-general-v-first-street-technology-inc_74b3)
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
- Did the MSCI acquisition close?
- Other states following Nebraska and Florida.
