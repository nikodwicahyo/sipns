"""
Modul: blueprints/auth/__init__.py
Deskripsi: Inisialisasi Blueprint untuk modul Autentikasi.

Import ``routes`` di bawah agar decorator ter-attach ke blueprint.
"""
from flask import Blueprint

auth_bp = Blueprint('auth', __name__, template_folder='../../templates/auth')

from app.blueprints.auth import routes  # noqa: E402,F401
