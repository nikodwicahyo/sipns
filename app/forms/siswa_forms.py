"""
Modul: siswa_forms.py
Deskripsi: WTForms untuk manajemen data siswa (tambah/edit).

Form ini dipakai oleh ``admin/routes.py`` di endpoint tambah & edit siswa.
Validator custom ``validate_nis`` memastikan NIS belum terdaftar (kecuali
untuk record yang sedang diedit).

Author : Niko Dwicahyo
Versi  : 1.0.0
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from app.models.siswa import Siswa


class SiswaForm(FlaskForm):
    """Form untuk tambah/edit siswa.

    Fields:
        id (int, hidden): ID siswa saat edit (None saat tambah).
        nis (str): Nomor Induk Siswa. Unik, immutable setelah dibuat.
        nama (str): Nama lengkap siswa. Maks 100 karakter.
        kelas (str): Kelas (mis. "X-IPA-1"). Maks 20 karakter, auto-trim.
        password (str, optional): Password akun siswa. Jika kosong,
            default = NIS (lihat ``admin/routes.py``).
        submit: Tombol simpan.

    Validators:
    - DataRequired untuk field wajib.
    - Length限制 untuk mencegah input overflow.
    - Custom ``validate_nis``: cek unik NIS di tabel siswa DAN di tabel
      user (karena username = NIS untuk siswa).
    """

    id = HiddenField()
    nis = StringField(
        'NIS',
        validators=[
            DataRequired(message='NIS wajib diisi'),
            Length(min=1, max=20, message='NIS maksimal 20 karakter'),
        ],
    )
    nama = StringField(
        'Nama Lengkap',
        validators=[
            DataRequired(message='Nama wajib diisi'),
            Length(max=100, message='Nama maksimal 100 karakter'),
        ],
    )
    kelas = StringField(
        'Kelas',
        validators=[
            DataRequired(message='Kelas wajib diisi'),
            Length(max=20, message='Kelas maksimal 20 karakter'),
        ],
        # Strip whitespace untuk handle " X-IPA-1 " → "X-IPA-1".
        filters=[lambda x: x.strip() if x else x],
    )
    password = PasswordField(
        'Password',
        validators=[
            Optional(),
            Length(min=8, message='Password minimal 8 karakter'),
        ],
    )
    submit = SubmitField('Simpan')

    def validate_nis(self, field):
        """Validator custom: NIS harus unik di tabel siswa DAN user.

        Saat edit (``self.id.data`` terisi), record dengan id yang sama
        dikecualikan dari pengecekan. Ini mencegah false-positive
        "NIS sudah terdaftar" saat user mengedit siswa tanpa mengubah NIS.

        Raises:
            ValidationError: Jika NIS sudah ada di siswa ATAU sudah
            dipakai sebagai username di tabel user (untuk role siswa).
        """
        from wtforms import ValidationError
        from app.models import User

        # Cek 1: NIS di tabel siswa (exclude record yang sedang diedit).
        existing = Siswa.cari_by_nis(field.data)
        if existing and (not self.id.data or existing.id != int(self.id.data)):
            raise ValidationError('NIS sudah terdaftar.')

        # Cek 2: NIS di tabel user (sebagai username) — penting karena
        # saat tambah user, username = NIS. Mencegah konflik dengan user
        # dari role lain yang kebetulan punya username sama.
        user = User.query.filter_by(username=field.data).first()
        if user and user.siswa_id and (not self.id.data or user.siswa_id != int(self.id.data)):
            raise ValidationError('Username sudah terdaftar di sistem.')
