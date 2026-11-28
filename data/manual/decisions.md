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

## Organizations module (2026-11-25)

- Scope (author): core list of organizations whose mission is GCR broadly or classic GCR (CSER, FHI, GCRI, ALLFED, CLTR, FLI, BERI, Global Challenges Foundation, Global Shield, Existential Risk Observatory, ALTER, Simon Institute, Good Ancestors, Legal Priorities Project) plus teaching / early-career programmes (SERI, CERI/ERA, UChicago XLab, Pivotal, and on the author's request the FernUniversität Hagen graduate programme "Existential Risks to Humanity").
- Budgets (author): public filings and annual reports only; gaps stay blank, no estimates.
- ALLFED budget before 2022 (author: "use annual reports"): no annual report with budget figures found; gap stays.
- Global Shield founding year: 2023, provided by the author (source type "author", no public source found).
- CERI founding year and the CHERI → Pivotal rename date: unknown to the author; left blank.

## Publications (2026-11-25)

- Search term (author): only "global catastrophic risk" on OpenAlex (phrase; OpenAlex stems, so "risks" matches too).
- Scope (author): two series with equal weight: phrase in title or abstract (224 works), and OpenAlex default search incl. full text (2,104 works, also catches passing mentions; full texts are indexed only for part of the literature).
- Topic tags are keyword mentions in title and abstract (data/manual/publication_topics.csv), not a judgment of what a paper is mainly about. Overview papers get several tags.
- OpenAlex without an API key allows only the first page with cursor paging, so page-number paging is used (fine up to 10,000 results). No API key was requested, to avoid sending the author's email.

## Staff functions and organization types (2026-11-25)

- Author: CSER, XLab, SERI and ERA do a lot of teaching; code teaching per person, not per organization.
- Function per person (research / teaching / policy / operations), accepted proposal: CSER "Assistant Professor in Global Risk and Resilience" and "Postgraduate Co-ordinator" → teaching; XLab director and deputy director → teaching, programme/research leads → research; ERA founder, associate director and research managers (who run the fellowship) → teaching; FernUni Hagen programme → teaching; admin, coordination and operations titles → operations; everyone else → the organization's default type (data/manual/org_types.csv). SERI lists no staff.
- Organization type and focus (data/manual/org_types.csv) follow the proposal shown to the author (research: FHI, CSER, GCRI, ALLFED, BERI, LawAI, ALTER; policy: Global Shield, FLI, CLTR, Simon Institute, Good Ancestors, ERO; teaching: XLab, ERA, FernUni). Focus "classic or multi-hazard" vs "AI or bio" follows the Q1 answers.
- ALLFED team page: since 2021 it shows names only (titles are on individual profiles) and does not list volunteers (author pointed this out).
- Two Coefficient grants in non-GCR funds recoded to Classic GCR: Penn State "Research on Emergency Food Resilience" (2020, $3.06M) and ALLFED Australia "Food System Resilience Initiatives" (2026, $343k). Classic GCR 2015-2025 is now $14.1M (0.9 %).

## Staff parsing validation (2026-11-25)

Author asked to validate parsing for all organizations. Each snapshot was scanned for name-like texts not captured by the parser. Fixes: ALTER staff in h6 headings added; FHI director added for 2015 and 2017-2021 via data/manual/team_additions.csv (listed without a readable profile link); BERI's embedded university staff taken from the count stated on its team page (5 in 2021, 6 in 2022, 15 in 2023, 19 in 2024, 15 in 2025; mostly at AI groups) in data/manual/org_staff.csv, not from names. Remaining known misses: CSER, XLab, FLI advisory boards and donors (not staff, by design); Global Shield 2024 country investigators and policy research contractors (not full-time staff); Good Ancestors board list; one ALTER person shown only as an image title.

## ALLFED staff corrections (2026-11-25, human-coded)

Author reviewed the 1 Dec 2025 team page. Still listed but no longer working there (data/manual/team_removals.csv): Laura Cook, Florian Ulrich Jehn, Aron Mill, Martina Kunz and Juan Esteban Lamilla left after the June 2025 cuts (removed from 2026, since the 2025 count uses the 1 July snapshot); Kevin Rassool, Daniel Morgan Rivers and Kyle Alvarado stopped in 2024 (removed from 2025). Ray Taylor is a co-founder who has not worked at ALLFED for years; author: stop counting him from 2024.

## 2026 staff gaps and researcher count (2026-11-25, human-coded)

- CSER, GCRI and BERI have no readable 2026 team page. Author: assume their 2025 teams stayed the same (data/manual/staff_carry_forward.csv; rows marked "assumed same as 2025").
- Author: skip the named list of classic GCR people; give a rough count on the overview page of people doing research at classic or multi-hazard GCR organizations. 2026: about 35 (ALLFED 20, CSER 11, XLab 2, BERI 2, GCRI 1). Generous: includes part-timers, CSER researchers on AI and bio, and everyone on ALLFED's page since it lists no titles.
- CSER researchers mainly on AI or bio move to the "AI or bio" focus in all years (data/manual/team_person_focus.csv): Lalitha Sundaram, Freya Jephcott, Tom Hobson (bio, from CSER profiles) and Shahar Avin (AI, LLM proposal accepted by author). CSER classic researchers 2026: 11 -> 7. Author: the overview count must say it covers only the high-profile organizations (smaller groups and independent researchers excluded, so the real number is likely higher) and that part-timers count as one person.
- ALLFED (author, 2026 page): research = David Denkenberger, Juan B. García Martínez, Farrah Dingal, Michael Hinge, James Mulhall, Rachel Palm, Luísa Lopes Monteiro, Ross Tieman, Alexey Turchin. The other 11 listed people are coded as operations (team_function_rules.csv), in all years they appear.
- CSER 2026 (author): SJ Beard, Lara Mani and Constantin Arnscheidt have left; the other classic researchers are still there or unknown, so kept. Carry-forward now copies people (not totals), so removals apply to carried years.
- ALLFED (author): Noah Wescombe does policy; the other 10 non-researchers are operations, also in earlier years.

## Staff page scope (2026-11-25, author)

- The staff page shows only organizations working on classic or several risks (author: AI growth is well known anyway). The organization list is the author's selection of the main GCR organizations, described on the site as a hand-picked, non-exhaustive list.
- Added on author request: Global Priorities Institute (research, 2018 to end of July 2025, team page 2019-2025) and Riesgos Catastróficos Globales / ORCG (policy, team pages only for 2023 and 2026; 2023 team carried to 2024 and 2025, LLM-coded). RCG co-founder Jaime Sevilla, listed in 2026 only as "Cofundador", is not counted as staff. Juan B. García Martínez appears at both ALLFED and RCG in 2026 and is counted at both.
- Author: the page notes that the shift toward teaching partly reflects the field getting more established and partly more information closer to the present.
- Added on author request: Odyssean Institute (team pages 2023-2026; its AI safety lead moved to the AI or bio focus, LLM-coded), Adapt Research (one person, Matt Boyd, counted from 2020 when the About page names GCR; data/manual/team_additions.csv) and SERI (only archived staff page is Nov 2026: faculty director Stephen Luby as teaching, operations manager). Excluded on author request: Pivotal (only AI) and the Global Challenges Foundation (very little research). The reference bars for total GCR funding were removed again (author: duplicate of the all-GCR view). "Chief of Staff" now counts as operations everywhere.

## Revisions (2026-11-26)

- R1 Good Ancestors Policy (Coefficient 2024 "Global Catastrophic Risks Advocacy", SFF 2024 and 2026): author: "Good Ancestor mostly does AI, classify them as CLTR". General x-risk -> AI. Its staff-page focus was already "AI or bio".
- R2 Effective Institutions Project (SFF 2024-2026 general support): author: "mostly does donor advisement now, reclassify". General x-risk -> EA & community, the same rule as Longview general support (Q12). Coefficient's 2024 "AI Governance Work" grant stays AI (stated purpose).
- Source URL of Coefficient grant 36537 (ALLFED Australia, "Food System Resilience Initiatives", 2026): the URL in Coefficient's own index does not load (reported by the author). Overridden in data/manual/source_url_overrides.csv to the grant database; the correct page could not be checked because the site blocks scripts.

## Naming and scope (2026-11-26)

- Author: "classic GCR" confuses readers (it suggests these were the original GCRs, while AI and bio were central from the start). Renamed everywhere (data, code, site, README) to "Nuclear, natural & resilience": nuclear war, volcanoes, asteroids, space weather, and keeping food systems and infrastructure running in a catastrophe. The rest of this log keeps the old name where it was used at the time.
- New umbrella "GCR outside AI and bio" = Nuclear, natural & resilience + General x-risk + Climate + Geoengineering. It only counts GCR-framed work; mainstream climate, nuclear security and disaster risk reduction funding are out of scope by design. The funding page and overview default to the umbrella.
- What the renamed category holds in practice (2015–2025, $14.1M, 27 grants, 96 % research): nuclear winter impact research $7.1M, food and infrastructure resilience $6.0M, space weather $0.5M, nuclear prevention only Longview's $0.5M regrant, volcanoes and asteroids nothing.
- Staff focus "classic or multi-hazard" renamed "beyond AI and bio".
- Global Priorities Institute removed from the staff page (author: "they mostly did longtermism, which is related, but not actually what I want to argue for here"); org_types focus set to "global priorities", data kept. FHI stays (author: "it was much more central than GPI to many GCR ideas").

## SFF matching pledges (2026-11-26)

- Prompted by Juan García Martínez's comments (SFF numbers lower than his own counts). Author: "Include the matching pledges". SFF matching pledges (‡) are now counted in amount_usd and still shown in matching_pledge_usd; leaving them out is a sensitivity scenario. Effect: SFF 2025 $24.9M -> $34.3M (Juan's count: $34.2M), 2026 $54.1M -> $63.1M; almost all pledges go to AI, so GCR outside AI and bio changes by $0 in 2015–2025 and +$0.18M in 2026.
- Other differences to Juan's counts, not changed: (a) the narrow default view he saw (ALLFED only) is replaced by "GCR outside AI and bio"; (b) he counts CLTR, Simon Institute, Oxford China Policy Lab, Langsikt and Good Ancestors as GCR policy, here they are AI or AI/bio by author decision (Q1, R1); counting them half or fully as General x-risk would raise GCR outside AI and bio 2015–2025 from $69.5M to $77.5M or $85.4M (4.4 % -> 4.9 % or 5.4 %); (c) ALLFED SFF 2023-H2 $164k and an extra $10k in 2025 are not on SFF's public recommendations page; to be added only with a public source.
- R3 Oxford China Policy Lab (SFF 2022–2026, counted by Juan as GCR policy): author: "seems pretty AI heavy on first glance". Stays AI, now human-coded.
- Later the same day the author renamed the category again, from "Nuclear, natural & resilience" to "Abrupt sunlight reduction & infrastructure collapse" (author: "loss is not correct"; named after how these catastrophes do harm, as in ALLFED's abrupt sunlight reduction and global catastrophic infrastructure loss). Pandemics stay under Bio even though they can also disrupt infrastructure.
- Author: the funding page defaults to abrupt sunlight reduction & infrastructure collapse (split by funder); the overview keeps GCR outside AI and bio.

## Forecasting out of GCR (2026-11-26)

- Author: "I don't think it makes sense to put forecasting as a whole under the GCR label." Forecasting (Q7) stays its own category but is now excluded from GCR totals and gets no activity code, like EA & community; it is shown only in the "Everything" view. Counting it as GCR is now the Q7 sensitivity scenario. Effect 2015–2025: GCR total $1.6B -> $1.5B, GCR outside AI and bio 4.4 % -> 4.5 %, AI share 2025 84 % -> 86 %. Activity rules used only for forecasting grants were deleted (Good Judgment, Manifold Markets, Metaculus, QURI, Rootclaim, Social Science Prediction Platform; LTFF grants to Samotsvety and for Metaculus).

## Topic definitions are definitions only (2026-11-27)

- Author: the "What the topics mean" list on the funding page works like a legend, so it says only what each topic covers and never where the money went. Abrupt sunlight reduction & infrastructure collapse uses the same wording as the overview.

## 2026-11-28 – Odyssean Institute off the staff page

- Removed on author request from the staff data and page (team page config, role rules, person focus, org type, organization row and its rows in `team_people_raw.csv`). Its grants stay in the funding data.
