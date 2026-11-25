# Data

- `raw/`: untouched downloads, dated so results can be reproduced from the same snapshot: Coefficient Giving's Algolia JSON, the SFF recommendations table, EA Funds JSON (LTFF), FLI programme pages, ProPublica Form 990 JSON and the OpenAlex results. Wayback Machine snapshots of team pages are cached in `raw/wayback/` but not committed (about 30 MB); `src/team_pages.py` downloads them again.
- `processed/`: tidy tables made by the code in `src/`.
  - `coefficient_giving_grants.csv`, `sff_grants.csv`, `ltff_grants.csv`, `fli_grants.csv`: one row per grant.
  - `grants_classified.csv`: all funders with hazard category and activity, each with coding source, confidence and rationale. `grants_by_category.csv`: the same, with split grants once per category.
  - `org_finances_990.csv`: Form 990 revenue and expenses.
  - `team_people_raw.csv`: everyone found on archived team pages. `team_people.csv`: the same after hand corrections, with role, function and focus. `staff_by_year.csv` and `staff_by_function.csv`: the counts.
  - `publications.csv`, `publication_authors.csv`, `publications_by_year.csv`: OpenAlex works.
- `manual/`: everything decided by hand: grant codes, activity rules, organization facts, staff page configuration, role and function rules, person-level corrections, and the decision log `decisions.md` with every question to the author and the answer.
- `border.geojson`: Winkel Tripel map border for map plots (see `CLAUDE.md`).
