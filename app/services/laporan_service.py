from app.models.nilai import Nilai
from app.models.siswa import Siswa
from app.services.nilai_service import hitung_statistik_kelas
from flask import render_template, url_for, has_request_context
from app.utils.time import now_jakarta, current_year_jakarta


def _get_base_url():
    try:
        if has_request_context():
            return url_for('static', filename='', _external=True)
    except Exception:
        pass
    return None


def generate_laporan_pdf(kelas, template='laporan/rekap_kelas.html'):
    import weasyprint
    try:
        data_nilai = (
            Nilai.query
            .join(Siswa, Nilai.siswa_id == Siswa.id)
            .filter(Siswa.kelas == kelas, Siswa.deleted_at.is_(None))
            .order_by(Siswa.nama)
            .all()
        )

        statistik = hitung_statistik_kelas(data_nilai)
        html_content = render_template(
            template,
            data=data_nilai,
            statistik=statistik,
            kelas=kelas,
            current_year=current_year_jakarta(),
            tanggal_cetak=now_jakarta().strftime('%d/%m/%Y %H:%M'),
        )
        pdf_bytes = weasyprint.HTML(
            string=html_content,
            base_url=_get_base_url(),
        ).write_pdf()
        return pdf_bytes
    except Exception as e:
        raise RuntimeError(f"Gagal generate PDF laporan: {e}") from e


def generate_transkrip_pdf(siswa_id):
    import weasyprint
    try:
        siswa = Siswa.query.get_or_404(siswa_id)
        data_nilai = Nilai.query.filter_by(siswa_id=siswa_id).all()
        html_content = render_template(
            'laporan/transkrip_siswa.html',
            siswa=siswa,
            data=data_nilai,
            current_year=current_year_jakarta(),
            tanggal_cetak=now_jakarta().strftime('%d/%m/%Y %H:%M'),
        )
        pdf_bytes = weasyprint.HTML(
            string=html_content,
            base_url=_get_base_url(),
        ).write_pdf()
        return pdf_bytes
    except Exception as e:
        raise RuntimeError(f"Gagal generate PDF transkrip: {e}") from e


def export_excel(kelas=None, dicetak_oleh=None):
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    from io import BytesIO

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Rekap Nilai"

    if kelas:
        query = Nilai.query.join(Siswa, Nilai.siswa_id == Siswa.id).filter(Siswa.kelas == kelas, Siswa.deleted_at.is_(None))
    else:
        query = Nilai.query.join(Siswa, Nilai.siswa_id == Siswa.id).filter(Siswa.deleted_at.is_(None))

    data_nilai = query.order_by(Siswa.kelas, Siswa.nama).all()

    title_font = Font(bold=True, size=14, color="1F4E79")
    info_font = Font(size=10, color="333333")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    summary_fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
    summary_font = Font(bold=True, size=11, color="1F4E79")
    thin_border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin"),
    )
    alt_fill = PatternFill(start_color="D9E2F3", end_color="D9E2F3", fill_type="solid")

    total_cols = 10
    headers = ["No", "NIS", "Nama", "Kelas", "Mata Pelajaran", "Tugas", "UTS", "UAS", "Nilai Akhir", "Status"]

    # Row 1: Title (merged)
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=total_cols)
    title_cell = ws.cell(row=1, column=1, value="LAPORAN REKAP NILAI SISWA")
    title_cell.font = title_font
    title_cell.alignment = Alignment(horizontal="center", vertical="center")

    # Row 2: Info
    label_kelas = kelas if kelas else "Semua Kelas"
    info_text = f"Kelas: {label_kelas} | Tanggal: {now_jakarta().strftime('%d/%m/%Y %H:%M')}"
    if dicetak_oleh:
        info_text += f" | Dicetak oleh: {dicetak_oleh}"
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=total_cols)
    info_cell = ws.cell(row=2, column=1, value=info_text)
    info_cell.font = info_font
    info_cell.alignment = Alignment(horizontal="left", vertical="center")

    # Row 3: Blank
    ws.merge_cells(start_row=3, start_column=1, end_row=3, end_column=total_cols)

    # Row 4: Column headers
    header_row = 4
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=header_row, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = thin_border

    # Data rows (from row 5)
    data_start_row = header_row + 1
    for i, n in enumerate(data_nilai, 1):
        row = data_start_row + i - 1
        values = [
            i,
            n.siswa.nis if n.siswa else '-',
            n.siswa.nama if n.siswa else '-',
            n.siswa.kelas if n.siswa else '-',
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

    # Summary row
    summary_row = data_start_row + len(data_nilai)
    if data_nilai:
        nilai_akhir_list = [float(n.nilai_akhir) for n in data_nilai if n.nilai_akhir is not None]
        lulus_count = sum(1 for n in data_nilai if n.status_lulus)
        if nilai_akhir_list:
            rata_rata = round(sum(nilai_akhir_list) / len(nilai_akhir_list), 2)
            tertinggi = max(nilai_akhir_list)
            terendah = min(nilai_akhir_list)
            persen_lulus = round((lulus_count / len(nilai_akhir_list)) * 100, 1)
        else:
            rata_rata = tertinggi = terendah = persen_lulus = 0

        ws.merge_cells(start_row=summary_row, start_column=1, end_row=summary_row, end_column=5)
        summary_label = ws.cell(row=summary_row, column=1, value="RINGKASAN")
        summary_label.font = summary_font
        summary_label.fill = summary_fill
        summary_label.border = thin_border
        for c in range(2, 6):
            ws.cell(row=summary_row, column=c).fill = summary_fill
            ws.cell(row=summary_row, column=c).border = thin_border

        summary_data = [
            ("Rata-rata", rata_rata),
            ("Tertinggi", tertinggi),
            ("Terendah", terendah),
            ("% Lulus", f"{persen_lulus}%"),
        ]
        for j, (label, val) in enumerate(summary_data):
            col = 6 + j
            cell = ws.cell(row=summary_row, column=col, value=val)
            cell.font = summary_font
            cell.fill = summary_fill
            cell.alignment = header_alignment
            cell.border = thin_border
            # Also write the label in a merged section or just the value

    # Auto-fit column widths
    for col in range(1, total_cols + 1):
        ws.column_dimensions[get_column_letter(col)].width = 18

    ws.column_dimensions['A'].width = 6
    ws.column_dimensions['C'].width = 28
    ws.column_dimensions['E'].width = 22
    ws.column_dimensions['J'].width = 14

    # Freeze panes below header row
    ws.freeze_panes = f'A{data_start_row}'

    output = BytesIO()
    wb.save(output)
    return output.getvalue()
