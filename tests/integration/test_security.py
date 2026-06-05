"""
Security tests untuk SIPNS.

Sesuai PRD.md:
- F6-066: CSRF protection aktif
- F6-067: Akses tanpa login ditolak
- F6-068: Role isolation (guru tidak bisa akses admin)
- F6-069: SQL injection tidak berbahaya
- F6-070: XSS payload ditampilkan sebagai teks
"""
import pytest

from app.models.siswa import Siswa
from app.models.user import User


class TestCSRFProtection:
    """Menguji bahwa CSRF protection aktif (F6-066)."""

    def test_csrf_form_tanpa_token_ditolak(self, csrf_app, csrf_client, db):
        """CSRF: POST form tanpa token CSRF -> 400."""
        # csrf_app sudah punya WTF_CSRF_ENABLED=True
        # Setup admin user
        admin = User(username='admin', role='admin', is_active=True)
        admin.set_password('Admin@123')
        db.session.add(admin)
        db.session.commit()

        # Login tanpa token (CSRF exempt untuk login biasanya, tapi kita test endpoint lain)
        # Login dulu untuk dapat session
        csrf_client.post('/auth/login', data={
            'username': 'admin',
            'password': 'Admin@123',
        }, follow_redirects=False)

        # Sekarang coba submit form siswa tanpa CSRF token
        # CSRFProtect akan reject request tanpa token
        response = csrf_client.post('/admin/siswa/tambah', data={
            'nis': '2024099',
            'nama': 'CSRF Test',
            'kelas': 'X-IPA-1',
        }, follow_redirects=False)
        # CSRF enabled -> 400 BAD REQUEST
        assert response.status_code == 400


class TestAksesTanpaLogin:
    """Menguji bahwa semua route terproteksi menolak akses tanpa login (F6-067)."""

    @pytest.mark.parametrize('route', [
        '/admin/dashboard',
        '/admin/siswa',
        '/admin/siswa/tambah',
        '/admin/guru',
        '/admin/guru/tambah',
        '/admin/users',
        '/admin/audit',
        '/guru/dashboard',
        '/guru/nilai/input',
        '/guru/nilai/rekap',
        '/siswa/dashboard',
        '/siswa/nilai',
        '/laporan/rekap-kelas',
        '/laporan/excel',
    ])
    def test_route_tanpa_login_redirect_ke_login(self, client, route):
        """Semua route terproteksi harus redirect ke /auth/login."""
        response = client.get(route, follow_redirects=False)
        assert response.status_code == 302
        assert '/auth/login' in response.headers['Location']


class TestRoleIsolation:
    """Menguji role isolation: setiap role hanya bisa akses endpointnya (F6-068)."""

    def test_guru_tidak_boleh_akses_admin_dashboard(self, login_guru):
        """Guru akses /admin/dashboard -> 403 atau redirect."""
        response = login_guru.get('/admin/dashboard', follow_redirects=False)
        assert response.status_code in (302, 403)

    def test_guru_tidak_boleh_akses_admin_siswa(self, login_guru):
        """Guru akses /admin/siswa -> 403 atau redirect."""
        response = login_guru.get('/admin/siswa', follow_redirects=False)
        assert response.status_code in (302, 403)

    def test_siswa_tidak_boleh_akses_guru_input_nilai(self, login_siswa):
        """Siswa akses /guru/nilai/input -> 403 atau redirect."""
        response = login_siswa.get('/guru/nilai/input', follow_redirects=False)
        assert response.status_code in (302, 403)

    def test_siswa_tidak_boleh_akses_admin(self, login_siswa):
        """Siswa akses /admin/users -> 403 atau redirect."""
        response = login_siswa.get('/admin/users', follow_redirects=False)
        assert response.status_code in (302, 403)

    def test_admin_tidak_boleh_akses_guru_dashboard(self, login_admin):
        """Admin akses /guru/dashboard -> 403 atau redirect."""
        response = login_admin.get('/guru/dashboard', follow_redirects=False)
        assert response.status_code in (302, 403)


class TestSQLInjection:
    """Menguji bahwa input SQL-like aman dari SQL injection (F6-069)."""

    def test_sql_injection_pada_nis_ditangani_aman(self, login_admin, db):
        """NIS dengan payload SQL injection harus ditangani ORM (tidak eksekusi).

        Payload dipersingkat (max 20 char sesuai Length validator) agar lolos
        validasi form dan benar-benar masuk ke DB untuk uji ORM safety.
        """
        # Payload pendek yang masih mengandung karakter SQL injection
        malicious_nis = "x';DROP--"
        response = login_admin.post('/admin/siswa/tambah', data={
            'nis': malicious_nis,
            'nama': 'SQLi Test',
            'kelas': 'X-IPA-1',
        }, follow_redirects=False)
        assert response.status_code == 302

        # Tabel siswa masih ada (tidak di-drop)
        siswa_list = Siswa.query.all()
        assert len(siswa_list) == 1
        siswa = siswa_list[0]
        assert siswa.nis == malicious_nis  # Disimpan sebagai string literal
        # Tabel masih bisa di-query
        assert Siswa.query.filter_by(nama='SQLi Test').first() is not None

    def test_sql_injection_pada_username_login(self, client):
        """Username dengan SQL injection tidak bypass auth."""
        response = client.post('/auth/login', data={
            'username': "admin' OR '1'='1",
            'password': 'whatever',
        }, follow_redirects=False)
        # Tidak authenticated, kembali ke login
        assert response.status_code == 200
        assert b'salah' in response.data.lower() or b'error' in response.data.lower()

    def test_sql_injection_pada_search_query(self, login_admin, sample_siswa):
        """Search dengan SQL injection tidak merusak data."""
        malicious = "'; DELETE FROM siswa; --"
        # Akses halaman daftar siswa
        response = login_admin.get(f'/admin/siswa?q={malicious}')
        assert response.status_code == 200
        # Siswa masih ada
        assert Siswa.query.count() == 3


class TestXSS:
    """Menguji bahwa input XSS ditampilkan sebagai teks (F6-070)."""

    def test_xss_pada_nama_siswa_ditampilkan_sebagai_teks(self, login_admin, db):
        """Nama dengan payload XSS harus di-escape Jinja2, tidak dieksekusi."""
        xss_payload = '<script>alert("xss")</script>'
        response = login_admin.post('/admin/siswa/tambah', data={
            'nis': '2024099',
            'nama': xss_payload,
            'kelas': 'X-IPA-1',
        }, follow_redirects=False)
        assert response.status_code == 302

        # Siswa tersimpan
        siswa = Siswa.query.filter_by(nis='2024099').first()
        assert siswa is not None
        assert siswa.nama == xss_payload  # Disimpan apa adanya

        # Tampilkan di halaman daftar
        response = login_admin.get('/admin/siswa')
        assert response.status_code == 200
        # Payload XSS harus di-escape (muncul sebagai teks)
        html = response.data.decode('utf-8', errors='ignore')
        # TIDAK boleh ada tag script yang aktif
        assert '<script>alert("xss")</script>' not in html
        # Yang ada adalah versi yang di-escape
        assert '&lt;script&gt;' in html or 'alert' in html

    def test_xss_pada_nama_siswa_di_template(self, login_admin, db):
        """Pastikan XSS payload di-escape di semua template (detail siswa)."""
        xss_payload = '<img src=x onerror=alert(1)>'
        siswa_baru = Siswa(nis='2024050', nama=xss_payload, kelas='X-IPA-1')
        db.session.add(siswa_baru)
        db.session.commit()

        # Buka halaman detail siswa
        response = login_admin.get(f'/admin/siswa/{siswa_baru.id}')
        assert response.status_code == 200
        html = response.data.decode('utf-8', errors='ignore')
        # TIDAK boleh ada tag yang tidak di-escape
        assert '<img src=x onerror=alert(1)>' not in html
        # Yang ada adalah versi yang di-escape
        assert '&lt;img' in html


class TestPasswordSecurity:
    """Menguji keamanan password handling."""

    def test_password_disimpan_sebagai_hash(self, db):
        """Password di-hash, TIDAK boleh plaintext di database."""
        from app.models.user import User
        user = User(username='secure', role='siswa')
        user.set_password('PlainTextPassword')
        db.session.add(user)
        db.session.commit()

        # Ambil ulang dari DB untuk verifikasi
        saved = User.query.filter_by(username='secure').first()
        # Password plaintext TIDAK boleh ada
        assert 'PlainTextPassword' not in saved.password_hash
        # Hash tidak sama dengan plaintext
        assert saved.password_hash != 'PlainTextPassword'
        # Tapi tetap bisa di-verify
        assert saved.check_password('PlainTextPassword')

    def test_password_hash_berbeda_untuk_password_sama(self, db):
        """Hash harus unik per password (salt random)."""
        from app.models.user import User
        u1 = User(username='u1', role='siswa')
        u1.set_password('SamePassword')
        u2 = User(username='u2', role='siswa')
        u2.set_password('SamePassword')
        # Hash harus berbeda karena salt random
        assert u1.password_hash != u2.password_hash
