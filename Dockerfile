# ---------- ACEest Fitness & Gym – Docker Image ----------
# Uses a slim base image to reduce attack surface and image size.

FROM python:3.9-slim

# Metadata
LABEL maintainer="ACEest DevOps Team"
LABEL description="ACEest Fitness & Gym Flask Application"
LABEL version="3.2.4"

# Prevent Python from writing .pyc files & enable unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create a non-root user for security
RUN groupadd -r aceest && useradd -r -g aceest aceest

WORKDIR /app

# Install dependencies first (layer caching optimisation)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source & UI templates
COPY app.py test_app.py ./
COPY templates/ templates/

# Switch to non-root user
USER aceest

# Expose the application port
EXPOSE 5000

# Health-check: verify the app responds on /
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/')" || exit 1

# Run with gunicorn for production-grade serving
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]