"""
Modul: forms/__init__.py
Deskripsi: Package forms berisi WTForms untuk seluruh modul aplikasi.
"""
from app.forms.auth_forms import LoginForm  # noqa: F401
from app.forms.siswa_forms import SiswaForm  # noqa: F401
from app.forms.guru_forms import GuruForm  # noqa: F401
from app.forms.nilai_forms import NilaiForm  # noqa: F401
from app.forms.user_forms import (  # noqa: F401
    TambahUserForm,
    EditUserForm,
    ResetPasswordForm,
)
