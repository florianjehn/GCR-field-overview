# Interactive site

Static GitHub Pages site (plain HTML, CSS and D3 7.9.0 from jsDelivr), built from the repository data.

- `index.html`: overview with headline numbers
- `funding.html`: grants by year, split and filtered by funder, topic and kind of work (default: classic GCR)
- `staff.html`: people on archived team pages per organization and year (default: classic and multi-hazard organizations)
- `publications.html`: OpenAlex works mentioning "global catastrophic risk" (default: works mentioning classic hazards)
- `data/*.json`: exported by `uv run python3 -m src.build_site`; rerun it after the data changes
- `assets/`: shared styles (`site.css`) and scripts

Preview locally with `python3 -m http.server -d docs` and open http://localhost:8000.
