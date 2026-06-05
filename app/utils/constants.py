"""
Modul: constants.py
Deskripsi: Konstanta terpusat untuk aturan bisnis SIPNS.

Semua nilai "ajaib" (KKM, bobot, rentang nilai, dll.) yang digunakan di
seluruh aplikasi didefinisikan di sini. Tujuannya:

1. **Single source of truth** — perubahan KKM hanya di satu tempat.
2. **Menghilangkan magic numbers** — sesuai TASK F7-013.
3. **Mempermudah audit** — reviewer dapat melihat semua aturan bisnis.

Usage:
    from app.utils.constants import KKM, BOBOT_TUGAS, BOBOT_UTS, BOBOT_UAS

Author : Niko Dwicahyo
Versi  : 1.0.0
"""
from decimal import Decimal


KKM: float = 70.0
"""Kriteria Ketuntasan Minimal. Siswa dengan nilai_akhir >= KKM dinyatakan Lulus.

Sesuai PRD.md §2.2 dan §5.4 (NILAI-04). Berlaku untuk semua mata pelajaran;
belum mendukung KKM per-mapel (lihat backlog BL-006).
"""

BOBOT_TUGAS: float = 0.30
"""Bobot komponen Nilai Tugas dalam kalkulasi nilai akhir (30%)."""

BOBOT_UTS: float = 0.30
"""Bobot komponen Nilai UTS dalam kalkulasi nilai akhir (30%)."""

BOBOT_UAS: float = 0.40
"""Bobot komponen Nilai UAS dalam kalkulasi nilai akhir (40%)."""

BOBOT_TOTAL: float = BOBOT_TUGAS + BOBOT_UTS + BOBOT_UAS
"""Total bobot ketiga komponen (harus bernilai 1.00 / 100%)."""

assert BOBOT_TOTAL == 1.0, (
    f"BOBOT_TOTAL harus 1.0, saat ini: {BOBOT_TOTAL}. "
    "Jika Anda mengubah salah satu BOBOT_*, periksa juga validasi_form dan formula."
)

RENTANG_NILAI_MIN: int = 0
"""Batas bawah nilai yang valid (inklusif)."""

RENTANG_NILAI_MAX: int = 100
"""Batas atas nilai yang valid (inklusif)."""

PEMBULATAN_DESIMAL: int = 2
"""Jumlah digit desimal untuk nilai_akhir (sesuai DECIMAL(5,2) di DB)."""

SESSION_LIFETIME_SECONDS: int = 7200
"""Durasi sesi login sebelum kadaluarsa (2 jam). Sesuai PRD §5.1 AUTH-03."""

DEFAULT_ADMIN_USERNAME: str = "admin"
"""Username default untuk akun admin (dibuat oleh flask seed)."""

DEFAULT_ADMIN_PASSWORD: str = "Admin@123"
"""Password default untuk akun admin seed. WAJIB diganti di production!"""

DEFAULT_GURU_PASSWORD: str = "Guru@123"
"""Password default untuk akun guru seed. WAJIB diganti di production!"""

PASSWORD_MIN_LENGTH: int = 8
"""Panjang minimum password yang diizinkan (sesuai PRD §6 Keamanan)."""

KONTROL_TIPE_DATA = (int, float, Decimal)
"""Tipe data numerik yang valid untuk kolom nilai (mendukung Decimal dari DB)."""
