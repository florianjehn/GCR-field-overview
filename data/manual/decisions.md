# Classification decisions

Log of category questions and the author's answers. Every grant affected by a
question carries its `question_id` in `data/manual/*_manual_codes.csv` and in
`data/processed/grants_classified.csv`. Once answered, affected rows switch
from `coding_source = LLM-coded` (confidence `low`) to `human-coded`.

## Categories

| Category | Meaning |
|---|---|
| AI | Risks from advanced AI: alignment, governance, evals, AI-specific field-building |
| Bio | Biosecurity and pandemic preparedness |
| Classic GCR | Non-AI, non-bio hazards: nuclear war/winter, volcanic, space weather, food resilience, asteroids, etc. |
| General x-risk | Cross-cutting work on several GCRs (multi-hazard institutes, x-risk policy) |
| EA & community | EA/rationality community building, effective giving, careers advice (excluded from GCR totals) |
| Not GCR | Outside GCR (global health, animal welfare, science, longevity, governance reform) |
| Unknown | Open question, not yet resolved |

## Coding sources

- `funder-label`: follows the funder's own fund (Coefficient Giving AI fund -> AI, Biosecurity fund -> Bio, other non-GCR funds -> Not GCR).
- `LLM-coded`: assigned by Claude from title, recipient and stated purpose. `confidence = high` means no question was raised.
- `human-coded`: confirmed or set by the author (answers below).

## Questions (asked 2026-11-25)

| ID | Question | Proposed default | Answer |
|---|---|---|---|
| Q1 | Multi-hazard GCR organizations (CSER, FHI, BERI general, CLTR, ALTER, Global Shield, Good Ancestors, Pour Demain, Langsikt, Simon Institute, APPG Future Generations, Legal Priorities Project, Macrostrategy Research Initiative, Odyssean, Sentinel, Millennium Project, Haydn Belfield; Existential Risk Observatory proposed AI) | General x-risk | answered, see below |
| Q1b | GCRI general support | General x-risk (alternative: Classic GCR) | answered, see below |
| Q2 | Future of Life Institute general support (Coefficient 2016-2020, SFF 2019-2021) | ? (AI or General x-risk) | answered, see below |
| Q3 | Student / early-career x-risk programmes (SERI, CERI, XLab, ERA, Pivotal, GCP, Condor Camp, Effisciences, x-risk courses, Precipice essay contest, GCR scholarships, RP XST) | General x-risk (alternative: EA & community) | answered, see below |
| Q4 | Climate and solar geoengineering grants (SRMGI/Degrees Initiative, Harvard SGRP, UCLA, FCEA, American U., Climate Overshoot Commission, Kigali Cooling, Ann Garth) | ? (Classic GCR or Not GCR) | answered, see below |
| Q5 | Global priorities research (GPI, Forethought Foundation 2023, RP Worldview Investigations) | ? (General x-risk or EA & community) | answered, see below |
| Q6 | Regranting to other funds (EA Funds LTFF/EAIF, AI Risk Mitigation Fund, Manifund) | Keep but flag; exclude from totals once LTFF grants are added to avoid double counting | answered, see below |
| Q7 | Generic forecasting (Metaculus, FRI general, Tetlock, ARLIS, RAND platform, QURI, Manifold, Rootclaim, Sage) | Not GCR | answered, see below |
| Q8 | Rationality community (CFAR, LessWrong, Lightcone general, FABRIC, rationality meetups, Zvi Mowshowitz) | EA & community (alternative: AI) | answered, see below |
| Q9 | Outreach media (Kurzgesagt, Rational Animations, Should We Studio, Good Impressions, COVID documentary) | ? | answered, see below |
| Q10 | Mixed AI/bio field-building (BlueDot, Meridian, Future Impact Group, Successif, Collider, Trajectory Labs, Impact Academy, Nonlinear) | AI | answered, see below |
| Q11 | Individual organizations with unclear focus (list in chat / manual code files) | Unknown | answered, see below |
| Q12 | Longview Philanthropy general support | ? | answered, see below |

## Answers (2026-11-25, given one by one in chat)

### Q1 – Multi-hazard GCR organizations
- CLTR / Alpenglow: AI ("pure AI").
- Pour Demain: 50 % AI / 50 % Bio ("only does AI and Bio").
- Langsikt (Centre for Long-Term Policy): 50 % AI / 50 % Bio ("only does AI and Bio, and some animal welfare").
- ALTER: 50 % AI / 50 % Bio (author asked for a link; ALTER site lists NIST AI Safety Institute Consortium and WHO pathogen surveillance network memberships; author chose the 50/50 rule for AI+Bio orgs).
- Simon Institute for Longterm Governance: AI.
- Legal Priorities Project: AI (successor is the Institute for Law & AI).
- Macrostrategy Research Initiative: Unknown ("page links to something different, scrap as unclear").
- Millennium Project: Not GCR ("does not seem to do GCR work at all").
- Haydn Belfield: AI ("pure AI by now").
- All others in Q1 (FHI, CSER, BERI general and CSER/FHI collaborations, Global Shield, Good Ancestors, APPG Future Generations, Odyssean, Sentinel): General x-risk confirmed. Existential Risk Observatory stays AI (not objected to).
- Rule: organizations working only on AI and Bio are split 50/50 between AI and Bio.

### New dimension: activity
- Author: "split this generally into funding for Research and funding for Policy, as these two will likely look very very different."
- Each grant gets an `activity`: Research / Policy & advocacy / Field-building & education / Other (operations, media, regranting).

### Q1b – GCRI
- General x-risk.

### Q2 – Future of Life Institute general support
- 50 % AI / 50 % General x-risk.

### Q3 – Student / early-career x-risk programmes
- General x-risk (activity: Field-building & education).

### Q4 – Climate and geoengineering
- Author: "New Climate and new Geoengineering category. Those should be separate."
- Geoengineering: SRMGI / Degrees Initiative, Harvard Solar Geoengineering Research Program, UCLA climate engineering governance, Forum for Climate Engineering Assessment, American University Solar Geoengineering Initiative.
- Climate: Kigali Cooling Efficiency Program, Global Commission on Governing Risks from Climate Overshoot (broad remit beyond SRM), Ann Garth climate change research.

### Q5 – Global priorities research
- EA & community (GPI, Forethought Foundation 2023, RP Worldview Investigations).

### Q6 – Regranting to other funds
- Flag as regrant and exclude from funding totals (Coefficient -> EA Funds; SFF -> LTFF, EAIF, AI Risk Mitigation Fund, Manifund). Category set to the receiving fund's focus for reference only.

### Q7 – Generic forecasting
- New Forecasting category for generic forecasting (Metaculus, FRI incl. general support, Tetlock/Penn, ARLIS, RAND platform, Swift Centre, QURI, FutureSearch, Manifold, Rootclaim, SSPP, Mantic, OPTIC, IISS, CEPR, Good Judgment AI question tool).
- Sage: 2024 "Software Tools for Forecasting" -> Forecasting; Coefficient 2025 general support and SFF grants -> AI.

### Q8 – Rationality community
- EA & community for all (CFAR, LessWrong, Lightcone general support, FABRIC, rationality meetups, Zvi Mowshowitz, Elizabeth Van Nostrand, Coordination Project). Lightcone flexHEG grant stays AI (stated purpose).

### Q9 – Outreach media
- Unknown (Kurzgesagt, Rational Animations, Should We Studio, Good Impressions, COVID documentary).

### Q10 – Mixed AI/bio field-building
- AI (BlueDot, Successif, Meridian, Future Impact Group, Trajectory Labs, Collider, Impact Academy, Nonlinear).

### Q12 – Longview Philanthropy general support
- EA & community.

## Activity questions (2026-11-25)

Activities: Research / Policy & advocacy / Field-building & education / Other (operations, media, regranting) / Unknown. Precedence: grant override > keyword rule on title (`activity_rules.csv`) > recipient default (`activity_recipient_codes.csv`).

- A1 – Policy think tanks (CSET, JHU CHS, IAPS, RAND general, NTI bio, Georgetown GHSS, Carnegie, CNAS, CIGI, CASA, RP AI governance team, Brown AI Governance Lab, Oxford Martin AIGI, CSIS, IST): Policy & advocacy for all, including university-based centres. Grants whose title states research stay Research.
- A2 – Mixed-mission organizations: Blueprint Biosecurity general support Other; Mirror Biology Dialogues Fund Policy & advocacy; Center for AI Safety general support Research; SL5 Task Force Policy & advocacy; FLI general support Policy & advocacy, iGEM Policy & advocacy, ORCG AI Risk Explorer Research, Renaissance BiTS accelerator Field-building, Good Forever Other (proposals accepted).
- A3 – Evals/demonstrations: Apollo Research Research; Palisade Research Policy & advocacy; Sage general support Other.
- A4 – Unknown-activity organizations: AI Alignment Foundation Policy & advocacy; Active Site Research and Oath Technologies Research.
- A5 – Smaller SFF organizations: proposals accepted (EIP Policy, Foresight Field-building, Collective Intelligence Project Research, Legal Safety Lab Policy, SaferAI Policy, Sentinel Research, Odyssean Research).
- A6 – Organizations with unknown focus: activity left Unknown.

## LTFF and FLI (2026-11-25)

- FLI–SFF overlap: FLI's "2023 Grants" page lists FLI's share of grants recommended through SFF's 2023 rounds (several amounts identical, SFF lists "FLI and Jaan Tallinn" as source). Author decision: the 13 FLI 2023 grants to organizations with an SFF 2023 recommendation at least as large are marked Duplicate and excluded from totals. Kept: Center for Humane Technology, Foresight Institute, UC Berkeley AI Policy Hub.
- Coefficient → FLI 2015 ("Artificial Intelligence Risk Reduction", $1.19M) funded FLI's 2015 AI safety programme, whose individual grants are in the FLI data: marked Regrant (Q6 rule).
- F1 USC Hollywood, Health & Society (FLI 2022, $170k): General x-risk / Other (proposal accepted).
- F2 FLI call on AI's impact on SDGs (2024, 10 × $15k): Not GCR (proposal accepted).
- L1 LTFF Joel Becker, forecasting and pandemics (2021, $42k): Forecasting (proposal accepted).
- L2 LTFF SHELTER Weekend civilisational resilience (2022, $27k): Classic GCR; Will Aldred nuclear risk + AI strategy (2022, $40k): 50 % Classic GCR / 50 % AI (proposals accepted).
- L3 Five LTFF grants coded AI from context (Coleman Snell research grant, PhD relocation, three cybersecurity trainings): AI (proposal accepted).
- Rules applied without asking, following earlier answers: CHERI/CERI/SERI student programmes → General x-risk (Q3); CFAR, SPARC, rationality → EA & community (Q8); LPP → AI (Q1); MRI → Unknown (Q1); Foresight → 50 % AI / 50 % Bio (Q11.6); generic forecasting → Forecasting (Q7).
