"""Unit tests for the jobRapid.ro secondary source."""

import json

from scraper import jobrapid

SEARCH_HTML = """
<div class='container_lista_continut ' data-company='Danny Com Als'
     data-id='1733087'
     data-href='/locuri-de-munca/lucrator-comercial-in-pantelimon-1733087.html'>
  <a class='job-title' href='/locuri-de-munca/lucrator-comercial-in-pantelimon-1733087.html'>Lucrator Comercial</a>
</div>
<div class='container_lista_continut ' data-company='Alta Firma SRL'
     data-id='999'
     data-href='/locuri-de-munca/alt-job-999.html'>
  <a class='job-title' href='/locuri-de-munca/alt-job-999.html'>Alt job</a>
</div>
"""

DETAIL_HTML = """
<html><body>
<script type="application/ld+json">
{
  "@context": "https://schema.org/",
  "@type": "JobPosting",
  "title": "Lucrator Comercial",
  "datePosted": "2026-11-14T09:59:12+02:00",
  "validThrough": "2027-02-14T23:59:59+02:00",
  "hiringOrganization": {"@type": "Organization", "name": "Danny Com Als"},
  "jobLocation": {"@type": "Place", "address": {
    "@type": "PostalAddress", "addressLocality": "Pantelimon",
    "addressRegion": "Ilfov", "addressCountry": "RO"
  }},
  "baseSalary": {"@type": "MonetaryAmount", "currency": "RON",
    "value": {"@type": "QuantitativeValue", "unitText": "MONTH", "value": 4350}},
  "url": "https://www.jobrapid.ro/locuri-de-munca/lucrator-comercial-in-pantelimon-1733087.html"
}
</script>
</body></html>
"""


class _Response:
    def __init__(self, text, status_code=200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


def test_extract_company_hrefs_filters_and_dedupes():
    html = SEARCH_HTML + SEARCH_HTML
    hrefs = jobrapid._extract_company_hrefs(html, "Danny Com Als")
    assert hrefs == ["/locuri-de-munca/lucrator-comercial-in-pantelimon-1733087.html"]


def test_normalize_name_ignores_legal_suffix():
    assert jobrapid._normalize_name("Danny Com Als S.R.L.") == jobrapid._normalize_name("Danny Com Als")


def test_parse_job_posting_extracts_fields():
    job = jobrapid.parse_job_posting(DETAIL_HTML, "https://fallback")
    assert job["title"] == "Lucrator Comercial"
    assert job["url"].endswith("lucrator-comercial-in-pantelimon-1733087.html")
    assert job["location"] == ["Pantelimon"]
    assert job["date"] == "2026-11-14T07:59:12Z"
    assert job["salary"] == "4350-4350 RON"


def test_parse_job_posting_returns_none_without_jsonld():
    assert jobrapid.parse_job_posting("<html></html>", "https://x") is None


def test_search_jobrapid_uses_company_filter(monkeypatch):
    def fake_post(url, **kwargs):
        assert url == jobrapid.SEARCH_URL
        assert kwargs["data"] == {"key": "Danny Com Als"}
        return _Response(SEARCH_HTML)

    def fake_get(url, **kwargs):
        assert url.endswith("lucrator-comercial-in-pantelimon-1733087.html")
        return _Response(DETAIL_HTML)

    monkeypatch.setattr(jobrapid.requests, "post", fake_post)
    monkeypatch.setattr(jobrapid.requests, "get", fake_get)

    jobs = jobrapid.search_jobrapid("Danny Com Als")

    assert len(jobs) == 1
    assert jobs[0]["title"] == "Lucrator Comercial"
    assert jobs[0]["salary"] == "4350-4350 RON"
    assert json.dumps(jobs)  # result is JSON-serializable
