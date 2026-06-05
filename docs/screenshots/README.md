# Screenshots SIPNS

Folder ini berisi **tangkapan layar (screenshot)** antarmuka SIPNS yang digunakan di dokumentasi
(laporan_tugas2.md, README.md, dan presentasi).

> **PENTING:** File dalam folder ini **tidak di-commit** ke repository (lihat `.gitignore`).
> Setiap kontributor/SIPNS admin perlu **mengambil dan menambahkan screenshot secara manual**
> dari aplikasi yang sedang berjalan.

---

## Cara Mengambil Screenshot

1. **Jalankan aplikasi** SIPNS:
   ```bash
   cd "E:\Proyek LSP\LSP 2\SIPNS"
   .\venv\Scripts\python.exe run.py
   ```

2. **Buka browser** Chrome/Firefox di `http://localhost:5000`

3. **Login** dengan akun default:
   - Admin: `admin` / `admin123`
   - Guru: `GR-001` / `guru123`
   - Siswa: `2024001` / `2024001`

4. **Ambil screenshot** menggunakan:
   - **Windows:** `Win + Shift + S` (Snip & Sketch), atau
   - **Browser DevTools:** `F12` → klik ikon "Toggle device toolbar" (Ctrl+Shift+M) untuk mobile view
   - **Extension:** [GoFullPage](https://chrome.google.com/webstore/detail/gofullpage/) untuk full-page screenshot

5. **Simpan** dengan nama file sesuai tabel di bawah

---

## Daftar Screenshot yang Diperlukan

Letakkan file dengan **nama persis** seperti di bawah ini di folder `docs/screenshots/`:

| No | Nama File | Halaman / Konten | Login Sebagai | Resolusi Rekomendasi |
|----|-----------|------------------|---------------|----------------------|
| 1 | `01_login.png` | Halaman login (/auth/login) | (logged out) | 1920×1080 |
| 2 | `02_dashboard_admin.png` | Dashboard admin dengan chart | `admin` | 1920×1080 |
| 3 | `03_daftar_siswa.png` | Halaman daftar siswa (DataTable) | `admin` | 1920×1080 |
| 4 | `04_input_nilai.png` | Form input nilai dengan live preview | `guru` (GR-001) | 1920×1080 |
| 5 | `05_nilai_siswa.png` | Halaman nilai siswa pribadi | `siswa` (2024001) | 1920×1080 |
| 6 | `06_detail_kalkulasi.png` | Modal/detail kalkulasi nilai | `siswa` (2024001) | 1920×1080 |
| 7 | `07_pilih_laporan.png` | Halaman pilih kelas untuk laporan | `admin` | 1920×1080 |
| 8 | `08_preview_laporan_pdf.png` | Tampilan laporan PDF (di browser) | `admin` | 1920×1080 |
| 9 | `09_audit_log.png` | Halaman audit log (admin) | `admin` | 1920×1080 |
| 10 | `10_export_excel.png` | File Excel hasil ekspor (screenshot dari MS Excel/LibreOffice) | `admin` | 1920×1080 |

---

## Panduan Tambahan

### Agar Screenshot Konsisten

- **Gunakan browser Chrome** (default development)
- **Disable extensions** yang mengubah tampilan (ad-blocker, dark mode, dll)
- **Hilangkan notifikasi** (pakai mode Incognito: `Ctrl+Shift+N`)
- **Gunakan data sample** dari seeder (`flask seed`) untuk konsistensi
- **Pastikan zoom 100%** (`Ctrl+0`)
- **Crop** screenshot hanya area konten utama (jangan termasuk taskbar/address bar)

### Checklist Kualitas

- [ ] Teks terbaca jelas (tidak blur/pecah)
- [ ] Tidak ada data sensitif terlihat (password)
- [ ] SweetAlert2/DataTables tampil dengan baik
- [ ] Chart.js tampil lengkap (bar + doughnut di dashboard)
- [ ] Status badge (hijau/merah) terlihat jelas
- [ ] Nama file persis sesuai tabel di atas (lowercase, underscore)

### Mobile Screenshots (Opsional)

Jika ingin menambahkan tampilan mobile (responsif), tambahkan file dengan prefix `mobile_`:

- `mobile_01_login.png`
- `mobile_02_dashboard_admin.png`
- dst.

Gunakan **device toolbar** di Chrome DevTools dengan preset **iPhone 12 Pro** atau **Pixel 5**.

---

## Kontribusi

Setelah menambahkan semua 10 screenshot, **jangan commit file `.png` ke git**
(folder ini ada di `.gitignore`). Cukup verifikasi visual secara lokal.

Jika Anda ingin menunjukkan screenshot di laporan/doc publik:
1. Export PDF dokumentasi dengan screenshot tertanam
2. Atau upload ke image hosting (Imgur, GitHub Issue) dan rujuk via URL

---

*Folder ini sengaja dikosongkan di repository. Kontributor: tambahkan screenshot sesuai tabel di atas.*
