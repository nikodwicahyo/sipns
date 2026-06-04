from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo


class TambahUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=50)])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password minimal 8 karakter'),
    ])
    role = SelectField('Role', choices=[
        ('admin', 'Admin'),
        ('guru', 'Guru'),
        ('siswa', 'Siswa'),
    ])
    is_active = BooleanField('Aktif', default=True)
    submit = SubmitField('Tambah User')


class ResetPasswordForm(FlaskForm):
    password_baru = PasswordField('Password Baru', validators=[
        DataRequired(),
        Length(min=8, message='Password minimal 8 karakter'),
    ])
    konfirmasi = PasswordField('Konfirmasi Password', validators=[
        DataRequired(),
        EqualTo('password_baru', message='Password tidak cocok'),
    ])
    submit = SubmitField('Reset Password')
