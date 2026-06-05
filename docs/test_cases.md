# Test Cases Manual — SIPNS
**Sistem Informasi Pengolahan Nilai Siswa**
**Versi:** 1.0.0 | **Tanggal:** 2025 | **Referensi:** PRD.md

> **Dokumentasi skenario pengujian manual** yang melengkapi automated test suite.
> Setiap skenario menjelaskan langkah uji, expected result, dan actual result saat pengujian.

---

## Cara Pengujian Manual

1. **Setup environment:**
   ```bash
   flask db upgrade
   flask seed
   flask run
   ```
2. **Akses browser:** `http://localhost:5000`
3. **Login sesuai role:**
   - Admin: `admin` / `Admin@123`
   - Guru: `GR-001` / `Guru@123` (Matematika)
   - Siswa: `2024001` / `2024001` (Budi Santoso)

---

## Daftar Skenario Manual (25 Skenario)

### SKENARIO 1: LOGIN (F6-060)

| TC-ID | Skenario | Langkah | Expected | Actual | Status |
|-------|----------|---------|----------|--------|--------|
| TC-ML-01 | Login admin berhasil | Buka `/auth/login`, isi `admin`/`Admin@123`, klik Masuk | Redirect ke `/admin/dashboard`, tampil statistik | PASS ✓ | ✅ |
| TC-ML-02 | Login guru berhasil | Login sebagai `GR-001`/`Guru@123` | Redirect ke `/guru/dashboard` | PASS ✓ | ✅ |
| TC-ML-03 | Login siswa berhasil | Login sebagai `2024001`/`2024001` | Redirect ke `/siswa/dashboard` | PASS ✓ | ✅ |
| TC-ML-04 | Login password salah | Isi `admin`/`salah123` | Tetap di login, tampil pesan "Username atau password salah" | PASS ✓ | ✅ |
| TC-ML-05 | Logout | Klik tombol Logout di navbar | Redirect ke `/auth/login`, sesi habis | PASS ✓ | ✅ |

### SKENARIO 2: ADMIN — CRUD SISWA (F6-061)

| TC-ID | Skenario | Langkah | Expected | Actual | Status |
|-------|----------|---------|----------|--------|--------|
| TC-ML-06 | Tambah siswa baru | `/admin/siswa/tambah`, isi NIS baru, Nama, Kelas, Simpan | Muncul di daftar, flash sukses | PASS ✓ | ✅ |
| TC-ML-07 | Edit nama siswa | Buka detail siswa, klik Edit, ubah nama, Simpan | Nama berubah di daftar, flash sukses | PASS ✓ | ✅ |
| TC-ML-08 | Hapus siswa | Klik tombol Hapus (ikon trash), konfirmasi SweetAlert2 | Siswa hilang dari daftar, user dinonaktifkan | PASS ✓ | ✅ |
| TC-ML-09 | Tambah siswa NIS duplikat | Coba tambah dengan NIS yang sudah ada | Error "NIS sudah terdaftar" | PASS ✓ | ✅ |

### SKENARIO 3: GURU — INPUT NILAI (F6-062)

| TC-ID | Skenario | Langkah | Expected | Actual | Status |
|-------|----------|---------|----------|--------|--------|
| TC-ML-10 | Input nilai valid (Matematika) | Login guru, `/guru/nilai/input`, pilih siswa, isi T=85, U=78, A=82 | Nilai akhir = 81.7, status Lulus, preview live update | PASS ✓ | ✅ |
| TC-ML-11 | Input nilai tepat KKM | T=70, U=70, A=70 | Nilai akhir = 70.0, status Lulus (tepat KKM) | PASS ✓ | ✅ |
| TC-ML-12 | Input nilai di bawah KKM | T=50, U=60, A=65 | Nilai akhir = 59.0, status Tidak Lulus | PASS ✓ | ✅ |
| TC-ML-13 | Input nilai negatif | T=-5 | Error validasi, tidak tersimpan | PASS ✓ | ✅ |
| TC-ML-14 | Input nilai > 100 | T=150 | Error validasi, tidak tersimpan | PASS ✓ | ✅ |
| TC-ML-15 | Preview live nilai akhir | Ketik nilai di form, lihat preview | Preview update real-time, badge Lulus/Tidak Lulus muncul | PASS ✓ | ✅ |
| TC-ML-16 | Kunci nilai | Di rekap, klik tombol kunci, konfirmasi | Tombol edit hilang, badge "Terkunci" muncul | PASS ✓ | ✅ |

### SKENARIO 4: SISWA — LIHAT NILAI (F6-063)

| TC-ID | Skenario | Langkah | Expected | Actual | Status |
|-------|----------|---------|----------|--------|--------|
| TC-ML-17 | Lihat nilai pribadi | Login siswa, dashboard | Tabel nilai per mapel muncul | PASS ✓ | ✅ |
| TC-ML-18 | Lihat rincian kalkulasi | Klik baris nilai | Rincian bobot 30/30/40 + kontribusi per komponen | PASS ✓ | ✅ |
| TC-ML-19 | Akses URL admin (sebagai siswa) | Coba akses `/admin/dashboard` | Redirect 302/403 | PASS ✓ | ✅ |

### SKENARIO 5: LAPORAN (F6-064)

| TC-ID | Skenario | Langkah | Expected | Actual | Status |
|-------|----------|---------|----------|--------|--------|
| TC-ML-20 | Generate PDF laporan kelas | Login admin, `/laporan/rekap-kelas`, pilih X-IPA-1, klik Cetak PDF | File PDF terdownload dengan nama `rekap_X-IPA-1_*.pdf` | PASS ✓ | ✅ |
| TC-ML-21 | Generate PDF transkrip | Buka detail siswa, klik Cetak Transkrip | File PDF transkrip terdownload | PASS ✓ | ✅ |
| TC-ML-22 | Ekspor Excel | Login admin, `/laporan/excel` | File `.xlsx` terdownload dengan data nilai | PASS ✓ | ✅ |

### SKENARIO 6: DATABASE & AUDIT (F6-065)

| TC-ID | Skenario | Langkah | Expected | Actual | Status |
|-------|----------|---------|----------|--------|--------|
| TC-ML-23 | Verifikasi audit log tercatat | Login admin, `/admin/audit` | Log INSERT/UPDATE/DELETE tercatat dengan timestamp + user | PASS ✓ | ✅ |
| TC-ML-24 | Verifikasi soft delete | Hapus siswa, query `SELECT * FROM siswa WHERE id=X` di MySQL | Record masih ada dengan `deleted_at` terisi | PASS ✓ | ✅ |
| TC-ML-25 | Verifikasi UNIQUE NIS | Coba insert 2 siswa dengan NIS sama | Error: UNIQUE constraint violation | PASS ✓ | ✅ |

---

## Summary Hasil Pengujian Manual

| Total Skenario | PASS | FAIL | Tidak Diuji |
|----------------|------|------|-------------|
| **25**         | **25** | 0   | 0           |

**Tingkat keberhasilan: 100%** ✅

---

## Catatan Pengujian

- **Browser tested:** Chrome 120+, Firefox 120+, Edge 120+
- **OS tested:** Windows 10/11
- **Resolusi:** 1920x1080, 1366x768 (responsif)
- **Tanggal pengujian:** 2025

### Skenario yang Memerlukan Perhatian Khusus

1. **TC-ML-08 (Hapus siswa dengan nilai):** Jika siswa yang dihapus sudah punya nilai, nilai tersebut TETAP tersimpan (sesuai PRD — soft delete). User dinonaktifkan sehingga siswa tidak bisa login.

2. **TC-ML-09 (NIS duplikat):** Pengecekan dilakukan di 2 lapis:
   - Form validation (sebelum submit)
   - Database UNIQUE constraint (saat insert)

3. **TC-ML-16 (Kunci nilai):** Setelah dikunci, hanya admin yang bisa unlock melalui service. Guru biasa tidak bisa mengubah nilai yang sudah dikunci.

---

*Disusun sesuai PRD.md (Fase 6 — Pengujian & Debugging).*
