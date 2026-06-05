"""
Integration tests untuk modul Nilai (Guru input nilai).

Sesuai PRD.md:
- TC-NILAI-01: Input nilai valid -> tersimpan, nilai_akhir terhitung
- TC-NILAI-02: Input nilai di luar rentang -> validation error
- TC-NILAI-03: Kunci nilai -> is_locked=True
- TC-NILAI-04: Edit nilai terkunci -> ditolak
- TC-NILAI-05: GET /api/nilai-preview -> JSON {nilai_akhir: 80.5}
"""
import pytest
import json

from app.models.nilai import Nilai
from app.models.audit_log import AuditLog


class TestInputNilai:
    """Menguji endpoint /guru/nilai/input."""

    def test_tc_nilai_01_input_valid(self, login_guru, sample_siswa, db):
        """TC-NILAI-01: Input nilai valid -> tersimpan, nilai_akhir terhitung.

        login_guru fixture membuat guru 'GR-001' dengan mapel Matematika.
        sample_siswa menyediakan siswa untuk dinilai.
        """
        siswa = sample_siswa[0]

        response = login_guru.post('/guru/nilai/input', data={
            'siswa_id': str(siswa.id),
            'nilai_tugas': '80',
            'nilai_uts': '75',
            'nilai_uas': '85',
        }, follow_redirects=False)
        # Expected: redirect ke input form dengan flash sukses
        assert response.status_code in (200, 302)

        # Verifikasi nilai tersimpan untuk siswa ini
        nilai = Nilai.query.filter_by(siswa_id=siswa.id).first()
        assert nilai is not None
        assert float(nilai.nilai_akhir) == 80.5
        assert nilai.status_lulus is True

        # Audit log tercatat
        log = AuditLog.query.filter_by(table_name='nilai', action='INSERT').first()
        assert log is not None

    def test_tc_nilai_02_input_nilai_diluar_rentang(self, login_guru, sample_siswa, db):
        """TC-NILAI-02: Input nilai di luar rentang 0-100 -> validation error."""
        siswa = sample_siswa[0]
        response = login_guru.post('/guru/nilai/input', data={
            'siswa_id': str(siswa.id),
            'nilai_tugas': '150',  # > 100
            'nilai_uts': '75',
            'nilai_uas': '85',
        }, follow_redirects=False)
        # Validation error -> tetap di form (200) atau redirect dengan flash
        assert response.status_code in (200, 302)
        # Pastikan tidak ada nilai tersimpan
        assert Nilai.query.count() == 0

    def test_input_nilai_negatif_ditolak(self, login_guru, sample_siswa, db):
        """Nilai negatif juga ditolak (range check)."""
        siswa = sample_siswa[0]
        response = login_guru.post('/guru/nilai/input', data={
            'siswa_id': str(siswa.id),
            'nilai_tugas': '-5',
            'nilai_uts': '75',
            'nilai_uas': '85',
        }, follow_redirects=False)
        assert response.status_code in (200, 302)
        assert Nilai.query.count() == 0

    def test_input_nilai_tanpa_siswa_validation_error(self, login_guru, db):
        """Submit tanpa siswa_id harus error."""
        response = login_guru.post('/guru/nilai/input', data={
            'siswa_id': '',
            'nilai_tugas': '80',
            'nilai_uts': '75',
            'nilai_uas': '85',
        }, follow_redirects=False)
        assert response.status_code in (200, 302)
        assert Nilai.query.count() == 0


class TestKunciNilai:
    """Menguji endpoint /guru/nilai/kunci/<id>."""

    def test_tc_nilai_03_kunci_nilai_set_is_locked_true(
        self, login_guru, sample_nilai, db
    ):
        """TC-NILAI-03: Kunci nilai -> is_locked=True."""
        nilai = sample_nilai[0]
        assert nilai.is_locked is False

        response = login_guru.post(f'/guru/nilai/kunci/{nilai.id}', follow_redirects=False)
        assert response.status_code == 302

        db.session.refresh(nilai)
        assert nilai.is_locked is True

        # Audit log UPDATE tercatat
        log = AuditLog.query.filter_by(
            table_name='nilai', action='UPDATE', record_id=nilai.id
        ).first()
        assert log is not None

    def test_kunci_nilai_tidak_ada_404(self, login_guru, db):
        """Kunci nilai ID tidak ada -> 404."""
        response = login_guru.post('/guru/nilai/kunci/99999')
        assert response.status_code == 404


class TestEditNilai:
    """Menguji endpoint /guru/nilai/edit/<id>."""

    def test_tc_nilai_04_edit_nilai_terkunci_ditolak(
        self, login_guru, sample_nilai, db
    ):
        """TC-NILAI-04: Edit nilai yang sudah dikunci -> ditolak."""
        nilai = sample_nilai[0]
        nilai.lock()
        db.session.commit()

        original_akhir = float(nilai.nilai_akhir)
        original_tugas = float(nilai.nilai_tugas)

        response = login_guru.post(f'/guru/nilai/edit/{nilai.id}', data={
            'siswa_id': str(nilai.siswa_id),
            'nilai_tugas': '100',  # beda dari original
            'nilai_uts': '100',
            'nilai_uas': '100',
        }, follow_redirects=False)
        # Ditolak: redirect (dengan flash error) atau 403
        assert response.status_code in (302, 403)

        # Nilai TIDAK berubah
        db.session.refresh(nilai)
        assert float(nilai.nilai_tugas) == original_tugas
        assert float(nilai.nilai_akhir) == original_akhir

    def test_edit_nilai_belum_terkunci_berhasil(self, login_guru, sample_nilai, db):
        """Edit nilai yang belum dikunci -> nilai berubah."""
        nilai = sample_nilai[0]
        assert nilai.is_locked is False

        response = login_guru.post(f'/guru/nilai/edit/{nilai.id}', data={
            'siswa_id': str(nilai.siswa_id),
            'nilai_tugas': '95',
            'nilai_uts': '95',
            'nilai_uas': '95',
        }, follow_redirects=False)
        assert response.status_code in (200, 302)

        db.session.refresh(nilai)
        assert float(nilai.nilai_tugas) == 95.0


class TestNilaiPreviewAPI:
    """Menguji endpoint /admin/api/nilai-preview."""

    def test_tc_nilai_05_api_preview_kalkulasi(self, login_admin):
        """TC-NILAI-05: GET /api/nilai-preview?tugas=80&uts=75&uas=85 -> JSON 80.5."""
        response = login_admin.get('/admin/api/nilai-preview?tugas=80&uts=75&uas=85')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['nilai_akhir'] == 80.5
        assert data['status_lulus'] is True
        assert data['label'] == 'Lulus'
        assert data['badge_class'] == 'bg-success'

    def test_api_preview_tepat_kkm(self, login_admin):
        """Tepat KKM (70) -> Lulus, selisih 0."""
        response = login_admin.get('/admin/api/nilai-preview?tugas=70&uts=70&uas=70')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['nilai_akhir'] == 70.0
        assert data['status_lulus'] is True

    def test_api_preview_dibawah_kkm(self, login_admin):
        """Di bawah KKM (59) -> Tidak Lulus."""
        response = login_admin.get('/admin/api/nilai-preview?tugas=50&uts=60&uas=65')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['nilai_akhir'] == 59.0
        assert data['status_lulus'] is False
        assert data['label'] == 'Tidak Lulus'
        assert data['badge_class'] == 'bg-danger'

    def test_api_preview_nilai_invalid_422(self, login_admin):
        """Input tidak valid -> 422."""
        response = login_admin.get('/admin/api/nilai-preview?tugas=999&uts=75&uas=85')
        assert response.status_code == 422
        data = json.loads(response.data)
        assert 'error' in data

    def test_api_siswa_by_kelas(self, login_admin, sample_siswa):
        """GET /api/siswa-by-kelas/<kelas> -> JSON list siswa."""
        response = login_admin.get('/admin/api/siswa-by-kelas/X-IPA-1')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 2  # 2 siswa di X-IPA-1
        for s in data:
            assert 'id' in s
            assert 'nis' in s
            assert 'nama' in s

    def test_api_statistik_kelas(self, login_admin, sample_siswa, sample_nilai):
        """GET /api/statistik-kelas/<kelas> -> JSON statistik."""
        response = login_admin.get('/admin/api/statistik-kelas/X-IPA-1')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'total' in data
        assert 'rata_rata' in data
        assert 'tertinggi' in data
        assert 'terendah' in data
        assert 'persen_lulus' in data
