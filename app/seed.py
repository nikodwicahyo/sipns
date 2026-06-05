"""
Modul: seed.py
Deskripsi: Seed data awal SIPNS (user contoh, siswa, guru, nilai sample).

Modul ini menyediakan Flask CLI command ``flask seed`` yang mengisi
database dengan data contoh untuk demo & development. Dalam mode testing,
fungsi ``seed_data()`` tidak dipanggil otomatis (lihat ``app/__init__.py``).

Data seed:
- 1 admin (username=admin, password=Admin@123)
- 3 guru (Matematika, Bahasa Indonesia, IPA)
- 10 siswa (2 kelas: X-IPA-1, X-IPA-2)
- 24 nilai (kombinasi sebagian siswa-mapel)

Untuk kredensial lengkap, lihat ``docs/seed_credentials.md``.

Author : Niko Dwicahyo
Versi  : 1.0.0
"""
import logging
from flask import current_app
from app import db
from app.models.user import User
from app.models.siswa import Siswa
from app.models.guru import Guru
from app.models.nilai import Nilai
from app.utils.constants import DEFAULT_ADMIN_PASSWORD, DEFAULT_GURU_PASSWORD


logger = logging.getLogger(__name__)


def seed_data():
    """Isi database dengan data awal (admin, guru, siswa, nilai sample).

    Fungsi ini **idempotent**: jika sudah ada user, tidak insert ulang
    (dicek via ``User.query.first()``). Tujuannya agar aman dipanggil
    berulang tanpa duplikasi.

    Raises:
        Exception: Dilempar apa adanya jika terjadi error DB. Caller
            (``register_commands`` di bawah) menangkap dan log ke Flask
            logger agar pesan tampil di console.
    """
    logger.info('Memulai proses seed data SIPNS...')

    # Guard: skip jika sudah ada data — mencegah duplikasi NIS/ID Guru.
    if User.query.first():
        logger.info('Data sudah pernah di-seed. Proses dilewati (idempotent).')
        return

    # ---- 1. Akun Admin ----
    admin = User(username='admin', role='admin', is_active=True)
    admin.set_password(DEFAULT_ADMIN_PASSWORD)
    db.session.add(admin)

    # ---- 2. Data Guru + Akun User terkait ----
    guru_data = [
        {'id_guru': 'GR-001', 'nama_guru': 'Dr. Siti Rahmawati', 'mata_pelajaran': 'Matematika'},
        {'id_guru': 'GR-002', 'nama_guru': 'Ahmad Fauzi, S.Pd.', 'mata_pelajaran': 'Bahasa Indonesia'},
        {'id_guru': 'GR-003', 'nama_guru': 'Dewi Sartika, S.Si.', 'mata_pelajaran': 'IPA'},
    ]

    guru_objects = []
    for g in guru_data:
        guru = Guru(
            id_guru=g['id_guru'],
            nama_guru=g['nama_guru'],
            mata_pelajaran=g['mata_pelajaran'],
        )
        db.session.add(guru)
        db.session.flush()  # flush agar guru.id terisi sebelum membuat User.

        user = User(username=g['id_guru'], role='guru', guru_id=guru.id, is_active=True)
        user.set_password(DEFAULT_GURU_PASSWORD)
        db.session.add(user)
        guru_objects.append(guru)

    # ---- 3. Data Siswa + Akun User terkait ----
    siswa_data = [
        {'nis': '2024001', 'nama': 'Budi Santoso', 'kelas': 'X-IPA-1'},
        {'nis': '2024002', 'nama': 'Ani Wijayanti', 'kelas': 'X-IPA-1'},
        {'nis': '2024003', 'nama': 'Citra Dewi Lestari', 'kelas': 'X-IPA-1'},
        {'nis': '2024004', 'nama': 'Doni Prasetyo', 'kelas': 'X-IPA-1'},
        {'nis': '2024005', 'nama': 'Eka Fitriani', 'kelas': 'X-IPA-1'},
        {'nis': '2024006', 'nama': 'Fajar Hidayat', 'kelas': 'X-IPA-2'},
        {'nis': '2024007', 'nama': 'Gita Permata Sari', 'kelas': 'X-IPA-2'},
        {'nis': '2024008', 'nama': 'Hendra Gunawan', 'kelas': 'X-IPA-2'},
        {'nis': '2024009', 'nama': 'Intan Nurhaliza', 'kelas': 'X-IPA-2'},
        {'nis': '2024010', 'nama': 'Joko Widodo', 'kelas': 'X-IPA-2'},
    ]

    siswa_objects = []
    for s in siswa_data:
        siswa = Siswa(nis=s['nis'], nama=s['nama'], kelas=s['kelas'])
        db.session.add(siswa)
        db.session.flush()  # siswa.id diperlukan untuk FK User.

        # Konvensi: password siswa = NIS (sederhana, untuk demo).
        user = User(username=s['nis'], role='siswa', siswa_id=siswa.id, is_active=True)
        user.set_password(s['nis'])
        db.session.add(user)
        siswa_objects.append(siswa)

    db.session.commit()
    logger.info(
        'Seed master data selesai: 1 admin, %d guru, %d siswa.',
        len(guru_objects),
        len(siswa_objects),
    )

    # ---- 4. Data Nilai (kombinasi sebagian siswa-mapel) ----
    nilai_samples = [
        {'siswa_idx': 0, 'guru_idx': 0, 'tugas': 85, 'uts': 78, 'uas': 82},
        {'siswa_idx': 0, 'guru_idx': 1, 'tugas': 90, 'uts': 85, 'uas': 88},
        {'siswa_idx': 0, 'guru_idx': 2, 'tugas': 75, 'uts': 80, 'uas': 78},
        {'siswa_idx': 1, 'guru_idx': 0, 'tugas': 70, 'uts': 75, 'uas': 72},
        {'siswa_idx': 1, 'guru_idx': 1, 'tugas': 88, 'uts': 82, 'uas': 85},
        {'siswa_idx': 1, 'guru_idx': 2, 'tugas': 65, 'uts': 70, 'uas': 68},
        {'siswa_idx': 2, 'guru_idx': 0, 'tugas': 92, 'uts': 88, 'uas': 90},
        {'siswa_idx': 2, 'guru_idx': 1, 'tugas': 78, 'uts': 80, 'uas': 75},
        {'siswa_idx': 2, 'guru_idx': 2, 'tugas': 85, 'uts': 82, 'uas': 86},
        {'siswa_idx': 3, 'guru_idx': 0, 'tugas': 60, 'uts': 55, 'uas': 58},
        {'siswa_idx': 3, 'guru_idx': 1, 'tugas': 70, 'uts': 65, 'uas': 68},
        {'siswa_idx': 3, 'guru_idx': 2, 'tugas': 55, 'uts': 60, 'uas': 50},
        {'siswa_idx': 4, 'guru_idx': 0, 'tugas': 80, 'uts': 78, 'uas': 85},
        {'siswa_idx': 4, 'guru_idx': 1, 'tugas': 75, 'uts': 70, 'uas': 72},
        {'siswa_idx': 5, 'guru_idx': 0, 'tugas': 95, 'uts': 90, 'uas': 92},
        {'siswa_idx': 5, 'guru_idx': 1, 'tugas': 82, 'uts': 85, 'uas': 80},
        {'siswa_idx': 6, 'guru_idx': 0, 'tugas': 68, 'uts': 72, 'uas': 70},
        {'siswa_idx': 6, 'guru_idx': 1, 'tugas': 77, 'uts': 75, 'uas': 80},
        {'siswa_idx': 7, 'guru_idx': 0, 'tugas': 50, 'uts': 45, 'uas': 55},
        {'siswa_idx': 7, 'guru_idx': 1, 'tugas': 60, 'uts': 58, 'uas': 62},
        {'siswa_idx': 8, 'guru_idx': 0, 'tugas': 88, 'uts': 85, 'uas': 90},
        {'siswa_idx': 8, 'guru_idx': 1, 'tugas': 92, 'uts': 88, 'uas': 85},
        {'siswa_idx': 9, 'guru_idx': 0, 'tugas': 72, 'uts': 68, 'uas': 75},
        {'siswa_idx': 9, 'guru_idx': 1, 'tugas': 80, 'uts': 78, 'uas': 82},
    ]

    for ns in nilai_samples:
        nilai = Nilai(
            siswa_id=siswa_objects[ns['siswa_idx']].id,
            guru_id=guru_objects[ns['guru_idx']].id,
            mata_pelajaran=guru_objects[ns['guru_idx']].mata_pelajaran,
            nilai_tugas=ns['tugas'],
            nilai_uts=ns['uts'],
            nilai_uas=ns['uas'],
        )
        # Panggil method OOP yang mendelegasikan ke fungsi terstruktur
        # di nilai_service (integrasi OOP ↔ Pemrograman Terstruktur).
        nilai.hitung_dan_simpan()
        db.session.add(nilai)

    db.session.commit()
    logger.info(
        'Seed nilai selesai: %d record nilai untuk %d siswa × %d mapel.',
        len(nilai_samples),
        len(siswa_objects),
        len(guru_objects),
    )
    logger.info('Seed data SIPNS berhasil! Silakan login dengan kredensial di docs/seed_credentials.md.')


def register_commands(app):
    """Daftarkan CLI command ``flask seed`` ke aplikasi Flask.

    Dipanggil dari ``app/__init__.py`` saat ``create_app()`` agar command
    tersedia via ``flask --app run.py seed``.

    Args:
        app (Flask): Instance aplikasi Flask.
    """

    @app.cli.command('seed')
    def seed_command():
        """Wrapper CLI untuk ``seed_data()`` dengan error handling."""
        try:
            with app.app_context():
                seed_data()
        except Exception as e:
            current_app.logger.exception('Seed gagal: %s', e)
            raise
