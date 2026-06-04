from app import db
from app.models.user import User
from app.models.siswa import Siswa
from app.models.guru import Guru
from app.models.nilai import Nilai
from datetime import datetime


def seed_data():
    print("Seeding data...")

    if User.query.first():
        print("Data already seeded. Skipping.")
        return

    admin = User(username='admin', role='admin', is_active=True)
    admin.set_password('Admin@123')
    db.session.add(admin)

    guru_data = [
        {'id_guru': 'GR-001', 'nama_guru': 'Dr. Siti Rahmawati', 'mata_pelajaran': 'Matematika'},
        {'id_guru': 'GR-002', 'nama_guru': 'Ahmad Fauzi, S.Pd.', 'mata_pelajaran': 'Bahasa Indonesia'},
        {'id_guru': 'GR-003', 'nama_guru': 'Dewi Sartika, S.Si.', 'mata_pelajaran': 'IPA'},
    ]

    guru_objects = []
    for g in guru_data:
        guru = Guru(id_guru=g['id_guru'], nama_guru=g['nama_guru'], mata_pelajaran=g['mata_pelajaran'])
        db.session.add(guru)
        db.session.flush()

        user = User(username=g['id_guru'], role='guru', guru_id=guru.id, is_active=True)
        user.set_password('Guru@123')
        db.session.add(user)
        guru_objects.append(guru)

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
        db.session.flush()

        user = User(username=s['nis'], role='siswa', siswa_id=siswa.id, is_active=True)
        user.set_password(s['nis'])
        db.session.add(user)
        siswa_objects.append(siswa)

    db.session.commit()

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
        nilai.hitung_dan_simpan()
        db.session.add(nilai)

    db.session.commit()
    print("Seed data berhasil!")


def register_commands(app):
    @app.cli.command('seed')
    def seed_command():
        seed_data()
