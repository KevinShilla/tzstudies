"""Tests for the AI /ask endpoint."""

import pytest
from unittest.mock import patch, MagicMock


class TestAskEndpoint:
    """POST /ask — AI study assistant."""

    def test_ask_requires_query(self, client):
        resp = client.post("/ask", json={})
        assert resp.status_code == 400
        data = resp.get_json()
        assert "error" in data

    def test_ask_empty_query(self, client):
        resp = client.post("/ask", json={"query": "   "})
        assert resp.status_code == 400

    def test_ask_no_api_key(self, client, app):
        """When OPENAI_API_KEY is not configured."""
        with app.app_context():
            app.config["OPENAI_API_KEY"] = ""
        resp = client.post("/ask", json={"query": "What is 2+2?"})
        assert resp.status_code == 503
        data = resp.get_json()
        assert "not configured" in data["error"]

    @patch("tzstudies.routes.ai.OpenAI")
    def test_ask_returns_answer(self, mock_openai_cls, client, app):
        """Mock OpenAI to return a known answer."""
        with app.app_context():
            app.config["OPENAI_API_KEY"] = "test-key"

        # Build mock chain: client.chat.completions.create().choices[0].message.content
        mock_msg = MagicMock()
        mock_msg.content = "The answer is 4."
        mock_choice = MagicMock()
        mock_choice.message = mock_msg
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_cls.return_value = mock_client

        resp = client.post("/ask", json={"query": "What is 2+2?"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["answer"] == "The answer is 4."

    @patch("tzstudies.routes.ai.OpenAI")
    def test_ask_handles_api_error(self, mock_openai_cls, client, app):
        """When OpenAI raises an exception."""
        with app.app_context():
            app.config["OPENAI_API_KEY"] = "test-key"

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API error")
        mock_openai_cls.return_value = mock_client

        resp = client.post("/ask", json={"query": "test"})
        assert resp.status_code == 502
        data = resp.get_json()
        assert "error" in data


class TestErrorPages:
    """Custom error page rendering."""

    def test_404_page(self, client):
        resp = client.get("/nonexistent-route")
        assert resp.status_code == 404
        assert b"404" in resp.data
        assert b"Page Not Found" in resp.data

    def test_404_has_home_link(self, client):
        resp = client.get("/nonexistent-route")
        assert b"Back to Home" in resp.data
