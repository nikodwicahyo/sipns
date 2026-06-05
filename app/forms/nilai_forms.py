"""
Modul: nilai_forms.py
Deskripsi: WTForms untuk input nilai siswa oleh guru.

Form ini dipakai oleh ``guru/routes.py`` di endpoint input/edit nilai.
Menggunakan ``DecimalField`` untuk presisi nilai (mendukung desimal),
dengan validator ``NumberRange`` 0-100 sesuai PRD §5.4 NILAI-01/02.

Author : Niko Dwicahyo
Versi  : 1.0.0
"""
from flask_wtf import FlaskForm
from wtforms import SelectField, DecimalField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class NilaiForm(FlaskForm):
    """Form untuk input/edit nilai siswa per mata pelajaran.

    Fields:
        siswa_id (int): Foreign key ke siswa. Di-populate dari route
            handler (``guru/routes.py``) berdasarkan kelas user.
        nilai_tugas (Decimal): Nilai tugas, rentang 0-100, 2 desimal.
        nilai_uts (Decimal): Nilai UTS, rentang 0-100, 2 desimal.
        nilai_uas (Decimal): Nilai UAS, rentang 0-100, 2 desimal.
        submit: Tombol simpan.

    Validators:
    - DataRequired untuk semua field nilai.
    - NumberRange(min=0, max=100) di sisi server — client-side JS
      juga melakukan validasi (lihat static/js/main.js) untuk UX yang
      lebih baik, tapi server-side adalah sumber kebenaran (defense
      in depth, sesuai PRD §6 Keamanan).

    Catatan UI:
    - Preview nilai akhir real-time di-handle oleh static/js/nilai-preview.js
      yang memanggil endpoint AJAX ``/api/nilai-preview``.
    - Form ini TIDAK punya field ``mata_pelajaran`` — di-set otomatis
      sesuai mapel guru yang login (lihat ``guru/routes.py``).
    """

    siswa_id = SelectField(
        'Siswa',
        coerce=int,
        validators=[DataRequired(message='Siswa wajib dipilih')],
    )
    nilai_tugas = DecimalField(
        'Nilai Tugas',
        places=2,
        validators=[
            DataRequired(message='Nilai Tugas wajib diisi'),
            NumberRange(min=0, max=100, message='Nilai harus 0-100'),
        ],
    )
    nilai_uts = DecimalField(
        'Nilai UTS',
        places=2,
        validators=[
            DataRequired(message='Nilai UTS wajib diisi'),
            NumberRange(min=0, max=100, message='Nilai harus 0-100'),
        ],
    )
    nilai_uas = DecimalField(
        'Nilai UAS',
        places=2,
        validators=[
            DataRequired(message='Nilai UAS wajib diisi'),
            NumberRange(min=0, max=100, message='Nilai harus 0-100'),
        ],
    )
    submit = SubmitField('Simpan Nilai')
