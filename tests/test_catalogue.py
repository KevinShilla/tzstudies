"""Regression coverage for filename variants and the student paper flows."""
import pytest

from tzstudies.catalogue import build_catalogue, identity
from tzstudies.models import Paper


@pytest.mark.parametrize("name", [
    "Mathematics-S4-2024.pdf", "Mathematics - S4 - 2024 (Answer Key).pdf",
    "Mathematics-S4-2024-AnswerKey.pdf", "Mathematics-S4-2024-English.pdf",
    "Mathematics-S4-2024 (1).pdf",
])
def test_filename_variants_share_identity(name):
    assert identity(name) == "mathematics-s4-2024"


def test_catalogue_matches_keys_and_hides_duplicate_copies(tmp_path):
    exams = tmp_path / "exams"
    keys = tmp_path / "answer_keys"
    exams.mkdir()
    keys.mkdir()
    for name in ["English-F2-2024.pdf", "English-F2-2024 (1).pdf", "English-F2-2023.pdf"]:
        (exams / name).touch()
    (keys / "English-F2-2024-AnswerKey.pdf").touch()
    catalogue = build_catalogue(exams, keys)
    assert len(catalogue) == 2
    assert catalogue[0]["filename"] == "English-F2-2024.pdf"
    assert catalogue[0]["answer_key"] == "English-F2-2024-AnswerKey.pdf"
    assert catalogue[0]["level"] == "Form 2"
    assert catalogue[1]["answer_key"] is None


def test_search_works_before_visiting_home(client):
    response = client.get("/search?q=English+Form+2+2024")
    assert response.status_code == 200
    assert b"English-F2-2024.pdf" in response.data
    assert b"English-F4-2024.pdf" not in response.data


@pytest.mark.parametrize("route", ["view", "download"])
def test_missing_file_does_not_create_paper(client, app, route):
    assert client.get(f"/{route}/missing.pdf").status_code == 404
    with app.app_context():
        assert Paper.query.filter_by(file_name="missing.pdf").first() is None


def test_answer_key_preview_requires_login(client):
    response = client.get("/view_key/BasicMath-F2-2023%20(Answer%20Key).pdf")
    assert response.status_code == 302
    assert "/login?next=" in response.location


def test_school_answer_key_preview_preserves_verified_issuer(auth_client, tmp_path, monkeypatch):
    import json

    from tzstudies.routes import papers

    exams, keys = tmp_path / "exams", tmp_path / "keys"
    exams.mkdir()
    keys.mkdir()
    filename = "English-S1-2024-School-Assessment.pdf"
    key = filename.removesuffix(".pdf") + "-AnswerKey.pdf"
    (exams / filename).touch()
    (keys / key).touch()
    (exams / "catalogue.json").write_text(json.dumps({"papers": {filename: {
        "board": "Primary School Assessment Group", "assessment": "Midterm exam"
    }}}), encoding="utf-8")
    monkeypatch.setattr(papers, "_get_exams_folder", lambda: str(exams))
    monkeypatch.setattr(papers, "_get_answer_keys_folder", lambda: str(keys))
    response = auth_client.get("/view_key/" + key)
    assert response.status_code == 200
    assert b"Primary School Assessment Group" in response.data
    assert b"Standard 1" in response.data
    assert b"NECTA" not in response.data


def test_login_returns_to_requested_key(client, sample_user):
    target = "/view_key/BasicMath-F2-2023%20(Answer%20Key).pdf"
    response = client.post("/login?next=" + target, data={"email": "test@example.com", "password": "password123"})
    assert response.status_code == 302
    assert response.location.startswith("/view_key/")


@pytest.mark.parametrize("target", ["https://example.com", "//example.com", "/\\example.com", "http://[invalid"])
def test_login_rejects_external_redirect(client, sample_user, target):
    from urllib.parse import quote
    response = client.post("/login?next=" + quote(target, safe=""), data={"email": "test@example.com", "password": "password123"})
    assert response.location == "/"


@pytest.mark.parametrize("body", [{"query": 123}, ["question"], {"query": "x" * 4001}])
def test_study_assistant_rejects_invalid_input(client, body):
    response = client.post("/ask", json=body)
    assert response.status_code == 400


def test_homepage_does_not_cache_account_state(client, sample_user):
    assert b"Hello, Test" not in client.get("/").data
    client.post("/login", data={"email": "test@example.com", "password": "password123"})
    assert b"Hello, Test" in client.get("/").data
    client.post("/logout")
    assert b"Hello, Test" not in client.get("/").data
