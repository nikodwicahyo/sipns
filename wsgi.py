"""
Modul: wsgi.py
Deskripsi: Production WSGI entry point untuk SIPNS.

Dipakai oleh Gunicorn di Render:
    gunicorn --bind 0.0.0.0:$PORT wsgi:app

Paksa memuat ``ProductionConfig`` (``FLASK_ENV=production``) agar
``SECRET_KEY`` & ``SESSION_COOKIE_SECURE`` selalu benar walau Render
menyetel env var di urutan yang berbeda.

Untuk development lokal, gunakan ``run.py`` yang me-load ``DevelopmentConfig``
berdasarkan ``FLASK_ENV=development`` dari ``.env``.
"""
from app import create_app

app = create_app('production')
