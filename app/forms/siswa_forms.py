from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
from app.models.siswa import Siswa


class SiswaForm(FlaskForm):
    nis = StringField('NIS', validators=[
        DataRequired(message='NIS wajib diisi'),
        Length(min=1, max=20, message='NIS maksimal 20 karakter'),
    ])
    nama = StringField('Nama Lengkap', validators=[
        DataRequired(message='Nama wajib diisi'),
        Length(max=100, message='Nama maksimal 100 karakter'),
    ])
    kelas = StringField('Kelas', validators=[
        DataRequired(message='Kelas wajib diisi'),
        Length(max=20, message='Kelas maksimal 20 karakter'),
    ])
    submit = SubmitField('Simpan')

    def validate_nis(self, field):
        if not self.id.data:
            existing = Siswa.cari_by_nis(field.data)
            if existing:
                from wtforms import ValidationError
                raise ValidationError('NIS sudah terdaftar.')
