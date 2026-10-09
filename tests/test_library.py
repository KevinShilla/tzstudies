"""Coverage, full-catalogue filtering, metadata cache isolation and PDF delivery."""
import hashlib
import json
from collections import Counter
from pathlib import Path

import pytest
from sqlalchemy import event

from tzstudies.catalogue import build_catalogue
from tzstudies.library import PAGE_SIZE

ROOT = Path(__file__).resolve().parents[1]


def test_all_primary_subjects_have_seven_verified_papers_from_2022_onward():
    catalogue = build_catalogue(ROOT / "exams", ROOT / "answer_keys")
    counts = Counter((paper["grade"], paper["subject_group"]) for paper in catalogue if paper["year"] and int(paper["year"]) >= 2022)
    assert all(counts[(f"S{number}", subject)] >= 7 for number in range(1, 7) for subject in ("math", "english", "kiswahili"))
    manifest = json.loads((ROOT / "exams" / "catalogue.json").read_text(encoding="utf-8"))
    for filename, paper in manifest["papers"].items():
        data = (ROOT / "exams" / filename).read_bytes()
        assert hashlib.sha256(data).hexdigest() == paper["sha256"]
        assert paper["board"] != "NECTA"  # These imports are school/regional assessments.


def test_library_pagination_is_bounded_and_filters_the_entire_catalogue(client):
    first = client.get("/")
    second = client.get("/?page=2")
    assert first.status_code == second.status_code == 200
    assert first.data.count(b'<article class="exam-card"') == PAGE_SIZE
    assert b'aria-current="page"' in first.data
    assert first.data != second.data
    filtered = client.get("/?grade=S2&subject=math&year=2022")
    assert b'data-grade="S2" data-subject="Mathematics" data-year="2022"' in filtered.data
    assert b'data-grade="F4"' not in filtered.data
    assert b'data-subject="English"' not in filtered.data
    legacy = client.get("/?grade=S4&subject=math&year=2023")
    assert b"Hisabati-S4-2023.pdf" in legacy.data
    assert b"Mathematics-S4-2023.pdf" in legacy.data


def test_pagination_retains_filters_and_answer_keys_are_available_only(client):
    filtered = client.get("/?subject=math")
    assert b"page=2" in filtered.data and b"subject=math" in filtered.data
    keys = client.get("/answer_keys?grade=S2")
    assert keys.status_code == 200
    assert keys.data.count(b'<article class="exam-card"') == PAGE_SIZE
    assert b'data-grade="S2"' in keys.data
    assert b'data-grade="S6"' not in keys.data
    assert b"AnswerKey.pdf" in keys.data


def test_every_imported_paper_has_its_approved_published_worked_key():
    manifest = json.loads((ROOT / "exams/catalogue.json").read_text(encoding="utf-8"))["papers"]
    catalogue = {paper["filename"]: paper for paper in build_catalogue(ROOT / "exams", ROOT / "answer_keys")}
    report = json.loads((ROOT / "output/primary-answer-key-review.json").read_text(encoding="utf-8"))["papers"]
    for filename, metadata in manifest.items():
        stem = Path(filename).stem
        solution = json.loads((ROOT / "answer_keys/solutions" / (stem + ".json")).read_text(encoding="utf-8"))
        key_name = stem + "-AnswerKey.pdf"
        data = (ROOT / "answer_keys" / key_name).read_bytes()
        assert catalogue[filename]["answer_key"] == key_name
        assert solution["sha256"] == metadata["sha256"]
        assert solution["reviewed"] is solution["visual_reviewed"] is True
        assert report[filename]["status"] == "published"
        assert not report[filename]["layout_errors"]
        assert hashlib.sha256(data).hexdigest() == solution["visual_review_pdf_sha256"] == report[filename]["pdf_sha256"]


@pytest.mark.parametrize("query", ["grade=S99", "subject=unknown", "year=22", "page=0", "page=-2", "page=999999999", "year=2022x", "q=" + "x" * 201])
def test_invalid_library_filters_rejected(client, query):
    assert client.get("/?" + query).status_code == 400


def test_metadata_cache_is_invalidated_and_does_not_share_mutable_rows(tmp_path):
    exams, keys = tmp_path / "exams", tmp_path / "keys"
    exams.mkdir()
    keys.mkdir()
    filename = "Mathematics-S1-2024-School.pdf"
    (exams / filename).touch()
    manifest = exams / "catalogue.json"
    manifest.write_text(json.dumps({"papers": {filename: {"board": "School A", "assessment": "Monthly test"}}}), encoding="utf-8")
    first = build_catalogue(exams, keys)
    first[0]["board"] = "Changed by caller"
    assert build_catalogue(exams, keys)[0]["board"] == "School A"
    manifest.write_text(json.dumps({"papers": {filename: {"board": "Another school", "assessment": "Mock exam"}}}), encoding="utf-8")
    assert build_catalogue(exams, keys)[0]["board"] == "Another school"


def test_homepage_no_longer_synchronizes_paper_rows_on_each_request(app, db, client):
    statements = []

    def record_statement(connection, cursor, statement, parameters, context, many):
        statements.append(statement.lower())

    with app.app_context():
        event.listen(db.engine, "before_cursor_execute", record_statement)
        try:
            assert client.get("/").status_code == 200
            assert client.get("/").status_code == 200
        finally:
            event.remove(db.engine, "before_cursor_execute", record_statement)
    assert not any("insert into paper" in statement or "from paper" in statement for statement in statements)


def test_imported_pdf_supports_range_and_conditional_requests(client):
    manifest = json.loads((ROOT / "exams" / "catalogue.json").read_text(encoding="utf-8"))
    filename = next(iter(manifest["papers"]))
    full = client.get("/serve/" + filename)
    assert full.status_code == 200 and full.data.startswith(b"%PDF-")
    assert "max-age=86400" in full.headers["Cache-Control"]
    partial = client.get("/serve/" + filename, headers={"Range": "bytes=0-31"})
    assert partial.status_code == 206 and len(partial.data) == 32
    assert client.get("/serve/" + filename, headers={"If-None-Match": full.headers["ETag"]}).status_code == 304


def test_history_detail_keeps_the_verified_school_issuer(auth_client, app, db):
    from tzstudies.models import Paper

    manifest = json.loads((ROOT / "exams" / "catalogue.json").read_text(encoding="utf-8"))
    filename, metadata = next(iter(manifest["papers"].items()))
    assert auth_client.get("/view/" + filename).status_code == 200
    with app.app_context():
        paper_id = db.session.query(Paper).filter_by(file_name=filename).one().id
    response = auth_client.get(f"/paper/{paper_id}")
    assert response.status_code == 200
    assert metadata["board"].encode() in response.data
    assert metadata["source_url"].encode() in response.data
    assert b"NECTA" not in response.data
