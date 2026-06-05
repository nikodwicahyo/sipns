"""
Modul: models/__init__.py
Deskripsi: Package models — mengekspor semua class OOP entitas SIPNS.

Semua model di-export via ``__all__`` sehingga dapat di-import
sekaligus dengan ``from app.models import User, Siswa, Guru, Nilai, AuditLog``.

Urutan import TIDAK penting di Python modern, tapi kami urutkan
berdasarkan dependency (parent sebelum child) untuk kejelasan:
1. User (tidak depend ke model lain)
2. Siswa, Guru (depend ke tabel referensi FK)
3. Nilai (depend ke Siswa, Guru)
4. AuditLog (depend ke User)
"""
from app.models.user import User
from app.models.siswa import Siswa
from app.models.guru import Guru
from app.models.nilai import Nilai
from app.models.audit_log import AuditLog

__all__ = ['User', 'Siswa', 'Guru', 'Nilai', 'AuditLog']
