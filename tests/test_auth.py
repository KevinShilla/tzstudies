"""Tests for authentication routes (signup, login, logout)."""

import pytest
from tzstudies.models import User


class TestSignup:
    """POST /signup — user registration."""

    def test_signup_page_loads(self, client):
        resp = client.get("/signup")
        assert resp.status_code == 200
        assert b"Create Account" in resp.data

    def test_signup_creates_user(self, client, app, db):
        resp = client.post("/signup", data={
            "name": "New User",
            "email": "new@example.com",
            "password": "secret123",
        }, follow_redirects=True)
        assert resp.status_code == 200
        with app.app_context():
            user = User.query.filter_by(email="new@example.com").first()
            assert user is not None
            assert user.name == "New User"

    def test_signup_rejects_duplicate_email(self, client, sample_user):
        resp = client.post("/signup", data={
            "name": "Dup User",
            "email": "test@example.com",
            "password": "password123",
        }, follow_redirects=True)
        assert b"already registered" in resp.data

    def test_signup_rejects_short_password(self, client):
        resp = client.post("/signup", data={
            "name": "Short Pass",
            "email": "short@example.com",
            "password": "abc",
        }, follow_redirects=True)
        assert b"at least 6 characters" in resp.data

    def test_signup_rejects_missing_fields(self, client):
        resp = client.post("/signup", data={
            "name": "",
            "email": "x@x.com",
            "password": "secret123",
        }, follow_redirects=True)
        assert b"required" in resp.data


class TestLogin:
    """POST /login — user authentication."""

    def test_login_page_loads(self, client):
        resp = client.get("/login")
        assert resp.status_code == 200
        assert b"Log In" in resp.data

    def test_login_valid_credentials(self, client, sample_user):
        resp = client.post("/login", data={
            "email": "test@example.com",
            "password": "password123",
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert b"Hello" in resp.data or b"TZStudies" in resp.data

    def test_login_invalid_password(self, client, sample_user):
        resp = client.post("/login", data={
            "email": "test@example.com",
            "password": "wrong-password",
        }, follow_redirects=True)
        assert b"Invalid" in resp.data

    def test_login_nonexistent_user(self, client):
        resp = client.post("/login", data={
            "email": "nobody@example.com",
            "password": "password123",
        }, follow_redirects=True)
        assert b"Invalid" in resp.data


class TestLogout:
    """GET /logout — session termination."""

    def test_logout_redirects_home(self, auth_client):
        resp = auth_client.get("/logout", follow_redirects=True)
        assert resp.status_code == 200
        # After logout, login link should appear
        assert b"Login" in resp.data or b"Log In" in resp.data

    def test_logout_requires_auth(self, client):
        resp = client.get("/logout", follow_redirects=True)
        assert resp.status_code == 200
        # Should redirect to login
        assert b"Log In" in resp.data
