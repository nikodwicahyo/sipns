"""
Modul: audit_log.py
Deskripsi: Model OOP untuk entitas AuditLog — pencatatan jejak aktivitas user.

Audit log adalah **fitur wajib** (PRD §5.7 AUDIT-01/02) yang mencatat
semua aksi CRUD beserta timestamp, user, dan IP address untuk kebutuhan
forensik & compliance.

Pola penggunaan::

    from app.services.audit_service import catat_audit_log
    catat_audit_log(
        user_id=current_user.id,
        action='INSERT',
        table_name='siswa',
        record_id=siswa.id,
        description='Tambah siswa baru',
        ip_address=request.remote_addr,
    )

Atau langsung via classmethod::

    AuditLog.log(
        user_id=current_user.id, action='UPDATE', table_name='guru', ...
    )

Author : Niko Dwicahyo
Versi  : 1.0.0
"""
import logging
from app import db
from datetime import datetime


logger = logging.getLogger(__name__)


class AuditLog(db.Model):
    """Model OOP entitas AuditLog — satu baris per aksi penting.

    Attributes:
        id (int): Primary key auto-increment.
        user_id (int): Foreign key ke ``users.id``. Nullable karena
            beberapa aksi (cron, system) bisa tanpa user (mis. seed).
        action (str): Jenis aksi — salah satu dari ``INSERT``, ``UPDATE``,
            ``DELETE``, ``LOGIN``, ``LOGOUT``, ``PRINT_PDF``, ``EXPORT_EXCEL``.
        table_name (str): Nama tabel/entitas yang terpengaruh (mis. ``siswa``,
            ``guru``, ``nilai``, ``users``).
        record_id (int): ID record yang diubah. Nullable untuk aksi
            global (mis. PRINT_PDF per kelas tanpa record_id spesifik).
        description (str): Narasi aksi — mis. "Tambah siswa Budi Santoso
            (NIS: 2024001)". Disarankan dalam Bahasa Indonesia.
        ip_address (str): Alamat IP user saat aksi dilakukan (untuk audit
            forensik). Maks 45 karakter (IPv6).
        created_at (datetime): Timestamp aksi. Default ``utcnow`` saat insert.
    """

    __tablename__ = 'audit_log'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(50), nullable=False)
    table_name = db.Column(db.String(50), nullable=False)
    record_id = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relasi ke User (lazy='joined' = eager load untuk mencegah N+1 di list view).
    user = db.relationship('User', backref='audit_logs', lazy='joined')

    def __repr__(self):
        return f'<AuditLog {self.action} on {self.table_name}#{self.record_id}>'

    @classmethod
    def log(cls, user_id, action, table_name, record_id=None, description=None, ip_address=None):
        """Buat dan simpan satu entry audit log.

        Args:
            user_id (int): ID user pelaku. Boleh ``None`` untuk aksi sistem.
            action (str): Jenis aksi (lihat attribute class).
            table_name (str): Nama tabel/entitas.
            record_id (int, optional): ID record. Default ``None``.
            description (str, optional): Narasi aksi. Default ``None``.
            ip_address (str, optional): IP address pelaku. Default ``None``.

        Returns:
            AuditLog | None: Objek log yang baru dibuat, atau ``None`` jika
            terjadi error saat commit (sudah di-log ke Flask logger).

        Note:
            Method ini **menangkap semua Exception** agar gangguan audit
            logging tidak menggangu operasi utama. Idealnya, audit log
            dicatat SETIAP saat setelah DB commit operasi utama berhasil,
            jadi jika logging gagal pun, data utama sudah aman.
        """
        try:
            log_entry = cls(
                user_id=user_id,
                action=action,
                table_name=table_name,
                record_id=record_id,
                description=description,
                ip_address=ip_address,
            )
            db.session.add(log_entry)
            db.session.commit()
            return log_entry
        except Exception as e:
            # Rollback agar partial transaction tidak menggangu session.
            db.session.rollback()
            # Pakai logger, bukan print() — agar muncul di log files & dashboard.
            logger.warning(
                'Audit log gagal dicatat (action=%s, table=%s): %s',
                action, table_name, e,
            )
            return None

    def to_dict(self):
        """Serialisasi objek AuditLog ke dict untuk JSON response (API/AJAX).

        Returns:
            dict: Representasi JSON-friendly. ``created_at`` dikonversi ke
            ISO 8601 string agar JSON-encodable. Field lain sudah JSON-safe.
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'table_name': self.table_name,
            'record_id': self.record_id,
            'description': self.description,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
