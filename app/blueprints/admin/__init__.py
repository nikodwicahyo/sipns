"""
Modul: blueprints/admin/__init__.py
Deskripsi: Inisialisasi Blueprint untuk modul Admin.

URL prefix: ``/admin`` (di-set di ``app/__init__.py::create_app``).
Import ``routes`` di bawah agar decorator ``@admin_bp.route`` ter-attach.
"""
from flask import Blueprint

admin_bp = Blueprint('admin', __name__, template_folder='../../templates/admin')

from app.blueprints.admin import routes  # noqa: E402,F401
