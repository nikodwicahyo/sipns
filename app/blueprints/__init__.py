"""
Modul: blueprints/__init__.py
Deskripsi: Package blueprints berisi semua Blueprint Flask untuk
            modularisasi routing (auth, admin, guru, siswa, laporan).
"""
from app.blueprints.auth import auth_bp  # noqa: F401
from app.blueprints.admin import admin_bp  # noqa: F401
from app.blueprints.guru import guru_bp  # noqa: F401
from app.blueprints.siswa import siswa_bp  # noqa: F401
from app.blueprints.laporan import laporan_bp  # noqa: F401
from app.blueprints.decorators import role_required  # noqa: F401
