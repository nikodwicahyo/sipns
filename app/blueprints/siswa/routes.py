from flask import render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from app.blueprints.siswa import siswa_bp
from app.blueprints.decorators import role_required
from app import db
from app.models import Siswa, Nilai
from app.services.nilai_service import hitung_statistik_kelas


@siswa_bp.route('/dashboard')
@login_required
@role_required('siswa')
def dashboard():
    siswa = Siswa.query.get(current_user.siswa_id)
    if not siswa:
        flash('Data siswa tidak ditemukan.', 'error')
        return redirect(url_for('auth.login'))

    nilai_list = Nilai.query.filter_by(siswa_id=siswa.id).all()
    stat = hitung_statistik_kelas(nilai_list)

    return render_template('siswa/dashboard.html',
                           siswa=siswa,
                           nilai_list=nilai_list,
                           stat=stat)


@siswa_bp.route('/nilai')
@login_required
@role_required('siswa')
def nilai_saya():
    siswa = Siswa.query.get(current_user.siswa_id)
    nilai_list = Nilai.query.filter_by(siswa_id=siswa.id).all()

    return render_template('siswa/nilai.html',
                           siswa=siswa,
                           nilai_list=nilai_list)


@siswa_bp.route('/nilai/<int:nilai_id>/detail')
@login_required
@role_required('siswa')
def detail_nilai(nilai_id):
    nilai = Nilai.query.get_or_404(nilai_id)
    if nilai.siswa_id != current_user.siswa_id:
        abort(403)

    detail = nilai.get_detail_kalkulasi()
    return render_template('siswa/nilai_detail.html', nilai=nilai, detail=detail)
