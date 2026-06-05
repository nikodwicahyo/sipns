"""
Modul: user_forms.py
Deskripsi: WTForms untuk manajemen user (admin only).

Berisi 3 form:
1. ``TambahUserForm`` — Form untuk tambah user baru.
2. ``EditUserForm`` — Form untuk edit profil user (tanpa password).
3. ``ResetPasswordForm`` — Form untuk reset password user.

Author : Niko Dwicahyo
Versi  : 1.0.0
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, Optional


class TambahUserForm(FlaskForm):
    """Form tambah user baru (admin only).

    Fields:
        username (str): Username unik. Maks 50 karakter.
        password (str): Password akun. Min 8 karakter (PRD §6).
        role (str): Pilihan 'admin', 'guru', atau 'siswa'.
        is_active (bool): Status aktif (default True).
        submit: Tombol tambah.
    """

    username = StringField(
        'Username',
        validators=[DataRequired(), Length(max=50)],
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=8, message='Password minimal 8 karakter'),
        ],
    )
    role = SelectField(
        'Role',
        choices=[
            ('admin', 'Admin'),
            ('guru', 'Guru'),
            ('siswa', 'Siswa'),
        ],
    )
    is_active = BooleanField('Aktif', default=True)
    submit = SubmitField('Tambah User')


class EditUserForm(FlaskForm):
    """Form edit profil user (tanpa ubah password).

    Fields:
        username (str): Username baru (dapat diubah).
        role (str): Role baru.
        is_active (bool): Status aktif.
        submit: Tombol simpan.
    """

    username = StringField(
        'Username',
        validators=[DataRequired(), Length(max=50)],
    )
    role = SelectField(
        'Role',
        choices=[
            ('admin', 'Admin'),
            ('guru', 'Guru'),
            ('siswa', 'Siswa'),
        ],
    )
    is_active = BooleanField('Aktif', default=True)
    submit = SubmitField('Simpan')


class ResetPasswordForm(FlaskForm):
    """Form reset password user (admin only).

    Fields:
        password_baru (str): Password baru. Min 8 karakter.
        konfirmasi (str): Konfirmasi password baru. Harus sama.
        submit: Tombol reset.

    Validators:
    - Length(min=8) untuk password_baru (sesuai PRD §6).
    - EqualTo('password_baru') untuk konfirmasi — mencegah typo.
    """

    password_baru = PasswordField(
        'Password Baru',
        validators=[
            DataRequired(),
            Length(min=8, message='Password minimal 8 karakter'),
        ],
    )
    konfirmasi = PasswordField(
        'Konfirmasi Password',
        validators=[
            DataRequired(),
            EqualTo('password_baru', message='Password tidak cocok'),
        ],
    )
    submit = SubmitField('Reset Password')
