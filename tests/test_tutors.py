"""Tests for tutor pages and tutor application."""

import pytest


class TestTutorsPage:
    """GET /tutors — tutor listing page."""

    def test_tutors_page_loads(self, client):
        resp = client.get("/tutors")
        assert resp.status_code == 200
        assert b"Find a Tutor" in resp.data

    def test_tutors_page_shows_tutors(self, client):
        resp = client.get("/tutors")
        # Should have at least one tutor card
        assert b"tutor-card" in resp.data


class TestBecomeTutor:
    """GET/POST /become_tutor — tutor application form."""

    def test_form_loads(self, client):
        resp = client.get("/become_tutor")
        assert resp.status_code == 200
        assert b"Become a Tutor" in resp.data
        assert b"Submit Application" in resp.data

    def test_submit_application(self, client, app, db):
        from tzstudies.models import TutorApplication

        resp = client.post("/become_tutor", data={
            "name": "Jane Doe",
            "location": "Dar es Salaam",
            "school": "Test School",
            "hourly_rate": "TSh 10,000",
            "experience": "3 years, Math & Science",
            "classes_taught": "Standard 4 - Form 2",
            "phone": "+255 123 456 789",
            "email": "jane@example.com",
            "profile_bio": "Experienced Math tutor.",
        }, follow_redirects=True)
        assert resp.status_code == 200

        with app.app_context():
            app_row = TutorApplication.query.filter_by(email="jane@example.com").first()
            assert app_row is not None
            assert app_row.name == "Jane Doe"
            assert app_row.location == "Dar es Salaam"


class TestTutorAPI:
    """GET /api/v1/tutors — JSON tutor listing."""

    def test_api_returns_json(self, client):
        resp = client.get("/api/v1/tutors")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "tutors" in data
        assert "count" in data
        assert isinstance(data["tutors"], list)
