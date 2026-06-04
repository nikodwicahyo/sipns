from flask import render_template, Response, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.blueprints.laporan import laporan_bp
from app.blueprints.decorators import role_required
from app import db
from app.models import Siswa, Nilai
from app.services.laporan_service import generate_laporan_pdf, generate_transkrip_pdf, export_excel
from datetime import datetime


@laporan_bp.route('/rekap-kelas')
@login_required
def index():
    kelas_list = Siswa.daftar_kelas()
    return render_template('laporan/index.html', kelas_list=kelas_list)


@laporan_bp.route('/pdf/kelas/<kelas>')
@login_required
def pdf_kelas(kelas):
    if current_user.is_siswa():
        abort(403)

    try:
        pdf_bytes = generate_laporan_pdf(kelas)
        tanggal = datetime.now().strftime('%Y%m%d')
        return Response(
            pdf_bytes,
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename=rekap_{kelas}_{tanggal}.pdf'
            },
        )
    except Exception as e:
        flash(f'Gagal generate PDF: {str(e)}', 'error')
        return redirect(url_for('laporan.index'))


@laporan_bp.route('/pdf/transkrip/<int:siswa_id>')
@login_required
def pdf_transkrip(siswa_id):
    if current_user.is_siswa() and current_user.siswa_id != siswa_id:
        abort(403)

    try:
        pdf_bytes = generate_transkrip_pdf(siswa_id)
        tanggal = datetime.now().strftime('%Y%m%d')
        siswa = Siswa.query.get_or_404(siswa_id)
        return Response(
            pdf_bytes,
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename=transkrip_{siswa.nis}_{tanggal}.pdf'
            },
        )
    except Exception as e:
        flash(f'Gagal generate PDF: {str(e)}', 'error')
        return redirect(url_for('laporan.index'))


@laporan_bp.route('/excel')
@login_required
def excel():
    if current_user.is_siswa():
        abort(403)

    kelas = request.args.get('kelas')
    try:
        excel_bytes = export_excel(kelas)
        tanggal = datetime.now().strftime('%Y%m%d')
        filename = f'nilai_{kelas if kelas else "semua"}_{tanggal}.xlsx'
        return Response(
            excel_bytes,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={
                'Content-Disposition': f'attachment; filename={filename}'
            },
        )
    except Exception as e:
        flash(f'Gagal ekspor Excel: {str(e)}', 'error')
        return redirect(url_for('laporan.index'))
