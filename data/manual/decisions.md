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
| Q1 | Multi-hazard GCR organisations (CSER, FHI, BERI general, CLTR, ALTER, Global Shield, Good Ancestors, Pour Demain, Langsikt, Simon Institute, APPG Future Generations, Legal Priorities Project, Macrostrategy Research Initiative, Odyssean, Sentinel, Millennium Project, Haydn Belfield; Existential Risk Observatory proposed AI) | General x-risk | pending |
| Q1b | GCRI general support | General x-risk (alternative: Classic GCR) | pending |
| Q2 | Future of Life Institute general support (Coefficient 2016-2020, SFF 2019-2021) | ? (AI or General x-risk) | pending |
| Q3 | Student / early-career x-risk programmes (SERI, CERI, XLab, ERA, Pivotal, GCP, Condor Camp, Effisciences, x-risk courses, Precipice essay contest, GCR scholarships, RP XST) | General x-risk (alternative: EA & community) | pending |
| Q4 | Climate and solar geoengineering grants (SRMGI/Degrees Initiative, Harvard SGRP, UCLA, FCEA, American U., Climate Overshoot Commission, Kigali Cooling, Ann Garth) | ? (Classic GCR or Not GCR) | pending |
| Q5 | Global priorities research (GPI, Forethought Foundation 2023, RP Worldview Investigations) | ? (General x-risk or EA & community) | pending |
| Q6 | Regranting to other funds (EA Funds LTFF/EAIF, AI Risk Mitigation Fund, Manifund) | Keep but flag; exclude from totals once LTFF grants are added to avoid double counting | pending |
| Q7 | Generic forecasting (Metaculus, FRI general, Tetlock, ARLIS, RAND platform, QURI, Manifold, Rootclaim, Sage) | Not GCR | pending |
| Q8 | Rationality community (CFAR, LessWrong, Lightcone general, FABRIC, rationality meetups, Zvi Mowshowitz) | EA & community (alternative: AI) | pending |
| Q9 | Outreach media (Kurzgesagt, Rational Animations, Should We Studio, Good Impressions, COVID documentary) | ? | pending |
| Q10 | Mixed AI/bio field-building (BlueDot, Meridian, Future Impact Group, Successif, Collider, Trajectory Labs, Impact Academy, Nonlinear) | AI | pending |
| Q11 | Individual organisations with unclear focus (list in chat / manual code files) | Unknown | pending |
| Q12 | Longview Philanthropy general support | ? | pending |
