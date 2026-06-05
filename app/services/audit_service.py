"""
Modul: audit_service.py
Deskripsi: Layanan terstruktur untuk pencatatan audit log aktivitas user.

Fungsi ``catat_audit_log`` adalah wrapper tipis di atas
``AuditLog.log()`` yang menambahkan sedikit logging context. Fungsi ini
dipanggil oleh SEMUA route handler setelah operasi CRUD berhasil,
sebagai bagian dari compliance trail (PRD §5.7 AUDIT-01).

Pola penggunaan::

    from app.services.audit_service import catat_audit_log
    ...
    db.session.commit()  # commit operasi utama dulu
    catat_audit_log(
        user_id=current_user.id,
        action='INSERT',
        table_name='siswa',
        record_id=siswa.id,
        description=f'Tambah siswa {siswa.nama}',
        ip_address=request.remote_addr,
    )

Author : Niko Dwicahyo
Versi  : 1.0.0
"""
from app.models.audit_log import AuditLog
from app import db


def catat_audit_log(user_id, action, table_name, record_id=None, description=None, ip_address=None):
    """Catat satu entry audit log ke database.

    Fungsi ini adalah **thin wrapper** di sekitar ``AuditLog.log()`` yang
    menerima parameter posisi (positional args) untuk kemudahan panggilan
    dari route handler. Tidak ada logika tambahan selain delegasi.

    Args:
        user_id (int): ID user pelaku. ``None`` untuk aksi sistem.
        action (str): Jenis aksi — ``INSERT`` | ``UPDATE`` | ``DELETE`` |
            ``LOGIN`` | ``LOGOUT`` | ``PRINT_PDF`` | ``EXPORT_EXCEL``.
        table_name (str): Nama tabel/entitas target (mis. ``siswa``).
        record_id (int, optional): ID record yang berubah. Default ``None``.
        description (str, optional): Narasi manusia-baca. Default ``None``.
        ip_address (str, optional): IP address pelaku (untuk forensik).
            Default ``None``.

    Returns:
        AuditLog | None: Objek log entry baru, atau ``None`` jika gagal
        (sudah ditangani internal di ``AuditLog.log`` — error di-log
        ke Flask logger agar tidak menggangu operasi utama).

    Note:
        Pemanggilan fungsi ini **tidak boleh** di-wrap dalam try/except
        di caller, karena ``AuditLog.log()`` sudah menangani exception
        secara internal. Cukup panggil langsung.
    """
    AuditLog.log(
        user_id=user_id,
        action=action,
        table_name=table_name,
        record_id=record_id,
        description=description,
        ip_address=ip_address,
    )
