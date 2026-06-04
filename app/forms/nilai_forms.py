from flask_wtf import FlaskForm
from wtforms import SelectField, DecimalField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class NilaiForm(FlaskForm):
    siswa_id = SelectField('Siswa', coerce=int, validators=[DataRequired()])
    nilai_tugas = DecimalField('Nilai Tugas', places=2, validators=[
        DataRequired(message='Nilai Tugas wajib diisi'),
        NumberRange(min=0, max=100, message='Nilai harus 0-100'),
    ])
    nilai_uts = DecimalField('Nilai UTS', places=2, validators=[
        DataRequired(message='Nilai UTS wajib diisi'),
        NumberRange(min=0, max=100, message='Nilai harus 0-100'),
    ])
    nilai_uas = DecimalField('Nilai UAS', places=2, validators=[
        DataRequired(message='Nilai UAS wajib diisi'),
        NumberRange(min=0, max=100, message='Nilai harus 0-100'),
    ])
    submit = SubmitField('Simpan Nilai')
