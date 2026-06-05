"""
Integration tests untuk modul Laporan (PDF + Excel).

Sesuai PRD.md:
- TC-LAP-01: GET /laporan/pdf/kelas/<kelas> -> 200 + application/pdf
- TC-LAP-02: GET /laporan/excel -> 200 + spreadsheet
- TC-LAP-03: Laporan kelas tidak ada -> 404 atau redirect

WeasyPrint di-mock via autouse fixture di tests/integration/conftest.py.
"""
import pytest

from app.models.nilai import Nilai


class TestLaporanPDF:
    """Menguji endpoint /laporan/pdf/* (WeasyPrint di-mock)."""

    def test_tc_lap_01_pdf_kelas_berhasil(self, login_admin, sample_nilai):
        """TC-LAP-01: GET /laporan/pdf/kelas/X-IPA-1 -> 200 + application/pdf."""
        response = login_admin.get('/laporan/pdf/kelas/X-IPA-1')
        assert response.status_code == 200
        assert response.content_type == 'application/pdf'
        # PDF body minimal mengandung signature
        assert response.data.startswith(b'%PDF-')
        # Header Content-Disposition untuk attachment
        assert 'attachment' in response.headers.get('Content-Disposition', '')
        assert 'rekap_X-IPA-1' in response.headers['Content-Disposition']

    def test_pdf_kelas_tanpa_nilai_redirect(self, login_admin, db):
        """TC-LAP-03: PDF kelas tanpa nilai -> redirect dengan flash."""
        # TIDAK ada siswa/nilai di kelas ini
        response = login_admin.get('/laporan/pdf/kelas/XI-IPS-99', follow_redirects=False)
        # Redirect ke halaman index dengan flash
        assert response.status_code == 302
        assert '/laporan' in response.headers['Location']

    def test_pdf_transkrip_siswa(self, login_admin, sample_siswa, sample_nilai):
        """GET /laporan/pdf/transkrip/<siswa_id> -> 200 + application/pdf."""
        siswa = sample_siswa[0]
        response = login_admin.get(f'/laporan/pdf/transkrip/{siswa.id}')
        assert response.status_code == 200
        assert response.content_type == 'application/pdf'
        assert response.data.startswith(b'%PDF-')
        assert 'attachment' in response.headers.get('Content-Disposition', '')
        assert f'transkrip_{siswa.nis}' in response.headers['Content-Disposition']

    def test_pdf_transkrip_siswa_tidak_ada_404(self, login_admin, db):
        """Transkrip siswa ID tidak ada -> 404."""
        response = login_admin.get('/laporan/pdf/transkrip/99999')
        assert response.status_code == 404

    def test_siswa_tidak_boleh_generate_pdf_kelas(self, login_siswa):
        """Siswa yang akses /laporan/pdf/kelas/* -> 403."""
        response = login_siswa.get('/laporan/pdf/kelas/X-IPA-1')
        assert response.status_code == 403

    def test_siswa_hanya_boleh_generate_transkrip_sendiri(self, login_siswa, siswa_user):
        """Siswa hanya boleh generate transkrip untuk siswa_id sendiri.

        login_siswa & siswa_user -> siswa NIS 2024001.
        Buat siswa kedua (NIS 2024002) untuk uji 403.
        """
        from app.models.siswa import Siswa
        from app.models.nilai import Nilai

        # Siswa kedua untuk uji 403
        other_siswa = Siswa(nis='2024002', nama='Other Siswa', kelas='X-IPA-1')
        from app import db
        db.session.add(other_siswa)
        db.session.commit()

        # Siswa kedua harusnya tidak bisa akses transkrip siswa lain
        response = login_siswa.get(f'/laporan/pdf/transkrip/{other_siswa.id}')
        assert response.status_code == 403


class TestLaporanExcel:
    """Menguji endpoint /laporan/excel (openpyxl real, tidak di-mock)."""

    def test_tc_lap_02_excel_semua_kelas(self, login_admin, sample_nilai):
        """TC-LAP-02: GET /laporan/excel -> 200 + spreadsheet."""
        response = login_admin.get('/laporan/excel')
        assert response.status_code == 200
        # Content-Type untuk xlsx
        assert 'spreadsheetml' in response.content_type or 'excel' in response.content_type.lower()
        # XLSX adalah file ZIP, signature 'PK'
        assert response.data[:2] == b'PK'
        # Content-Disposition untuk download
        assert 'attachment' in response.headers.get('Content-Disposition', '')

    def test_excel_filter_per_kelas(self, login_admin, sample_siswa, sample_nilai):
        """GET /laporan/excel?kelas=X-IPA-1 -> Excel filtered."""
        response = login_admin.get('/laporan/excel?kelas=X-IPA-1')
        assert response.status_code == 200
        assert 'spreadsheetml' in response.content_type or 'excel' in response.content_type.lower()
        # Filename mengandung nama kelas
        assert 'X-IPA-1' in response.headers.get('Content-Disposition', '')

    def test_excel_kelas_tidak_ada_redirect(self, login_admin, db):
        """Excel untuk kelas tanpa data -> redirect dengan flash."""
        response = login_admin.get('/laporan/excel?kelas=EMPTY-CLASS', follow_redirects=False)
        assert response.status_code == 302

    def test_siswa_tidak_boleh_generate_excel(self, login_siswa):
        """Siswa yang akses /laporan/excel -> 403."""
        response = login_siswa.get('/laporan/excel')
        assert response.status_code == 403


class TestLaporanIndex:
    """Menguji endpoint /laporan/rekap-kelas (halaman UI)."""

    def test_halaman_index_laporan_untuk_admin(self, login_admin, sample_nilai):
        """GET /laporan/rekap-kelas -> 200, menampilkan daftar kelas dengan nilai."""
        response = login_admin.get('/laporan/rekap-kelas')
        assert response.status_code == 200
        # HTML harus memuat list kelas
        assert b'X-IPA-1' in response.data or b'kelas' in response.data.lower()

    def test_halaman_index_laporan_tanpa_login_redirect(self, client):
        """GET /laporan/rekap-kelas tanpa login -> 302 ke login."""
        response = client.get('/laporan/rekap-kelas', follow_redirects=False)
        assert response.status_code == 302
        assert '/auth/login' in response.headers['Location']


class TestLaporanAuditLog:
    """Memastikan generate laporan tercatat di audit log."""

    def test_generate_pdf_mencatat_audit_log(self, login_admin, sample_nilai, db):
        """Generate PDF harus menulis audit log dengan action PRINT_PDF."""
        from app.models.audit_log import AuditLog
        response = login_admin.get('/laporan/pdf/kelas/X-IPA-1')
        assert response.status_code == 200
        # Audit log tercatat
        log = AuditLog.query.filter_by(action='PRINT_PDF').first()
        assert log is not None
        assert 'X-IPA-1' in log.description

    def test_generate_excel_mencatat_audit_log(self, login_admin, sample_nilai, db):
        """Generate Excel harus menulis audit log dengan action EXPORT_EXCEL."""
        from app.models.audit_log import AuditLog
        response = login_admin.get('/laporan/excel')
        assert response.status_code == 200
        log = AuditLog.query.filter_by(action='EXPORT_EXCEL').first()
        assert log is not None
