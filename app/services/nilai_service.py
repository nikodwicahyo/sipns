"""
Modul: nilai_service.py
Deskripsi: Layanan terstruktur untuk kalkulasi, validasi, dan statistik nilai.

Modul ini mengimplementasikan paradigma **Pemrograman Terstruktur** —
semua logika bisnis inti diekspresikan sebagai fungsi/prosedur murni
(tanpa `self`, tanpa `cls`) yang menerima argumen dan mengembalikan nilai.

Fungsi-fungsi ini dipanggil oleh:
- Model OOP `Nilai` di `app/models/nilai.py` (method `hitung_dan_simpan`),
  menunjukkan integrasi antara paradigma terstruktur dan OOP.
- Blueprint route handler untuk endpoint AJAX `/api/nilai-preview`.
- Test suite (`tests/unit/test_nilai_service.py`).

Author : Niko Dwicahyo
Versi  : 1.0.0
"""
from app.utils.constants import (
    BOBOT_TUGAS,
    BOBOT_UTS,
    BOBOT_UAS,
    KKM,
    KONTROL_TIPE_DATA,
    PEMBULATAN_DESIMAL,
    RENTANG_NILAI_MAX,
    RENTANG_NILAI_MIN,
)


def validasi_rentang_nilai(nilai, label="Nilai"):
    """Memvalidasi apakah ``nilai`` berada dalam rentang valid ``[0, 100]``.

    Dipakai sebagai gate-check sebelum kalkulasi nilai akhir. Memvalidasi
    tipe data numerik (mendukung ``Decimal`` dari kolom Numeric DB) dan
    rentang inklusif 0 sampai 100 (sesuai PRD §2.3 aturan bisnis).

    Args:
        nilai (int | float | decimal.Decimal): Nilai yang akan divalidasi.
        label (str, optional): Label komponen nilai untuk pesan error.
            Berguna untuk diagnosa — contoh: "Tugas", "UTS", "UAS".
            Defaults to ``"Nilai"``.

    Returns:
        bool: ``True`` jika nilai valid (numerik DAN dalam rentang).

    Raises:
        ValueError: Jika ``nilai`` bukan numerik, atau di luar rentang
            ``[RENTANG_NILAI_MIN, RENTANG_NILAI_MAX]``. Pesan mencantumkan
            label dan nilai input untuk memudahkan debugging.

    Examples:
        >>> validasi_rentang_nilai(85)
        True
        >>> validasi_rentang_nilai(100)
        True
        >>> validasi_rentang_nilai(0)
        True
        >>> validasi_rentang_nilai(101)
        Traceback (most recent call last):
            ...
        ValueError: Nilai harus berada di antara 0 dan 100. Nilai '101' tidak valid.
        >>> validasi_rentang_nilai('abc')
        Traceback (most recent call last):
            ...
        ValueError: Nilai harus berupa angka.
        >>> validasi_rentang_nilai(150, label='Nilai UAS')
        Traceback (most recent call last):
            ...
        ValueError: Nilai UAS harus berada di antara 0 dan 100. Nilai '150' tidak valid.
    """
    # isinstance dengan bool=False by design: bool adalah subclass int di Python
    # (True==1, False==0) tapi nilai tugas/UTS/UAS tidak pernah boolean.
    if isinstance(nilai, bool) or not isinstance(nilai, KONTROL_TIPE_DATA):
        raise ValueError(f"{label} harus berupa angka.")
    if not (RENTANG_NILAI_MIN <= nilai <= RENTANG_NILAI_MAX):
        raise ValueError(
            f"{label} harus berada di antara 0 dan 100. Nilai '{nilai}' tidak valid."
        )
    return True


def hitung_nilai_akhir(nilai_tugas, nilai_uts, nilai_uas):
    """Menghitung nilai akhir siswa dengan formula bobot 30/30/40.

    Formula (sesuai PRD §2.2 dan §5.4 NILAI-03)::

        nilai_akhir = (BOBOT_TUGAS * tugas)
                    + (BOBOT_UTS   * uts)
                    + (BOBOT_UAS   * uas)

    Args:
        nilai_tugas (int | float | decimal.Decimal): Nilai tugas (0-100).
        nilai_uts (int | float | decimal.Decimal): Nilai UTS (0-100).
        nilai_uas (int | float | decimal.Decimal): Nilai UAS (0-100).

    Returns:
        float: Nilai akhir dibulatkan ``PEMBULATAN_DESIMAL`` (2) desimal.

    Raises:
        ValueError: Dilempar dari ``validasi_rentang_nilai`` jika salah
            satu nilai input di luar rentang 0-100 atau bukan numerik.

    Examples:
        >>> hitung_nilai_akhir(80, 75, 85)
        80.5
        >>> hitung_nilai_akhir(70, 70, 70)
        70.0
        >>> hitung_nilai_akhir(0, 0, 0)
        0.0
        >>> hitung_nilai_akhir(101, 80, 80)
        Traceback (most recent call last):
            ...
        ValueError: Tugas harus berada di antara 0 dan 100. Nilai '101' tidak valid.
    """
    # 1. Validasi ketiga nilai — gagal cepat sebelum kalkulasi.
    validasi_rentang_nilai(nilai_tugas, "Tugas")
    validasi_rentang_nilai(nilai_uts, "UTS")
    validasi_rentang_nilai(nilai_uas, "UAS")

    # 2. Terapkan formula bobot (Tugas 30% + UTS 30% + UAS 40% = 100%).
    #    Konstanta BOBOT_* didefinisikan terpusat di app.utils.constants.
    nilai_akhir = (BOBOT_TUGAS * nilai_tugas) + (BOBOT_UTS * nilai_uts) + (BOBOT_UAS * nilai_uas)

    # 3. Bulatkan ke 2 desimal sesuai presisi DECIMAL(5,2) di database.
    return round(nilai_akhir, PEMBULATAN_DESIMAL)


def tentukan_status_kelulusan(nilai_akhir, kkm=KKM):
    """Menentukan status kelulusan siswa berdasarkan nilai akhir dan KKM.

    Aturan (sesuai PRD §5.4 NILAI-04): siswa **lulus** jika
    ``nilai_akhir >= KKM``; sebaliknya **tidak lulus**.

    Args:
        nilai_akhir (int | float | decimal.Decimal): Nilai akhir hasil
            kalkulasi ``hitung_nilai_akhir``.
        kkm (float, optional): Kriteria Ketuntasan Minimal. Default
            menggunakan konstanta ``KKM`` (70.0). Bisa dioverride
            untuk pengujian atau konfigurasi masa depan.

    Returns:
        dict: Dictionary berisi:
            - ``lulus`` (bool): ``True`` jika nilai_akhir >= KKM.
            - ``label`` (str): "Lulus" atau "Tidak Lulus".
            - ``badge_class`` (str): Bootstrap badge class — ``bg-success``
              untuk Lulus, ``bg-danger`` untuk Tidak Lulus.
            - ``selisih`` (float): Selisih nilai_akhir - KKM (positif=lulus,
              negatif=tidak lulus). Dibulatkan ``PEMBULATAN_DESIMAL`` desimal.

    Examples:
        >>> tentukan_status_kelulusan(80)
        {'lulus': True, 'label': 'Lulus', 'badge_class': 'bg-success', 'selisih': 10.0}
        >>> tentukan_status_kelulusan(69.9)
        {'lulus': False, 'label': 'Tidak Lulus', 'badge_class': 'bg-danger', 'selisih': -0.1}
        >>> tentukan_status_kelulusan(74, kkm=75)
        {'lulus': False, 'label': 'Tidak Lulus', 'badge_class': 'bg-danger', 'selisih': -1.0}
    """
    lulus = nilai_akhir >= kkm
    return {
        'lulus': lulus,
        'label': 'Lulus' if lulus else 'Tidak Lulus',
        'badge_class': 'bg-success' if lulus else 'bg-danger',
        'selisih': round(nilai_akhir - kkm, PEMBULATAN_DESIMAL),
    }


def hitung_statistik_kelas(data_nilai):
    """Menghitung statistik agregat nilai untuk satu kelas/kelompok.

    Digunakan oleh:
    - Dashboard admin/guru (chart + card statistik).
    - Halaman rekap nilai.
    - Laporan PDF & Excel.

    Args:
        data_nilai (list[Nilai | object]): Daftar objek nilai. Objek
            minimal harus punya atribut ``nilai_akhir`` (Numeric/None) dan
            ``status_lulus`` (bool/None). Boleh juga berupa mock object
            (lihat test ``_FakeNilai`` di ``test_nilai_service.py``).

    Returns:
        dict: Statistik agregat berisi:
            - ``total`` (int): Jumlah record nilai_akhir yang tidak None.
            - ``rata_rata`` (float): Rata-rata nilai_akhir.
            - ``tertinggi`` (float): Nilai_akhir maksimum.
            - ``terendah`` (float): Nilai_akhir minimum.
            - ``jumlah_lulus`` (int): Record dengan status_lulus=True.
            - ``jumlah_tidak_lulus`` (int): Record dengan status_lulus=False.
            - ``persen_lulus`` (float): Persentase lulus (0-100), 1 desimal.

    Edge cases:
        - ``data_nilai`` kosong atau semua ``nilai_akhir=None``:
          return default dict dengan nilai 0 (tidak raise exception).

    Examples:
        >>> hitung_statistik_kelas([])
        {'rata_rata': 0, 'tertinggi': 0, 'terendah': 0, 'persen_lulus': 0, 'total': 0,
         'jumlah_lulus': 0, 'jumlah_tidak_lulus': 0}
    """
    # Default result untuk kasus kosong — mencegah error di caller (template, chart).
    if not data_nilai:
        return {
            'rata_rata': 0, 'tertinggi': 0, 'terendah': 0, 'persen_lulus': 0,
            'total': 0, 'jumlah_lulus': 0, 'jumlah_tidak_lulus': 0,
        }

    # Filter hanya record yang punya nilai_akhir (skip record tanpa nilai).
    # Ini penting saat ada sebagian siswa yang sudah diinput nilainya dan sebagian belum.
    nilai_list = [n.nilai_akhir for n in data_nilai if n.nilai_akhir is not None]
    if not nilai_list:
        return {
            'rata_rata': 0, 'tertinggi': 0, 'terendah': 0, 'persen_lulus': 0,
            'total': 0, 'jumlah_lulus': 0, 'jumlah_tidak_lulus': 0,
        }

    # jumlah_lulus dihitung dari SEMUA data_nilai (bukan hanya yang ada nilai_akhir),
    # karena status_lulus bisa True/False tanpa nilai_akhir (edge case di UI).
    # Gunakan ekspresi eksplisit n.status_lulus is True agar tidak salah
    # menghitung None sebagai tidak_lulus.
    lulus_count = sum(1 for n in data_nilai if n.status_lulus is True)
    tidak_lulus_count = sum(1 for n in data_nilai if n.status_lulus is False)

    return {
        'total': len(nilai_list),
        'rata_rata': round(sum(nilai_list) / len(nilai_list), PEMBULATAN_DESIMAL),
        'tertinggi': max(nilai_list),
        'terendah': min(nilai_list),
        'jumlah_lulus': lulus_count,
        'jumlah_tidak_lulus': tidak_lulus_count,
        'persen_lulus': round((lulus_count / len(nilai_list)) * 100, 1),
    }
