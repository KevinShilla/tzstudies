"""Shared test fixtures for TZStudies."""

import os
import pytest

from tzstudies import create_app
from tzstudies.extensions import db as _db
from tzstudies.models import User, Paper
from werkzeug.security import generate_password_hash


@pytest.fixture(scope="session")
def app():
    """Create the Flask application for the test session."""
    app = create_app("testing")
    yield app


@pytest.fixture(autouse=True)
def _setup_db(app):
    """Create tables before each test, drop after."""
    with app.app_context():
        _db.create_all()
        yield
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture()
def db(app):
    """Database session scoped to a single test."""
    return _db


@pytest.fixture()
def sample_user(app, db):
    """Insert and return a sample user."""
    with app.app_context():
        user = User(
            email="test@example.com",
            name="Test User",
            pw_hash=generate_password_hash("password123"),
        )
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture()
def auth_client(client, sample_user):
    """A test client already logged in as the sample user."""
    client.post("/login", data={
        "email": "test@example.com",
        "password": "password123",
    }, follow_redirects=True)
    return client


@pytest.fixture()
def sample_papers(app, db):
    """Insert some sample papers into the database."""
    with app.app_context():
        papers = [
            Paper(file_name="BasicMath-F2-2021.pdf", category="exam", grade="F2"),
            Paper(file_name="English-F4-2023.pdf", category="exam", grade="F4"),
        ]
        db.session.add_all(papers)
        db.session.commit()
        return papers
