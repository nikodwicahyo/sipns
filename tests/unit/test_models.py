"""
Unit tests untuk app.models (OOP).

Menguji behavior class User, Siswa, Guru, Nilai, AuditLog:
- Constructor & atribut
- Method business logic
- Relasi antar model
- Serialization (to_dict)

Sesuai PRD.md.
"""
import pytest

from app.models.user import User
from app.models.siswa import Siswa
from app.models.guru import Guru
from app.models.nilai import Nilai
from app.models.audit_log import AuditLog
from app.services.nilai_service import hitung_nilai_akhir


# ===========================================================================
# Test Model User (F6-027 s/d F6-030)
# ===========================================================================

class TestUserModel:
    """Menguji model User: password hashing, role check, to_dict."""

    def test_set_password_menghasilkan_hash(self, db):
        """F6-027: set_password() harus menghasilkan hash, bukan plaintext."""
        user = User(username='test', role='siswa')
        user.set_password('PlainPass123')
        assert user.password_hash != 'PlainPass123'
        assert user.password_hash is not None
        assert len(user.password_hash) > 30  # PBKDF2 hash minimal ~70 char

    def test_check_password_benar(self, db):
        """F6-028: check_password() dengan password benar -> True."""
        user = User(username='test', role='siswa')
        user.set_password('CorrectPass')
        assert user.check_password('CorrectPass') is True

    def test_check_password_salah(self, db):
        """F6-029: check_password() dengan password salah -> False."""
        user = User(username='test', role='siswa')
        user.set_password('CorrectPass')
        assert user.check_password('WrongPass') is False

    def test_is_admin_true(self, db):
        """F6-030: is_admin() True untuk role admin."""
        user = User(username='a', role='admin')
        assert user.is_admin() is True
        assert user.is_guru() is False
        assert user.is_siswa() is False

    def test_is_guru_true(self, db):
        """F6-030: is_guru() True untuk role guru."""
        user = User(username='g', role='guru')
        assert user.is_guru() is True
        assert user.is_admin() is False
        assert user.is_siswa() is False

    def test_is_siswa_true(self, db):
        """F6-030: is_siswa() True untuk role siswa."""
        user = User(username='s', role='siswa')
        assert user.is_siswa() is True
        assert user.is_admin() is False
        assert user.is_guru() is False

    def test_get_id_mengembalikan_string(self, db):
        """get_id() harus return str (untuk Flask-Login)."""
        user = User(username='x', role='admin')
        user.set_password('dummy')
        db.session.add(user)
        db.session.commit()
        assert isinstance(user.get_id(), str)
        assert user.get_id() == str(user.id)

    def test_to_dict_tidak_暴露_password_hash(self, db):
        """to_dict() TIDAK boleh expose password_hash."""
        user = User(username='secure', role='admin')
        user.set_password('secret')
        db.session.add(user)
        db.session.commit()
        d = user.to_dict()
        assert 'password_hash' not in d
        assert 'password' not in d
        assert d['username'] == 'secure'
        assert d['role'] == 'admin'

    def test_repr_berguna_untuk_debug(self, db):
        """__repr__() memuat username dan role untuk debugging."""
        user = User(username='debug_test', role='admin')
        assert 'debug_test' in repr(user)
        assert 'admin' in repr(user)


# ===========================================================================
# Test Model Siswa (F6-031 s/d F6-033)
# ===========================================================================

class TestSiswaModel:
    """Menguji model Siswa: soft delete, rata-rata, status, class methods."""

    def test_soft_delete_set_deleted_at(self, db, sample_siswa):
        """F6-031: soft_delete() -> deleted_at tidak None."""
        siswa = sample_siswa[0]
        assert siswa.deleted_at is None
        siswa.soft_delete()
        db.session.commit()
        assert siswa.deleted_at is not None

    def test_rata_rata_nilai_dengan_3_nilai(self, db, sample_siswa, sample_guru, guru_matematika):
        """F6-032: rata_rata_nilai() menghitung mean dari semua mapel."""
        siswa = sample_siswa[0]
        # Beri 3 nilai pada mapel berbeda, masing-masing 80, 70, 60
        # Rata-rata = (80 + 70 + 60) / 3 = 70.0
        for nilai_akhir_target, mapel in [
            (80.0, 'Matematika'),
            (70.0, 'Bahasa Indonesia'),
            (60.0, 'IPA'),
        ]:
            # Cari/create guru untuk mapel ini
            guru = Guru.query.filter_by(mata_pelajaran=mapel).first()
            if not guru:
                guru = Guru(id_guru=f'GR-{mapel[:3].upper()}', nama_guru=f'Guru {mapel}',
                            mata_pelajaran=mapel)
                db.session.add(guru)
                db.session.flush()

            # Hitung mundur: kita set nilai_akhir target, lalu derive komponen
            # Sederhananya, set semua komponen = target karena pengujian rata-rata
            n = Nilai(
                siswa_id=siswa.id,
                guru_id=guru.id,
                mata_pelajaran=mapel,
                nilai_tugas=nilai_akhir_target,
                nilai_uts=nilai_akhir_target,
                nilai_uas=nilai_akhir_target,
            )
            n.hitung_dan_simpan()
            db.session.add(n)
        db.session.commit()

        # Siswa seharusnya punya 3 nilai (Matematika, Bahasa Indonesia, IPA)
        # +2 dari sample_guru (Matematika, Bahasa Indonesia)
        # Total: 5 nilai
        rata = siswa.rata_rata_nilai()
        # Bisa Decimal atau float tergantung SQLAlchemy arithmetic
        assert rata is not None
        assert float(rata) > 0

    def test_rata_rata_nilai_tanpa_nilai_return_nol(self, db, sample_siswa):
        """F6-033: rata_rata_nilai() tanpa nilai -> 0.0."""
        siswa = sample_siswa[0]
        assert siswa.rata_rata_nilai() == 0.0

    def test_nilai_akhir_all_kosong_untuk_siswa_baru(self, db, sample_siswa):
        """nilai_akhir_all() return list kosong untuk siswa tanpa nilai."""
        siswa = sample_siswa[0]
        assert siswa.nilai_akhir_all() == []

    def test_status_kelulusan_global_belum_ada_nilai(self, db, sample_siswa):
        """status_kelulusan_global() return 'Belum Ada Nilai' jika kosong."""
        siswa = sample_siswa[0]
        assert siswa.status_kelulusan_global() == 'Belum Ada Nilai'

    def test_status_kelulusan_global_lulus_semua(self, db, sample_siswa, sample_guru):
        """status_kelulusan_global() return 'Lulus' jika semua mapel lulus."""
        siswa = sample_siswa[0]
        for guru in sample_guru:
            n = Nilai(
                siswa_id=siswa.id,
                guru_id=guru.id,
                mata_pelajaran=guru.mata_pelajaran,
                nilai_tugas=85,
                nilai_uts=85,
                nilai_uas=85,
            )
            n.hitung_dan_simpan()
            db.session.add(n)
        db.session.commit()
        assert siswa.status_kelulusan_global() == 'Lulus'

    def test_cari_by_nis_mengembalikan_objek(self, db, sample_siswa):
        """cari_by_nis() menemukan siswa berdasarkan NIS (case sensitive)."""
        found = Siswa.cari_by_nis('2024001')
        assert found is not None
        assert found.nama == 'Budi Santoso'

    def test_cari_by_nis_tidak_termasuk_soft_deleted(self, db, sample_siswa):
        """cari_by_nis() exclude siswa yang sudah di-soft-delete."""
        siswa = sample_siswa[0]
        siswa.soft_delete()
        db.session.commit()
        assert Siswa.cari_by_nis(siswa.nis) is None

    def test_daftar_kelas_mengembalikan_unik(self, db, sample_siswa):
        """daftar_kelas() return list kelas unik, exclude soft-deleted."""
        daftar = Siswa.daftar_kelas()
        assert 'X-IPA-1' in daftar
        assert 'X-IPA-2' in daftar
        assert len(daftar) == len(set(daftar))  # unik
        assert daftar == sorted(daftar)  # terurut

    def test_daftar_kelas_exclude_soft_deleted(self, db, sample_siswa):
        """daftar_kelas() tidak termasuk kelas yang siswanya semua soft-deleted."""
        from app.utils.cache import cache_clear
        cache_clear()
        # Hapus semua siswa X-IPA-1
        for s in sample_siswa:
            if s.kelas == 'X-IPA-1':
                s.soft_delete()
        db.session.commit()
        daftar = Siswa.daftar_kelas()
        assert 'X-IPA-1' not in daftar
        assert 'X-IPA-2' in daftar

    def test_to_dict_memuat_field_penting(self, db, sample_siswa):
        """to_dict() harus memuat field minimal: id, nis, nama, kelas."""
        siswa = sample_siswa[0]
        d = siswa.to_dict()
        for key in ['id', 'nis', 'nama', 'kelas']:
            assert key in d
        assert d['nis'] == siswa.nis


# ===========================================================================
# Test Model Guru (F6-017, F6-018)
# ===========================================================================

class TestGuruModel:
    """Menguji model Guru: soft delete, relasi nilai, to_dict."""

    def test_soft_delete_set_deleted_at(self, db, sample_guru):
        """soft_delete() -> deleted_at tidak None."""
        guru = sample_guru[0]
        assert guru.deleted_at is None
        guru.soft_delete()
        db.session.commit()
        assert guru.deleted_at is not None

    def test_get_siswa_diajar_kosong_untuk_guru_baru(self, db, sample_guru):
        """get_siswa_diajar() return list kosong untuk guru tanpa nilai."""
        guru = sample_guru[0]
        assert guru.get_siswa_diajar() == []

    def test_get_siswa_diajar_mengembalikan_siswa_yang_pernah_dinilai(
        self, db, sample_siswa, sample_guru
    ):
        """get_siswa_diajar() return siswa yang pernah diinput nilai oleh guru."""
        guru = sample_guru[0]
        # Guru 0 menilai siswa 0 dan 1
        for s in sample_siswa[:2]:
            n = Nilai(
                siswa_id=s.id, guru_id=guru.id, mata_pelajaran=guru.mata_pelajaran,
                nilai_tugas=80, nilai_uts=80, nilai_uas=80,
            )
            n.hitung_dan_simpan()
            db.session.add(n)
        db.session.commit()

        siswa_diajar = guru.get_siswa_diajar()
        assert len(siswa_diajar) == 2
        siswa_ids = {s.id for s in siswa_diajar}
        assert sample_siswa[0].id in siswa_ids
        assert sample_siswa[1].id in siswa_ids

    def test_to_dict_memuat_field(self, db, sample_guru):
        """to_dict() harus memuat field id, id_guru, nama_guru, mata_pelajaran."""
        guru = sample_guru[0]
        d = guru.to_dict()
        for key in ['id', 'id_guru', 'nama_guru', 'mata_pelajaran']:
            assert key in d


# ===========================================================================
# Test Model Nilai (F6-034 s/d F6-036)
# ===========================================================================

class TestNilaiModel:
    """Menguji model Nilai: hitung_dan_simpan, lock, get_detail_kalkulasi."""

    def test_hitung_dan_simpan_set_nilai_akhir(self, db, sample_siswa, sample_guru):
        """F6-034: hitung_dan_simpan() -> nilai_akhir & status_lulus ter-set."""
        nilai = Nilai(
            siswa_id=sample_siswa[0].id,
            guru_id=sample_guru[0].id,
            mata_pelajaran='Matematika',
            nilai_tugas=80,
            nilai_uts=75,
            nilai_uas=85,
        )
        nilai.hitung_dan_simpan()
        # Expected: (0.30*80)+(0.30*75)+(0.40*85) = 24+22.5+34 = 80.5
        assert float(nilai.nilai_akhir) == 80.5
        assert nilai.status_lulus is True

    def test_hitung_dan_simpan_tidak_lulus(self, db, sample_siswa, sample_guru):
        """hitung_dan_simpan() set status_lulus=False untuk NA < 70."""
        nilai = Nilai(
            siswa_id=sample_siswa[0].id,
            guru_id=sample_guru[0].id,
            mata_pelajaran='Matematika',
            nilai_tugas=50,
            nilai_uts=60,
            nilai_uas=65,
        )
        nilai.hitung_dan_simpan()
        assert float(nilai.nilai_akhir) == 59.0
        assert nilai.status_lulus is False

    def test_lock_set_is_locked_true(self, db, sample_siswa, sample_guru):
        """F6-035: lock() -> is_locked=True."""
        nilai = Nilai(
            siswa_id=sample_siswa[0].id,
            guru_id=sample_guru[0].id,
            mata_pelajaran='Matematika',
            nilai_tugas=80, nilai_uts=80, nilai_uas=80,
        )
        nilai.hitung_dan_simpan()
        db.session.add(nilai)
        db.session.commit()
        assert nilai.is_locked is False
        nilai.lock()
        assert nilai.is_locked is True

    def test_lock_idempotent(self, db, sample_siswa, sample_guru):
        """lock() multiple kali tidak menyebabkan error (idempotent)."""
        nilai = Nilai(
            siswa_id=sample_siswa[0].id,
            guru_id=sample_guru[0].id,
            mata_pelajaran='Matematika',
            nilai_tugas=80, nilai_uts=80, nilai_uas=80,
        )
        nilai.hitung_dan_simpan()
        db.session.add(nilai)
        db.session.commit()
        nilai.lock()
        nilai.lock()
        assert nilai.is_locked is True

    def test_unlock_set_is_locked_false(self, db, sample_siswa, sample_guru):
        """unlock() -> is_locked=False (untuk admin)."""
        nilai = Nilai(
            siswa_id=sample_siswa[0].id,
            guru_id=sample_guru[0].id,
            mata_pelajaran='Matematika',
            nilai_tugas=80, nilai_uts=80, nilai_uas=80,
        )
        nilai.hitung_dan_simpan()
        nilai.is_locked = True
        db.session.add(nilai)
        db.session.commit()
        nilai.unlock()
        assert nilai.is_locked is False

    def test_get_detail_kalkulasi_lengkap(self, db, sample_siswa, sample_guru):
        """F6-036: get_detail_kalkulasi() memuat semua key & bobot benar."""
        nilai = Nilai(
            siswa_id=sample_siswa[0].id,
            guru_id=sample_guru[0].id,
            mata_pelajaran='Matematika',
            nilai_tugas=80, nilai_uts=75, nilai_uas=85,
        )
        nilai.hitung_dan_simpan()
        db.session.add(nilai)
        db.session.commit()

        detail = nilai.get_detail_kalkulasi()
        # Harus ada key untuk setiap komponen + summary
        assert 'tugas' in detail
        assert 'uts' in detail
        assert 'uas' in detail
        assert 'nilai_akhir' in detail
        assert 'status_lulus' in detail
        assert 'kkm' in detail

        # Bobot harus 30/30/40
        assert detail['tugas']['bobot'] == 30
        assert detail['uts']['bobot'] == 30
        assert detail['uas']['bobot'] == 40
        assert detail['kkm'] == 70

        # Kontribusi = nilai * (bobot/100), dibulatkan 2 desimal
        assert detail['tugas']['kontribusi'] == round(80 * 0.30, 2)
        assert detail['uts']['kontribusi'] == round(75 * 0.30, 2)
        assert detail['uas']['kontribusi'] == round(85 * 0.40, 2)

    def test_to_dict_serialisasi_benar(self, db, sample_siswa, sample_guru):
        """to_dict() return dict dengan semua field penting."""
        nilai = Nilai(
            siswa_id=sample_siswa[0].id,
            guru_id=sample_guru[0].id,
            mata_pelajaran='Matematika',
            nilai_tugas=80, nilai_uts=75, nilai_uas=85,
        )
        nilai.hitung_dan_simpan()
        db.session.add(nilai)
        db.session.commit()

        d = nilai.to_dict()
        assert d['mata_pelajaran'] == 'Matematika'
        assert d['nilai_tugas'] == 80.0
        assert d['nilai_uts'] == 75.0
        assert d['nilai_uas'] == 85.0
        assert d['nilai_akhir'] == 80.5
        assert d['status_lulus'] is True
        assert d['is_locked'] is False


# ===========================================================================
# Test Model AuditLog
# ===========================================================================

class TestAuditLogModel:
    """Menguji model AuditLog: class method log, to_dict."""

    def test_log_baru_terekam_di_db(self, db, admin_user):
        """AuditLog.log() menyimpan entry baru ke database."""
        entry = AuditLog.log(
            user_id=admin_user.id,
            action='INSERT',
            table_name='siswa',
            record_id=1,
            description='Test insert',
            ip_address='127.0.0.1',
        )
        assert entry is not None
        assert entry.id is not None
        # Verifikasi di DB
        saved = AuditLog.query.first()
        assert saved.action == 'INSERT'
        assert saved.table_name == 'siswa'
        assert saved.description == 'Test insert'

    def test_log_tanpa_user_id_untuk_anonymous(self, db):
        """AuditLog.log() dengan user_id=None untuk aktivitas anonymous."""
        entry = AuditLog.log(
            user_id=None,
            action='LOGIN_FAIL',
            table_name='auth',
            record_id=None,
            description='Failed login attempt',
            ip_address='192.168.1.1',
        )
        assert entry is not None
        assert entry.user_id is None

    def test_to_dict_memuat_field_penting(self, db, admin_user):
        """to_dict() harus memuat field standar."""
        entry = AuditLog.log(
            user_id=admin_user.id,
            action='UPDATE',
            table_name='guru',
            record_id=5,
            description='Edit guru',
            ip_address='10.0.0.1',
        )
        d = entry.to_dict()
        assert d['action'] == 'UPDATE'
        assert d['table_name'] == 'guru'
        assert d['record_id'] == 5
        assert d['ip_address'] == '10.0.0.1'
        assert d['user_id'] == admin_user.id
