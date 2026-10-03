FROM python:3.13-slim AS base

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m appuser && mkdir -p /app/instance /app/uploads/cvs && chown -R appuser:appuser /app/instance /app/uploads && chmod 700 /app/instance /app/uploads/cvs
USER appuser

EXPOSE 5000
CMD ["gunicorn", "tzstudies:create_app('production')", "--bind", "0.0.0.0:5000", "--workers", "4"]
