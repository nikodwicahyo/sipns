from app.models.nilai import Nilai
from app.models.siswa import Siswa
from app.services.nilai_service import hitung_statistik_kelas
from flask import render_template
import weasyprint


def generate_laporan_pdf(kelas, template='laporan/rekap_kelas.html'):
    data_nilai = (
        Nilai.query
        .join(Siswa)
        .filter(Siswa.kelas == kelas, Siswa.deleted_at.is_(None))
        .order_by(Siswa.nama)
        .all()
    )

    statistik = hitung_statistik_kelas(data_nilai)
    html_content = render_template(template, data=data_nilai, statistik=statistik, kelas=kelas)
    return weasyprint.HTML(string=html_content).write_pdf()


def generate_transkrip_pdf(siswa_id):
    siswa = Siswa.query.get_or_404(siswa_id)
    data_nilai = Nilai.query.filter_by(siswa_id=siswa_id).all()
    html_content = render_template('laporan/transkrip_siswa.html', siswa=siswa, data=data_nilai)
    return weasyprint.HTML(string=html_content).write_pdf()


def export_excel(kelas=None):
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    from io import BytesIO

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Rekap Nilai"

    if kelas:
        query = Nilai.query.join(Siswa).filter(Siswa.kelas == kelas, Siswa.deleted_at.is_(None))
    else:
        query = Nilai.query.join(Siswa).filter(Siswa.deleted_at.is_(None))

    data_nilai = query.order_by(Siswa.kelas, Siswa.nama).all()

    header_font = Font(bold=True, color="FFFFFF", size=11)
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    thin_border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin"),
    )
    alt_fill = PatternFill(start_color="D9E2F3", end_color="D9E2F3", fill_type="solid")

    headers = ["No", "NIS", "Nama", "Kelas", "Mata Pelajaran", "Tugas", "UTS", "UAS", "Nilai Akhir", "Status"]
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = thin_border

    for i, n in enumerate(data_nilai, 1):
        row = i + 1
        values = [
            i,
            n.siswa.nis,
            n.siswa.nama,
            n.siswa.kelas,
            n.mata_pelajaran,
            float(n.nilai_tugas),
            float(n.nilai_uts),
            float(n.nilai_uas),
            float(n.nilai_akhir) if n.nilai_akhir else '',
            'Lulus' if n.status_lulus else 'Tidak Lulus',
        ]
        for col, val in enumerate(values, 1):
            cell = ws.cell(row=row, column=col, value=val)
            cell.border = thin_border
            if i % 2 == 0:
                cell.fill = alt_fill

    for col in range(1, len(headers) + 1):
        ws.column_dimensions[get_column_letter(col)].width = 18

    ws.freeze_panes = 'A2'

    output = BytesIO()
    wb.save(output)
    return output.getvalue()
