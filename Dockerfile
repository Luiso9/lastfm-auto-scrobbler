FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app

RUN groupadd -r scrobbler && useradd -r -g scrobbler scrobbler

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY main.py .

COPY config.json .

RUN mkdir -p /app/config

RUN chown -R scrobbler:scrobbler /app

USER scrobbler

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import sys; sys.path.insert(0, '/app/src'); from configHandler import configHandler; configHandler()" || exit 1

CMD ["python", "main.py"]