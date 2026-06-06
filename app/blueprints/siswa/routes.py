"""
Modul: blueprints/siswa/routes.py
Deskripsi: Route handler untuk modul Siswa (lihat nilai pribadi).

Endpoint:
- ``GET /siswa/dashboard``              → Dashboard siswa (nilai pribadi).
- ``GET /siswa/nilai``                  → Tabel nilai semua mapel.
- ``GET /siswa/nilai/<id>/detail``      → Rincian kalkulasi 1 nilai.

Akses:
- Hanya siswa yang bisa akses (``@role_required('siswa')``).
- Siswa hanya bisa lihat nilai MILIKNYA sendiri (cek ``current_user.siswa_id``).

Author : Niko Dwicahyo
Versi  : 1.0.0
"""
import logging
from flask import render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from app.blueprints.siswa import siswa_bp
from app.blueprints.decorators import role_required
from app import db
from app.models import Siswa, Nilai
from app.services.nilai_service import hitung_statistik_kelas

logger = logging.getLogger(__name__)


# ===========================================================================
# DASHBOARD SISWA
# ===========================================================================

@siswa_bp.route('/dashboard')
@login_required
@role_required('siswa')
def dashboard():
    """Halaman dashboard siswa: ringkasan nilai pribadi & visualisasi.

    Guard: jika user tidak terkait Siswa (orphan account) → flash & logout.
    Menghitung:
    - Statistik agregat nilai siswa.
    - Status kelulusan global (semua mapel Lulus / Tidak Lulus).
    - Total mata pelajaran yang sudah dinilai.
    - Chart data: perbandingan nilai per mapel (radar) + rasio kelulusan (doughnut).
    """
    siswa = Siswa.query.get(current_user.siswa_id)
    if not siswa:
        flash('Data siswa tidak ditemukan.', 'error')
        return redirect(url_for('auth.login'))

    # Ambil semua nilai siswa ini + hitung statistik agregat.
    nilai_list = Nilai.query.filter_by(siswa_id=siswa.id).all()
    stat = hitung_statistik_kelas(nilai_list)

    # Precompute status global dari nilai_list yang sudah di-load
    # untuk menghindari query ulang dari template via siswa.status_kelulusan_global().
    records = [n for n in nilai_list if n.status_lulus is not None]
    if not records:
        status_global = 'Belum Ada Nilai'
    else:
        status_global = 'Lulus' if all(n.status_lulus for n in records) else 'Tidak Lulus'

    # Total mata pelajaran unik yang sudah dinilai.
    total_mapel = len({n.mata_pelajaran for n in nilai_list if n.mata_pelajaran})

    # Counts kelulusan untuk doughnut chart.
    total_lulus = sum(1 for n in nilai_list if n.status_lulus is True)
    total_tidak_lulus = sum(1 for n in nilai_list if n.status_lulus is False)

    # Chart data: nilai per mapel (untuk radar chart).
    # Diurutkan berdasarkan nama mapel untuk konsistensi visual.
    mapel_nilai_pairs = sorted(
        [
            (n.mata_pelajaran, float(n.nilai_akhir))
            for n in nilai_list
            if n.nilai_akhir is not None and n.mata_pelajaran
        ],
        key=lambda x: x[0],
    )
    chart_labels = [p[0] for p in mapel_nilai_pairs]
    chart_data = [p[1] for p in mapel_nilai_pairs]

    return render_template(
        'siswa/dashboard.html',
        siswa=siswa,
        nilai_list=nilai_list,
        stat=stat,
        status_global=status_global,
        total_mapel=total_mapel,
        total_lulus=total_lulus,
        total_tidak_lulus=total_tidak_lulus,
        chart_labels=chart_labels,
        chart_data=chart_data,
    )


# ===========================================================================
# NILAI SAYA
# ===========================================================================

@siswa_bp.route('/nilai')
@login_required
@role_required('siswa')
def nilai_saya():
    """Halaman daftar nilai siswa (semua mata pelajaran).

    Menampilkan tabel nilai per mapel dengan badge status lulus
    & tombol "Unduh Transkrip PDF".
    """
    siswa = Siswa.query.get(current_user.siswa_id)
    nilai_list = Nilai.query.filter_by(siswa_id=siswa.id).all()

    return render_template('siswa/nilai.html',
                           siswa=siswa,
                           nilai_list=nilai_list)


@siswa_bp.route('/nilai/<int:nilai_id>/detail')
@login_required
@role_required('siswa')
def detail_nilai(nilai_id):
    """Halaman detail kalkulasi satu nilai (rincian bobot 30/30/40).

    Guard: tolak akses jika ``nilai.siswa_id != current_user.siswa_id``
    (siswa hanya boleh lihat nilai sendiri).
    """
    nilai = Nilai.query.get_or_404(nilai_id)
    if nilai.siswa_id != current_user.siswa_id:
        abort(403)

    detail = nilai.get_detail_kalkulasi()
    return render_template('siswa/nilai_detail.html', nilai=nilai, detail=detail)
