"""
Modul: blueprints/auth/routes.py
Deskripsi: Route handler untuk modul Autentikasi (AUTH).

Endpoint:
- ``GET/POST /auth/login``  → Form login (semua role).
- ``GET     /auth/logout`` → Logout (semua role yang sedang login).

Helper:
- ``redirect_by_role(user)`` → Redirect user ke dashboard sesuai role-nya.

Author : Niko Dwicahyo
Versi  : 1.0.0
"""
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.blueprints.auth import auth_bp
from app.forms.auth_forms import LoginForm
from app.models.user import User


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Halaman & handler form login untuk Admin/Guru/Siswa.

    GET  → Render form login kosong.
    POST → Validasi form, verifikasi kredensial, redirect by role.

    Flow:
    1. Cek apakah user sudah login → redirect ke dashboard masing-masing.
    2. POST + valid: query user, cek password, cek is_active.
    3. Berhasil: ``login_user(user)`` + flash + redirect by role.
    4. Gagal: flash error + render ulang form (status 200).

    Returns:
        Response: Halaman login (200) atau redirect (302).
    """
    # Jika sudah authenticated, langsung redirect ke dashboard (no re-login).
    if current_user.is_authenticated:
        return redirect_by_role(current_user)

    form = LoginForm()
    if form.validate_on_submit():
        # Query user berdasarkan username (case-sensitive, indexed).
        user = User.query.filter_by(username=form.username.data).first()

        # Verifikasi password hash + cek akun aktif.
        if not user or not user.check_password(form.password.data):
            flash('Username atau password salah.', 'error')
            return render_template('auth/login.html', form=form)

        if not user.is_active:
            flash('Akun Anda tidak aktif. Hubungi admin.', 'error')
            return render_template('auth/login.html', form=form)

        # Login berhasil → set session & redirect.
        login_user(user)
        flash(f'Selamat datang, {user.username}!', 'success')
        return redirect_by_role(user)

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout user yang sedang login.

    Membersihkan Flask-Login session, flash pesan sukses, redirect
    ke halaman login. Dipanggil dari tombol "Logout" di navbar.
    """
    logout_user()
    flash('Anda berhasil logout.', 'success')
    return redirect(url_for('auth.login'))


def redirect_by_role(user):
    """Redirect user ke dashboard sesuai role-nya (admin/guru/siswa).

    Helper ini dipanggil oleh ``login()`` (setelah berhasil) dan oleh
    route handler lain yang perlu mengirim user ke halaman default-nya.

    Args:
        user (User): Instance user yang sudah login.

    Returns:
        Response: HTTP 302 redirect ke URL dashboard sesuai role.
    """
    if user.is_admin():
        return redirect(url_for('admin.dashboard'))
    elif user.is_guru():
        return redirect(url_for('guru.dashboard'))
    else:
        return redirect(url_for('siswa.dashboard'))
