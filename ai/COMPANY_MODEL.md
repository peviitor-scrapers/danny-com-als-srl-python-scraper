# Company Model

Company document published to the peviitor company core (`/v1/firme/company/`).

## Source of truth

`scraper/config/company.json` — never edit other copies; they are generated.

## Fields

| Field        | Type   | Description                                                        |
|--------------|--------|--------------------------------------------------------------------|
| `id`         | string | CIF (8 digits, no RO prefix)                                       |
| `company`    | string | Legal name from Trade Register (UPPERCASE, diacritics required)    |
| `brand`      | string | Public brand name                                                  |
| `group`      | string | Parent company group (optional)                                    |
| `status`     | string | `activ` / `suspendat` / `inactiv` / `radiat`                       |
| `location`   | array  | Romanian cities/addresses (diacritics accepted)                    |
| `website`    | array  | Company website (canonical HTTP/HTTPS URL)                         |
| `career`     | array  | Careers/board URL (canonical HTTP/HTTPS URL)                       |
| `lastScraped`| string | Date of last scrape (ISO 8601)                                     |
| `scraperFile`| string | GitHub Actions workflow URL (no raw)                               |

## Notes

- Fields marked `array` are multi-valued arrays stored as arrays in SOLR.
- `status = "activ"` means jobs are kept; otherwise jobs are removed.
- `website` and `career` should be canonical URLs without a trailing slash.
- `scraperFile` must be the full workflow URL, not the raw file URL.

## Upsert behavior

`upsert_company` passes the CIF **as-is** (no zero-padding, per AGENTS.md
commandment 2) and PUTs to `/v1/firme/company/add/`. The live
address/location from ANAF (CUIScan) takes precedence over the static
config when available.

## Example

```json
{
  "id": "03213771",
  "company": "DANNY COM ALS SRL",
  "brand": "Danny Com Als",
  "status": "activ",
  "location": ["Dobroești"],
  "website": [],
  "career": ["https://mediere.anofm.ro/app/module/mediere/jobs"],
  "scraperFile": "https://github.com/peviitor-scrapers/danny-com-als-srl-python-scraper/actions/workflows/job-seeker-ro-spider.yml"
}
```

`website` is empty because DANNY COM ALS SRL has no public website; `career`
points to the ANOFM jobs page, the only source of its job postings.

`id` is the CIF zero-padded to 8 digits, as required by the peviitor company
model; ANOFM and ANAF/CUIScan queries use the raw CIF `3213771`.
