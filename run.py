"""
Modul: run.py
Deskripsi: Entry point untuk development lokal SIPNS.

Cara pakai:
    # development (default, debug aktif):
    python run.py

    # production-like lokal (debug off, pakai ProductionConfig):
    FLASK_ENV=production FLASK_DEBUG=0 python run.py

    # custom port / host:
    FLASK_RUN_PORT=8000 python run.py

Untuk deployment production di Render, gunakan ``wsgi.py`` (Gunicorn).
"""
import os

from app import create_app

app = create_app()

if __name__ == '__main__':
    debug = os.getenv('FLASK_DEBUG', '0') == '1'
    host = os.getenv('FLASK_RUN_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_RUN_PORT', '5000'))
    app.run(host=host, port=port, debug=debug)
