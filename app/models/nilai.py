"""
Modul: nilai.py
Deskripsi: Model OOP untuk entitas Nilai.

Class ``Nilai`` mengintegrasikan paradigma OOP (SQLAlchemy ORM) dengan
Pemrograman Terstruktur (fungsi ``hitung_nilai_akhir`` dan
``tentukan_status_kelulusan`` dari ``app.services.nilai_service``).

Constraint utama:
- UNIQUE(siswa_id, mata_pelajaran) → satu siswa hanya punya satu nilai
  per mata pelajaran (PRD §14 Batasan #1).
- CHECK 0-100 pada semua komponen nilai (Tugas/UTS/UAS/akhir) →
  penjagaan di level DB selain validasi form & service.

Author : Niko Dwicahyo
Versi  : 1.0.0
"""
from app import db
from datetime import datetime
from app.services.nilai_service import hitung_nilai_akhir, tentukan_status_kelulusan
from app.utils.constants import (
    BOBOT_TUGAS,
    BOBOT_UTS,
    BOBOT_UAS,
    KKM,
    PEMBULATAN_DESIMAL,
    RENTANG_NILAI_MAX,
    RENTANG_NILAI_MIN,
)


class Nilai(db.Model):
    """Model OOP entitas Nilai — record nilai siswa per mata pelajaran.

    Model ini adalah contoh **integrasi OOP ↔ Pemrograman Terstruktur**:
    method ``hitung_dan_simpan()`` memanggil fungsi terstruktur murni dari
    ``nilai_service`` untuk melakukan kalkulasi dan validasi, sehingga
    logika bisnis tetap terisolasi dan dapat diuji secara unit.

    Attributes:
        id (int): Primary key auto-increment.
        siswa_id (int): Foreign key ke ``siswa.id``. Wajib diisi.
        guru_id (int): Foreign key ke ``guru.id``. Wajib diisi (guru
            yang menginput nilai).
        mata_pelajaran (str): Nama mata pelajaran (mis. "Matematika").
        nilai_tugas (Decimal): Nilai tugas harian, 0-100.
        nilai_uts (Decimal): Nilai Ujian Tengah Semester, 0-100.
        nilai_uas (Decimal): Nilai Ujian Akhir Semester, 0-100.
        nilai_akhir (Decimal): Hasil kalkulasi otomatis oleh
            ``hitung_dan_simpan()`` (kosong saat pertama insert).
        status_lulus (bool): ``True`` jika ``nilai_akhir >= KKM``,
            ``False`` jika tidak lulus. ``None`` sebelum dihitung.
        is_locked (bool): ``True`` jika nilai sudah dikunci guru
            (tidak dapat diubah, hanya admin yang bisa unlock).
        created_at (datetime): Timestamp insert.
        updated_at (datetime): Timestamp update terakhir (auto via
            SQLAlchemy ``onupdate``).
    """

    __tablename__ = 'nilai'

    id = db.Column(db.Integer, primary_key=True)
    siswa_id = db.Column(db.Integer, db.ForeignKey('siswa.id'), nullable=False)
    guru_id = db.Column(db.Integer, db.ForeignKey('guru.id'), nullable=False)
    mata_pelajaran = db.Column(db.String(100), nullable=False)
    nilai_tugas = db.Column(db.Numeric(5, 2), nullable=False)
    nilai_uts = db.Column(db.Numeric(5, 2), nullable=False)
    nilai_uas = db.Column(db.Numeric(5, 2), nullable=False)
    # nilai_akhir & status_lulus di-skip dari CHECK agar bisa NULL saat insert
    # pertama (record baru akan dihitung via hitung_dan_simpan sebelum commit).
    nilai_akhir = db.Column(db.Numeric(5, 2), nullable=True)
    status_lulus = db.Column(db.Boolean, nullable=True)
    is_locked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        # Satu siswa hanya boleh punya satu nilai per mata pelajaran.
        db.UniqueConstraint('siswa_id', 'mata_pelajaran', name='uq_siswa_mapel'),
        # DB-level guard untuk rentang nilai 0-100 (defense in depth).
        db.CheckConstraint(
            f'nilai_tugas >= {RENTANG_NILAI_MIN} AND nilai_tugas <= {RENTANG_NILAI_MAX}',
            name='ck_nilai_tugas_range',
        ),
        db.CheckConstraint(
            f'nilai_uts >= {RENTANG_NILAI_MIN} AND nilai_uts <= {RENTANG_NILAI_MAX}',
            name='ck_nilai_uts_range',
        ),
        db.CheckConstraint(
            f'nilai_uas >= {RENTANG_NILAI_MIN} AND nilai_uas <= {RENTANG_NILAI_MAX}',
            name='ck_nilai_uas_range',
        ),
        db.CheckConstraint(
            f'nilai_akhir >= {RENTANG_NILAI_MIN} AND nilai_akhir <= {RENTANG_NILAI_MAX}',
            name='ck_nilai_akhir_range',
        ),
    )

    def __repr__(self):
        return (
            f'<Nilai siswa_id={self.siswa_id} mapel={self.mata_pelajaran} '
            f'akhir={self.nilai_akhir}>'
        )

    def hitung_dan_simpan(self):
        """Hitung nilai_akhir & status_lulus dengan memanggil fungsi terstruktur.

        Method ini adalah titik integrasi utama antara OOP (model) dan
        Pemrograman Terstruktur (service). Pola: objek menyimpan data
        (``nilai_tugas``, ``nilai_uts``, ``nilai_uas``), lalu **mendelegasikan**
        logika kalkulasi ke fungsi murni di ``nilai_service`` yang tidak
        punya akses ke ``self`` atau ORM.

        Keuntungan integrasi ini:
        - Fungsi kalkulasi mudah di-unit-test tanpa Flask app context.
        - Logika terpusat — perubahan formula hanya di satu tempat.
        - Model tetap tipis (thin model), tidak mengandung business logic
          selain delegasi.

        Side effect: method ini **memodifikasi** ``self.nilai_akhir`` dan
        ``self.status_lulus`` di tempat. Caller (``guru/routes.py``)
        bertanggung jawab melakukan ``db.session.commit()`` untuk
        menyimpan perubahan.
        """
        # Konversi Decimal→float karena service signature expects float
        # (untuk kompatibilitas dengan Decimal arithmetic SQLAlchemy).
        self.nilai_akhir = hitung_nilai_akhir(
            float(self.nilai_tugas),
            float(self.nilai_uts),
            float(self.nilai_uas),
        )
        # Status lulus diturunkan dari KKM terpusat (app.utils.constants.KKM).
        status = tentukan_status_kelulusan(float(self.nilai_akhir))
        self.status_lulus = status['lulus']

    def lock(self):
        """Kunci nilai agar tidak dapat diubah kembali oleh guru.

        Idempotent: pemanggilan berulang pada nilai yang sudah terkunci
        tidak menimbulkan efek tambahan. Untuk membuka kunci, gunakan
        ``unlock()`` (khusus admin sesuai PRD §14 Batasan #2).
        """
        if not self.is_locked:
            self.is_locked = True

    def unlock(self):
        """Buka kunci nilai — hanya boleh dipanggil oleh admin.

        Method ini TIDAK melakukan pengecekan role — otorisasi menjadi
        tanggung jawab route handler (lihat ``admin/routes.py`` jika
        endpoint unlock ditambahkan di masa depan).
        """
        self.is_locked = False

    def get_detail_kalkulasi(self):
        """Kembalikan rincian kalkulasi nilai akhir untuk ditampilkan ke siswa.

        Returns:
            dict: Struktur detail per-komponen, masing-masing berisi
            ``nilai`` (float), ``bobot`` (int persen), dan ``kontribusi``
            (float, nilai * bobot). Plus info ``nilai_akhir``, ``status_lulus``,
            dan ``kkm`` untuk transparansi rumus.

        Contoh:
            >>> n = Nilai(nilai_tugas=80, nilai_uts=75, nilai_uas=85)
            >>> n.hitung_dan_simpan()
            >>> n.get_detail_kalkulasi()
            {'tugas': {'nilai': 80.0, 'bobot': 30, 'kontribusi': 24.0},
             'uts':   {'nilai': 75.0, 'bobot': 30, 'kontribusi': 22.5},
             'uas':   {'nilai': 85.0, 'bobot': 40, 'kontribusi': 34.0},
             'nilai_akhir': 80.5, 'status_lulus': True, 'kkm': 70.0}
        """
        # Bobot persen dan bobot desimal: konsisten dengan
        # BOBOT_TUGAS/UTS/UAS di constants.py (30% / 30% / 40%).
        return {
            'tugas': {
                'nilai': float(self.nilai_tugas),
                'bobot': int(BOBOT_TUGAS * 100),
                'kontribusi': round(float(self.nilai_tugas) * BOBOT_TUGAS, PEMBULATAN_DESIMAL),
            },
            'uts': {
                'nilai': float(self.nilai_uts),
                'bobot': int(BOBOT_UTS * 100),
                'kontribusi': round(float(self.nilai_uts) * BOBOT_UTS, PEMBULATAN_DESIMAL),
            },
            'uas': {
                'nilai': float(self.nilai_uas),
                'bobot': int(BOBOT_UAS * 100),
                'kontribusi': round(float(self.nilai_uas) * BOBOT_UAS, PEMBULATAN_DESIMAL),
            },
            'nilai_akhir': float(self.nilai_akhir),
            'status_lulus': self.status_lulus,
            'kkm': KKM,
        }

    def to_dict(self):
        """Serialisasi objek Nilai ke dict untuk JSON response (API/AJAX).

        Returns:
            dict: Representasi JSON-friendly. ``nilai_akhir`` bertipe
            ``float`` atau ``None`` (jika belum dihitung). Field
            ``nilai_tugas/uts/uas`` dikonversi dari ``Decimal`` ke
            ``float`` agar JSON-encodable.

        Note:
            Password/secret TIDAK termasuk (tidak relevan untuk Nilai),
            tapi method ini mengikuti pola ``to_dict()`` semua model lain
            untuk konsistensi API.
        """
        return {
            'id': self.id,
            'mata_pelajaran': self.mata_pelajaran,
            'nilai_tugas': float(self.nilai_tugas),
            'nilai_uts': float(self.nilai_uts),
            'nilai_uas': float(self.nilai_uas),
            'nilai_akhir': float(self.nilai_akhir) if self.nilai_akhir else None,
            'status_lulus': self.status_lulus,
            'is_locked': self.is_locked,
        }

    def to_dict(self):
        return {
            'id': self.id,
            'mata_pelajaran': self.mata_pelajaran,
            'nilai_tugas': float(self.nilai_tugas),
            'nilai_uts': float(self.nilai_uts),
            'nilai_uas': float(self.nilai_uas),
            'nilai_akhir': float(self.nilai_akhir) if self.nilai_akhir else None,
            'status_lulus': self.status_lulus,
            'is_locked': self.is_locked,
        }
