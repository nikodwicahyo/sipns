"""
Modul: user.py
Deskripsi: Model OOP untuk entitas User — representasi akun login sistem.

Class ``User`` mewarisi ``db.Model`` (SQLAlchemy ORM) dan ``UserMixin``
(Flask-Login). Setiap ``User`` TEPAT berelasi ke satu ``Siswa`` ATAU
satu ``Guru`` (satu-ke-satu, mutually exclusive), sesuai role-nya.
User dengan role ``admin`` tidak berelasi ke Siswa/Guru.

Konvensi username:
- Admin: username bebas (default: "admin").
- Guru:  username = ``Guru.id_guru`` (mis. "GR-001").
- Siswa: username = ``Siswa.nis`` (mis. "2024001").

Keamanan:
- Password disimpan sebagai ``password_hash`` (PBKDF2-SHA256 via
  ``werkzeug.security.generate_password_hash``). Plain text password
  tidak pernah disimpan atau di-log.
- Field ``password_hash`` TIDAK diserialize ke JSON (``to_dict`` tidak
  mengeksposnya) untuk mencegah kebocoran hash.

Author : Niko Dwicahyo
Versi  : 1.0.0
"""
from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(db.Model, UserMixin):
    """Model OOP entitas User — akun login untuk Admin/Guru/Siswa.

    Attributes:
        id (int): Primary key auto-increment.
        username (str): Username unik untuk login. Maks 50 karakter.
        password_hash (str): Hash password (PBKDF2-SHA256, ~255 char).
            Diset via ``set_password()`` — tidak boleh di-set langsung.
        role (str): Salah satu dari ``'admin'``, ``'guru'``, ``'siswa'``.
        is_active (bool): Status akun. ``False`` = tidak bisa login
            (digunakan untuk soft-delete akun siswa/guru yang dihapus).
        siswa_id (int, FK): Relasi ke ``siswa.id`` (nullable, role=siswa).
        guru_id (int, FK): Relasi ke ``guru.id`` (nullable, role=guru).
        created_at (datetime): Timestamp insert akun.
        updated_at (datetime): Timestamp update terakhir.

    Relasi:
        siswa (Siswa): One-to-one ke Siswa (jika role=siswa).
        guru (Guru): One-to-one ke Guru (jika role=guru).
        audit_logs (list[AuditLog]): Daftar log aktivitas user ini.
    """

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    # FK ke siswa/guru — salah satu (atau tidak sama sekali) terisi
    # tergantung role. Validasi dilakukan di business logic, bukan di DB.
    siswa_id = db.Column(db.Integer, db.ForeignKey('siswa.id'), nullable=True)
    guru_id = db.Column(db.Integer, db.ForeignKey('guru.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        """Hash dan simpan password baru ke ``self.password_hash``.

        Menggunakan ``werkzeug.security.generate_password_hash`` dengan
        algoritma default PBKDF2-SHA256. Method ini WAJIB dipanggil
        (bukan set ``password_hash`` langsung) untuk memastikan hash
        yang aman.

        Args:
            password (str): Password plaintext dari user. Tidak ada
            validasi strength di sini — itu menjadi tanggung jawab
            form validator (lihat ``forms/user_forms.py``).
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifikasi password plaintext terhadap ``self.password_hash``.

        Args:
            password (str): Password plaintext dari form login.

        Returns:
            bool: ``True`` jika password cocok dengan hash, ``False``
            sebaliknya. Aman terhadap timing attack (Werkzeug menggunakan
            ``hmac.compare_digest`` secara internal).
        """
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        """Cek apakah user memiliki role admin.

        Returns:
            bool: ``True`` jika ``self.role == 'admin'``.
        """
        return self.role == 'admin'

    def is_guru(self):
        """Cek apakah user memiliki role guru.

        Returns:
            bool: ``True`` jika ``self.role == 'guru'``.
        """
        return self.role == 'guru'

    def is_siswa(self):
        """Cek apakah user memiliki role siswa.

        Returns:
            bool: ``True`` jika ``self.role == 'siswa'``.
        """
        return self.role == 'siswa'

    def get_id(self):
        """Kembalikan identifier user untuk Flask-Login session.

        Method ini WAJIB ada karena Flask-Login memakainya untuk
        serialisasi user ID ke session cookie. Override default
        ``UserMixin.get_id()`` (yang return unicode) untuk memastikan
        tipe ``str`` (sesuai signature Flask-Login terbaru).

        Returns:
            str: ``str(self.id)``.
        """
        return str(self.id)

    def __repr__(self):
        return f'<User {self.username}: {self.role}>'

    def to_dict(self):
        """Serialisasi objek User ke dict untuk JSON response.

        Returns:
            dict: Representasi JSON-friendly. Field ``password_hash``
            SENGAJA TIDAK disertakan untuk mencegah kebocoran hash
            ke client/JSON response.
        """
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'is_active': self.is_active,
            'siswa_id': self.siswa_id,
            'guru_id': self.guru_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
