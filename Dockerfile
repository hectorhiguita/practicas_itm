# ── Stage 1: build deps ───────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: runtime ─────────────────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Instalar solo librerías de runtime (no gcc)
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copiar dependencias ya instaladas
COPY --from=builder /install /usr/local

# Copiar código fuente
COPY src/ ./src/
COPY main.py .
COPY seed_db_itm.py .
COPY entrypoint.sh .

# Usuario no-root para seguridad
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
RUN chmod +x entrypoint.sh
USER appuser

EXPOSE 5000

# Healthcheck apuntando al endpoint existente
HEALTHCHECK --interval=30s --timeout=10s --start-period=90s --retries=5 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/health')" || exit 1

# Entrypoint: inicializa BD (una vez) y luego arranca gunicorn sin --preload
CMD ["./entrypoint.sh"]
