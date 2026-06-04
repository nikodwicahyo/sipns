def validasi_rentang_nilai(nilai, label="Nilai"):
    if not isinstance(nilai, (int, float)):
        raise ValueError(f"{label} harus berupa angka.")
    if not (0 <= nilai <= 100):
        raise ValueError(f"{label} harus berada di antara 0 dan 100. Nilai '{nilai}' tidak valid.")
    return True


def hitung_nilai_akhir(nilai_tugas, nilai_uts, nilai_uas):
    validasi_rentang_nilai(nilai_tugas, "Tugas")
    validasi_rentang_nilai(nilai_uts, "UTS")
    validasi_rentang_nilai(nilai_uas, "UAS")

    nilai_akhir = (0.30 * nilai_tugas) + (0.30 * nilai_uts) + (0.40 * nilai_uas)
    return round(nilai_akhir, 2)


def tentukan_status_kelulusan(nilai_akhir, kkm=70.0):
    lulus = nilai_akhir >= kkm
    return {
        'lulus': lulus,
        'label': 'Lulus' if lulus else 'Tidak Lulus',
        'badge_class': 'bg-success' if lulus else 'bg-danger',
        'selisih': round(nilai_akhir - kkm, 2),
    }


def hitung_statistik_kelas(data_nilai):
    if not data_nilai:
        return {'rata_rata': 0, 'tertinggi': 0, 'terendah': 0, 'persen_lulus': 0, 'total': 0}

    nilai_list = [n.nilai_akhir for n in data_nilai if n.nilai_akhir is not None]
    if not nilai_list:
        return {'rata_rata': 0, 'tertinggi': 0, 'terendah': 0, 'persen_lulus': 0, 'total': 0}

    lulus_count = sum(1 for n in data_nilai if n.status_lulus)

    return {
        'total': len(nilai_list),
        'rata_rata': round(sum(nilai_list) / len(nilai_list), 2),
        'tertinggi': max(nilai_list),
        'terendah': min(nilai_list),
        'jumlah_lulus': lulus_count,
        'jumlah_tidak_lulus': len(nilai_list) - lulus_count,
        'persen_lulus': round((lulus_count / len(nilai_list)) * 100, 1),
    }
