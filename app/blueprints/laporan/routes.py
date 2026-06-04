from flask import render_template, Response, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.blueprints.laporan import laporan_bp
from app.blueprints.decorators import role_required
from app import db
from app.models import Siswa, Nilai
from app.services.laporan_service import generate_laporan_pdf, generate_transkrip_pdf, export_excel
from app.services.audit_service import catat_audit_log
from app.utils.time import now_jakarta


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
        tanggal = now_jakarta().strftime('%Y%m%d')
        catat_audit_log(
            user_id=current_user.id,
            action='PRINT_PDF',
            table_name='nilai',
            description=f'Cetak PDF rekap nilai kelas {kelas}',
            ip_address=request.remote_addr,
        )
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
        tanggal = now_jakarta().strftime('%Y%m%d')
        siswa = Siswa.query.get_or_404(siswa_id)
        catat_audit_log(
            user_id=current_user.id,
            action='PRINT_PDF',
            table_name='nilai',
            record_id=siswa_id,
            description=f'Cetak PDF transkrip {siswa.nama}',
            ip_address=request.remote_addr,
        )
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
        dicetak_oleh = current_user.username
        if current_user.is_guru() and current_user.guru:
            dicetak_oleh = current_user.guru.nama_guru
        elif current_user.is_siswa() and current_user.siswa:
            dicetak_oleh = current_user.siswa.nama
        excel_bytes = export_excel(kelas, dicetak_oleh=dicetak_oleh)
        tanggal = now_jakarta().strftime('%Y%m%d')
        catat_audit_log(
            user_id=current_user.id,
            action='EXPORT_EXCEL',
            table_name='nilai',
            description=f'Ekspor Excel nilai kelas {kelas or "semua"}',
            ip_address=request.remote_addr,
        )
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
