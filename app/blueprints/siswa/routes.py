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
    """Halaman dashboard siswa: ringkasan nilai pribadi & status kelulusan.

    Guard: jika user tidak terkait Siswa (orphan account) → flash & logout.
    """
    siswa = Siswa.query.get(current_user.siswa_id)
    if not siswa:
        flash('Data siswa tidak ditemukan.', 'error')
        return redirect(url_for('auth.login'))

    # Ambil semua nilai siswa ini + hitung statistik agregat.
    nilai_list = Nilai.query.filter_by(siswa_id=siswa.id).all()
    stat = hitung_statistik_kelas(nilai_list)

    return render_template('siswa/dashboard.html',
                           siswa=siswa,
                           nilai_list=nilai_list,
                           stat=stat)


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
