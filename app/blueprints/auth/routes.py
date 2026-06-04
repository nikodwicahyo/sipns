from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.blueprints.auth import auth_bp
from app.forms.auth_forms import LoginForm
from app.models.user import User


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect_by_role(current_user)

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if not user or not user.check_password(form.password.data):
            flash('Username atau password salah.', 'error')
            return render_template('auth/login.html', form=form)

        if not user.is_active:
            flash('Akun Anda tidak aktif. Hubungi admin.', 'error')
            return render_template('auth/login.html', form=form)

        login_user(user)
        flash(f'Selamat datang, {user.username}!', 'success')
        return redirect_by_role(user)

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda berhasil logout.', 'success')
    return redirect(url_for('auth.login'))


def redirect_by_role(user):
    if user.is_admin():
        return redirect(url_for('admin.dashboard'))
    elif user.is_guru():
        return redirect(url_for('guru.dashboard'))
    else:
        return redirect(url_for('siswa.dashboard'))
