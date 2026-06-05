"""
Integration tests untuk modul Manajemen Siswa (SISWA).

Sesuai PRD.md F6-044:
- TC-SISWA-01: Tambah siswa valid -> data + audit log
- TC-SISWA-02: Tambah siswa NIS duplikat -> error validation
- TC-SISWA-03: Edit siswa -> data berubah
- TC-SISWA-04: Hapus siswa -> soft delete
"""
import pytest

from app.models.siswa import Siswa
from app.models.user import User
from app.models.audit_log import AuditLog


class TestSiswaCreate:
    """Menguji endpoint /admin/siswa/tambah."""

    def test_tc_siswa_01_tambah_siswa_valid(self, login_admin, db):
        """TC-SISWA-01: Tambah siswa valid -> data di DB + user tercipta + audit log."""
        response = login_admin.post('/admin/siswa/tambah', data={
            'nis': '2024099',
            'nama': 'Siswa Baru',
            'kelas': 'X-IPA-1',
        }, follow_redirects=False)
        assert response.status_code == 302
        assert '/admin/siswa' in response.headers['Location']

        # Verifikasi siswa ada di DB
        siswa = Siswa.query.filter_by(nis='2024099').first()
        assert siswa is not None
        assert siswa.nama == 'Siswa Baru'
        assert siswa.kelas == 'X-IPA-1'
        assert siswa.deleted_at is None

        # Verifikasi user terkait tercipta
        user = User.query.filter_by(username='2024099').first()
        assert user is not None
        assert user.role == 'siswa'
        assert user.siswa_id == siswa.id

        # Verifikasi audit log
        log = AuditLog.query.filter_by(table_name='siswa', action='INSERT').first()
        assert log is not None
        assert 'Siswa Baru' in log.description

    def test_tambah_siswa_dengan_password_custom(self, login_admin, db):
        """Tambah siswa dengan password custom (bukan default NIS)."""
        response = login_admin.post('/admin/siswa/tambah', data={
            'nis': '2024098',
            'nama': 'Custom Pass',
            'kelas': 'X-IPA-2',
            'password': 'CustomPass123',
        }, follow_redirects=False)
        assert response.status_code == 302

        user = User.query.filter_by(username='2024098').first()
        assert user is not None
        # Verifikasi password yang diset adalah custom, bukan NIS
        assert user.check_password('CustomPass123')
        assert not user.check_password('2024098')

    def test_tc_siswa_02_tambah_nis_duplikat(self, login_admin, sample_siswa, db):
        """TC-SISWA-02: Tambah siswa NIS duplikat -> validation error."""
        # sample_siswa sudah punya NIS 2024001
        response = login_admin.post('/admin/siswa/tambah', data={
            'nis': '2024001',  # duplikat
            'nama': 'Duplikat',
            'kelas': 'X-IPA-1',
        }, follow_redirects=False)
        # Validation error -> tidak redirect, tetap di form (200)
        # atau redirect dengan flash error
        assert response.status_code in (200, 302)

        # Cek Siswa tidak bertambah
        count = Siswa.query.filter_by(nis='2024001').count()
        assert count == 1  # hanya yang dari sample_siswa

    def test_tambah_siswa_form_kosong_validation_error(self, login_admin, db):
        """Form kosong harus gagal validasi."""
        response = login_admin.post('/admin/siswa/tambah', data={
            'nis': '',
            'nama': '',
            'kelas': '',
        }, follow_redirects=False)
        assert response.status_code == 200  # Tetap di form


class TestSiswaEdit:
    """Menguji endpoint /admin/siswa/edit/<id>."""

    def test_tc_siswa_03_edit_siswa_berhasil(self, login_admin, sample_siswa, db):
        """TC-SISWA-03: Edit siswa -> nama & kelas berubah, NIS tetap."""
        siswa = sample_siswa[0]
        original_nis = siswa.nis

        response = login_admin.post(f'/admin/siswa/edit/{siswa.id}', data={
            'nis': original_nis,  # NIS tidak diubah
            'nama': 'Budi Updated',
            'kelas': 'X-IPA-2',
        }, follow_redirects=False)
        assert response.status_code == 302

        db.session.refresh(siswa)
        assert siswa.nama == 'Budi Updated'
        assert siswa.kelas == 'X-IPA-2'
        assert siswa.nis == original_nis  # NIS tidak berubah

        # Audit log UPDATE tercatat
        log = AuditLog.query.filter_by(
            table_name='siswa', action='UPDATE', record_id=siswa.id
        ).first()
        assert log is not None

    def test_edit_siswa_get_form_pre_filled(self, login_admin, sample_siswa):
        """GET /admin/siswa/edit/<id> -> form terisi data existing."""
        siswa = sample_siswa[0]
        response = login_admin.get(f'/admin/siswa/edit/{siswa.id}')
        assert response.status_code == 200
        # Cek data siswa muncul di HTML
        assert siswa.nama.encode() in response.data
        assert siswa.nis.encode() in response.data

    def test_edit_siswa_tidak_ada_404(self, login_admin, db):
        """Edit siswa ID yang tidak ada -> 404."""
        response = login_admin.get('/admin/siswa/edit/99999')
        assert response.status_code == 404


class TestSiswaDelete:
    """Menguji endpoint /admin/siswa/hapus/<id> (soft delete)."""

    def test_tc_siswa_04_hapus_siswa_soft_delete(self, login_admin, sample_siswa, db):
        """TC-SISWA-04: Hapus siswa -> soft delete (deleted_at terisi, user nonaktif)."""
        siswa = sample_siswa[0]
        original_user_active = siswa.user.is_active if siswa.user else None

        response = login_admin.post(f'/admin/siswa/hapus/{siswa.id}', follow_redirects=False)
        assert response.status_code == 302

        db.session.refresh(siswa)
        # Soft delete: deleted_at terisi
        assert siswa.deleted_at is not None
        # User terkait dinonaktifkan
        if siswa.user:
            db.session.refresh(siswa.user)
            assert siswa.user.is_active is False

        # Audit log DELETE tercatat
        log = AuditLog.query.filter_by(
            table_name='siswa', action='DELETE', record_id=siswa.id
        ).first()
        assert log is not None

    def test_hapus_siswa_tidak_ada_404(self, login_admin, db):
        """Hapus siswa ID yang tidak ada -> 404."""
        response = login_admin.post('/admin/siswa/hapus/99999')
        assert response.status_code == 404

    def test_daftar_siswa_exclude_soft_deleted(self, login_admin, sample_siswa, db):
        """GET /admin/siswa -> tidak menampilkan siswa yang sudah di-soft-delete."""
        # Hapus satu siswa
        siswa = sample_siswa[0]
        siswa.soft_delete()
        db.session.commit()

        response = login_admin.get('/admin/siswa')
        assert response.status_code == 200
        # Siswa yang dihapus TIDAK muncul di daftar
        assert siswa.nama.encode() not in response.data
        # Siswa lain masih muncul
        assert sample_siswa[1].nama.encode() in response.data

    def test_hapus_siswa_role_lain_tidak_boleh(self, login_guru, sample_siswa):
        """Guru tidak boleh akses endpoint hapus siswa."""
        siswa = sample_siswa[0]
        response = login_guru.post(f'/admin/siswa/hapus/{siswa.id}', follow_redirects=False)
        assert response.status_code in (302, 403)


class TestSiswaDetail:
    """Menguji endpoint /admin/siswa/<id>."""

    def test_detail_siswa_tampil(self, login_admin, sample_siswa, sample_nilai):
        """GET /admin/siswa/<id> -> tampil info siswa + daftar nilai."""
        siswa = sample_siswa[0]
        response = login_admin.get(f'/admin/siswa/{siswa.id}')
        assert response.status_code == 200
        assert siswa.nama.encode() in response.data
        assert siswa.nis.encode() in response.data

    def test_detail_siswa_tidak_ada_404(self, login_admin, db):
        """Detail siswa ID tidak ada -> 404."""
        response = login_admin.get('/admin/siswa/99999')
        assert response.status_code == 404
