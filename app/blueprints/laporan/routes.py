"""
Modul: blueprints/laporan/routes.py
Deskripsi: Route handler untuk modul Laporan (PDF & Excel).

Endpoint:
- ``GET /laporan/rekap-kelas``                 → Halaman pilih kelas (UI).
- ``GET /laporan/pdf/kelas/<kelas>``            → Generate PDF rekap kelas.
- ``GET /laporan/pdf/transkrip/<siswa_id>``     → Generate PDF transkrip siswa.
- ``GET /laporan/excel``                        → Generate & download XLSX.

Akses:
- Admin & Guru: semua endpoint.
- Siswa: TIDAK boleh akses (403).

Catatan penting:
- HTTPException (404, 403) di-re-raise apa adanya di semua handler
  yang memanggil service. Lihat debugging_log.md Bug #005 untuk
  konteks historis.
- Audit log dicatat SETELAH PDF/Excel berhasil di-generate.

Author : Niko Dwicahyo
Versi  : 1.0.0
"""
import logging
from flask import render_template, Response, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.blueprints.laporan import laporan_bp
from app.blueprints.decorators import role_required
from app import db
from app.models import Siswa, Nilai
from app.services.laporan_service import generate_laporan_pdf, generate_transkrip_pdf, export_excel
from app.services.audit_service import catat_audit_log
from app.utils.time import now_jakarta

logger = logging.getLogger(__name__)


# ===========================================================================
# INDEX — Halaman pilih kelas
# ===========================================================================

@laporan_bp.route('/rekap-kelas')
@login_required
def index():
    """Halaman UI untuk pilih kelas sebelum cetak/export laporan.

    Dropdown berisi daftar kelas yang punya data nilai (distinct dari
    Nilai JOIN Siswa, exclude soft-deleted).
    """
    kelas_list = [
        r[0] for r in db.session.query(Siswa.kelas)
        .join(Nilai, Nilai.siswa_id == Siswa.id)
        .filter(Siswa.deleted_at.is_(None))
        .distinct().order_by(Siswa.kelas).all()
    ]
    return render_template('laporan/index.html', kelas_list=kelas_list)


# ===========================================================================
# PDF REKAP KELAS
# ===========================================================================

@laporan_bp.route('/pdf/kelas/<path:kelas>')
@login_required
def pdf_kelas(kelas):
    """Generate & download PDF rekap nilai satu kelas.

    Args:
        kelas (str): Nama kelas (path param, support nama dengan
            karakter khusus seperti '/', spasi, dll.).

    Returns:
        Response: File PDF sebagai attachment, atau redirect + flash
        jika tidak ada data nilai untuk kelas tersebut.

    Raises:
        403: Jika user adalah siswa (siswa tidak boleh akses laporan kelas).
    """
    # Guard: siswa tidak boleh cetak laporan kelas.
    if current_user.is_siswa():
        abort(403)

    # Guard: tolak generate PDF jika kelas tidak punya data nilai.
    if not Nilai.query.join(Siswa, Nilai.siswa_id == Siswa.id).filter(
        Siswa.kelas == kelas, Siswa.deleted_at.is_(None)
    ).first():
        flash(f'Tidak ada data nilai untuk kelas {kelas}.', 'warning')
        return redirect(url_for('laporan.index'))

    try:
        # Panggil service untuk generate PDF.
        pdf_bytes = generate_laporan_pdf(kelas)
        tanggal = now_jakarta().strftime('%Y%m%d')

        # Audit log SETELAH PDF berhasil di-generate.
        catat_audit_log(
            user_id=current_user.id,
            action='PRINT_PDF',
            table_name='nilai',
            description=f'Cetak PDF rekap nilai kelas {kelas}',
            ip_address=request.remote_addr,
        )
        # Sanitize filename: replace '/' agar tidak dianggap path separator.
        safe_kelas = kelas.replace('/', '_')
        return Response(
            pdf_bytes,
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename=rekap_{safe_kelas}_{tanggal}.pdf'
            },
        )
    except Exception as e:
        flash(f'Gagal generate PDF: {str(e)}', 'error')
        return redirect(url_for('laporan.index'))


# ===========================================================================
# PDF TRANSKRIP SISWA
# ===========================================================================

@laporan_bp.route('/pdf/transkrip/<int:siswa_id>')
@login_required
def pdf_transkrip(siswa_id):
    """Generate & download PDF transkrip nilai personal satu siswa.

    Siswa hanya boleh akses transkrip MILIKNYA sendiri.

    Args:
        siswa_id (int): Primary key siswa.

    Returns:
        Response: File PDF transkrip (1 halaman).

    Raises:
        403: Jika siswa mencoba akses transkrip siswa lain.
        404: Jika siswa_id tidak ada di database.
    """
    # Guard: siswa hanya boleh akses transkrip sendiri.
    if current_user.is_siswa() and current_user.siswa_id != siswa_id:
        abort(403)

    from werkzeug.exceptions import HTTPException

    try:
        # Service raise 404 jika siswa tidak ada — kita teruskan apa adanya.
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
    except HTTPException:
        # Pertahankan HTTP semantics — JANGAN dibungkus RuntimeError.
        raise
    except Exception as e:
        flash(f'Gagal generate PDF: {str(e)}', 'error')
        return redirect(url_for('laporan.index'))


# ===========================================================================
# EXCEL EXPORT
# ===========================================================================

@laporan_bp.route('/excel')
@login_required
def excel():
    """Generate & download file Excel (.xlsx) rekap nilai.

    Query param:
        kelas (str, optional): Filter per kelas. Jika kosong, export
        semua kelas.

    Returns:
        Response: File XLSX sebagai attachment.

    Raises:
        403: Jika user adalah siswa.
    """
    if current_user.is_siswa():
        abort(403)

    kelas = request.args.get('kelas')

    # Guard: tolak export Excel jika kelas yang diminta tidak punya data.
    if kelas and not Nilai.query.join(Siswa, Nilai.siswa_id == Siswa.id).filter(
        Siswa.kelas == kelas, Siswa.deleted_at.is_(None)
    ).first():
        flash(f'Tidak ada data nilai untuk kelas {kelas}.', 'warning')
        return redirect(url_for('laporan.index'))

    try:
        # Tentukan "dicetak_oleh" sesuai role: nama untuk guru/siswa,
        # username untuk admin.
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
        safe_kelas = kelas.replace('/', '_') if kelas else None
        filename = f'nilai_{safe_kelas if kelas else "semua"}_{tanggal}.xlsx'
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
