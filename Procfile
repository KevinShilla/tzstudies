release: FLASK_APP=app.py flask db upgrade
web: gunicorn "tzstudies:create_app('production')"
