from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Length
from app.models.guru import Guru


class GuruForm(FlaskForm):
    id = HiddenField()
    id_guru = StringField('ID Guru', validators=[
        DataRequired(message='ID Guru wajib diisi'),
        Length(max=20, message='ID Guru maksimal 20 karakter'),
    ])
    nama_guru = StringField('Nama Guru', validators=[
        DataRequired(message='Nama Guru wajib diisi'),
        Length(max=100, message='Nama Guru maksimal 100 karakter'),
    ])
    mata_pelajaran = StringField('Mata Pelajaran', validators=[
        DataRequired(message='Mata Pelajaran wajib diisi'),
        Length(max=100, message='Mata Pelajaran maksimal 100 karakter'),
    ])
    submit = SubmitField('Simpan')

    def validate_id_guru(self, field):
        from wtforms import ValidationError
        from app.models import User
        existing = Guru.query.filter_by(id_guru=field.data, deleted_at=None).first()
        if existing and (not self.id.data or existing.id != int(self.id.data)):
            raise ValidationError('ID Guru sudah terdaftar.')
        user = User.query.filter_by(username=field.data).first()
        if user and user.guru_id and (not self.id.data or user.guru_id != int(self.id.data)):
            raise ValidationError('Username sudah terdaftar di sistem.')
