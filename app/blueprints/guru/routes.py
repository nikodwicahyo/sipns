from flask import render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from app.blueprints.guru import guru_bp
from app.blueprints.decorators import role_required
from app import db
from app.models import Siswa, Guru, Nilai
from app.forms.nilai_forms import NilaiForm
from app.services.audit_service import catat_audit_log
from app.services.nilai_service import hitung_statistik_kelas
from sqlalchemy import func


@guru_bp.route('/dashboard')
@login_required
@role_required('guru')
def dashboard():
    guru = Guru.query.get(current_user.guru_id)
    if not guru:
        flash('Data guru tidak ditemukan.', 'error')
        return redirect(url_for('auth.login'))

    total_siswa = db.session.query(func.count(func.distinct(Nilai.siswa_id))).filter(
        Nilai.guru_id == guru.id
    ).scalar() or 0

    kelas_tercatat = db.session.query(Siswa.kelas).join(Nilai, Nilai.siswa_id == Siswa.id).filter(
        Nilai.guru_id == guru.id, Siswa.deleted_at.is_(None)
    ).distinct().all()
    kelas_list = [k[0] for k in kelas_tercatat]

    return render_template('guru/dashboard.html',
                           guru=guru,
                           total_siswa=total_siswa,
                           kelas_list=kelas_list,
                           mata_pelajaran=guru.mata_pelajaran)


@guru_bp.route('/nilai/input', methods=['GET', 'POST'])
@login_required
@role_required('guru')
def input_nilai():
    guru = Guru.query.get(current_user.guru_id)
    if not guru:
        flash('Data guru tidak ditemukan.', 'error')
        return redirect(url_for('guru.dashboard'))

    form = NilaiForm()
    kelas_list = Siswa.daftar_kelas()
    siswa_list = Siswa.query.filter(Siswa.deleted_at.is_(None)).all()
    form.siswa_id.choices = [(s.id, f'{s.nis} - {s.nama} ({s.kelas})') for s in siswa_list]

    if form.validate_on_submit():
        existing = Nilai.query.filter_by(
            siswa_id=form.siswa_id.data,
            mata_pelajaran=guru.mata_pelajaran,
        ).first()

        if existing and existing.is_locked:
            flash('Nilai sudah terkunci dan tidak dapat diubah.', 'error')
            return redirect(url_for('guru.input_nilai'))

        if existing:
            nilai = existing
            nilai.nilai_tugas = form.nilai_tugas.data
            nilai.nilai_uts = form.nilai_uts.data
            nilai.nilai_uas = form.nilai_uas.data
        else:
            nilai = Nilai(
                siswa_id=form.siswa_id.data,
                guru_id=guru.id,
                mata_pelajaran=guru.mata_pelajaran,
                nilai_tugas=form.nilai_tugas.data,
                nilai_uts=form.nilai_uts.data,
                nilai_uas=form.nilai_uas.data,
            )

        nilai.hitung_dan_simpan()
        db.session.add(nilai)
        db.session.commit()

        catat_audit_log(
            user_id=current_user.id,
            action='INSERT' if not existing else 'UPDATE',
            table_name='nilai',
            record_id=nilai.id,
            description=f'Nilai {guru.mata_pelajaran} untuk siswa ID {nilai.siswa_id}',
            ip_address=request.remote_addr,
        )

        flash(f'Nilai {guru.mata_pelajaran} berhasil disimpan.', 'success')
        return redirect(url_for('guru.input_nilai'))

    return render_template('guru/nilai/input.html', form=form, guru=guru, kelas_list=kelas_list)


@guru_bp.route('/nilai/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('guru')
def edit_nilai(id):
    nilai = Nilai.query.get_or_404(id)
    if nilai.is_locked:
        flash('Nilai sudah terkunci dan tidak dapat diubah.', 'error')
        return redirect(url_for('guru.rekap_nilai'))

    guru = Guru.query.get(current_user.guru_id)
    form = NilaiForm(obj=nilai)

    siswa_list = Siswa.query.filter(Siswa.deleted_at.is_(None)).all()
    form.siswa_id.choices = [(s.id, f'{s.nis} - {s.nama}') for s in siswa_list]

    if form.validate_on_submit():
        nilai.nilai_tugas = form.nilai_tugas.data
        nilai.nilai_uts = form.nilai_uts.data
        nilai.nilai_uas = form.nilai_uas.data
        nilai.hitung_dan_simpan()
        db.session.commit()

        flash('Nilai berhasil diperbarui.', 'success')
        return redirect(url_for('guru.rekap_nilai'))

    return render_template('guru/nilai/input.html', form=form, guru=guru, edit_mode=True)


@guru_bp.route('/nilai/kunci/<int:id>', methods=['POST'])
@login_required
@role_required('guru')
def kunci_nilai(id):
    nilai = Nilai.query.get_or_404(id)
    nilai.lock()
    db.session.commit()

    catat_audit_log(
        user_id=current_user.id,
        action='UPDATE',
        table_name='nilai',
        record_id=nilai.id,
        description=f'Kunci nilai {nilai.mata_pelajaran} siswa ID {nilai.siswa_id}',
        ip_address=request.remote_addr,
    )

    flash('Nilai berhasil dikunci.', 'success')
    return redirect(url_for('guru.rekap_nilai'))


@guru_bp.route('/nilai/rekap')
@login_required
@role_required('guru')
def rekap_nilai():
    guru = Guru.query.get(current_user.guru_id)
    kelas_list = Siswa.daftar_kelas()

    data_nilai = Nilai.query.filter_by(guru_id=guru.id).join(Siswa, Nilai.siswa_id == Siswa.id).filter(
        Siswa.deleted_at.is_(None)
    ).order_by(Siswa.kelas, Siswa.nama).all()

    statistik = hitung_statistik_kelas(data_nilai)

    return render_template('guru/nilai/rekap.html',
                           guru=guru,
                           data_nilai=data_nilai,
                           statistik=statistik,
                           kelas_list=kelas_list)
