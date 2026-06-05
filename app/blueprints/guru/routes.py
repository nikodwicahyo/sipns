"""
Modul: blueprints/guru/routes.py
Deskripsi: Route handler untuk modul Guru (input & kelola nilai).

Endpoint:
- ``GET     /guru/dashboard``       → Dashboard guru.
- ``GET/POST /guru/nilai/input``    → Form input nilai baru.
- ``GET/POST /guru/nilai/edit/<id>``→ Form edit nilai (jika belum dikunci).
- ``POST    /guru/nilai/kunci/<id>``→ Kunci nilai (set is_locked=True).
- ``GET     /guru/nilai/rekap``     → Rekap nilai kelas yang diampu.

Aturan bisnis:
- Guru hanya bisa input/edit nilai untuk mata pelajaran yang DIAMPU
  (lihat ``Guru.mata_pelajaran``).
- Nilai yang sudah ``is_locked=True`` tidak bisa diubah (kecuali admin).

Author : Niko Dwicahyo
Versi  : 1.0.0
"""
import logging
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

logger = logging.getLogger(__name__)


# ===========================================================================
# DASHBOARD GURU
# ===========================================================================

@guru_bp.route('/dashboard')
@login_required
@role_required('guru')
def dashboard():
    """Halaman dashboard guru: info mapel, total siswa, kelas yang diampu.

    Menghitung:
    - Total siswa unik yang pernah dinilai guru ini.
    - Daftar kelas (distinct) yang pernah dinilai guru ini.
    """
    guru = Guru.query.get(current_user.guru_id)
    if not guru:
        flash('Data guru tidak ditemukan.', 'error')
        return redirect(url_for('auth.login'))

    # Count distinct siswa_id dari tabel nilai where guru_id = guru.id.
    total_siswa = db.session.query(func.count(func.distinct(Nilai.siswa_id))).filter(
        Nilai.guru_id == guru.id
    ).scalar() or 0

    # Ambil daftar kelas (distinct) yang pernah dinilai guru ini.
    kelas_tercatat = db.session.query(Siswa.kelas).join(Nilai, Nilai.siswa_id == Siswa.id).filter(
        Nilai.guru_id == guru.id, Siswa.deleted_at.is_(None)
    ).distinct().all()
    kelas_list = [k[0] for k in kelas_tercatat]

    return render_template('guru/dashboard.html',
                           guru=guru,
                           total_siswa=total_siswa,
                           kelas_list=kelas_list,
                           mata_pelajaran=guru.mata_pelajaran)


# ===========================================================================
# INPUT & KELOLA NILAI
# ===========================================================================

@guru_bp.route('/nilai/input', methods=['GET', 'POST'])
@login_required
@role_required('guru')
def input_nilai():
    """Halaman & handler form input nilai baru (atau update nilai existing).

    Flow:
    1. Ambil data guru yang sedang login (untuk ``mata_pelajaran``).
    2. GET: populate dropdown siswa (semua siswa aktif).
    3. POST: cek apakah nilai untuk (siswa_id, mapel) sudah ada.
       - Ada & locked → flash error (tidak bisa diubah).
       - Ada & not locked → UPDATE nilai existing.
       - Tidak ada → INSERT nilai baru.
    4. Panggil ``nilai.hitung_dan_simpan()`` (integrasi OOP ↔ terstruktur).
    5. Commit, audit log, flash, redirect.
    """
    guru = Guru.query.get(current_user.guru_id)
    if not guru:
        flash('Data guru tidak ditemukan.', 'error')
        return redirect(url_for('guru.dashboard'))

    form = NilaiForm()
    kelas_list = Siswa.daftar_kelas()
    siswa_list = Siswa.query.filter(Siswa.deleted_at.is_(None)).all()
    # Choices untuk SelectField siswa: format "NIS - Nama (Kelas)".
    form.siswa_id.choices = [(s.id, f'{s.nis} - {s.nama} ({s.kelas})') for s in siswa_list]

    if form.validate_on_submit():
        # Cek apakah nilai untuk (siswa, mapel) sudah ada.
        existing = Nilai.query.filter_by(
            siswa_id=form.siswa_id.data,
            mata_pelajaran=guru.mata_pelajaran,
        ).first()

        if existing and existing.is_locked:
            flash('Nilai sudah terkunci dan tidak dapat diubah.', 'error')
            return redirect(url_for('guru.input_nilai'))

        if existing:
            # Update nilai existing (tidak insert baru).
            nilai = existing
            nilai.nilai_tugas = form.nilai_tugas.data
            nilai.nilai_uts = form.nilai_uts.data
            nilai.nilai_uas = form.nilai_uas.data
            action = 'UPDATE'
        else:
            # Insert nilai baru.
            nilai = Nilai(
                siswa_id=form.siswa_id.data,
                guru_id=guru.id,
                mata_pelajaran=guru.mata_pelajaran,
                nilai_tugas=form.nilai_tugas.data,
                nilai_uts=form.nilai_uts.data,
                nilai_uas=form.nilai_uas.data,
            )
            action = 'INSERT'

        # Hitung nilai_akhir & status_lulus via service terstruktur.
        nilai.hitung_dan_simpan()
        db.session.add(nilai)
        db.session.commit()

        catat_audit_log(
            user_id=current_user.id,
            action=action,
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
    """Halaman & handler form edit nilai.

    Guard: tolak edit jika ``is_locked=True``. Hanya field nilai
    (tugas/uts/uas) yang diedit — siswa_id & mata_pelajaran immutable.
    """
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
        nilai.hitung_dan_simpan()  # recalculate nilai_akhir.
        db.session.commit()

        flash('Nilai berhasil diperbarui.', 'success')
        return redirect(url_for('guru.rekap_nilai'))

    return render_template('guru/nilai/input.html', form=form, guru=guru, edit_mode=True)


@guru_bp.route('/nilai/kunci/<int:id>', methods=['POST'])
@login_required
@role_required('guru')
def kunci_nilai(id):
    """Kunci nilai (``is_locked = True``).

    Setelah dikunci, nilai tidak bisa diubah oleh guru (lihat ``edit_nilai``).
    Hanya admin yang bisa unlock (lihat backlog BL-007).
    """
    nilai = Nilai.query.get_or_404(id)
    nilai.lock()  # idempotent: no-op jika sudah locked.
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
    """Halaman rekap nilai kelas yang diampu guru.

    Menampilkan tabel nilai semua siswa yang pernah dinilai guru ini
    (diurutkan by kelas, nama), dengan badge status lulus & tombol
    kunci nilai per baris.
    """
    guru = Guru.query.get(current_user.guru_id)
    kelas_list = Siswa.daftar_kelas()

    # Query nilai guru ini, JOIN siswa (exclude soft-deleted).
    data_nilai = (
        Nilai.query
        .filter_by(guru_id=guru.id)
        .join(Siswa, Nilai.siswa_id == Siswa.id)
        .filter(Siswa.deleted_at.is_(None))
        .order_by(Siswa.kelas, Siswa.nama)
        .all()
    )

    # Statistik agregat untuk header halaman.
    statistik = hitung_statistik_kelas(data_nilai)

    return render_template('guru/nilai/rekap.html',
                           guru=guru,
                           data_nilai=data_nilai,
                           statistik=statistik,
                           kelas_list=kelas_list)


# ===========================================================================
# API ENDPOINTS (AJAX) — GURU
# ===========================================================================
#
# Endpoint AJAX di blueprint ``admin`` di-harden dengan
# ``@role_required('admin')`` (lihat ``app/blueprints/admin/routes.py``).
# Untuk mempertahankan fungsionalitas input nilai oleh guru (dropdown
# siswa berdasarkan kelas + preview kalkulasi), tersedia endpoint
# paralel di blueprint ini yang diizinkan untuk role ``guru``.

@guru_bp.route('/api/siswa-by-kelas/<path:kelas>')
@login_required
@role_required('guru')
def api_siswa_by_kelas(kelas):
    """API (guru): list siswa (JSON) berdasarkan kelas untuk AJAX dropdown.

    Args:
        kelas (str): Nama kelas (path param, support nama dengan spasi/slash).

    Returns:
        Response: JSON array berisi ``{id, nis, nama, kelas}`` untuk
        setiap siswa aktif (tidak soft-deleted). Digunakan oleh
        ``guru/nilai/input.html`` saat guru memilih kelas untuk
        mem-populate dropdown siswa.
    """
    siswa_list = Siswa.query.filter(
        Siswa.kelas == kelas, Siswa.deleted_at.is_(None)
    ).order_by(Siswa.nama).all()
    return jsonify([{
        'id': s.id,
        'nis': s.nis,
        'nama': s.nama,
        'kelas': s.kelas,
    } for s in siswa_list])


@guru_bp.route('/api/nilai-preview')
@login_required
@role_required('guru')
def api_nilai_preview():
    """API (guru): preview kalkulasi nilai akhir real-time (AJAX).

    Query params: ``tugas``, ``uts``, ``uas`` (semua numeric 0-100).
    Response JSON: ``{nilai_akhir, status_lulus, label, badge_class}``
    atau error 422 jika input tidak valid.

    Digunakan oleh ``guru/nilai/input.html`` setiap guru mengetik di
    form input nilai, untuk update preview live sebelum submit.
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
        return jsonify({'error': str(e)}), 422
    except Exception:
        return jsonify({'error': 'Terjadi kesalahan'}), 500
