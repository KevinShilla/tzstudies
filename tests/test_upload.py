"""Paper contributions should handle invalid files and email outages."""

from io import BytesIO
from unittest.mock import patch


def test_relabelled_file_is_rejected(client):
    response = client.post('/upload_exams', data={'exam_pdf': (BytesIO(b'not a PDF'), 'exam.pdf')}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Please choose a readable PDF file' in response.data


def test_email_outage_returns_helpful_message(client, app, monkeypatch):
    monkeypatch.setitem(app.config, 'MAIL_USERNAME', 'library@example.com')
    with patch('tzstudies.routes.upload.mail.send', side_effect=OSError('mail offline')):
        response = client.post('/upload_exams', data={'exam_pdf': (BytesIO(b'%PDF-1.7\n'), 'exam.pdf')}, follow_redirects=True)
    assert response.status_code == 200
    assert b'We couldn&#39;t send your paper' in response.data


def test_contribution_sends_pdf_for_review(client, app, monkeypatch):
    monkeypatch.setitem(app.config, 'MAIL_USERNAME', 'library@example.com')
    with patch('tzstudies.routes.upload.mail.send') as send:
        response = client.post('/upload_exams', data={'exam_pdf': (BytesIO(b'%PDF-1.7\n'), 'English-F2-2025.pdf')}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Your file has been sent to the team' in response.data
    assert send.call_args.args[0].attachments[0].filename == 'English-F2-2025.pdf'
