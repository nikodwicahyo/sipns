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
from sqlalchemy import func, case

logger = logging.getLogger(__name__)


# ===========================================================================
# DASHBOARD GURU
# ===========================================================================

@guru_bp.route('/dashboard')
@login_required
@role_required('guru')
def dashboard():
    """Halaman dashboard guru: ringkasan nilai & aktivitas mengajar.

    Menghitung (sesuai akun guru yang login):
    - Total siswa aktif di kelas-kelas yang diajar (belum tentu dinilai).
    - Daftar kelas (distinct) yang pernah dinilai.
    - Siswa yang sudah dinilai (distinct) vs siswa yang belum dinilai.
    - Total record nilai, rata-rata, kelulusan.
    - Chart data: rata-rata nilai per kelas.
    - 10 nilai terbaru untuk tabel ringkasan.
    """
    guru = Guru.query.get(current_user.guru_id)
    if not guru:
        flash('Data guru tidak ditemukan.', 'error')
        return redirect(url_for('auth.login'))

    # Base filter: hanya nilai yang diinput oleh guru ini.
    base_filter = [Nilai.guru_id == guru.id]

    # 1. Daftar kelas (distinct) yang pernah dinilai guru ini.
    #    Digunakan juga untuk menghitung total siswa di kelas yang diajar.
    kelas_tercatat = (
        db.session.query(Siswa.kelas)
        .join(Nilai, Nilai.siswa_id == Siswa.id)
        .filter(*base_filter, Siswa.deleted_at.is_(None))
        .distinct()
        .all()
    )
    kelas_list = [k[0] for k in kelas_tercatat]

    # 2. Total siswa aktif di kelas-kelas yang diajar guru ini.
    #    Inklusi siswa yang belum dinilai (mereka adalah "belum dinilai").
    if kelas_list:
        total_siswa = (
            db.session.query(func.count(Siswa.id))
            .filter(Siswa.kelas.in_(kelas_list), Siswa.deleted_at.is_(None))
            .scalar()
            or 0
        )
    else:
        # Guru belum pernah menginput nilai => belum diketahui kelas
        # yang diajar => 0 siswa (tidak menampilkan total siswa dari
        # kelas yang tidak terkait dengan guru ini).
        total_siswa = 0

    # 3. Siswa yang sudah memiliki nilai dari guru ini (distinct siswa_id).
    siswa_dinilai = (
        db.session.query(func.count(func.distinct(Nilai.siswa_id)))
        .filter(*base_filter)
        .scalar()
        or 0
    )

    # 4. Siswa yang belum dinilai (di kelas yang sama dengan yang diajar).
    siswa_belum_dinilai = max(total_siswa - siswa_dinilai, 0)

    # 5. Statistik agregat: total nilai, rata-rata, kelulusan.
    agg = (
        db.session.query(
            func.count(Nilai.id).label('total'),
            func.avg(Nilai.nilai_akhir).label('rata_rata'),
            func.count(case((Nilai.status_lulus.is_(True), 1))).label('lulus'),
            func.count(case((Nilai.status_lulus.is_(False), 1))).label('tidak_lulus'),
        )
        .filter(*base_filter)
        .first()
    )
    total_nilai = int(agg.total or 0)
    rata_rata = round(float(agg.rata_rata), 2) if agg.rata_rata is not None else 0
    total_lulus = int(agg.lulus or 0)
    total_tidak_lulus = int(agg.tidak_lulus or 0)
    persen_lulus = (
        round((total_lulus / total_nilai * 100), 1)
        if total_nilai > 0
        else 0
    )

    # 6. 10 nilai terbaru (eagerload siswa untuk mencegah N+1 di template).
    recent_nilai = (
        Nilai.query
        .options(db.joinedload(Nilai.siswa))
        .filter(*base_filter)
        .order_by(Nilai.created_at.desc())
        .limit(10)
        .all()
    )

    # 7. Chart data: rata-rata nilai per kelas (satu GROUP BY query).
    chart_rows = (
        db.session.query(
            Siswa.kelas.label('kelas'),
            func.avg(Nilai.nilai_akhir).label('rata_rata'),
        )
        .join(Nilai, Nilai.siswa_id == Siswa.id)
        .filter(
            *base_filter,
            Siswa.deleted_at.is_(None),
            Nilai.nilai_akhir.isnot(None),
        )
        .group_by(Siswa.kelas)
        .order_by(Siswa.kelas)
        .all()
    )
    chart_labels = [r.kelas for r in chart_rows]
    chart_data = [
        round(float(r.rata_rata), 2) if r.rata_rata is not None else 0
        for r in chart_rows
    ]

    return render_template(
        'guru/dashboard.html',
        guru=guru,
        mata_pelajaran=guru.mata_pelajaran,
        total_siswa=total_siswa,
        siswa_dinilai=siswa_dinilai,
        siswa_belum_dinilai=siswa_belum_dinilai,
        kelas_list=kelas_list,
        rata_rata=rata_rata,
        total_lulus=total_lulus,
        total_tidak_lulus=total_tidak_lulus,
        persen_lulus=persen_lulus,
        recent_nilai=recent_nilai,
        chart_labels=chart_labels,
        chart_data=chart_data,
    )


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

    if request.method == 'POST':
        siswa_choices = (
            Siswa.query
            .filter(Siswa.deleted_at.is_(None))
            .order_by(Siswa.kelas, Siswa.nama)
            .all()
        )
        form.siswa_id.choices = [
            (s.id, f'{s.nis} - {s.nama} ({s.kelas})') for s in siswa_choices
        ]
    else:
        form.siswa_id.choices = []

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

    return render_template(
        'guru/nilai/input.html',
        form=form,
        guru=guru,
        kelas_list=kelas_list,
        selected_kelas=None,
    )


@guru_bp.route('/nilai/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('guru')
def edit_nilai(id):
    """Halaman & handler form edit nilai.

    Guard: tolak edit jika ``is_locked=True``. Hanya field nilai
    (tugas/uts/uas) yang diedit — siswa_id & mata_pelajaran immutable.
    """
    nilai = Nilai.query.options(db.joinedload(Nilai.siswa)).get_or_404(id)
    if nilai.is_locked:
        flash('Nilai sudah terkunci dan tidak dapat diubah.', 'error')
        return redirect(url_for('guru.rekap_nilai'))

    guru = Guru.query.get(current_user.guru_id)
    form = NilaiForm(obj=nilai)

    form.siswa_id.choices = [(nilai.siswa_id, f'{nilai.siswa.nis} - {nilai.siswa.nama}')] if nilai.siswa else []

    if form.validate_on_submit():
        nilai.nilai_tugas = form.nilai_tugas.data
        nilai.nilai_uts = form.nilai_uts.data
        nilai.nilai_uas = form.nilai_uas.data
        nilai.hitung_dan_simpan()  # recalculate nilai_akhir.
        db.session.commit()

        flash('Nilai berhasil diperbarui.', 'success')
        return redirect(url_for('guru.rekap_nilai'))

    return render_template(
        'guru/nilai/edit.html',
        form=form,
        guru=guru,
        nilai=nilai,
    )


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
        .options(db.joinedload(Nilai.siswa))
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


@guru_bp.route('/api/cek-nilai')
@login_required
@role_required('guru')
def api_cek_nilai():
    """API (guru): cek apakah siswa sudah punya nilai untuk mapel guru.

    Dipanggil oleh ``guru/nilai/input.html`` setiap kali guru memilih
    siswa di dropdown, untuk menampilkan info UI (sebelum submit):
    - ``exists=False``  → "Belum ada nilai, akan dibuat baru."
    - ``exists=True`` & ``is_locked=False`` → "Sudah ada nilai (T/UTS/UAS),
        submit akan MENGUBAH nilai existing." + tombol shortcut ke edit.
    - ``exists=True`` & ``is_locked=True``  → "Nilai terkunci, tidak
        dapat diubah. Gunakan halaman edit / hubungi admin."

    Query params:
        siswa_id (int, required): Primary key siswa.

    Returns:
        Response: JSON ``{exists, is_locked, nilai_id, nilai_tugas,
        nilai_uts, nilai_uas, nilai_akhir, status_lulus}``. Field nilai
        di-cast ke ``float`` agar JSON-encodable. Return 400 jika
        ``siswa_id`` kosong/invalid, 404 jika siswa tidak ditemukan.
    """
    siswa_id = request.args.get('siswa_id', type=int)
    if not siswa_id:
        return jsonify({'error': 'siswa_id wajib diisi'}), 400

    siswa = Siswa.query.get(siswa_id)
    if not siswa or siswa.deleted_at is not None:
        return jsonify({'error': 'Siswa tidak ditemukan'}), 404

    guru = Guru.query.get(current_user.guru_id)
    if not guru:
        return jsonify({'error': 'Data guru tidak ditemukan'}), 404

    existing = Nilai.query.filter_by(
        siswa_id=siswa_id,
        mata_pelajaran=guru.mata_pelajaran,
    ).first()

    if not existing:
        return jsonify({
            'exists': False,
            'is_locked': False,
            'nilai_id': None,
            'nilai_tugas': None,
            'nilai_uts': None,
            'nilai_uas': None,
            'nilai_akhir': None,
            'status_lulus': None,
        })

    return jsonify({
        'exists': True,
        'is_locked': bool(existing.is_locked),
        'nilai_id': existing.id,
        'nilai_tugas': float(existing.nilai_tugas) if existing.nilai_tugas is not None else None,
        'nilai_uts': float(existing.nilai_uts) if existing.nilai_uts is not None else None,
        'nilai_uas': float(existing.nilai_uas) if existing.nilai_uas is not None else None,
        'nilai_akhir': float(existing.nilai_akhir) if existing.nilai_akhir is not None else None,
        'status_lulus': bool(existing.status_lulus) if existing.status_lulus is not None else None,
    })
