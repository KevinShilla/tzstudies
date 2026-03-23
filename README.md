# TZStudies

[![CI](https://github.com/YOUR_USERNAME/tzstudies/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/tzstudies/actions)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**A full-stack educational platform providing free past exam papers, answer keys, AI-powered tutoring, and a tutor marketplace for Tanzanian students.**

## Features

- **Exam Paper Library** — Browse, search, filter, and download national exam PDFs (Standard 4 through Form 6)
- **AI Study Assistant** — Ask curriculum questions and receive step-by-step explanations powered by GPT-4o-mini
- **Answer Keys** — Authenticated access to marking schemes and worked solutions
- **Tutor Marketplace** — Find verified tutors by subject, or apply to become one
- **User Accounts** — Secure signup/login with email verification and password reset
- **Admin Dashboard** — Analytics, user management, and tutor application review
- **Activity History** — Track recently viewed and downloaded papers

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Flask 3.1 (Application Factory pattern with Blueprints) |
| **Database** | PostgreSQL + SQLAlchemy ORM + Alembic migrations |
| **Authentication** | Flask-Login (session-based) + itsdangerous tokens |
| **AI** | OpenAI GPT-4o-mini via official Python SDK |
| **Security** | Flask-WTF (CSRF), Flask-Limiter (rate limiting), Flask-Talisman (headers) |
| **Caching** | Flask-Caching (SimpleCache / Redis) |
| **Email** | Flask-Mail (Gmail SMTP) |
| **Testing** | pytest + pytest-cov (35+ tests) |
| **CI/CD** | GitHub Actions |
| **Containerization** | Docker + docker-compose |
| **Deployment** | Render (Gunicorn) |

## Architecture

```
tzstudies/
  __init__.py          # Application factory (create_app)
  config.py            # Config classes (Dev / Test / Prod)
  extensions.py        # Flask extension instances
  models.py            # SQLAlchemy models (User, Paper, History, TutorApplication)
  routes/
    auth.py            # Signup, login, logout, email verification, password reset
    papers.py          # Exam browsing, viewing, downloading, history
    tutors.py          # Tutor marketplace, applications, API
    ai.py              # OpenAI-powered Q&A endpoint
    upload.py          # Exam PDF upload via email
    admin.py           # Admin dashboard with analytics
templates/             # Jinja2 templates (base.html + page templates)
static/
  css/styles.css       # Responsive CSS (mobile-first, 3 breakpoints)
  js/script.js         # Client-side search, filtering, AI chat
tests/                 # pytest test suite
  conftest.py          # Fixtures (app, client, auth_client, sample data)
  test_auth.py         # Authentication tests
  test_papers.py       # Paper browsing/downloading tests
  test_tutors.py       # Tutor page and application tests
  test_api.py          # AI endpoint and error page tests
```

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL (or SQLite for local development)
- Gmail account with App Password (for email features)
- OpenAI API key (for AI Study Assistant)

### Local Setup

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/tzstudies.git
cd tzstudies

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your values (SECRET_KEY, DATABASE_URL, etc.)

# Run database migrations
flask db upgrade

# Start the development server
python app.py
```

The app will be available at `http://localhost:5000`.

### Docker Setup

```bash
docker-compose up --build
```

This starts the Flask app and a PostgreSQL database. Access at `http://localhost:5000`.

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage report
python -m pytest tests/ -v --cov=tzstudies --cov-report=term-missing
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | Flask session secret (generate with `python -c "import secrets; print(secrets.token_hex(32))"`) |
| `DATABASE_URL` | No | PostgreSQL URL (defaults to SQLite) |
| `OPENAI_API_KEY` | No | OpenAI API key for AI Study Assistant |
| `MAIL_USERNAME` | No | Gmail address for email features |
| `MAIL_PASSWORD` | No | Gmail App Password |
| `REDIS_URL` | No | Redis URL for rate limiter storage |

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/` | No | Homepage with exam listing |
| `GET` | `/view/<filename>` | No | Inline PDF viewer |
| `GET` | `/download/<filename>` | No | Download exam PDF |
| `GET` | `/download_key/<filename>` | Yes | Download answer key |
| `GET` | `/answer_keys` | No | Answer key listing |
| `GET` | `/history` | Yes | User paper history |
| `GET` | `/tutors` | No | Tutor marketplace |
| `POST` | `/become_tutor` | No | Submit tutor application |
| `POST` | `/ask` | No | AI study assistant (JSON) |
| `GET` | `/api/v1/tutors` | No | Tutor data (JSON) |
| `GET` | `/admin/` | Admin | Admin dashboard |
| `GET` | `/admin/api/stats` | Admin | Dashboard stats (JSON) |
| `GET` | `/health` | No | Health check endpoint |

## License

This project is licensed under the MIT License.
