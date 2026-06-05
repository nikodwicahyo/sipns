"""
Modul: auth_forms.py
Deskripsi: WTForms untuk modul autentikasi (login).

Menggunakan Flask-WTF untuk CSRF protection otomatis dan WTForms validators
sehingga validasi form terjadi di server-side (defense in depth —
bukan hanya client-side JavaScript).

Author : Niko Dwicahyo
Versi  : 1.0.0
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    """Form login untuk Admin/Guru/Siswa (3 role berbagi satu form).

    Fields:
        username (str): Username login. Untuk siswa = NIS.
        password (str): Password akun.
        submit: Tombol submit.

    Validators:
        DataRequired pada semua field — pesan dalam Bahasa Indonesia.

    Catatan keamanan:
    - CSRF token di-inject otomatis oleh Flask-WTF (lihat meta tag di base.html).
    - Tidak ada validasi credentials di form — hanya di ``auth/routes.py``
      untuk memastikan authorization logic terpusat.
    """

    username = StringField(
        'Username',
        validators=[DataRequired(message='Username wajib diisi')],
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(message='Password wajib diisi')],
    )
    submit = SubmitField('Masuk')
