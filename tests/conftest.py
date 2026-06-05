"""
Konfigurasi pytest untuk SIPNS.

Modul ini berisi fixture bersama untuk unit dan integration test.
Strategi isolasi: app session-scoped (hanya inisialisasi, tidak create schema),
db function-scoped dengan drop_all + create_all untuk reset penuh per test.
"""
import os

os.environ['FLASK_ENV'] = 'testing'

import pytest
from app import create_app, db as _db
from app.models.user import User
from app.models.siswa import Siswa
from app.models.guru import Guru
from app.models.nilai import Nilai
from app.models.audit_log import AuditLog


@pytest.fixture(scope='function')
def app():
    """Function-scoped app fixture: Flask app + database fresh per test.

    Setiap test mendapat Flask app yang benar-benar baru (termasuk app context,
    session, SQLAlchemy binding) sehingga tidak ada state pollution antar test.

    Trade-off: ~50-100ms overhead per test untuk re-create app, tapi ini
    jaminan terkuat untuk isolasi. Untuk 50+ test, total overhead ~5-10 detik
    masih dalam batas wajar.
    """
    flask_app = create_app('testing')
    with flask_app.app_context():
        _db.create_all()
        yield flask_app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope='function')
def db(app):
    """Function-scoped database proxy (disediakan oleh app fixture).

    Fixture ini hanya yield reference ke _db yang sudah di-setup oleh `app`.
    """
    yield _db


@pytest.fixture(scope='function')
def client(app, db):
    """Flask test client terikat app + db."""
    return app.test_client()


@pytest.fixture(scope='function')
def admin_user(db):
    """User admin aktif untuk testing."""
    user = User(username='admin', role='admin', is_active=True)
    user.set_password('Admin@123')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture(scope='function')
def guru_user(db):
    """User guru + entitas Guru untuk testing.

    Returns:
        tuple: (user_obj, guru_obj)
    """
    guru = Guru(id_guru='GR-001', nama_guru='Test Guru', mata_pelajaran='Matematika')
    db.session.add(guru)
    db.session.flush()
    user = User(username='GR-001', role='guru', guru_id=guru.id, is_active=True)
    user.set_password('Guru@123')
    db.session.add(user)
    db.session.commit()
    return user, guru


@pytest.fixture(scope='function')
def guru_matematika(db):
    """Guru pengampu Matematika (konsisten dengan PRD seed data)."""
    guru = Guru(id_guru='GR-MAT-UNI', nama_guru='Dr. Siti', mata_pelajaran='Matematika')
    db.session.add(guru)
    db.session.flush()
    user = User(username='GR-MAT-UNI', role='guru', guru_id=guru.id, is_active=True)
    user.set_password('Guru@123')
    db.session.add(user)
    db.session.commit()
    return user, guru


@pytest.fixture(scope='function')
def siswa_user(db):
    """User siswa + entitas Siswa untuk testing.

    Returns:
        tuple: (user_obj, siswa_obj)
    Login siswa: username=NIS, password=NIS (mengikuti konvensi seed).
    """
    siswa = Siswa(nis='2024001', nama='Test Siswa', kelas='X-IPA-1')
    db.session.add(siswa)
    db.session.flush()
    user = User(username='2024001', role='siswa', siswa_id=siswa.id, is_active=True)
    user.set_password('2024001')
    db.session.add(user)
    db.session.commit()
    return user, siswa


@pytest.fixture(scope='function')
def sample_siswa(db):
    """3 siswa: 2 di X-IPA-1, 1 di X-IPA-2."""
    siswa_list = [
        Siswa(nis='2024001', nama='Budi Santoso', kelas='X-IPA-1'),
        Siswa(nis='2024002', nama='Ani Wijayanti', kelas='X-IPA-1'),
        Siswa(nis='2024003', nama='Citra Dewi', kelas='X-IPA-2'),
    ]
    for s in siswa_list:
        db.session.add(s)
    db.session.commit()
    return siswa_list


@pytest.fixture(scope='function')
def sample_guru(db):
    """2 guru: Matematika + Bahasa Indonesia.

    ID unik (GR-SMP-*) untuk menghindari konflik dengan `guru_user` fixture
    yang menggunakan 'GR-001'.
    """
    guru_list = [
        Guru(id_guru='GR-SMP-MAT', nama_guru='Dr. Siti', mata_pelajaran='Matematika'),
        Guru(id_guru='GR-SMP-BIN', nama_guru='Ahmad Fauzi', mata_pelajaran='Bahasa Indonesia'),
    ]
    for g in guru_list:
        db.session.add(g)
    db.session.commit()
    return guru_list


@pytest.fixture(scope='function')
def sample_nilai(db, sample_siswa, sample_guru):
    """Nilai untuk semua kombinasi siswa-mapel (3x2=6 records).

    Nilai random dalam rentang valid (60-100) agar konsisten lulus.
    """
    import random
    rng = random.Random(42)  # deterministic untuk reproducibility
    nilai_list = []
    for siswa in sample_siswa:
        for guru in sample_guru:
            n = Nilai(
                siswa_id=siswa.id,
                guru_id=guru.id,
                mata_pelajaran=guru.mata_pelajaran,
                nilai_tugas=rng.uniform(60, 100),
                nilai_uts=rng.uniform(60, 100),
                nilai_uas=rng.uniform(60, 100),
            )
            n.hitung_dan_simpan()
            db.session.add(n)
            nilai_list.append(n)
    db.session.commit()
    return nilai_list


@pytest.fixture(scope='function')
def sample_audit_logs(db, admin_user):
    """3 audit log entries untuk testing endpoint audit."""
    from datetime import datetime, timedelta
    logs = []
    for i, (action, table) in enumerate([
        ('INSERT', 'siswa'),
        ('UPDATE', 'guru'),
        ('DELETE', 'nilai'),
    ]):
        log = AuditLog(
            user_id=admin_user.id,
            action=action,
            table_name=table,
            record_id=i + 1,
            description=f'Test {action} on {table}',
            ip_address='127.0.0.1',
            created_at=datetime.utcnow() - timedelta(hours=i),
        )
        db.session.add(log)
        logs.append(log)
    db.session.commit()
    return logs


# --- Login fixtures (via real POST /auth/login untuk menguji alur nyata) ---

@pytest.fixture(scope='function')
def login_admin(client, admin_user):
    """Login sebagai admin via POST /auth/login. Mengembalikan client."""
    response = client.post('/auth/login', data={
        'username': 'admin',
        'password': 'Admin@123',
    }, follow_redirects=False)
    assert response.status_code in (200, 302), f'Login admin gagal: {response.status_code}'
    return client


@pytest.fixture(scope='function')
def login_guru(client, guru_user):
    """Login sebagai guru via POST /auth/login."""
    user, _ = guru_user
    response = client.post('/auth/login', data={
        'username': user.username,
        'password': 'Guru@123',
    }, follow_redirects=False)
    assert response.status_code in (200, 302), f'Login guru gagal: {response.status_code}'
    return client


@pytest.fixture(scope='function')
def login_siswa(client, siswa_user):
    """Login sebagai siswa via POST /auth/login.

    Siswa login: username=NIS, password=NIS (mengikuti seed/PRD).
    """
    user, _ = siswa_user
    response = client.post('/auth/login', data={
        'username': user.username,
        'password': user.username,  # password = NIS
    }, follow_redirects=False)
    assert response.status_code in (200, 302), f'Login siswa gagal: {response.status_code}'
    return client
