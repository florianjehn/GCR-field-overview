Raw input data for the project. Generally not synced to version control unless files are small and text-based (< 10 MB).

Included in this template:
- `border.geojson` — Winkel Tripel map border, used for published map plots.

## Grant data

- `raw/`: untouched downloads, dated (Coefficient Giving Algolia JSON, SFF HTML).
- `processed/coefficient_giving_grants.csv`, `processed/sff_grants.csv`: one row per grant/recommendation (`src/coefficient_grants.py`, `src/sff_grants.py`).
- `manual/`: hand classification (`*_manual_codes.csv`) and the decision log (`decisions.md`).
- `processed/grants_classified.csv`: all funders combined with category, coding source and confidence (`src/classify_grants.py`).
