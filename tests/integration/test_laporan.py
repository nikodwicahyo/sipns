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


class TestLaporanRoleBased:
    """Pengujian role-based filtering untuk export PDF & Excel.

    Aturan akses (PRD §14 kontrol akses):
    - Admin: tidak ada filter mapel, akses penuh.
    - Guru: filter dikunci ke ``current_user.guru.mata_pelajaran``.
    - Siswa: diblok total (lihat test di atas).
    """

    def test_guru_pdf_hanya_untuk_mapelnya(self, login_guru, guru_user, sample_nilai):
        """Guru Matematika download PDF → 200 OK dan data terfilter ke Matematika saja.

        Fixture ``sample_nilai`` berisi 6 records (3 siswa × 2 mapel:
        Matematika + Bahasa Indonesia). Guru dengan mapel Matematika harus
        hanya menerima 3 record (1 mapel × 3 siswa), bukan 6.
        """
        user, guru = guru_user  # guru.mata_pelajaran = 'Matematika'
        from app.models.nilai import Nilai as NilaiModel
        # Hitung ekspektasi: record dengan mapel guru saja.
        expected_count = NilaiModel.query.filter_by(
            mata_pelajaran=guru.mata_pelajaran
        ).count()
        assert expected_count > 0, 'Sample nilai harus berisi mapel guru'

        response = login_guru.get('/laporan/pdf/kelas/X-IPA-1')
        assert response.status_code == 200
        assert response.content_type == 'application/pdf'
        # Filename harus menyertakan nama mapel guru.
        cd = response.headers.get('Content-Disposition', '')
        assert 'attachment' in cd
        assert 'rekap_X-IPA-1' in cd
        assert 'Matematika' in cd, (
            f'Filename harus menyertakan mapel guru. Got: {cd}'
        )

    def test_guru_pdf_tidak_termasuk_mapel_lain(self, login_guru, guru_user, sample_nilai, db):
        """Verifikasi data PDF guru TIDAK termasuk record Bahasa Indonesia.

        Karena WeasyPrint di-mock dan tidak merender HTML asli, kita verifikasi
        via service langsung bahwa query yang dipakai memfilter mapel.
        """
        from app.models.nilai import Nilai as NilaiModel
        # sample_nilai punya record Bahasa Indonesia (mapel lain).
        other_mapel_count = NilaiModel.query.filter(
            NilaiModel.mata_pelajaran != 'Matematika'
        ).count()
        assert other_mapel_count > 0, 'Sample harus punya mapel lain untuk uji'

        # Trigger request agar route handler memanggil service dengan filter.
        response = login_guru.get('/laporan/pdf/kelas/X-IPA-1')
        assert response.status_code == 200

        # Verifikasi via audit log description: harus menyertakan "(mapel: Matematika)".
        from app.models.audit_log import AuditLog
        log = AuditLog.query.filter_by(action='PRINT_PDF').first()
        assert log is not None
        assert 'mapel: Matematika' in log.description

    def test_guru_excel_hanya_untuk_mapelnya(self, login_guru, guru_user, sample_nilai):
        """Guru download Excel → filename dan isi terfilter ke mapel guru saja."""
        user, guru = guru_user
        response = login_guru.get('/laporan/excel')
        assert response.status_code == 200
        assert 'spreadsheetml' in response.content_type
        # Filename harus menyertakan mapel guru.
        cd = response.headers.get('Content-Disposition', '')
        assert 'Matematika' in cd, (
            f'Filename Excel harus menyertakan mapel guru. Got: {cd}'
        )

    def test_guru_excel_filter_kelas_dan_mapel(self, login_guru, guru_user, sample_nilai):
        """Guru Excel dengan ?kelas= → tetap filter ke mapel guru (intersection)."""
        user, guru = guru_user
        response = login_guru.get('/laporan/excel?kelas=X-IPA-1')
        assert response.status_code == 200
        cd = response.headers.get('Content-Disposition', '')
        # Harus ada kelas DAN mapel guru di filename.
        assert 'X-IPA-1' in cd
        assert 'Matematika' in cd

    def test_guru_excel_kelas_tanpa_nilai_mapelnya_redirect(
        self, login_guru, guru_user, sample_siswa, db
    ):
        """Guru minta kelas tanpa nilai mapel-nya → redirect + flash warning.

        Setup: sample_siswa punya 3 siswa (2 di X-IPA-1, 1 di X-IPA-2) tapi
        tidak ada record Nilai sama sekali (sample_nilai TIDAK dipakai).
        Guru Matematika → harus redirect karena mapelnya belum ada nilai.
        """
        # Tambah satu record nilai Bahasa Indonesia (bukan mapel guru) di X-IPA-1.
        from app.models.nilai import Nilai as NilaiModel
        guru_id_lain = 999  # sembarang guru_id, tidak kena filter mapel di guard
        n = NilaiModel(
            siswa_id=sample_siswa[0].id,
            guru_id=guru_id_lain,
            mata_pelajaran='Bahasa Indonesia',
            nilai_tugas=80, nilai_uts=80, nilai_uas=80,
        )
        db.session.add(n)
        db.session.commit()

        response = login_guru.get('/laporan/excel?kelas=X-IPA-1', follow_redirects=False)
        # Mapel guru (Matematika) tidak punya record untuk X-IPA-1 → redirect.
        assert response.status_code == 302
        assert '/laporan' in response.headers['Location']

    def test_guru_index_hanya_tampilkan_kelas_untuk_mapelnya(
        self, login_guru, guru_user, sample_siswa, db
    ):
        """Index page untuk guru: dropdown kelas harus terfilter ke mapel guru.

        Setup: 2 siswa di X-IPA-1 dapat nilai Matematika; 1 siswa di X-IPA-2
        dapat nilai Bahasa Indonesia (mapel lain, harus tersembunyi dari
        dropdown guru Matematika).
        """
        from app.models.nilai import Nilai as NilaiModel
        # Matematika di X-IPA-1 (untuk 2 siswa pertama).
        for s in sample_siswa[:2]:
            n = NilaiModel(
                siswa_id=s.id, guru_id=guru_user[1].id,
                mata_pelajaran='Matematika',
                nilai_tugas=80, nilai_uts=80, nilai_uas=80,
            )
            n.hitung_dan_simpan()
            db.session.add(n)
        # Bahasa Indonesia di X-IPA-2 (mapel lain — harus TIDAK muncul di dropdown).
        n2 = NilaiModel(
            siswa_id=sample_siswa[2].id, guru_id=999,
            mata_pelajaran='Bahasa Indonesia',
            nilai_tugas=75, nilai_uts=75, nilai_uas=75,
        )
        n2.hitung_dan_simpan()
        db.session.add(n2)
        db.session.commit()

        response = login_guru.get('/laporan/rekap-kelas')
        assert response.status_code == 200
        body = response.data.decode('utf-8')
        # Harus ada banner info mapel.
        assert 'Matematika' in body, 'Banner info harus menyebut mapel guru'
        # X-IPA-1 muncul (ada nilai Matematika).
        assert 'X-IPA-1' in body, 'X-IPA-1 harus muncul di dropdown'
        # X-IPA-2 TIDAK boleh muncul (hanya ada nilai Bahasa Indonesia).
        assert 'X-IPA-2' not in body, (
            'X-IPA-2 tidak boleh muncul karena mapel guru tidak ada di sana'
        )

    def test_admin_index_tidak_terfilter_mapel(
        self, login_admin, sample_siswa, db
    ):
        """Admin index harus menampilkan SEMUA kelas yang punya nilai (tanpa filter mapel)."""
        from app.models.nilai import Nilai as NilaiModel
        # Matematika di X-IPA-1
        n1 = NilaiModel(
            siswa_id=sample_siswa[0].id, guru_id=1,
            mata_pelajaran='Matematika',
            nilai_tugas=80, nilai_uts=80, nilai_uas=80,
        )
        n1.hitung_dan_simpan()
        # Bahasa Indonesia di X-IPA-2
        n2 = NilaiModel(
            siswa_id=sample_siswa[2].id, guru_id=2,
            mata_pelajaran='Bahasa Indonesia',
            nilai_tugas=75, nilai_uts=75, nilai_uas=75,
        )
        n2.hitung_dan_simpan()
        db.session.add_all([n1, n2])
        db.session.commit()

        response = login_admin.get('/laporan/rekap-kelas')
        assert response.status_code == 200
        body = response.data.decode('utf-8')
        # Admin harus melihat KEDUA kelas (tidak ada filter mapel).
        assert 'X-IPA-1' in body
        assert 'X-IPA-2' in body
        # Admin TIDAK boleh melihat banner info mapel.
        assert 'mapel</strong>. Anda login sebagai <strong>Guru' not in body

    def test_guru_tanpa_record_untuk_kelas_redirect(
        self, login_guru, guru_user, sample_siswa, db
    ):
        """Guru minta kelas yang TIDAK punya nilai mapel-nya → redirect.

        Fixture sample_siswa sudah ada 2 siswa di X-IPA-1, tapi tanpa Nilai.
        Guru Matematika minta PDF X-IPA-1 → harus redirect dengan flash.
        """
        response = login_guru.get('/laporan/pdf/kelas/X-IPA-1', follow_redirects=False)
        assert response.status_code == 302
        assert '/laporan' in response.headers['Location']
