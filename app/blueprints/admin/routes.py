import os
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
from app.forms.user_forms import TambahUserForm, ResetPasswordForm
from app.services.audit_service import catat_audit_log
from app.services.nilai_service import hitung_statistik_kelas
from sqlalchemy import func


@admin_bp.route('/dashboard')
@login_required
@role_required('admin')
def dashboard():
    total_siswa = Siswa.query.filter(Siswa.deleted_at.is_(None)).count()
    total_guru = Guru.query.filter(Guru.deleted_at.is_(None)).count()
    total_nilai = Nilai.query.count()
    total_lulus = Nilai.query.filter(Nilai.status_lulus == True).count()
    total_all_nilai = Nilai.query.filter(Nilai.status_lulus.isnot(None)).count()
    persen_lulus = round((total_lulus / total_all_nilai * 100), 1) if total_all_nilai > 0 else 0

    recent_nilai = Nilai.query.order_by(Nilai.created_at.desc()).limit(10).all()

    kelas_list = Siswa.daftar_kelas()
    chart_labels = []
    chart_data = []
    for kelas in kelas_list:
        data_nilai = Nilai.query.join(Siswa).filter(
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
                           total_tidak_lulus=total_all_nilai - total_lulus)


@admin_bp.route('/siswa')
@login_required
@role_required('admin')
def daftar_siswa():
    siswa_list = Siswa.query.filter(Siswa.deleted_at.is_(None)).all()
    return render_template('admin/siswa/index.html', siswa_list=siswa_list)


@admin_bp.route('/siswa/tambah', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def tambah_siswa():
    form = SiswaForm()
    if form.validate_on_submit():
        siswa = Siswa(nis=form.nis.data, nama=form.nama.data, kelas=form.kelas.data)
        db.session.add(siswa)
        db.session.flush()

        user = User(username=form.nis.data, role='siswa', siswa_id=siswa.id)
        user.set_password(form.nis.data)
        db.session.add(user)
        db.session.commit()

        catat_audit_log(
            user_id=current_user.id,
            action='INSERT',
            table_name='siswa',
            record_id=siswa.id,
            description=f'Tambah siswa {siswa.nama} (NIS: {siswa.nis})',
            ip_address=request.remote_addr,
        )
        flash(f'Siswa {siswa.nama} berhasil ditambahkan.', 'success')
        return redirect(url_for('admin.daftar_siswa'))

    return render_template('admin/siswa/form.html', form=form, title='Tambah Siswa')


@admin_bp.route('/siswa/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_siswa(id):
    siswa = Siswa.query.get_or_404(id)
    form = SiswaForm(obj=siswa)
    if form.validate_on_submit():
        siswa.nama = form.nama.data
        siswa.kelas = form.kelas.data
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

    form.nis.render_kw = {'disabled': True}
    return render_template('admin/siswa/form.html', form=form, siswa=siswa, title='Edit Siswa')


@admin_bp.route('/siswa/hapus/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def hapus_siswa(id):
    siswa = Siswa.query.get_or_404(id)
    siswa.soft_delete()
    if siswa.user:
        siswa.user.is_active = False
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
    siswa = Siswa.query.get_or_404(id)
    nilai_list = Nilai.query.filter_by(siswa_id=id).all()
    return render_template('admin/siswa/detail.html', siswa=siswa, nilai_list=nilai_list)


@admin_bp.route('/guru')
@login_required
@role_required('admin')
def daftar_guru():
    guru_list = Guru.query.filter(Guru.deleted_at.is_(None)).all()
    return render_template('admin/guru/index.html', guru_list=guru_list)


@admin_bp.route('/guru/tambah', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def tambah_guru():
    form = GuruForm()
    if form.validate_on_submit():
        guru = Guru(
            id_guru=form.id_guru.data,
            nama_guru=form.nama_guru.data,
            mata_pelajaran=form.mata_pelajaran.data,
        )
        db.session.add(guru)
        db.session.flush()

        user = User(username=form.id_guru.data, role='guru', guru_id=guru.id)
        user.set_password(form.id_guru.data)
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
        return redirect(url_for('admin.daftar_guru'))

    return render_template('admin/guru/form.html', form=form, title='Tambah Guru')


@admin_bp.route('/guru/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_guru(id):
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
@login_required
@role_required('admin')
def hapus_guru(id):
    guru = Guru.query.get_or_404(id)
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


@admin_bp.route('/users')
@login_required
@role_required('admin')
def daftar_user():
    users = User.query.all()
    return render_template('admin/users/index.html', users=users)


@admin_bp.route('/users/toggle-aktif/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def toggle_aktif_user(id):
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


@admin_bp.route('/audit')
@login_required
@role_required('admin')
def audit_log():
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).all()
    return render_template('admin/audit/index.html', logs=logs)


# --- Health Check ---

@admin_bp.route('/health')
@login_required
@role_required('admin')
def health_check():
    import time
    start = time.time()
    db_status = {}
    db_error = None
    try:
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


# --- API Endpoints ---

@admin_bp.route('/api/siswa-by-kelas/<kelas>')
@login_required
def api_siswa_by_kelas(kelas):
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
def api_nilai_preview():
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
        return jsonify({'error': str(e)}), 422
    except Exception as e:
        return jsonify({'error': 'Terjadi kesalahan'}), 500


@admin_bp.route('/api/statistik-kelas/<kelas>')
@login_required
def api_statistik_kelas(kelas):
    data_nilai = Nilai.query.join(Siswa).filter(
        Siswa.kelas == kelas, Siswa.deleted_at.is_(None)
    ).all()
    from app.services.nilai_service import hitung_statistik_kelas
    stat = hitung_statistik_kelas(data_nilai)
    return jsonify(stat)
