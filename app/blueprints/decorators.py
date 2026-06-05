"""
Modul: blueprints/decorators.py
Deskripsi: Custom decorator untuk kontrol akses berbasis role.

Berisi ``@role_required(role)`` — decorator yang memastikan user yang
mengakses route memiliki role tertentu. Mengembalikan 403 jika tidak.
"""
from functools import wraps
from flask import abort
from flask_login import current_user


def role_required(role):
    """Decorator: pastikan user yang mengakses route memiliki ``role``.

    Cara pakai::

        @app.route('/admin/dashboard')
        @login_required  # WAJIB di bawah @route, di atas @role_required
        @role_required('admin')
        def dashboard():
            ...

    Catatan urutan decorator:
    - ``@route`` paling atas (paling luar).
    - ``@login_required`` di tengah (cek autentikasi dulu).
    - ``@role_required`` paling bawah (paling dekat dengan fungsi).
    - Ini karena decorator dieksekusi bottom-up saat runtime.

    Args:
        role (str): Role yang diizinkan (mis. ``'admin'``). Harus persis
        sama dengan ``User.role`` di DB.

    Returns:
        function: Decorator function yang membungkus view function.

    Raises:
        403 Forbidden: Jika user belum login, atau user.role != role.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Jika belum login, kembalikan 403 (Flask-Login redirect ke
            # login_view biasanya, tapi kita eksplisit 403 untuk kejelasan).
            if not current_user.is_authenticated:
                abort(403)
            # Cek role — gunakan perbandingan strict equality.
            if current_user.role != role:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
