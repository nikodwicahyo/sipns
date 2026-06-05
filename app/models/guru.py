"""
Modul: guru.py
Deskripsi: Model OOP untuk entitas Guru — representasi data pengajar.

Class ``Guru`` mirip dengan ``Siswa`` — mendukung soft delete (``deleted_at``)
untuk mempertahankan histori nilai yang pernah di-input guru tersebut.

Guru yang akan di-soft-delete DICEK dulu apakah masih memiliki
``Nilai`` yang ``is_locked=True`` (lihat ``admin/routes.py``). Jika ada,
guru tidak boleh dihapus untuk menjaga integritas data nilai.

Author : Niko Dwicahyo
Versi  : 1.0.0
"""
from app import db
from datetime import datetime


class Guru(db.Model):
    """Model OOP entitas Guru.

    Attributes:
        id (int): Primary key auto-increment.
        id_guru (str): Kode ID Guru (mis. "GR-001"). Unik, immutable
            (lihat ``guru_forms.py`` — field disabled saat edit).
        nama_guru (str): Nama lengkap guru. Maks 100 karakter.
        mata_pelajaran (str): Mata pelajaran yang diampu guru ini
            (mis. "Matematika"). Guru hanya bisa input nilai untuk
            mapel ini (lihat ``guru/routes.py``).
        created_at (datetime): Timestamp insert.
        updated_at (datetime): Timestamp update terakhir.
        deleted_at (datetime, nullable): Timestamp soft delete.

    Relasi:
        nilai_diinput (list[Nilai]): Semua nilai yang pernah diinput
            oleh guru ini (lazy='dynamic').
        user (User): One-to-one ke User (untuk login role guru).
    """

    __tablename__ = 'guru'

    id = db.Column(db.Integer, primary_key=True)
    id_guru = db.Column(db.String(20), unique=True, nullable=False)
    nama_guru = db.Column(db.String(100), nullable=False)
    mata_pelajaran = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Soft delete: NULL = aktif, non-NULL = waktu hapus.
    deleted_at = db.Column(db.DateTime, nullable=True)

    # Relasi one-to-many ke Nilai (satu guru bisa input banyak nilai).
    nilai_diinput = db.relationship('Nilai', backref='guru', lazy='dynamic',
                                     foreign_keys='Nilai.guru_id')
    # Relasi one-to-one ke User (untuk login role guru).
    user = db.relationship('User', backref='guru', uselist=False,
                           foreign_keys='User.guru_id')

    def __repr__(self):
        return f'<Guru {self.id_guru}: {self.nama_guru}>'

    def get_siswa_diajar(self):
        """Kembalikan daftar siswa yang pernah dinilai oleh guru ini.

        Query: distinct siswa_id dari tabel nilai dimana guru_id = self.id,
        lalu resolve ke instance Siswa. Dipakai untuk menampilkan
        "Siswa yang Diajar" di dashboard guru.

        Returns:
            list[Siswa]: Daftar siswa unik (tidak duplikat) yang pernah
            diberi nilai oleh guru ini. Bisa kosong.
        """
        from app.models.siswa import Siswa
        from app.models.nilai import Nilai
        # Subquery: distinct siswa_id yang pernah dinilai guru ini.
        siswa_ids = db.session.query(Nilai.siswa_id).filter_by(
            guru_id=self.id
        ).distinct().all()
        # Resolve ID → instance Siswa.
        return Siswa.query.filter(
            Siswa.id.in_([s[0] for s in siswa_ids])
        ).all()

    def soft_delete(self):
        """Lakukan soft delete dengan menandai ``deleted_at = utcnow()``.

        PENTING: Method ini TIDAK melakukan commit. Caller (route handler)
        wajib commit setelah ini. Sebelum memanggil ini, route handler
        harus sudah memvalidasi bahwa guru tidak memiliki nilai yang
        masih terkunci (lihat ``admin/routes.py::hapus_guru``).
        """
        self.deleted_at = datetime.utcnow()

    def to_dict(self):
        """Serialisasi objek Guru ke dict untuk JSON response.

        Returns:
            dict: Representasi JSON-friendly. Tidak termasuk
            ``created_at``/``deleted_at`` karena biasanya tidak
            relevan untuk response API.
        """
        return {
            'id': self.id,
            'id_guru': self.id_guru,
            'nama_guru': self.nama_guru,
            'mata_pelajaran': self.mata_pelajaran,
        }

    @classmethod
    def daftar_guru_aktif(cls):
        """Ambil daftar guru aktif (exclude soft-deleted), terurut nama.

        Dipakai untuk populate dropdown filter guru di halaman laporan.
        Hanya menampilkan guru yang masih aktif sehingga user tidak
        bisa memfilter ke guru yang sudah dihapus.

        Returns:
            list[Guru]: List instance Guru, ter alfabetis by ``nama_guru``.
            Bisa kosong jika belum ada guru.
        """
        return (
            cls.query
            .filter(cls.deleted_at.is_(None))
            .order_by(cls.nama_guru)
            .all()
        )
