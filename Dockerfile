FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

RUN groupadd -r scrobbler && useradd -r -g scrobbler scrobbler

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

RUN chown -R scrobbler:scrobbler /app

USER scrobbler

CMD ["python", "src/main.py"]
