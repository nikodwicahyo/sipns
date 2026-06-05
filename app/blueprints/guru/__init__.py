"""
Modul: blueprints/guru/__init__.py
Deskripsi: Inisialisasi Blueprint untuk modul Guru.

URL prefix: ``/guru`` (di-set di ``app/__init__.py::create_app``).
"""
from flask import Blueprint

guru_bp = Blueprint('guru', __name__, template_folder='../../templates/guru')

from app.blueprints.guru import routes  # noqa: E402,F401
