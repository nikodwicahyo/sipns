"""
Modul: blueprints/admin/routes.py
Deskripsi: Route handler untuk modul Admin (manajemen sistem).

Berisi semua endpoint yang hanya bisa diakses role ``admin``:
- Dashboard dengan statistik agregat + chart.
- CRUD siswa, guru, user.
- Audit log viewer.
- Health check endpoint.
- API endpoint untuk AJAX (dropdown siswa, preview nilai, statistik kelas).

Semua route di file ini di-decorate dengan ``@login_required`` dan
``@role_required('admin')`` (lihat ``app/blueprints/decorators.py``)
untuk mencegah akses tanpa autentikasi & tanpa role yang sesuai.

Author : Niko Dwicahyo
Versi  : 1.0.0
"""
import os
import logging
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, jsonify, abort
from app.utils.time import now_jakarta
from flask_login import login_required, current_user
from app.blueprints.admin import admin_bp
from app.blueprints.decorators import role_required
from app import db
from app.models import User, Siswa, Guru, Nilai, AuditLog
from app.forms.siswa_forms import SiswaForm
from app.forms.guru_forms import GuruForm
from app.forms.user_forms import TambahUserForm, EditUserForm, ResetPasswordForm
from app.services.audit_service import catat_audit_log
from app.services.nilai_service import hitung_statistik_kelas
from sqlalchemy import func

logger = logging.getLogger(__name__)


# ===========================================================================
# DASHBOARD
# ===========================================================================

@admin_bp.route('/dashboard')
@login_required
@role_required('admin')
def dashboard():
    """Halaman dashboard admin dengan statistik agregat & chart data.

    Menghitung:
    - Total siswa aktif (exclude soft-deleted).
    - Total guru aktif.
    - Total record nilai.
    - Persentase kelulusan global.
    - 10 nilai terbaru (untuk tabel ringkasan).
    - Chart data: rata-rata nilai per kelas (untuk bar chart).

    Returns:
        Response: Render template ``admin/dashboard.html`` dengan konteks lengkap.
    """
    # Aggregate counts — exclude soft-deleted siswa/guru.
    total_siswa = Siswa.query.filter(Siswa.deleted_at.is_(None)).count()
    total_guru = Guru.query.filter(Guru.deleted_at.is_(None)).count()
    total_nilai = Nilai.query.count()

    # Hitung kelulusan global: loop siswa, cek apakah SEMUA mapel lulus.
    siswa_list = Siswa.query.filter(Siswa.deleted_at.is_(None)).all()
    total_lulus = 0
    total_tidak_lulus = 0
    for s in siswa_list:
        # Ambil record nilai yang punya status_lulus (skip None = belum dihitung).
        nilai_records = s.nilai.filter(Nilai.status_lulus.isnot(None)).all()
        if not nilai_records:
            continue
        if all(n.status_lulus for n in nilai_records):
            total_lulus += 1
        else:
            total_tidak_lulus += 1
    # Guard division by zero — jika belum ada nilai, persen = 0.
    persen_lulus = (
        round((total_lulus / (total_lulus + total_tidak_lulus) * 100), 1)
        if (total_lulus + total_tidak_lulus) > 0
        else 0
    )

    # 10 nilai terbaru untuk tabel ringkasan di dashboard.
    recent_nilai = Nilai.query.order_by(Nilai.created_at.desc()).limit(10).all()

    # Chart data: rata-rata nilai per kelas (untuk bar chart).
    kelas_list = Siswa.daftar_kelas()
    chart_labels = []
    chart_data = []
    for kelas in kelas_list:
        # Query JOIN Nilai+Siswa, filter per kelas (exclude soft-deleted siswa).
        data_nilai = Nilai.query.join(Siswa, Nilai.siswa_id == Siswa.id).filter(
            Siswa.kelas == kelas, Siswa.deleted_at.is_(None)
        ).all()
        stat = hitung_statistik_kelas(data_nilai)
        chart_labels.append(kelas)
        chart_data.append(stat['rata_rata'])

    return render_template('admin/dashboard.html',
                           total_siswa=total_siswa,
                           total_guru=total_guru,
                           total_nilai=total_nilai,
                           persen_lulus=persen_lulus,
                           recent_nilai=recent_nilai,
                           chart_labels=chart_labels,
                           chart_data=chart_data,
                           total_lulus=total_lulus,
                           total_tidak_lulus=total_tidak_lulus)


# ===========================================================================
# MANAJEMEN SISWA
# ===========================================================================

@admin_bp.route('/siswa')
@login_required
@role_required('admin')
def daftar_siswa():
    """Halaman daftar siswa (admin only).

    Menampilkan semua siswa AKTIF (exclude soft-deleted) dalam tabel
    DataTables. Aksi per baris: Edit, Hapus, Detail.

    Returns:
        Response: Render ``admin/siswa/index.html`` dengan list siswa.
    """
    siswa_list = Siswa.query.filter(Siswa.deleted_at.is_(None)).all()
    return render_template('admin/siswa/index.html', siswa_list=siswa_list)


@admin_bp.route('/siswa/tambah', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def tambah_siswa():
    """Halaman & handler form tambah siswa baru.

    GET  → Render form kosong.
    POST → Validasi form, insert siswa + user, audit log, redirect.

    Validasi:
    - NIS unik (validator form + DB UNIQUE constraint).
    - Password: default = NIS jika kosong (lihat ``siswa_forms.py``).

    Returns:
        Response: Render form (200) atau redirect ke daftar siswa (302).
    """
    form = SiswaForm()
    if form.validate_on_submit():
        try:
            siswa = Siswa(nis=form.nis.data, nama=form.nama.data, kelas=form.kelas.data)
            db.session.add(siswa)
            db.session.flush()  # flush agar siswa.id terisi untuk FK User.

            # Default password: NIS itu sendiri (konvensi sederhana).
            password = form.password.data if form.password.data else form.nis.data
            user = User(username=form.nis.data, role='siswa', siswa_id=siswa.id)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            # Audit log SETELAH commit (best practice — log hanya jika op utama sukses).
            catat_audit_log(
                user_id=current_user.id,
                action='INSERT',
                table_name='siswa',
                record_id=siswa.id,
                description=f'Tambah siswa {siswa.nama} (NIS: {siswa.nis})',
                ip_address=request.remote_addr,
            )
            flash(f'Siswa {siswa.nama} berhasil ditambahkan.', 'success')
            flash(f'Default login — Username: {user.username}, Password: {password}', 'info')
            return redirect(url_for('admin.daftar_siswa'))
        except Exception as e:
            db.session.rollback()
            logger.exception('Gagal menambah siswa')
            flash(f'Gagal menambah siswa: {str(e)}', 'error')
            return redirect(url_for('admin.daftar_siswa'))

    return render_template('admin/siswa/form.html', form=form, title='Tambah Siswa')


@admin_bp.route('/siswa/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_siswa(id):
    """Halaman & handler form edit siswa.

    GET  → Pre-fill form dengan data siswa existing. NIS disabled.
    POST → Update nama & kelas (NIS immutable sesuai PRD §14 Batasan #3).

    Args:
        id (int): Primary key siswa yang akan diedit.

    Returns:
        Response: Render form (200) atau redirect (302).
    """
    siswa = Siswa.query.get_or_404(id)
    form = SiswaForm(obj=siswa)
    if form.validate_on_submit():
        siswa.nama = form.nama.data
        siswa.kelas = form.kelas.data
        # CATATAN: NIS TIDAK diubah (immutable per PRD §14 Batasan #3).
        db.session.commit()

        catat_audit_log(
            user_id=current_user.id,
            action='UPDATE',
            table_name='siswa',
            record_id=siswa.id,
            description=f'Edit siswa {siswa.nama} (NIS: {siswa.nis})',
            ip_address=request.remote_addr,
        )
        flash(f'Data siswa {siswa.nama} berhasil diubah.', 'success')
        return redirect(url_for('admin.daftar_siswa'))

    # Disable field NIS di form edit (immutable).
    form.nis.render_kw = {'disabled': True}
    return render_template('admin/siswa/form.html', form=form, siswa=siswa, title='Edit Siswa')


@admin_bp.route('/siswa/hapus/<int:id>', methods=['POST'])
@admin_bp.route('/siswa/<int:id>/hapus', methods=['POST'])  # alias untuk kompatibilitas
@login_required
@role_required('admin')
def hapus_siswa(id):
    """Soft-delete siswa dan nonaktifkan akun user terkait.

    Tidak benar-benar menghapus data (FK nilai harus tetap valid).
    Sebaliknya: set ``deleted_at`` + ``User.is_active=False``.

    Args:
        id (int): Primary key siswa yang akan di-soft-delete.

    Returns:
        Response: Redirect ke daftar siswa dengan flash message.
    """
    siswa = Siswa.query.get_or_404(id)
    siswa.soft_delete()  # set deleted_at = utcnow()
    if siswa.user:
        siswa.user.is_active = False  # prevent login siswa terkait.
    db.session.commit()

    catat_audit_log(
        user_id=current_user.id,
        action='DELETE',
        table_name='siswa',
        record_id=siswa.id,
        description=f'Hapus siswa {siswa.nama} (NIS: {siswa.nis})',
        ip_address=request.remote_addr,
    )
    flash(f'Siswa {siswa.nama} berhasil dihapus.', 'success')
    return redirect(url_for('admin.daftar_siswa'))


@admin_bp.route('/siswa/<int:id>')
@login_required
@role_required('admin')
def detail_siswa(id):
    """Halaman profil detail siswa + riwayat nilai.

    Args:
        id (int): Primary key siswa.

    Returns:
        Response: Render ``admin/siswa/detail.html``.
    """
    siswa = Siswa.query.get_or_404(id)
    nilai_list = Nilai.query.filter_by(siswa_id=id).all()
    return render_template('admin/siswa/detail.html', siswa=siswa, nilai_list=nilai_list)


# ===========================================================================
# MANAJEMEN GURU
# ===========================================================================

@admin_bp.route('/guru')
@login_required
@role_required('admin')
def daftar_guru():
    """Halaman daftar guru (admin only).

    Returns:
        Response: Render ``admin/guru/index.html`` dengan list guru.
    """
    guru_list = Guru.query.filter(Guru.deleted_at.is_(None)).all()
    return render_template('admin/guru/index.html', guru_list=guru_list)


@admin_bp.route('/guru/tambah', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def tambah_guru():
    """Halaman & handler form tambah guru baru.

    Default password: 'Guru@123' (lihat ``DEFAULT_GURU_PASSWORD``).
    """
    form = GuruForm()
    if form.validate_on_submit():
        try:
            guru = Guru(
                id_guru=form.id_guru.data,
                nama_guru=form.nama_guru.data,
                mata_pelajaran=form.mata_pelajaran.data,
            )
            db.session.add(guru)
            db.session.flush()  # flush agar guru.id terisi untuk FK User.

            # Default password jika kosong: 'Guru@123' (konvensi seed).
            password = form.password.data if form.password.data else 'Guru@123'
            user = User(username=form.id_guru.data, role='guru', guru_id=guru.id)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            catat_audit_log(
                user_id=current_user.id,
                action='INSERT',
                table_name='guru',
                record_id=guru.id,
                description=f'Tambah guru {guru.nama_guru} ({guru.mata_pelajaran})',
                ip_address=request.remote_addr,
            )
            flash(f'Guru {guru.nama_guru} berhasil ditambahkan.', 'success')
            flash(f'Default login — Username: {user.username}, Password: {password}', 'info')
            return redirect(url_for('admin.daftar_guru'))
        except Exception as e:
            db.session.rollback()
            logger.exception('Gagal menambah guru')
            flash(f'Gagal menambah guru: {str(e)}', 'error')
            return redirect(url_for('admin.daftar_guru'))

    return render_template('admin/guru/form.html', form=form, title='Tambah Guru')


@admin_bp.route('/guru/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_guru(id):
    """Halaman & handler form edit guru (nama_guru & mata_pelajaran saja)."""
    guru = Guru.query.get_or_404(id)
    form = GuruForm(obj=guru)
    if form.validate_on_submit():
        guru.nama_guru = form.nama_guru.data
        guru.mata_pelajaran = form.mata_pelajaran.data
        db.session.commit()

        catat_audit_log(
            user_id=current_user.id,
            action='UPDATE',
            table_name='guru',
            record_id=guru.id,
            description=f'Edit guru {guru.nama_guru}',
            ip_address=request.remote_addr,
        )
        flash(f'Data guru {guru.nama_guru} berhasil diubah.', 'success')
        return redirect(url_for('admin.daftar_guru'))

    return render_template('admin/guru/form.html', form=form, guru=guru, title='Edit Guru')


@admin_bp.route('/guru/hapus/<int:id>', methods=['POST'])
@admin_bp.route('/guru/<int:id>/hapus', methods=['POST'])  # alias
@login_required
@role_required('admin')
def hapus_guru(id):
    """Soft-delete guru. TOLAK jika masih ada nilai yang terkunci.

    Catatan: nilai yang tidak terkunci boleh tetap ada (FK valid),
    tapi nilai terkunci akan kehilangan ``guru`` reference-nya jika
    guru dihapus paksa. Karenanya tolak hapus untuk menjaga audit trail.
    """
    guru = Guru.query.get_or_404(id)
    # Guard: tolak hapus jika ada nilai yang masih terkunci.
    locked_nilai = Nilai.query.filter_by(guru_id=id, is_locked=True).first()
    if locked_nilai:
        flash('Guru tidak dapat dihapus karena masih memiliki nilai terkunci.', 'error')
        return redirect(url_for('admin.daftar_guru'))

    guru.soft_delete()
    if guru.user:
        guru.user.is_active = False
    db.session.commit()

    catat_audit_log(
        user_id=current_user.id,
        action='DELETE',
        table_name='guru',
        record_id=guru.id,
        description=f'Hapus guru {guru.nama_guru}',
        ip_address=request.remote_addr,
    )
    flash(f'Guru {guru.nama_guru} berhasil dihapus.', 'success')
    return redirect(url_for('admin.daftar_guru'))


# ===========================================================================
# MANAJEMEN USER (ADMIN ONLY)
# ===========================================================================

@admin_bp.route('/users')
@login_required
@role_required('admin')
def daftar_user():
    """Halaman daftar semua user (admin, guru, siswa)."""
    users = User.query.all()
    return render_template('admin/users/index.html', users=users)


@admin_bp.route('/users/toggle-aktif/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def toggle_aktif_user(id):
    """Toggle status ``is_active`` user (aktif ↔ nonaktif)."""
    user = User.query.get_or_404(id)
    user.is_active = not user.is_active
    db.session.commit()

    status = 'diaktifkan' if user.is_active else 'dinonaktifkan'
    flash(f'User {user.username} berhasil {status}.', 'success')
    return redirect(url_for('admin.daftar_user'))


@admin_bp.route('/users/reset-password/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def reset_password_user(id):
    """Halaman & handler reset password user (admin only).

    GET  → Render form reset password.
    POST → Update password_hash user, audit log, redirect.
    """
    user = User.query.get_or_404(id)
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password_baru.data)
        db.session.commit()

        catat_audit_log(
            user_id=current_user.id,
            action='UPDATE',
            table_name='users',
            record_id=user.id,
            description=f'Reset password user {user.username}',
            ip_address=request.remote_addr,
        )
        flash(f'Password {user.username} berhasil direset.', 'success')
        return redirect(url_for('admin.daftar_user'))

    return render_template('admin/users/reset_password.html', form=form, user=user)


@admin_bp.route('/users/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_user(id):
    """Halaman & handler form edit profil user (username, role, is_active)."""
    user = User.query.get_or_404(id)
    form = EditUserForm(obj=user)
    if form.validate_on_submit():
        try:
            user.username = form.username.data
            user.role = form.role.data
            user.is_active = form.is_active.data
            db.session.commit()

            catat_audit_log(
                user_id=current_user.id,
                action='UPDATE',
                table_name='users',
                record_id=user.id,
                description=f'Edit user {user.username}',
                ip_address=request.remote_addr,
            )
            flash(f'User {user.username} berhasil diperbarui.', 'success')
            return redirect(url_for('admin.daftar_user'))
        except Exception as e:
            db.session.rollback()
            flash(f'Gagal memperbarui user: {str(e)}', 'error')
            return redirect(url_for('admin.daftar_user'))

    return render_template('admin/users/form.html', form=form, user=user, title='Edit User')


@admin_bp.route('/users/hapus/<int:id>', methods=['POST'])
@admin_bp.route('/users/<int:id>/hapus', methods=['POST'])  # alias
@login_required
@role_required('admin')
def hapus_user(id):
    """Hard-delete user (HARD delete, bukan soft-delete).

    PERHATIAN: Berbeda dengan hapus_siswa/hapus_guru, user di-hard-delete.
    Hanya boleh jika user tidak menghapus dirinya sendiri.
    Audit log dicatat SEBELUM delete (untuk forensik pasca-delete).
    """
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash('Tidak dapat menghapus akun sendiri.', 'error')
        return redirect(url_for('admin.daftar_user'))

    catat_audit_log(
        user_id=current_user.id,
        action='DELETE',
        table_name='users',
        record_id=user.id,
        description=f'Hapus user {user.username} ({user.role})',
        ip_address=request.remote_addr,
    )

    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.username} berhasil dihapus.', 'success')
    return redirect(url_for('admin.daftar_user'))


# ===========================================================================
# AUDIT LOG
# ===========================================================================

@admin_bp.route('/audit')
@login_required
@role_required('admin')
def audit_log():
    """Halaman viewer audit log (urut descending by created_at)."""
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).all()
    return render_template('admin/audit/index.html', logs=logs)


# ===========================================================================
# HEALTH CHECK
# ===========================================================================

@admin_bp.route('/health')
@login_required
@role_required('admin')
def health_check():
    """Endpoint health check: test koneksi DB & tampilkan env info.

    Berguna untuk monitoring & diagnostik di production. Response
    HTML (bukan JSON) agar bisa diakses manual via browser.
    """
    import time
    start = time.time()
    db_status = {}
    db_error = None
    try:
        # SELECT 1 → test koneksi paling murah.
        db.session.execute(db.text('SELECT 1'))
        elapsed = round((time.time() - start) * 1000, 2)
        db_status = {'status': 'connected', 'response_time_ms': elapsed}
    except Exception as e:
        elapsed = round((time.time() - start) * 1000, 2)
        db_status = {'status': 'error', 'response_time_ms': elapsed}
        db_error = str(e)

    healthy = db_error is None

    return render_template(
        'admin/health.html',
        healthy=healthy,
        db_status=db_status,
        db_error=db_error,
        flask_env=os.environ.get('FLASK_ENV', 'unknown'),
        timestamp=now_jakarta(),
    )


# ===========================================================================
# API ENDPOINTS (AJAX)
# ===========================================================================

@admin_bp.route('/api/siswa-by-kelas/<path:kelas>')
@login_required
@role_required('admin')
def api_siswa_by_kelas(kelas):
    """API: Ambil list siswa (JSON) berdasarkan kelas — untuk AJAX populate dropdown.

    Args:
        kelas (str): Nama kelas (path param, support nama dengan spasi/slash).

    Returns:
        Response: JSON array berisi {id, nis, nama} untuk setiap siswa aktif.
    """
    siswa_list = Siswa.query.filter(
        Siswa.kelas == kelas, Siswa.deleted_at.is_(None)
    ).order_by(Siswa.nama).all()
    return jsonify([{
        'id': s.id,
        'nis': s.nis,
        'nama': s.nama,
    } for s in siswa_list])


@admin_bp.route('/api/nilai-preview')
@login_required
@role_required('admin')
def api_nilai_preview():
    """API: Preview kalkulasi nilai akhir real-time (AJAX).

    Query params: tugas, uts, uas (semua numeric 0-100).
    Response JSON: {nilai_akhir, status_lulus, label, badge_class}
    atau error 422 jika input tidak valid.

    Endpoint ini dipanggil oleh ``static/js/nilai-preview.js`` setiap
    user mengetik di form input nilai, untuk update preview live
    sebelum submit.
    """
    try:
        tugas = float(request.args.get('tugas', 0))
        uts = float(request.args.get('uts', 0))
        uas = float(request.args.get('uas', 0))

        from app.services.nilai_service import hitung_nilai_akhir, tentukan_status_kelulusan
        nilai_akhir = hitung_nilai_akhir(tugas, uts, uas)
        status = tentukan_status_kelulusan(nilai_akhir)

        return jsonify({
            'nilai_akhir': nilai_akhir,
            'status_lulus': status['lulus'],
            'label': status['label'],
            'badge_class': status['badge_class'],
        })
    except ValueError as e:
        # Input di luar rentang 0-100 atau bukan numerik → 422 Unprocessable.
        return jsonify({'error': str(e)}), 422
    except Exception as e:
        return jsonify({'error': 'Terjadi kesalahan'}), 500


@admin_bp.route('/api/statistik-kelas/<path:kelas>')
@login_required
@role_required('admin')
def api_statistik_kelas(kelas):
    """API: Statistik agregat nilai per kelas (untuk Chart.js)."""
    data_nilai = Nilai.query.join(Siswa, Nilai.siswa_id == Siswa.id).filter(
        Siswa.kelas == kelas, Siswa.deleted_at.is_(None)
    ).all()
    from app.services.nilai_service import hitung_statistik_kelas
    stat = hitung_statistik_kelas(data_nilai)
    return jsonify(stat)
