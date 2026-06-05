# =============================================================================
# Dockerfile untuk Hugging Face Spaces - SIPNS
# =============================================================================
#
# Build context: root project directory
# Base image  : python:3.12-slim (Debian Bookworm, kecil ~150MB + deps)
# Target port  : 7860 (wajib untuk HF Spaces Docker SDK)
#
# Cara build lokal (untuk testing):
#   docker build -t sipns .
#   docker run -p 7860:7860 \
#     -e DATABASE_URL='mysql+pymysql://...' \
#     -e SECRET_KEY='...' \
#     sipns
#
# Cara kerja:
#   1. Install OS dependencies untuk WeasyPrint (libpango, libcairo, dll)
#   2. Install Python dependencies dari requirements.txt
#   3. Copy seluruh source code
#   4. Saat container start: jalankan migration + seed, lalu gunicorn
# =============================================================================

FROM python:3.12-slim

# ---- System dependencies untuk WeasyPrint ----
# WeasyPrint butuh libpango + libcairo + libgdk-pixbuf + libffi.
# fonts-dejavu-core -> font default untuk render teks di PDF.
# shared-mime-info -> MIME type detection untuk static files.
# Hapus apt cache di akhir untuk kecilkan image size.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpango-1.0-0 \
        libpangoft2-1.0-0 \
        libharfbuzz0b \
        libcairo2 \
        libgdk-pixbuf-2.0-0 \
        libffi-dev \
        shared-mime-info \
        fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# ---- Working directory ----
WORKDIR /app

# ---- Python dependencies ----
# Copy requirements.txt dulu & install (cached layer).
# Kalau requirements.txt tidak berubah, layer ini di-reuse di rebuild berikutnya.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ---- Application source code ----
# Copy seluruh source (file yang tidak perlu di-exclude via .dockerignore).
COPY . .

# ---- Create logs directory (digunakan oleh ProductionConfig) ----
RUN mkdir -p /app/logs

# ---- Hugging Face Spaces Docker SDK configuration ----
# HF Spaces WAJIB listen di port 7860 untuk Docker SDK.
# app_port di README.md frontmatter juga harus 7860.
ENV PORT=7860
EXPOSE 7860

# ---- Health check (opsional, untuk monitoring internal) ----
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:7860/healthz').read()" \
    || exit 1

# ---- Entrypoint ----
# Sama strategi seperti Render: flask db upgrade && flask seed di-merge
# dengan CMD gunicorn (HF Spaces tidak punya konsep preDeployCommand).
# Keduanya idempotent:
#   - flask db upgrade: Alembic skip jika tidak ada migration baru
#   - flask seed:       guard `if User.query.first(): return` di app/seed.py
# Trade-off: tambah ~2-3 detik ke cold start.
CMD ["sh", "-c", "flask db upgrade && flask seed && gunicorn --bind 0.0.0.0:$PORT --workers 1 --preload --timeout 60 --access-logfile - --error-logfile - --log-level info wsgi:app"]
