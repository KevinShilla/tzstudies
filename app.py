"""Entry point for TZStudies.

Usage:
    Development:  python app.py
    Production:   gunicorn "tzstudies:create_app()"
"""

from tzstudies import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
