# Production image — non-root, slim base
FROM python:3.12-slim AS base

# Baked into /app/version.txt for GET /api/v1/versions/ (CI tag or short SHA).
ARG VERSION=dev
ENV APP_VERSION=${VERSION}

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq5 \
        curl \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --system app \
    && useradd --system --gid app --create-home --home-dir /app app

WORKDIR /app

COPY requirements/ requirements/
RUN pip install --upgrade pip \
    && pip install -r requirements/production.txt

COPY --chown=app:app . /app/

RUN mkdir -p /app/media /app/staticfiles /app/logs \
    && chmod +x /app/docker/*.sh /app/wait-for-it.sh \
    && echo "${APP_VERSION}" > /app/version.txt \
    && chown app:app /app/version.txt \
    && chown -R app:app /app/media /app/staticfiles /app/logs

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD curl -fsS http://127.0.0.1:8000/api/v1/health/ || exit 1
