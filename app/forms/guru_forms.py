"""
Modul: guru_forms.py
Deskripsi: WTForms untuk manajemen data guru (tambah/edit).

Pola mirip dengan ``siswa_forms.py`` — form ini dipakai oleh
``admin/routes.py`` untuk endpoint CRUD guru. Validator custom
``validate_id_guru`` memastikan ID Guru unik.

Author : Niko Dwicahyo
Versi  : 1.0.0
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from app.models.guru import Guru


class GuruForm(FlaskForm):
    """Form untuk tambah/edit guru.

    Fields:
        id (int, hidden): ID guru saat edit (None saat tambah).
        id_guru (str): Kode ID Guru (mis. "GR-001"). Unik.
        nama_guru (str): Nama lengkap guru. Maks 100 karakter.
        mata_pelajaran (str): Mata pelajaran yang diampu. Maks 100 karakter.
        password (str, optional): Password akun guru. Jika kosong,
            default = 'Guru@123' (lihat ``admin/routes.py``).
        submit: Tombol simpan.

    Validators:
    - DataRequired untuk field wajib.
    - Length限制 untuk mencegah input overflow.
    - Custom ``validate_id_guru``: cek unik di tabel guru DAN user.
    """

    id = HiddenField()
    id_guru = StringField(
        'ID Guru',
        validators=[
            DataRequired(message='ID Guru wajib diisi'),
            Length(max=20, message='ID Guru maksimal 20 karakter'),
        ],
    )
    nama_guru = StringField(
        'Nama Guru',
        validators=[
            DataRequired(message='Nama Guru wajib diisi'),
            Length(max=100, message='Nama Guru maksimal 100 karakter'),
        ],
    )
    mata_pelajaran = StringField(
        'Mata Pelajaran',
        validators=[
            DataRequired(message='Mata Pelajaran wajib diisi'),
            Length(max=100, message='Mata Pelajaran maksimal 100 karakter'),
        ],
    )
    password = PasswordField(
        'Password',
        validators=[
            Optional(),
            Length(min=8, message='Password minimal 8 karakter'),
        ],
    )
    submit = SubmitField('Simpan')

    def validate_id_guru(self, field):
        """Validator custom: ID Guru harus unik di tabel guru DAN user.

        Saat edit, record dengan id yang sama dikecualikan. Ini mencegah
        false-positive "ID Guru sudah terdaftar" saat edit tanpa ubah ID.

        Raises:
            ValidationError: Jika ID Guru sudah ada di tabel guru ATAU
            sudah dipakai sebagai username user role guru.
        """
        from wtforms import ValidationError
        from app.models import User

        # Cek 1: ID Guru di tabel guru (exclude yang sedang diedit).
        existing = Guru.query.filter_by(id_guru=field.data, deleted_at=None).first()
        if existing and (not self.id.data or existing.id != int(self.id.data)):
            raise ValidationError('ID Guru sudah terdaftar.')

        # Cek 2: ID Guru di tabel user (sebagai username).
        user = User.query.filter_by(username=field.data).first()
        if user and user.guru_id and (not self.id.data or user.guru_id != int(self.id.data)):
            raise ValidationError('Username sudah terdaftar di sistem.')
