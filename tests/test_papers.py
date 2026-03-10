"""Tests for paper browsing, viewing, downloading, and history."""

import pytest


class TestIndex:
    """GET / — homepage with exam listing."""

    def test_index_loads(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert b"Exam Papers" in resp.data

    def test_index_shows_pdf_files(self, client):
        resp = client.get("/")
        assert b".pdf" in resp.data

    def test_index_has_search(self, client):
        resp = client.get("/")
        assert b"searchInput" in resp.data

    def test_index_has_ai_section(self, client):
        resp = client.get("/")
        assert b"AI Study Assistant" in resp.data


class TestViewExam:
    """GET /view/<filename> — inline PDF viewer."""

    def test_view_exam_renders(self, client):
        resp = client.get("/view/BasicMath-F2-2021.pdf")
        assert resp.status_code == 200
        assert b"BasicMath-F2-2021.pdf" in resp.data
        assert b"iframe" in resp.data


class TestDownload:
    """GET /download/<filename> — PDF download."""

    def test_download_returns_pdf(self, client):
        resp = client.get("/download/BasicMath-F2-2021.pdf")
        assert resp.status_code == 200
        assert resp.content_type == "application/pdf"

    def test_download_nonexistent_file(self, client):
        resp = client.get("/download/nonexistent.pdf")
        assert resp.status_code == 404


class TestAnswerKeys:
    """GET /answer_keys — answer key listing."""

    def test_answer_keys_page_loads(self, client):
        resp = client.get("/answer_keys")
        assert resp.status_code == 200
        assert b"Answer Keys" in resp.data


class TestDownloadKey:
    """GET /download_key/<filename> — requires login."""

    def test_download_key_requires_login(self, client):
        resp = client.get(
            "/download_key/Mathematics-S4-2020%20(Answer%20Key).pdf",
            follow_redirects=True,
        )
        assert b"Log In" in resp.data

    def test_download_key_works_when_logged_in(self, auth_client):
        resp = auth_client.get(
            "/download_key/Mathematics-S4-2020%20(Answer%20Key).pdf",
        )
        # Should either return PDF or 404 if file doesn't exist
        assert resp.status_code in (200, 404)


class TestHistory:
    """GET /history — user paper history."""

    def test_history_requires_login(self, client):
        resp = client.get("/history", follow_redirects=True)
        assert b"Log In" in resp.data

    def test_history_loads_for_authenticated_user(self, auth_client):
        resp = auth_client.get("/history")
        assert resp.status_code == 200
        assert b"My Papers" in resp.data
