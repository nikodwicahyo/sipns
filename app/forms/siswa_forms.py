from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Length
from app.models.siswa import Siswa


class SiswaForm(FlaskForm):
    id = HiddenField()
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
    ], filters=[lambda x: x.strip() if x else x])
    submit = SubmitField('Simpan')

    def validate_nis(self, field):
        from wtforms import ValidationError
        from app.models import User
        existing = Siswa.cari_by_nis(field.data)
        if existing and (not self.id.data or existing.id != int(self.id.data)):
            raise ValidationError('NIS sudah terdaftar.')
        user = User.query.filter_by(username=field.data).first()
        if user and user.siswa_id and (not self.id.data or user.siswa_id != int(self.id.data)):
            raise ValidationError('Username sudah terdaftar di sistem.')
