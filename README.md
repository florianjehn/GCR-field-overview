# GCR Field Overview

How has the field of global catastrophic risk (GCR) research developed over the last ten years or so? This repo tracks who funds it, how much, for which hazards and for which kind of work. I want numbers that are solid and easy to check, so every grant links to its public source and every classification records who made it and why.

It covers grant funding from four funders, the main GCR organizations (founding, closure, budgets where public), staff listed on their team pages over time, and publications in OpenAlex. An interactive site in `docs/` lets you explore all of it.

## Quick start

```bash
uv sync
uv run python3 -m src.coefficient_grants   # download Coefficient Giving grants
uv run python3 -m src.sff_grants           # download SFF recommendations
uv run python3 -m src.ltff_grants          # download LTFF grants
uv run python3 -m src.fli_grants           # download FLI grants
uv run python3 -m src.classify_grants      # classify everything -> data/processed/
uv run python3 -m src.sensitivity          # robustness of headline numbers -> results/
uv run python3 -m src.org_finances         # Form 990 revenue/expenses (ProPublica)
uv run python3 -m src.team_pages           # people on archived team pages (Wayback Machine)
uv run python3 -m src.staff_counts         # roles and staff counts per year
uv run python3 -m src.publications         # OpenAlex works mentioning "global catastrophic risk"
uv run python3 -m src.build_site           # export JSON for the site in docs/
uv run python3 -m src.scope_figure         # figure of what the categories cover -> results/figures/
uv run pytest
```

Downloads are dated (`data/raw/`) so results can be reproduced from the same snapshot.

## Data sources

| Funder | Source | Grants | Years | Notes |
|---|---|---|---|---|
| Coefficient Giving (formerly Open Philanthropy) | Public Algolia search index behind [coefficientgiving.org/funds](https://coefficientgiving.org/funds/) (the site has no CSV export and blocks scripts; the index is what every browser loads) | 3,067 | 2012–2026 | Complete per the index's own counts. Each grant links to its page. |
| Survival and Flourishing Fund (SFF) | [survivalandflourishing.fund/recommendations](https://survivalandflourishing.fund/recommendations) | 586 | 2019–2026 | Recommendations, not confirmed payouts. Matching pledges (‡, paid only if the recipient raises matching funds) are counted in the amounts since 2026-11-26 and also shown separately in `matching_pledge_usd`. Sum $214M ≈ SFF's own "~$216MM". |
| Long-Term Future Fund (LTFF) | JSON embedded in [funds.effectivealtruism.org/grants](https://funds.effectivealtruism.org/grants) | 700 | 2017–2026 | Published grants only; totals are a lower bound (e.g. 2023: $5.2M here vs. higher reported payouts). |
| Future of Life Institute (FLI) | [futureoflife.org/grant-program/…](https://futureoflife.org/our-work/grantmaking-work/) programme pages | 147 | 2015–2025 | Yearly pages "highlight some" grants, so a lower bound. Some award years are inferred (`data/manual/fli_programs.csv`). |

## How grants were classified

Every grant gets two labels:

- Hazard category: AI, Bio, Abrupt sunlight reduction & infrastructure collapse (catastrophes that block out the sun or knock out infrastructure: nuclear war, large volcanic eruptions, asteroids, space weather, plus food and infrastructure resilience; called "Classic GCR" until 2026-11-26), General x-risk (cross-cutting), Geoengineering, Climate, Forecasting, plus categories excluded from GCR totals: EA & community, Not GCR, Regrant (money passed to another fund whose grants are counted there), Duplicate (same money already counted under another funder) and Unknown. A grant can be split, e.g. `AI=0.5;Bio=0.5`.
- Activity (GCR-relevant grants only): Research, Policy & advocacy, Field-building & education, Other (operations, media, regranting), Unknown. The website calls grants outside the GCR categories or with unknown activity "Unknown/not assessed".

Each label carries a coding source (`funder-label`, `LLM-coded`, `human-coded`), a confidence and a rationale, in `data/processed/grants_classified.csv`. For the hazard category, 2,707 grants follow the funder label, 1,406 are LLM-coded and 387 human-coded. For the activity, 2,047 are LLM-coded and 174 human-coded.

### Steps

1. Funder labels first. Coefficient's own funds are used where they are unambiguous: "Navigating Transformative AI" → AI, "Biosecurity & Pandemic Preparedness" (and its science sub-fund) → Bio, non-GCR funds (animal welfare, global health, …) → Not GCR. One grant filed by the funder under AI but clearly about farm animals was corrected.
2. Hand coding where labels are not enough. Coefficient's "Global Catastrophic Risks Opportunities" fund turned out to be mostly EA/longtermist community building, so all 352 grants in it (plus Forecasting and Other Areas) were coded one by one from title and recipient. All 390 SFF organizations were coded by organization (SFF grants are almost all "general support"), with a purpose-level override where the stated purpose differs (e.g. flexHEG prototyping → AI) and the dedicated SFF-2024-FlexHEGs round → AI. All 700 LTFF grants were coded from their descriptions (keyword defaults, then about 130 hand corrections after reading every description). All 147 FLI grants were coded by hand.
3. Questions to the author whenever unsure. Every grant where the coding was not clearly right got a question id instead of a silent guess. Questions were asked one by one in the chat; answers and the reasoning are logged verbatim in [`data/manual/decisions.md`](data/manual/decisions.md), and affected rows switched to `human-coded`. Questions asked:
   - Q1–Q12 (hazard categories): multi-hazard organizations (CSER, FHI, CLTR, GCRI, …), FLI general support, student x-risk programmes, climate and geoengineering, global priorities research, regranting, forecasting, the rationality community, outreach media, mixed AI/bio field-building, Longview, and about 20 individual organizations with unclear focus (the rest left Unknown at the author's request).
   - A1–A6 (activity): policy think tanks, mixed-mission organizations (Blueprint, Mirror Biology Dialogues Fund, CAIS, SL5 Task Force), evals/demonstration groups (Apollo, Palisade, Sage), and organizations with unknown activity.
   - FLI/LTFF: FLI–SFF double counting, F1–F2 (two FLI programmes), L1–L3 (eight LTFF grants).
4. Rules carried over without asking. Once the author answered a question, the same rule was applied to equivalent grants at other funders (e.g. student x-risk programmes → General x-risk; CFAR/rationality → EA & community). These are listed at the end of `decisions.md`.
5. Activity coding. Ordered keyword rules on grant titles ([`data/manual/activity_rules.csv`](data/manual/activity_rules.csv)), then recipient defaults for "general support" grants ([`activity_recipient_codes.csv`](data/manual/activity_recipient_codes.csv)), then grant-level overrides ([`activity_grant_overrides.csv`](data/manual/activity_grant_overrides.csv)). Every keyword match was reviewed by hand; misfires (e.g. "rare *event*", "*policy* network", "AI governance *work*shop") led to rule fixes or overrides, and each fix was checked by diffing all grants before and after. A title stating research is coded Research even at think tanks.
6. Double counting. Money that passes through two funders is counted once: Coefficient and SFF grants to LTFF/EA Funds and other regranting funds are marked Regrant; Coefficient's 2015 grant to FLI's AI programme is marked Regrant because FLI's individual grants are included; FLI's 2023 grants that are FLI's share of SFF recommendations are marked Duplicate.
7. Sensitivity analysis ([`src/sensitivity.py`](src/sensitivity.py), [`results/sensitivity.csv`](results/sensitivity.csv)): each decision is replaced by its main alternative and the headline numbers recomputed. See below.

### Where to check a number

- A grant: its `source_url` in `data/processed/grants_classified.csv` (Coefficient links to the individual grant page; SFF, LTFF and FLI link to the list page; search for the recipient).
- Why it has its category: `coding_source`, `rationale` and `question_id` in the same file; the question and the author's answer in `data/manual/decisions.md`.
- Funding totals by category: `data/processed/grants_by_category.csv` (split grants appear once per category with `amount_usd_share`).
- That nothing got lost on the way: `tests/test_data_integrity.py` checks that the processed Coefficient and LTFF tables add up to the raw downloads, that every hand code is applied, and that the site data has every grant with an amount (one Coefficient investment, Impossible Foods 2016, has no stated amount).

## Robustness of the headline numbers

Headline metrics over 2015–2025 (nominal USD, Coefficient + SFF + LTFF + FLI, excluding EA & community, Not GCR, Regrant, Duplicate):

| Scenario | Abrupt sunlight reduction & infrastructure collapse total ($M) | Its share of GCR funding | All GCR outside AI and bio per year 2023–25 ($M) | AI share 2025 |
|---|---|---|---|---|
| Baseline | 14.1 | 0.9 % | 5.6 | 84 % |
| Multi-hazard orgs (CSER, FHI, GCRI, …) counted as abrupt sunlight reduction & infrastructure collapse | 38.4 | 2.4 % | 5.6 | 84 % |
| Climate + geoengineering counted as abrupt sunlight reduction & infrastructure collapse | 30.3 | 1.9 % | 5.6 | 84 % |
| All Unknown money assumed abrupt sunlight reduction & infrastructure collapse | 36.3 | 2.3 % | 9.7 | 84 % |
| All three together (most generous) | 76.8 | 4.8 % | 9.7 | 84 % |
| Longview general support counted as General x-risk | 14.1 | 0.9 % | 12.6 | 84 % |
| Student x-risk programmes counted as EA & community | 14.1 | 0.9 % | 3.0 | 84 % |
| Global priorities research counted as General x-risk | 14.1 | 0.9 % | 7.6 | 83 % |
| Generic forecasting counted as Not GCR | 14.1 | 0.9 % | 5.6 | 86 % |
| SFF matching pledges left out (the default before 2026-11-26) | 14.1 | 0.9 % | 5.6 | 83 % |

The remaining alternatives (FLI split, regrants, Lightcone, media, mixed field-building, 50/50 splits, FLI duplicates) change no metric by more than about half a percentage point (largest: mixed field-building split 50/50, AI share 2025 −0.5 points) and leave the yearly non-AI, non-bio amount unchanged; full table in `results/sensitivity.csv`.

So the choices do matter for how big the small categories are. The abrupt sunlight reduction & infrastructure collapse total moves by up to ~5× ($14M to $77M), and the yearly amount for all GCR outside AI and bio in 2023–25 ranges from $3.0M to $12.6M, depending on whether student programmes and Longview count. They don't change the overall picture, though. Even in the most generous reading abrupt sunlight reduction & infrastructure collapse gets under 5 % of GCR philanthropy, while AI gets over 80 % in 2025.

## Organizations and staff

- `data/manual/organizations.csv` and `org_events.csv`: founding and closure dates and key events for the core organizations, each with a source and whether it is primary, secondary or provided by the author.
- `data/processed/org_finances_990.csv`: revenue and expenses from US Form 990 filings (FLI, BERI, ALLFED Institute). `data/manual/org_finances_manual.csv` and `org_staff.csv`: figures from reports and UK company filings (e.g. CLTR's average employees from Companies House, FHI's budget and staff from its final report and Open Philanthropy's 2014 conversation notes).
- Staff per year: one archived snapshot per year of each team page (closest to 1 July). `data/manual/team_pages.csv` says how names are found on each site, `team_role_rules.csv` maps section names and job titles to roles (staff, scholar, student, volunteer, affiliate, board, alumni). Every person row links to its snapshot. Team pages are not payrolls: they list part-timers and sometimes volunteers, and layout changes can look like hires or cuts (e.g. GCRI stopped listing associates in 2019).
- Scope of the staff page: the author's hand-picked list of main GCR organizations working beyond AI and bio (FHI, CSER, GCRI, ALLFED, BERI, Odyssean Institute, Adapt Research, Global Shield, Riesgos Catastróficos Globales, XLab, SERI, FernUni Hagen programme). AI- or bio-focused organizations are still in the data (`staff_by_function.csv`) but not shown.
- Function per person (research, teaching, policy, operations) in `data/processed/staff_by_function.csv`: org-specific and generic title rules in `data/manual/team_function_rules.csv` (e.g. CSER's MPhil teaching posts, admin titles as operations), otherwise the organization's type in `data/manual/org_types.csv`, which also sets its focus (beyond AI and bio vs AI or bio; the Global Priorities Institute has its own focus, global priorities, and is left off the staff page).
- Manual corrections: `team_additions.csv` adds people the parser can't read (FHI's director 2015–2021, Adapt Research, SERI's 2026 staff page), `team_removals.csv` drops people the author knows had left although still listed (ALLFED, CSER). `staff_carry_forward.csv` copies a team to years without a readable page (CSER, GCRI and BERI 2025 → 2026 on the author's instruction; Riesgos Catastróficos Globales 2023 → 2024 and 2025), marked "assumed same as …". `team_person_focus.csv` moves people who mainly work on AI or bio (four at CSER, Odyssean's AI safety lead) to the AI or bio focus. ALLFED's page has no job titles, so the author named who does research (`team_function_rules.csv`). BERI's embedded university staff come from the count stated on its team page.
- Parsing was validated by scanning every snapshot for name-like text the parser missed; what is still not captured is mainly boards, advisors, donors and contractors (details in `data/manual/decisions.md`). `tests/test_data_integrity.py` checks on every run that each manual correction names a real person, that no role or function rule is dead, and that removals were applied.

## Publications

`src/publications.py` downloads all OpenAlex works with the phrase "global catastrophic risk" (plurals match), in two scopes with equal weight: in title or abstract (224 works), and anywhere including full text (2,104 works). Ten works have no publication year in OpenAlex, so the yearly series add up to 223 and 2,095. Topic mentions (AI, bio, nuclear, volcanic, space, food, climate) are keyword matches in title and abstract.

## Interactive site

`docs/` is a static GitHub Pages site (see `docs/README.md`). The funding page defaults to abrupt sunlight reduction & infrastructure collapse, the overview to GCR outside AI and bio (that category plus general x-risk and climate & geoengineering). To publish it: repository Settings → Pages → Deploy from branch `main`, folder `/docs`.

## Known gaps

- Only four philanthropic funders; government and academic funding are not included.
- LTFF and FLI publish only part of their grants; SFF publishes recommendations, not payouts.
- 2026 is partial (to November) and recent years are affected by publication lags.
- Amounts are nominal USD (no inflation adjustment yet).
- Staff counts come from team pages of a hand-picked set of organizations; pages list part-timers, lag behind hires and departures, and some years have no archived page.

## Repository layout

```
data/raw/          dated raw downloads
data/processed/    tidy grant tables and classified outputs
data/manual/       hand codes, rules and the decision log
results/           analysis outputs (sensitivity table)
docs/              interactive site (GitHub Pages)
src/               download, classification and analysis code
tests/             pytest suite
style/             matplotlib style sheet
```

Coding conventions are in [`CLAUDE.md`](CLAUDE.md). License: [Apache 2.0](LICENSE).
