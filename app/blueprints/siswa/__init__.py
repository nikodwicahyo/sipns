"""
Modul: blueprints/siswa/__init__.py
Deskripsi: Inisialisasi Blueprint untuk modul Siswa.

URL prefix: ``/siswa`` (di-set di ``app/__init__.py::create_app``).
"""
from flask import Blueprint

siswa_bp = Blueprint('siswa', __name__, template_folder='../../templates/siswa')

from app.blueprints.siswa import routes  # noqa: E402,F401
