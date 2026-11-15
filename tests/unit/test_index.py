"""Unit tests for the index pipeline (ANOFM + jobRapid)."""

import json

from scraper import index


def test_map_to_job_model_adds_company_and_status():
    index.COMPANY_NAME = "DANNY COM ALS SRL"
    raw = {
        "url": "https://mediere.anofm.ro/app/module/mediere/job/1",
        "title": "Lucrător comercial",
        "location": ["Dobroești"],
    }
    job = index.map_to_job_model(raw, "3213771")
    assert job["company"] == "DANNY COM ALS SRL"
    assert job["cif"] == "3213771"
    assert job["status"] == "scraped"
    assert job["location"] == ["Dobroești"]
    assert job["date"]


def test_map_to_job_model_without_location():
    raw = {"url": "https://mediere.anofm.ro/app/module/mediere/job/2",
           "title": "Vânzător"}
    job = index.map_to_job_model(raw, "3213771", company_name="DANNY COM ALS SRL")
    assert "location" not in job


def test_map_to_job_model_preserves_salary():
    raw = {
        "url": "https://www.jobrapid.ro/locuri-de-munca/lucrator-comercial-in-pantelimon-1733087.html",
        "title": "Lucrator Comercial",
        "location": ["Pantelimon"],
        "salary": "4350-4350 RON",
    }
    job = index.map_to_job_model(raw, "3213771", company_name="DANNY COM ALS SRL")
    assert job["salary"] == "4350-4350 RON"


def test_transform_jobs_for_solr_uppercases_company():
    jobs = [{"url": "https://x/job", "title": "Test", "location": ["Cluj-Napoca"]}]
    transformed = index.transform_jobs_for_solr({"company": "Danny Com Als SRL", "jobs": jobs})
    assert transformed["company"] == "DANNY COM ALS SRL"
    assert transformed["jobs"][0]["location"] == ["Cluj-Napoca"]


def test_transform_jobs_for_solr_location_fallback():
    jobs = [{"url": "https://x/job", "title": "Test", "location": []}]
    transformed = index.transform_jobs_for_solr({"company": "DANNY COM ALS SRL", "jobs": jobs})
    assert transformed["jobs"][0]["location"] == ["România"]


def test_transform_jobs_for_solr_missing_location_fallback():
    jobs = [{"url": "https://x/job", "title": "Test"}]
    transformed = index.transform_jobs_for_solr({"company": "DANNY COM ALS SRL", "jobs": jobs})
    assert transformed["jobs"][0]["location"] == ["România"]


def test_main_writes_summary(tmp_path, monkeypatch):
    fake_jobs = [
        {"url": f"https://mediere.anofm.ro/app/module/mediere/job/{i}",
         "title": f"Job {i}", "location": ["Dobroești"]}
        for i in range(3)
    ]
    fake_jobrapid = [{
        "url": "https://www.jobrapid.ro/locuri-de-munca/lucrator-comercial-in-pantelimon-1733087.html",
        "title": "Lucrator Comercial",
        "location": ["Pantelimon"],
        "salary": "4350-4350 RON",
        "date": "2026-11-14T07:59:12Z",
    }]
    monkeypatch.setattr(index, "query_solr", lambda cif: {"numFound": 0, "docs": []})
    monkeypatch.setattr(index, "upsert_jobs", lambda jobs: None)
    monkeypatch.setattr(index, "delete_job_by_url", lambda url: None)
    monkeypatch.setattr(index, "upsert_company", lambda cfg: None)
    monkeypatch.setattr(index, "validate_and_get_company", lambda *a, **k: {
        "company": "DANNY COM ALS SRL", "cif": "03213771", "status": "active",
        "address": "DOBROEȘTI"})
    monkeypatch.setattr(index, "search_anofm", lambda cif: fake_jobs)
    monkeypatch.setattr(index, "search_jobrapid", lambda name: fake_jobrapid)
    monkeypatch.setattr(index.time, "sleep", lambda s: None)

    index.main(root=tmp_path)

    out = tmp_path / "scraper" / "jobs.json"
    assert out.exists()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert len(data["jobs"]) == 4
    assert data["company"] == "DANNY COM ALS SRL"
    assert data["source"] == "mediere.anofm.ro, jobrapid.ro"
    urls = {job["url"] for job in data["jobs"]}
    assert fake_jobrapid[0]["url"] in urls
    assert any(job.get("salary") == "4350-4350 RON" for job in data["jobs"])
    assert (tmp_path / "docs" / "jobs.md").exists()


def test_main_inactive_company_skips_scrape(tmp_path, monkeypatch):
    deleted = []
    monkeypatch.setattr(index, "query_solr", lambda cif: {"numFound": 1, "docs": []})
    monkeypatch.setattr(index, "validate_and_get_company", lambda *a, **k: {
        "company": "DANNY COM ALS SRL", "cif": "03213771", "status": "inactive"})
    monkeypatch.setattr(index, "delete_jobs_by_cif", lambda cif: deleted.append(cif))
    monkeypatch.setattr(index, "search_anofm",
                        lambda cif: (_ for _ in ()).throw(AssertionError("should not scrape")))

    index.main(root=tmp_path)

    assert deleted == ["03213771"]
