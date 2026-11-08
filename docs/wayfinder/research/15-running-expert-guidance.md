# Research 15: Running expert guidance sources

Ticket: `tickets/15-research-running-expert-guidance.md`. Researched 2026-11-08.

## Summary

- Peer-reviewed or consensus sources found (abstracts verified via Europe PMC / PubMed / PMC): Gabbett 2016, Impellizzeri 2020 + 2021, Nielsen 2014, Mujika & Padilla 2003, Bosquet 2007, Seiler 2010, Esteve-Lanao 2007, Stoggl & Sperlich 2014, Meeusen 2013 (ECSS/ACSM), Soligard 2016 (IOC), Buchheit 2014, Plews 2012/2013, Kiviniemi 2007, Bellenger 2016.
- COROS publishes definitions on its own site: Base Fitness = 42 days, Load Impact = 7 days, Intensity Trend = ratio with labelled percentage bands, Recovery % bands, HRV labels. No numeric thresholds for HRV or resting HR labels.
- No COROS page was found that defines a metric called "Training Load Ratio" or uses ATI/CTI. COROS's equivalent is Intensity Trend (Load Impact / Base Fitness). Treat "ATI/CTI" naming as unverified for COROS.
- Biggest disagreement: the acute:chronic workload ratio (ACWR) "sweet spot" (Gabbett) versus authors who say it has no evidence for injury prevention (Impellizzeri). The 10% weekly rule is also weakly supported.
- Coaches' books (Daniels, Pfitzinger, Lydiard, Hansons, Fitzgerald, Magness, etc.) are listed only as candidates; none were checked against the original text. Owner to add or veto.

## Verification legend

- [V] = I read the text of the abstract/page (via Europe PMC, PMC, or a COROS page fetch). Page fetches were summarised by a small model, so COROS figures are [V-summary]: re-check against the live page before they go into the spec.
- [U] = unverified: from search snippets or secondary sources, or not checked.

## 1. COROS: how COROS defines its metrics and labels

Sources (COROS first-party):
- Training Status explainer: https://coros.com/stories/coros-metrics/c/prepare-for-your-next-race-with-training-status
- Training Load explainer: https://au.coros.com/stories/coros-metrics/c/training-load
- Recovery metrics explainer: https://coros.com/stories/coros-metrics/c/your-coros-recovery-metrics-explained
- COROS support centre (EvoLab / fitness metrics): https://support.coros.com/hc/en-us/articles/4412802807444-EvoLab . Direct fetch returned HTTP 502 (also 4412789816724), so support-centre wording was seen only in search snippets [U].

### Load metrics

- Training Load (per workout) [V-summary]: one value per activity estimating cardiovascular stress; combines duration and intensity (HR or pace; power for cycling when available); TRIMP-based. Strength work scores low.
- Weekly Training Load [V-summary]: sum of TL for each Monday-to-Sunday week (fixed week, not rolling). Graph shows a suggested weekly range learned from the user's habits; COROS gives no numeric bounds and says low/medium/high varies by person.
- Base Fitness [V-summary]: 42-day rolling average of daily training load (long-term). Search snippet of the support article says "the last 42 days" [U].
- Load Impact [V-summary]: 7-day rolling average of daily training load (short-term).
- Intensity Trend [V-summary]: Load Impact / Base Fitness, shown as a percentage.
  - Disagreement inside COROS material: an older/other COROS story reportedly gives "Load Impact - Base Fitness" (subtraction) [U, seen only in a search summary]. The ratio form matches the percentage bands, so the ratio is the likely correct one.
  - A third-party guide (runningxpert.com) describes the base window as six weeks and a "fatigue" figure as Load Impact minus Base; third-party, not high-trust [U]. COROS pages do not define a metric named "Fatigue" in what I read.

### Training Status labels (Intensity Trend bands) [V-summary]

| Label | Intensity Trend | COROS meaning (paraphrased) |
|---|---|---|
| Excessive | 150% and above (one source says ">150%", another ">=150%") | Possible overreaching; reduce load |
| Optimized | 100-149% | Base Fitness building |
| Maintaining | 80-99% | Moderate recent load, Base Fitness steady |
| Resuming | 50-79% | Load rising again after Decreasing |
| Performance | 50-79% | Reduced load, primed for hard efforts (race readiness) |
| Decreasing | 0-49% | Base Fitness falling |

- Resuming and Performance share 50-79%; the label depends on the previous status (Performance after Maintaining, Resuming after Decreasing).
- Boundary wording differs slightly across COROS pages (150% edge). Verify before coding thresholds.

### Recovery and physiology labels

- Recovery % bands [V-summary, confirmed by two fetches/searches]: 0-19% Exhausted, 20-69% Fatigued, 70-89% Normal, 90-100% Fresh. Recovery uses Base Fitness, Training Load and energy left since the last workout; no formula given. COROS's own example caption labels a 64% reading "Tired", which does not match the band names (inconsistency in COROS material).
- Overnight HRV labels [V-summary]: Elevated (above normal range), Normal, Reduced (slightly below), Low (significantly below). Baseline range is personal (example 45-57 ms). No numeric cut-offs for labels.
- Resting HR [V-summary]: lowest HR on waking; COROS gives no thresholds. Says a falling trend suggests improving aerobic fitness and a sudden rise can reflect overtraining, illness or travel.
- Not covered by pages I read: Training Effect, Stamina, Performance (running fitness) score, VO2max method. [U]

### Implication for the chatbot

- COROS labels are COROS's own model, not validated science; cite them as "COROS says". The chatbot can quote label and band from the data (the connector already returns them per ticket 09) rather than recompute.

## 2. Peer-reviewed and consensus sources, by topic

### Load progression and injury

- Gabbett 2016, BJSM, "The training-injury prevention paradox". PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC4789704 [V-summary]
  - Recommends keeping ACWR about 0.8-1.3 ("sweet spot"); ratios 1.5 and above are the "danger zone" (cricket data: 2-4x injury risk next 7 days).
  - Recommends limiting weekly load increases to under 10%; cautions against applying to individuals.
  - Evidence base is team sport (cricket, rugby league, soccer), not distance running.
- Impellizzeri et al. 2020, IJSPP, "Acute:Chronic Workload Ratio: Conceptual Issues and Fundamental Pitfalls", https://doi.org/10.1123/ijspp.2019-0864 [V]
  - Conclusion (paraphrased): no evidence supports using ACWR in load-management or training recommendations to reduce injury; ratio is statistically problematic.
- Impellizzeri et al. 2021, Sports Med, "...Time to Dismiss ACWR and Its Underlying Theory", https://doi.org/10.1007/s40279-020-01378-6 [V]
  - Substituting contrived chronic loads gave similar effects; ACWR added no predictive advantage in their analysis.
- Soligard et al. 2016, IOC consensus, "How much is too much? (Part 1)", https://doi.org/10.1136/bjsports-2016-096581 [V abstract only]
  - Says poor load management (including rapid changes in load) is a major injury risk factor; gives guidelines for prescribing and monitoring load. Specific numbers not read [U].
- Nielsen et al. 2014, JOSPT, "Excessive progression in weekly running distance and risk of running-related injuries", https://doi.org/10.2519/jospt.2014.5164 [V]
  - 874 novice runners, 1-year cohort. Groups: under 10%, 10-30%, over 30% weekly distance progression. No significant difference in overall injury rate. Over 30% over 2 weeks had higher rate of distance-related injuries versus under 10% (HR 1.59, CI 0.96-2.66, P=.07, not significant). Authors call it exploratory.
  - Note: the "10% rule" is therefore weakly supported even in the running-specific study; Gabbett's "<10%" is from other populations.

### Easy vs hard distribution

- Seiler 2010, IJSPP, https://doi.org/10.1123/ijspp.5.3.276 [V]
  - Observational: elite endurance athletes do about 80% of sessions at low intensity (below about 2 mM lactate) and about 20% hard. Notes that intensification studies in well-trained athletes show no convincing long-term gain from more HIIT.
- Esteve-Lanao et al. 2007, J Strength Cond Res, https://doi.org/10.1519/r-19725.1 [V partial abstract]
  - 12 sub-elite runners, 5 months: more time in zone 1 (about 80% vs about 67%) compared; abstract was truncated, result not read [U].
- Stoggl & Sperlich 2014, Front Physiol, https://doi.org/10.3389/fphys.2014.00033 [V]
  - 48 well-trained athletes, 9 weeks: polarized group had the largest VO2peak gain (+11.7%) versus threshold, high-intensity, high-volume groups. Mixed sports, short study.
- Disagreement: the "80/20" pattern is descriptive in elites (Seiler); supportive trials are small and short. Coaches' methods differ (see section 3). Treat 80/20 as a common guideline, not a law.

### Tapering

- Mujika & Padilla 2003, MSSE, https://doi.org/10.1249/01.mss.0000074448.73931.11 [V]
  - Keep intensity, cut volume up to 60-90%, cut frequency by no more than 20%; duration 4 to over 28 days; progressive (non-linear) taper beats step taper; performance gain about 3% (range 0.5-6%).
- Bosquet et al. 2007, MSSE meta-analysis, https://doi.org/10.1249/mss.0b013e31806010e0 [V]
  - Best: 2-week taper, volume cut exponentially by 41-60%, no change in intensity or frequency.
- Disagreement: volume cut "up to 60-90%" (Mujika) versus "41-60%" (Bosquet); duration "4 to 28+ days" versus "2 weeks". Not contradictory but ranges differ; both agree: keep intensity, cut volume. These are mostly non-running or mixed endurance samples [U for per-sport breakdown].

### Recovery, overreaching, overtraining

- Meeusen et al. 2013, ECSS/ACSM joint consensus, https://doi.org/10.1249/mss.0b013e318279a10a [V abstract]
  - Distinguishes functional overreaching, non-functional overreaching and overtraining syndrome; says distinguishing the last two is very difficult and depends on clinical outcome; key idea "prolonged maladaptation". Diagnosis is for clinicians: the bot must not diagnose.

### HR, HRV and resting HR

- Buchheit 2014, Front Physiol, https://doi.org/10.3389/fphys.2014.00073 [V]
  - Resting and submaximal HR measures can inform training status; interpret changes against measurement error, smallest important change, and training context.
- Plews et al. 2013, Sports Med, https://doi.org/10.1007/s40279-013-0071-8 [V]
  - In elite athletes, both increases and decreases in HRV have been linked to negative adaptation; interpretation is not straightforward.
- Plews et al. 2012, Eur J Appl Physiol, https://doi.org/10.1007/s00421-012-2354-4 [V]
  - Case study of two triathletes; trends in 7-day rolling HRV average and its variability preceded non-functional overreaching in one. n=2.
- Kiviniemi et al. 2007, Eur J Appl Physiol, https://doi.org/10.1007/s00421-007-0552-2 [V]
  - 26 moderately fit men, 4 weeks: HRV-guided training (hard days only when HRV not below reference) gave larger VO2peak/Vmax gain than a fixed plan. Small, short.
- Bellenger et al. 2016, Sports Med, meta-analysis, https://doi.org/10.1007/s40279-016-0484-2 [V aim only; results truncated, not read]
- Disagreement: HRV-guided training shows benefit in small trials; elite-athlete data are mixed (Plews 2013). No source gives universal HRV or resting-HR cut-offs; use personal baseline and trend (consistent with how COROS words it).

## 3. Coaches and books (candidates, not verified)

All below are [U]: named from general knowledge; I did not open the originals, so the "what it recommends" is intentionally not stated. Owner to add or veto.

- Jack Daniels, *Daniels' Running Formula* (VDOT pace zones, phases).
- Pete Pfitzinger and Scott Douglas, *Advanced Marathoning*.
- Arthur Lydiard (aerobic base building).
- Luke Humphrey / Hansons, *Hansons Marathon Method*.
- Matt Fitzgerald, *80/20 Running* (popularises Seiler's distribution).
- Steve Magness, *The Science of Running*.
- Possible gap: any Vietnamese-language coaches/resources the owner prefers.

Disagreement to expect (to confirm when sources are chosen): polarized/80-20 versus threshold-heavy or marathon-pace-heavy plans; different views on weekly mileage jumps and long-run size [U].

## 4. Copyright and local storage

- Journal abstracts: PubMed/Europe PMC display them, but the abstract text is still the publisher's/authors' copyright. Safe pattern: store own paraphrased notes plus citation (DOI, authors, year) and short quotes only where needed. [U: not a legal opinion]
- Open access: PMC article 4789704 (Gabbett) and Frontiers papers (Buchheit, Stoggl; Frontiers is open access under CC-BY, to be confirmed per paper [U]) allow reuse with attribution under their licence; check each licence before copying text.
- COROS pages: covered by COROS website terms; I did not read them (the terms URL redirected) [U]. Store paraphrased definitions and numbers with links, not copied page text.
- Books: copyrighted. Store only owner-written summaries and page-level citations; do not copy passages. Facts, numbers and ideas are not copyrightable, but expression is.
- Recommended for ticket 16: store short paraphrased "guidance cards" (claim, numbers, source link, confidence, population caveat), not article text.

## 5. Notes for the guardrails (ticket 14 / 16)

- Many numeric rules (ACWR 0.8-1.3, <10% weekly increase) come from team sports or novices and are contested; the bot should flag uncertainty and cite the source.
- Medical: Meeusen says overtraining diagnosis is clinical; keep to "COROS shows X; expert source says Y".
- Cheaper, stronger candidates for rules: taper (Mujika, Bosquet), easy/hard distribution (Seiler), and COROS's own label meanings.
