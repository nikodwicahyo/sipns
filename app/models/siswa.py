"""
Modul: siswa.py
Deskripsi: Model OOP untuk entitas Siswa — representasi data siswa.

Class ``Siswa`` mendukung **soft delete** — data tidak dihapus dari
database saat tombol "Hapus" diklik, melainkan ``deleted_at`` di-set
ke ``utcnow()``. Hal ini untuk:
1. Mempertahankan histori nilai (FK constraint ke tabel ``nilai``).
2. Memungkinkan audit trail forensik.
3. Memudahkan recovery (cukup set ``deleted_at = NULL``).

Siswa yang di-soft-delete secara otomatis membuat ``User`` terkait
menjadi ``is_active=False`` (lihat ``admin/routes.py``), sehingga siswa
tersebut tidak bisa login meskipun data masih ada.

Author : Niko Dwicahyo
Versi  : 1.0.0
"""
from app import db
from datetime import datetime


class Siswa(db.Model):
    """Model OOP entitas Siswa.

    Attributes:
        id (int): Primary key auto-increment.
        nis (str): Nomor Induk Siswa. Unik, **immutable** setelah dibuat
            (lihat ``siswa_forms.py`` — field disabled saat edit).
        nama (str): Nama lengkap siswa. Maks 100 karakter.
        kelas (str): Kelas (mis. "X-IPA-1"). Maks 20 karakter.
        created_at (datetime): Timestamp insert.
        updated_at (datetime): Timestamp update terakhir.
        deleted_at (datetime, nullable): Timestamp soft delete. ``None``
            = aktif; non-None = dihapus (tidak muncul di query default).

    Relasi:
        nilai (list[Nilai]): Semua nilai siswa ini (lazy='dynamic').
        user (User): One-to-one ke User (untuk login role siswa).
    """

    __tablename__ = 'siswa'

    id = db.Column(db.Integer, primary_key=True)
    nis = db.Column(db.String(20), unique=True, nullable=False, index=True)
    nama = db.Column(db.String(100), nullable=False)
    kelas = db.Column(db.String(20), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Soft delete: NULL = aktif, non-NULL = waktu hapus.
    deleted_at = db.Column(db.DateTime, nullable=True)

    # Relasi one-to-many ke Nilai (satu siswa punya banyak nilai).
    # lazy='dynamic' → return Query object, bukan list. Cocok untuk
    # query besar atau filtering lebih lanjut.
    nilai = db.relationship('Nilai', backref='siswa', lazy='dynamic',
                            foreign_keys='Nilai.siswa_id')
    # Relasi one-to-one ke User (untuk login). uselist=False = bukan list.
    user = db.relationship('User', backref='siswa', uselist=False,
                           foreign_keys='User.siswa_id')

    def __repr__(self):
        return f'<Siswa {self.nis}: {self.nama}>'

    def nilai_akhir_all(self):
        """Kembalikan list nilai akhir siswa lintas mata pelajaran.

        Returns:
            list[float | Decimal]: Daftar nilai_akhir yang tidak None.
            Bisa kosong jika siswa belum punya nilai.
        """
        return [n.nilai_akhir for n in self.nilai if n.nilai_akhir is not None]

    def rata_rata_nilai(self):
        """Hitung rata-rata nilai akhir siswa dari semua mata pelajaran.

        Returns:
            float: Rata-rata dibulatkan 2 desimal. ``0.0`` jika siswa
            belum punya nilai.
        """
        nilai_list = self.nilai_akhir_all()
        return round(sum(nilai_list) / len(nilai_list), 2) if nilai_list else 0.0

    def status_kelulusan_global(self):
        """Tentukan status kelulusan siswa secara global (semua mapel).

        Logika:
        - Jika belum ada nilai (semua ``status_lulus`` None) → "Belum Ada Nilai".
        - Jika SEMUA mapel ``status_lulus=True`` → "Lulus".
        - Jika ADA mapel ``status_lulus=False`` → "Tidak Lulus".

        Returns:
            str: Salah satu dari ``"Lulus"``, ``"Tidak Lulus"``,
            atau ``"Belum Ada Nilai"``.
        """
        # Lazy import: ``Nilai`` di-resolve saat method dipanggil (bukan
        # saat module di-load) untuk menghindari circular import.
        from app.models.nilai import Nilai
        # Filter record yang punya status_lulus (skip None = belum dihitung).
        nilai_records = self.nilai.filter(Nilai.status_lulus.isnot(None)).all()
        if not nilai_records:
            return 'Belum Ada Nilai'
        return 'Lulus' if all(n.status_lulus for n in nilai_records) else 'Tidak Lulus'

    def soft_delete(self):
        """Lakukan soft delete dengan menandai ``deleted_at = utcnow().

        PENTING: Method ini TIDAK melakukan commit. Caller (route handler)
        wajib melakukan ``db.session.commit()`` setelah ini.
        Efek samping: nilai-nilai siswa TETAP ada di database (FK masih valid),
        hanya record siswa yang ditandai "dihapus".
        """
        self.deleted_at = datetime.utcnow()

    def to_dict(self):
        """Serialisasi objek Siswa ke dict untuk JSON response.

        Returns:
            dict: Representasi JSON-friendly, termasuk field turunan
            (``rata_rata``, ``status``) yang dihitung on-the-fly.
        """
        return {
            'id': self.id,
            'nis': self.nis,
            'nama': self.nama,
            'kelas': self.kelas,
            'rata_rata': self.rata_rata_nilai(),
            'status': self.status_kelulusan_global(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def cari_by_nis(cls, nis):
        """Cari siswa berdasarkan NIS, exclude yang sudah soft-deleted.

        Class method yang mengembalikan instance siswa aktif (belum dihapus).
        Dipakai oleh form validator untuk cek keunikan NIS.

        Args:
            nis (str): Nomor Induk Siswa yang dicari.

        Returns:
            Siswa | None: Instance siswa jika ditemukan dan aktif,
            ``None`` jika tidak ada / sudah dihapus.
        """
        return cls.query.filter_by(nis=nis, deleted_at=None).first()

    @classmethod
    def daftar_kelas(cls):
        """Ambil daftar kelas unik yang tersedia (exclude soft-deleted).

        Returns:
            list[str]: Daftar nama kelas unik, terurut alfabetis.
            Dipakai untuk populate dropdown filter kelas di UI.
        """
        result = db.session.query(cls.kelas).filter(
            cls.deleted_at.is_(None)
        ).distinct().order_by(cls.kelas).all()
        return [r[0] for r in result]
