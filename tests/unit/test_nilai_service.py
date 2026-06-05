"""
Unit tests untuk app.services.nilai_service (Pemrograman Terstruktur).

Menguji fungsi-fungsi kalkulasi dan validasi nilai secara terisolasi
(tanpa Flask app context, tanpa database).

Sesuai PRD.md:
- F6-003 s/d F6-010: Test validasi_rentang_nilai (TC-VAL-01..07)
- F6-011 s/d F6-017: Test hitung_nilai_akhir (TC-HIT-01..07)
- F6-018 s/d F6-022: Test tentukan_status_kelulusan (TC-STAT-01..05)
- F6-023 s/d F6-025: Test hitung_statistik_kelas (TC-STAT-06..08)
"""
import math
import pytest

from app.services.nilai_service import (
    validasi_rentang_nilai,
    hitung_nilai_akhir,
    tentukan_status_kelulusan,
    hitung_statistik_kelas,
)


# ===========================================================================
# TC-VAL: Test validasi_rentang_nilai (F6-004 s/d F6-010)
# ===========================================================================

class TestValidasiRentangNilai:
    """Menguji fungsi validasi_rentang_nilai() dengan 7 skenario."""

    def test_tc_val_01_nilai_nol_batas_bawah_valid(self):
        """TC-VAL-01: nilai = 0 harus valid (batas bawah inklusif)."""
        assert validasi_rentang_nilai(0) is True

    def test_tc_val_02_nilai_seratus_batas_atas_valid(self):
        """TC-VAL-02: nilai = 100 harus valid (batas atas inklusif)."""
        assert validasi_rentang_nilai(100) is True

    def test_tc_val_03_nilai_desimal_valid(self):
        """TC-VAL-03: nilai desimal 50.5 harus valid."""
        assert validasi_rentang_nilai(50.5) is True

    def test_tc_val_04_nilai_negatif_invalid(self):
        """TC-VAL-04: nilai negatif -1 harus raise ValueError.

        Default label adalah 'Nilai' (lihat signature fungsi). Untuk uji
        label kustom, gunakan test_label_custom_diterapkan.
        """
        with pytest.raises(ValueError) as exc_info:
            validasi_rentang_nilai(-1)
        assert 'antara 0 dan 100' in str(exc_info.value)
        assert "'-1'" in str(exc_info.value)

    def test_tc_val_05_nilai_lebih_dari_100_invalid(self):
        """TC-VAL-05: nilai 101 harus raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            validasi_rentang_nilai(101)
        assert 'antara 0 dan 100' in str(exc_info.value)
        assert '101' in str(exc_info.value)

    def test_tc_val_06_tipe_string_invalid(self):
        """TC-VAL-06: tipe string 'abc' harus raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            validasi_rentang_nilai('abc')
        assert 'harus berupa angka' in str(exc_info.value)

    def test_tc_val_07_nilai_none_invalid(self):
        """TC-VAL-07: nilai None harus raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            validasi_rentang_nilai(None)
        assert 'harus berupa angka' in str(exc_info.value)

    def test_label_custom_diterapkan(self):
        """Bonus: label kustom harus muncul di pesan error."""
        with pytest.raises(ValueError) as exc_info:
            validasi_rentang_nilai(150, label='Nilai UAS')
        assert 'Nilai UAS' in str(exc_info.value)


# ===========================================================================
# TC-HIT: Test hitung_nilai_akhir (F6-011 s/d F6-017)
# ===========================================================================

class TestHitungNilaiAkhir:
    """Menguji fungsi hitung_nilai_akhir() dengan formula 30/30/40."""

    def test_tc_hit_01_kasus_normal(self):
        """TC-HIT-01: T=80, U=75, A=85 -> (0.30*80)+(0.30*75)+(0.40*85) = 80.5."""
        result = hitung_nilai_akhir(80, 75, 85)
        assert result == 80.5

    def test_tc_hit_02_tepat_kkm(self):
        """TC-HIT-02: semua 70 -> 70.0 (tepat pada KKM, masih lulus)."""
        result = hitung_nilai_akhir(70, 70, 70)
        assert result == 70.0

    def test_tc_hit_03_semua_nol(self):
        """TC-HIT-03: semua 0 -> 0.0 (kasus minimum)."""
        result = hitung_nilai_akhir(0, 0, 0)
        assert result == 0.0

    def test_tc_hit_04_semua_sempurna(self):
        """TC-HIT-04: semua 100 -> 100.0 (kasus maksimum)."""
        result = hitung_nilai_akhir(100, 100, 100)
        assert result == 100.0

    def test_tc_hit_05_di_bawah_kkm(self):
        """TC-HIT-05: T=50, U=60, A=65 -> 59.0 (di bawah KKM 70)."""
        result = hitung_nilai_akhir(50, 60, 65)
        assert result == 59.0

    def test_tc_hit_06_nilai_diluar_rentang_tugas(self):
        """TC-HIT-06: T=101 harus raise ValueError dari validasi_rentang_nilai."""
        with pytest.raises(ValueError) as exc_info:
            hitung_nilai_akhir(101, 50, 50)
        assert 'Tugas' in str(exc_info.value)

    def test_tc_hit_06b_nilai_diluar_rentang_uts(self):
        """TC-HIT-06b: U=150 harus raise ValueError."""
        with pytest.raises(ValueError):
            hitung_nilai_akhir(80, 150, 80)

    def test_tc_hit_06c_nilai_diluar_rentang_uas(self):
        """TC-HIT-06c: A=-10 harus raise ValueError."""
        with pytest.raises(ValueError):
            hitung_nilai_akhir(80, 80, -10)

    def test_tc_hit_07_total_bobot_seratus_persen(self):
        """TC-HIT-07: Konstanta bobot harus 30+30+40 = 100% (uji via kontribusi).

        Jika T=U=A=100, kontribusi = 30+30+40 = 100 (maks).
        Kita uji bahwa semua nilai sama -> nilai akhir = nilai input (bobot total = 1).
        """
        arbitrary_value = 73.5
        result = hitung_nilai_akhir(arbitrary_value, arbitrary_value, arbitrary_value)
        assert math.isclose(result, arbitrary_value, rel_tol=1e-9)

    def test_pembulatan_2_desimal(self):
        """Hasil dibulatkan ke 2 desimal (uji dengan nilai yang menghasilkan 3 desimal)."""
        # 0.30 * 33.333 + 0.30 * 33.333 + 0.40 * 33.333 = 33.333
        result = hitung_nilai_akhir(33.333, 33.333, 33.333)
        assert result == 33.33


# ===========================================================================
# TC-STAT: Test tentukan_status_kelulusan (F6-018 s/d F6-022)
# ===========================================================================

class TestTentukanStatusKelulusan:
    """Menguji fungsi tentukan_status_kelulusan() dengan KKM dan custom KKM."""

    def test_tc_stat_01_di_atas_kkm_lulus(self):
        """TC-STAT-01: 80 -> lulus=True, label='Lulus'."""
        result = tentukan_status_kelulusan(80)
        assert result['lulus'] is True
        assert result['label'] == 'Lulus'
        assert result['badge_class'] == 'bg-success'
        assert result['selisih'] == 10.0

    def test_tc_stat_02_tepat_kkm_lulus(self):
        """TC-STAT-02: 70 (tepat KKM) -> lulus=True."""
        result = tentukan_status_kelulusan(70)
        assert result['lulus'] is True
        assert result['label'] == 'Lulus'
        assert result['selisih'] == 0.0

    def test_tc_stat_03_sedikit_di_bawah_kkm_tidak_lulus(self):
        """TC-STAT-03: 69.9 -> lulus=False (di bawah KKM)."""
        result = tentukan_status_kelulusan(69.9)
        assert result['lulus'] is False
        assert result['label'] == 'Tidak Lulus'
        assert result['badge_class'] == 'bg-danger'
        assert result['selisih'] == -0.1

    def test_tc_stat_04_nilai_nol_tidak_lulus(self):
        """TC-STAT-04: 0 -> lulus=False, selisih=-70."""
        result = tentukan_status_kelulusan(0)
        assert result['lulus'] is False
        assert result['selisih'] == -70.0

    def test_tc_stat_05_custom_kkm(self):
        """TC-STAT-05: KKM=75, nilai=74 -> tidak lulus."""
        result = tentukan_status_kelulusan(74, kkm=75)
        assert result['lulus'] is False
        assert result['selisih'] == -1.0

    def test_tc_stat_05b_custom_kkm_lulus(self):
        """TC-STAT-05b: KKM=75, nilai=80 -> lulus."""
        result = tentukan_status_kelulusan(80, kkm=75)
        assert result['lulus'] is True
        assert result['selisih'] == 5.0

    def test_struktur_dict_lengkap(self):
        """Memastikan semua key yang dibutuhkan ada di dict result."""
        result = tentukan_status_kelulusan(80)
        expected_keys = {'lulus', 'label', 'badge_class', 'selisih'}
        assert set(result.keys()) == expected_keys


# ===========================================================================
# TC-STAT: Test hitung_statistik_kelas (F6-023 s/d F6-025)
# ===========================================================================

class _FakeNilai:
    """Mock object yang mensimulasikan atribut Nilai untuk hitung_statistik_kelas."""

    def __init__(self, nilai_akhir=None, status_lulus=False):
        self.nilai_akhir = nilai_akhir
        self.status_lulus = status_lulus


class TestHitungStatistikKelas:
    """Menguji fungsi hitung_statistik_kelas() dengan list dummy."""

    def test_tc_stat_06_list_kosong(self):
        """TC-STAT-06: list kosong -> semua nilai 0, total=0, tidak error."""
        result = hitung_statistik_kelas([])
        assert result['total'] == 0
        assert result['rata_rata'] == 0
        assert result['tertinggi'] == 0
        assert result['terendah'] == 0
        assert result['persen_lulus'] == 0

    def test_tc_stat_07_satu_siswa_lulus(self):
        """TC-STAT-07: 1 siswa lulus -> persen_lulus=100, total=1."""
        data = [_FakeNilai(nilai_akhir=85.0, status_lulus=True)]
        result = hitung_statistik_kelas(data)
        assert result['total'] == 1
        assert result['rata_rata'] == 85.0
        assert result['tertinggi'] == 85.0
        assert result['terendah'] == 85.0
        assert result['jumlah_lulus'] == 1
        assert result['jumlah_tidak_lulus'] == 0
        assert result['persen_lulus'] == 100.0

    def test_tc_stat_08_dua_dari_tiga_lulus(self):
        """TC-STAT-08: 3 siswa, 2 lulus -> persen_lulus=66.7."""
        data = [
            _FakeNilai(nilai_akhir=80.0, status_lulus=True),
            _FakeNilai(nilai_akhir=75.0, status_lulus=True),
            _FakeNilai(nilai_akhir=60.0, status_lulus=False),
        ]
        result = hitung_statistik_kelas(data)
        assert result['total'] == 3
        assert result['jumlah_lulus'] == 2
        assert result['jumlah_tidak_lulus'] == 1
        assert result['persen_lulus'] == 66.7
        # rata-rata: (80 + 75 + 60) / 3 = 71.67
        assert result['rata_rata'] == 71.67
        assert result['tertinggi'] == 80.0
        assert result['terendah'] == 60.0

    def test_semua_nilai_none_aman(self):
        """Edge case: semua nilai_akhir=None -> tidak error, return default."""
        data = [_FakeNilai(nilai_akhir=None, status_lulus=False) for _ in range(3)]
        result = hitung_statistik_kelas(data)
        assert result['total'] == 0
        assert result['rata_rata'] == 0

    def test_campuran_nilai_none_dan_ada(self):
        """Edge case: sebagian nilai None, sebagian ada -> hanya hitung yang ada."""
        data = [
            _FakeNilai(nilai_akhir=80.0, status_lulus=True),
            _FakeNilai(nilai_akhir=None, status_lulus=False),
            _FakeNilai(nilai_akhir=60.0, status_lulus=False),
        ]
        result = hitung_statistik_kelas(data)
        assert result['total'] == 2
        assert result['rata_rata'] == 70.0
