# Update Repo About

Keep the GitHub repository metadata up to date.

## Description

Scraper automat pentru locurile de muncă DANNY COM ALS SRL (CIF: 03213771) — extrage
de pe mediere.anofm.ro și publică pe peviitor.ro

## Homepage

https://peviitor-scrapers.github.io/danny-com-als-srl-python-scraper/

## Topics (exactly 2, per TOPICS.md)

- job-seeker-ro-spider
- peviitor-ro

## Workflow file

`.github/workflows/job-seeker-ro-spider.yml`

## How to apply

```bash
gh repo edit peviitor-scrapers/danny-com-als-srl-python-scraper \
  --description "Scraper automat pentru locurile de muncă DANNY COM ALS SRL (CIF: 03213771) — extrage de pe mediere.anofm.ro și publică pe peviitor.ro" \
  --homepage "https://peviitor-scrapers.github.io/danny-com-als-srl-python-scraper/"
```

## GitHub Pages

- Source: branch `main`, path `/docs` (static site, no Pages workflow needed).
- Builds automatically on every push to `main` (`build_type: legacy`).
- Site: https://peviitor-scrapers.github.io/danny-com-als-srl-python-scraper/
- `docs/jobs.md` is regenerated on each scrape and served on the site.
- Homepage on the repo points to the Pages URL (same as the EPAM template).
