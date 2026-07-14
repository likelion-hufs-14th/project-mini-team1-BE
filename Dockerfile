# ---- Builder stage ----
FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

COPY modi/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Runtime stage ----
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r django && useradd -r -g django django

COPY --from=builder /install /usr/local

WORKDIR /app

COPY modi/ .

RUN SECRET_KEY=dummy-key-for-collectstatic python manage.py collectstatic --noinput

RUN chown -R django:django /app

USER django

EXPOSE 8000

CMD ["gunicorn", "modi.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
