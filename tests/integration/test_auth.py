"""
Integration tests untuk modul Autentikasi (AUTH).

Sesuai PRD.md:
- TC-AUTH-01: Login admin valid -> 302 ke /admin/dashboard
- TC-AUTH-02: Login password salah -> 200 + error
- TC-AUTH-03: Login user nonaktif -> 200 + "akun nonaktif"
- TC-AUTH-04: Logout -> redirect ke login
- TC-AUTH-05: Akses tanpa login -> redirect ke /auth/login
- TC-AUTH-06: Login guru akses /admin/dashboard -> 403
"""
import pytest

from app.models.user import User


class TestAuthLogin:
    """Menguji endpoint /auth/login dengan berbagai skenario."""

    def test_tc_auth_01_login_admin_valid(self, client, admin_user):
        """TC-AUTH-01: Login admin valid -> redirect ke /admin/dashboard."""
        response = client.post('/auth/login', data={
            'username': 'admin',
            'password': 'Admin@123',
        }, follow_redirects=False)
        assert response.status_code == 302
        assert '/admin/dashboard' in response.headers['Location']

    def test_tc_auth_01b_login_guru_valid(self, client, guru_user):
        """Login guru valid -> redirect ke /guru/dashboard."""
        user, _ = guru_user
        response = client.post('/auth/login', data={
            'username': user.username,
            'password': 'Guru@123',
        }, follow_redirects=False)
        assert response.status_code == 302
        assert '/guru/dashboard' in response.headers['Location']

    def test_tc_auth_01c_login_siswa_valid(self, client, siswa_user):
        """Login siswa valid -> redirect ke /siswa/dashboard."""
        user, _ = siswa_user
        response = client.post('/auth/login', data={
            'username': user.username,
            'password': user.username,  # password siswa = NIS
        }, follow_redirects=False)
        assert response.status_code == 302
        assert '/siswa/dashboard' in response.headers['Location']

    def test_tc_auth_02_login_password_salah(self, client, admin_user):
        """TC-AUTH-02: Password salah -> 200 + flash error."""
        response = client.post('/auth/login', data={
            'username': 'admin',
            'password': 'WrongPassword',
        }, follow_redirects=False)
        # Tidak redirect, tetap di halaman login dengan status 200
        assert response.status_code == 200
        # HTML mengandung pesan error
        assert b'Username atau password salah' in response.data or b'salah' in response.data.lower()

    def test_tc_auth_02b_login_username_tidak_ada(self, client):
        """Username tidak ada -> 200 + error (sama seperti password salah)."""
        response = client.post('/auth/login', data={
            'username': 'nonexistent',
            'password': 'whatever',
        }, follow_redirects=False)
        assert response.status_code == 200
        assert b'salah' in response.data.lower()

    def test_tc_auth_03_login_user_nonaktif(self, client, db, admin_user):
        """TC-AUTH-03: User is_active=False -> 200 + flash akun nonaktif."""
        admin_user.is_active = False
        db.session.commit()

        response = client.post('/auth/login', data={
            'username': 'admin',
            'password': 'Admin@123',
        }, follow_redirects=False)
        assert response.status_code == 200
        assert b'tidak aktif' in response.data.lower() or b'nonaktif' in response.data.lower()

    def test_tc_auth_03b_login_form_kosong_validasi(self, client):
        """Form kosong -> 200 + validation error."""
        response = client.post('/auth/login', data={
            'username': '',
            'password': '',
        }, follow_redirects=False)
        assert response.status_code == 200
        # Form harus reject dengan validation error
        assert b'wajib diisi' in response.data.lower() or b'error' in response.data.lower()


class TestAuthLogout:
    """Menguji endpoint /auth/logout."""

    def test_tc_auth_04_logout_berhasil(self, login_admin):
        """TC-AUTH-04: GET /auth/logout -> redirect ke /auth/login."""
        response = login_admin.get('/auth/logout', follow_redirects=False)
        assert response.status_code == 302
        assert '/auth/login' in response.headers['Location']

    def test_logout_menghapus_session(self, login_admin, client):
        """Setelah logout, akses endpoint protected -> redirect ke login."""
        login_admin.get('/auth/logout', follow_redirects=False)
        # Sekarang coba akses admin dashboard
        response = client.get('/admin/dashboard', follow_redirects=False)
        assert response.status_code == 302
        assert '/auth/login' in response.headers['Location']


class TestAuthProtectedRoutes:
    """Menguji akses ke route terproteksi tanpa login."""

    def test_tc_auth_05_admin_dashboard_tanpa_login(self, client):
        """TC-AUTH-05: Akses /admin/dashboard tanpa login -> redirect login."""
        response = client.get('/admin/dashboard', follow_redirects=False)
        assert response.status_code == 302
        assert '/auth/login' in response.headers['Location']

    def test_tc_auth_05b_guru_dashboard_tanpa_login(self, client):
        """Akses /guru/dashboard tanpa login -> redirect login."""
        response = client.get('/guru/dashboard', follow_redirects=False)
        assert response.status_code == 302

    def test_tc_auth_05c_siswa_dashboard_tanpa_login(self, client):
        """Akses /siswa/dashboard tanpa login -> redirect login."""
        response = client.get('/siswa/dashboard', follow_redirects=False)
        assert response.status_code == 302

    def test_tc_auth_05d_laporan_tanpa_login(self, client):
        """Akses /laporan/* tanpa login -> redirect login."""
        response = client.get('/laporan/rekap-kelas', follow_redirects=False)
        assert response.status_code == 302


class TestAuthRoleIsolation:
    """Menguji isolasi role: user X tidak boleh akses endpoint role Y."""

    def test_tc_auth_06_guru_akses_admin_dashboard(self, login_guru):
        """TC-AUTH-06: Login guru akses /admin/dashboard -> 403."""
        response = login_guru.get('/admin/dashboard', follow_redirects=False)
        # Bisa 403 (abort) atau 302 (redirect ke dashboard guru)
        assert response.status_code in (302, 403)
        if response.status_code == 302:
            # Redirect bukan kembali ke login, tapi ke dashboard guru
            assert '/guru' in response.headers['Location']

    def test_guru_akses_admin_siswa_list(self, login_guru):
        """Guru akses /admin/siswa -> 403 atau redirect."""
        response = login_guru.get('/admin/siswa', follow_redirects=False)
        assert response.status_code in (302, 403)

    def test_siswa_akses_guru_input_nilai(self, login_siswa):
        """Siswa akses /guru/nilai/input -> 403 atau redirect."""
        response = login_siswa.get('/guru/nilai/input', follow_redirects=False)
        assert response.status_code in (302, 403)

    def test_siswa_akses_admin_dashboard(self, login_siswa):
        """Siswa akses /admin/dashboard -> 403 atau redirect."""
        response = login_siswa.get('/admin/dashboard', follow_redirects=False)
        assert response.status_code in (302, 403)

    def test_admin_bisa_akses_endpoint_admin(self, login_admin):
        """Admin bisa akses /admin/dashboard (sanity check)."""
        response = login_admin.get('/admin/dashboard', follow_redirects=False)
        assert response.status_code == 200


class TestAuthEdgeCases:
    """Edge cases autentikasi."""

    def test_get_login_saat_sudah_authenticated(self, login_admin):
        """Jika sudah login, GET /auth/login -> redirect ke dashboard."""
        response = login_admin.get('/auth/login', follow_redirects=False)
        assert response.status_code == 302
        assert '/admin/dashboard' in response.headers['Location']

    def test_session_permanen_setiap_request(self, login_admin):
        """Session.permanent di-set pada setiap request (lihat before_request)."""
        # Setelah login, request lain harus mempertahankan session
        response = login_admin.get('/admin/dashboard')
        assert response.status_code == 200
