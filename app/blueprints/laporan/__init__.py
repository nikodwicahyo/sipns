"""
Modul: blueprints/laporan/__init__.py
Deskripsi: Inisialisasi Blueprint untuk modul Laporan.

URL prefix: ``/laporan`` (di-set di ``app/__init__.py::create_app``).
"""
from flask import Blueprint

laporan_bp = Blueprint('laporan', __name__, template_folder='../../templates/laporan')

from app.blueprints.laporan import routes  # noqa: E402,F401
