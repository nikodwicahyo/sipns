# Laporan Tugas 1 — Analisis & Perancangan SIPNS

**Sistem Informasi Pengolahan Nilai Siswa**
**Versi:** 1.0.0 | **Tahun:** 2026 | **Fase:** 1 (Tugas 1)
**Referensi:** [PRD.md](../../PRD.md) v1.0.0

---

## Daftar Isi

1. [Tujuan Sistem](#1-tujuan-sistem)
2. [Analisis Kebutuhan Pengguna](#2-analisis-kebutuhan-pengguna)
3. [Fungsi Utama Sistem](#3-fungsi-utama-sistem)
4. [Spesifikasi Fungsional & Non-Fungsional](#4-spesifikasi-fungsional--non-fungsional)
5. [Alur Kerja Sistem](#5-alur-kerja-sistem)
6. [Rancangan Antarmuka](#6-rancangan-antarmuka)
7. [Rancangan Database](#7-rancangan-database)
8. [Batasan Sistem](#8-batasan-sistem)
9. [Rancangan Fungsi Terstruktur](#9-rancangan-fungsi-terstruktur)
10. [Rancangan Class OOP](#10-rancangan-class-oop)

---

## 1. Tujuan Sistem

**SIPNS (Sistem Informasi Pengolahan Nilai Siswa)** adalah aplikasi web berbasis Python/Flask yang bertujuan untuk:

| No  | Tujuan                                                       | Implementasi                                        |
| --- | ------------------------------------------------------------ | --------------------------------------------------- |
| 1   | Menyimpan dan mengelola data siswa secara terpusat dan aman  | Tabel `siswa` + role-based access                   |
| 2   | Mengotomasi perhitungan nilai akhir berdasarkan formula baku | Fungsi `hitung_nilai_akhir()` di `nilai_service.py` |
| 3   | Menentukan status kelulusan siswa secara otomatis            | Fungsi `tentukan_status_kelulusan()`                |
| 4   | Menyajikan laporan nilai dalam format PDF                    | `generate_laporan_pdf()` (WeasyPrint)               |
| 5   | Menerapkan kontrol akses berbasis peran (RBAC)               | Decorator `@role_required`                          |
| 6   | Mendemonstrasikan Pemrograman Terstruktur + OOP              | `app/services/` + `app/models/`                     |

**Outcome yang diharapkan:**

- Menggantikan proses manual (kertas/spreadsheet) dengan platform digital
- Meningkatkan akurasi & transparansi pengolahan nilai
- Mempermudah akses real-time bagi Admin, Guru, dan Siswa

---

## 2. Analisis Kebutuhan Pengguna

### 2.1 Admin

| Kebutuhan                                 | Prioritas | Status Implementasi                              |
| ----------------------------------------- | --------- | ------------------------------------------------ |
| Login dengan kredensial admin             | Wajib     | ✅ `/auth/login` + `@role_required('admin')`     |
| CRUD data siswa                           | Wajib     | ✅ `/admin/siswa/{,tambah,edit,hapus,<id>}`      |
| CRUD data guru                            | Wajib     | ✅ `/admin/guru/{,tambah,edit,hapus}`            |
| Manajemen user (reset password, aktivasi) | Wajib     | ✅ `/admin/users/{,toggle-aktif,reset-password}` |
| Lihat & cetak laporan PDF                 | Wajib     | ✅ `/laporan/pdf/kelas/<kelas>`                  |
| Lihat audit log                           | Penting   | ✅ `/admin/audit`                                |
| Dashboard statistik                       | Penting   | ✅ `/admin/dashboard` (Chart.js)                 |
| Ekspor Excel                              | Penting   | ✅ `/laporan/excel`                              |

### 2.2 Guru

| Kebutuhan                               | Prioritas | Status Implementasi                          |
| --------------------------------------- | --------- | -------------------------------------------- |
| Login dengan kredensial guru            | Wajib     | ✅ Username = ID Guru (mis. GR-001)          |
| Input nilai (Tugas, UTS, UAS) per mapel | Wajib     | ✅ `/guru/nilai/input`                       |
| Edit nilai sebelum dikunci              | Wajib     | ✅ `/guru/nilai/edit/<id>` (jika not locked) |
| Lihat rekap nilai kelas                 | Wajib     | ✅ `/guru/nilai/rekap`                       |
| Kunci nilai                             | Penting   | ✅ `POST /guru/nilai/kunci/<id>`             |
| Generate PDF rekap kelas                | Penting   | ✅ `/laporan/pdf/kelas/<kelas>`              |
| Preview kalkulasi real-time             | Penting   | ✅ AJAX `/api/nilai-preview`                 |

### 2.3 Siswa

| Kebutuhan               | Prioritas | Status Implementasi                    |
| ----------------------- | --------- | -------------------------------------- |
| Login dengan NIS        | Wajib     | ✅ Username = NIS, password = NIS      |
| Lihat nilai pribadi     | Wajib     | ✅ `/siswa/nilai`                      |
| Lihat status kelulusan  | Wajib     | ✅ Banner di dashboard                 |
| Lihat rincian kalkulasi | Penting   | ✅ `/siswa/nilai/<id>/detail`          |
| Unduh transkrip PDF     | Opsional  | ✅ `/laporan/pdf/transkrip/<siswa_id>` |

---

## 3. Fungsi Utama Sistem

### 3.1 Modul Inti

| Modul               | Kode    | Deskripsi                                                   |
| ------------------- | ------- | ----------------------------------------------------------- |
| **Autentikasi**     | AUTH    | Login multi-role, session, password hashing (PBKDF2-SHA256) |
| **Manajemen Siswa** | SISWA   | CRUD + soft delete + profil detail                          |
| **Manajemen Guru**  | GURU    | CRUD + soft delete + filter mapel                           |
| **Nilai**           | NILAI   | Input, edit, kunci, kalkulasi otomatis, status kelulusan    |
| **Laporan**         | LAPORAN | PDF rekap kelas, PDF transkrip, ekspor Excel                |
| **Dashboard**       | DASH    | Statistik + Chart.js (bar, doughnut) per role               |
| **Audit Log**       | AUDIT   | Pencatatan semua operasi CRUD + IP address                  |

### 3.2 Aturan Bisnis (Business Rules)

| Aturan                            | Konstanta           | Lokasi                                   |
| --------------------------------- | ------------------- | ---------------------------------------- |
| KKM (Kriteria Ketuntasan Minimal) | `70`                | `app/utils/constants.py: KKM`            |
| Bobot komponen nilai              | T:30%, U:30%, A:40% | `constants.py: BOBOT_*`                  |
| Rentang nilai valid               | `0 ≤ n ≤ 100`       | `constants.py: RENTANG_NILAI_*`          |
| Pembulatan nilai akhir            | 2 desimal           | `constants.py: PEMBULATAN_DESIMAL`       |
| Session lifetime                  | 7200 detik (2 jam)  | `constants.py: SESSION_LIFETIME_SECONDS` |
| Password minimum length           | 8 karakter          | `constants.py: PASSWORD_MIN_LENGTH`      |

---

## 4. Spesifikasi Fungsional & Non-Fungsional

### 4.1 Spesifikasi Fungsional

#### AUTH (Autentikasi)

| Kode    | Fitur                     | Endpoint/Method                                   |
| ------- | ------------------------- | ------------------------------------------------- |
| AUTH-01 | Login multi-role          | `GET/POST /auth/login`                            |
| AUTH-02 | Logout aman               | `GET /auth/logout`                                |
| AUTH-03 | Session 2 jam             | `Flask-Login` + `PERMANENT_SESSION_LIFETIME=7200` |
| AUTH-04 | Password hashing PBKDF2   | `werkzeug.security.generate_password_hash`        |
| AUTH-05 | Flash message SweetAlert2 | `flash()` + `static/js/main.js`                   |

#### NILAI

| Kode     | Fitur                              | Detail                                |
| -------- | ---------------------------------- | ------------------------------------- |
| NILAI-01 | Input nilai                        | Form WTForms, range 0-100             |
| NILAI-02 | Validasi server-side & client-side | WTForms validators + JS               |
| NILAI-03 | Hitung nilai akhir otomatis        | `nilai.hitung_dan_simpan()` → service |
| NILAI-04 | Status Lulus/Tidak Lulus           | `>= KKM (70)`                         |
| NILAI-05 | Edit nilai (sebelum lock)          | Cek `is_locked == False`              |
| NILAI-06 | Kunci nilai                        | `nilai.lock()` set `is_locked = True` |
| NILAI-07 | Rekap nilai                        | Tabel DataTables + badge status       |

### 4.2 Spesifikasi Non-Fungsional

| Kategori            | Ketentuan                                     | Implementasi                                     |
| ------------------- | --------------------------------------------- | ------------------------------------------------ |
| **Performa**        | Load < 3 detik, query < 1 detik (≤1000 siswa) | Index DB, eager loading, DataTables pagination   |
| **Keamanan**        | PBKDF2 hash, CSRF, ORM, XSS auto-escape       | Werkzeug, Flask-WTF, SQLAlchemy, Jinja2          |
| **Reliabilitas**    | 50 user konkuren                              | Stateless session, MySQL connection pool         |
| **Usability**       | Responsif (mobile), belajar < 30 menit        | Bootstrap 5.3, DataTables, SweetAlert2           |
| **Maintainability** | PEP 8, docstring, README                      | Tercakup di Fase 7 (kode refactor + dokumentasi) |
| **Skalabilitas**    | Modular (Blueprint)                           | `app/blueprints/{auth,admin,guru,siswa,laporan}` |
| **Kompatibilitas**  | Chrome 100+, Firefox 100+, Edge 100+          | Standar HTML5 + ES6 JS                           |

---

## 5. Alur Kerja Sistem

### 5.1 Alur Login

```
[Mulai]
   │
   ▼
[Buka Halaman Login]
   │
   ▼
[Input Username & Password]
   │
   ▼
[Validasi Form?] ──TIDAK──► [Tampilkan Error Validasi inline]
   │                                    │
   YA                                   └──► [Kembali ke Form]
   │
   ▼
[Cek Kredensial di DB] (User.query.filter_by + check_password)
   │
   ├── GAGAL ──► [Flash: "Username atau password salah"] ──► [Kembali ke Form]
   │
   └── BERHASIL
         │
         ▼
     [Cek Role User]
         │
         ├── admin ──► [Redirect: /admin/dashboard]
         ├── guru  ──► [Redirect: /guru/dashboard]
         └── siswa ──► [Redirect: /siswa/dashboard]
```

> 📊 Lihat diagram visual: [`docs/Flowchart alurr login.png`](../Flowchart%20alurr%20login.png)

### 5.2 Alur Input & Kalkulasi Nilai

```
[Guru: Halaman Input Nilai /guru/nilai/input]
   │
   ▼
[Pilih Siswa & (Otomatis: Mapel Guru)]
   │
   ▼
[Input Nilai Tugas, UTS, UAS]
   │
   ▼
[Validasi Client-side JS] (range 0-100)
   │── GAGAL ──► [Tampilkan error inline merah]
   │
   YA ──► [AJAX GET /api/nilai-preview?tugas=..&uts=..&uas=..]
                │
                └──► [Tampilkan Preview: "Nilai Akhir: 81.70 → LULUS"]
   │
   ▼
[Submit Form]
   │
   ▼
[Validasi Server-side WTForms]
   │── GAGAL ──► [Return error inline]
   │
   YA
   │
   ▼
[Service hitung_nilai_akhir()] → [0.30×T + 0.30×U + 0.40×A]
   │
   ▼
[Service tentukan_status_kelulusan()] → [lulus/belum lulus]
   │
   ▼
[db.session.commit()] → [Simpan ke Database]
   │
   ▼
[catat_audit_log(INSERT/UPDATE)] → [Audit Log Table]
   │
   ▼
[SweetAlert2: "Nilai berhasil disimpan"]
```

> 📊 Lihat diagram visual: [`docs/Flowchart alur input nilai.png`](../Flowchart%20alur%20input%20nilai.png)

### 5.3 Alur Generate Laporan PDF

```
[User: /laporan/rekap-kelas]
   │
   ▼
[Pilih Kelas dari Dropdown]
   │
   ▼
[Klik "Cetak PDF" → GET /laporan/pdf/kelas/<kelas>]
   │
   ▼
[Service generate_laporan_pdf(kelas)]
   │  1. Query JOIN Nilai + Siswa, filter kelas
   │  2. hitung_statistik_kelas()
   │  3. Render template Jinja2 → HTML
   │  4. WeasyPrint HTML.write_pdf() → bytes
   │
   ▼
[Audit Log: PRINT_PDF]
   │
   ▼
[Response: application/pdf, Content-Disposition: attachment]
   │
   ▼
[Browser: Download file "rekap_X-IPA-1_YYYYMMDD.pdf"]
```

> 📊 Lihat diagram visual: [`docs/Flowchart generate laporan.png`](../Flowchart%20generate%20laporan.png)

### 5.4 Use Case Diagram (Ringkasan)

```
                    ┌─────────────────────────────────────────┐
                    │              SIPNS System                │
                    │                                         │
  ┌───────┐         │  ┌─────────────────────────────────┐    │
  │ Admin │─────────┼──┤ Kelola Siswa (CRUD)             │    │
  └───────┘         │  └─────────────────────────────────┘    │
      │             │  ┌─────────────────────────────────┐    │
      ├─────────────┼──┤ Kelola Guru (CRUD)              │    │
      │             │  └─────────────────────────────────┘    │
      ├─────────────┼──┤ Kelola User                     │    │
      │             │  └─────────────────────────────────┘    │
      └─────────────┼──┤ Lihat Audit Log & Laporan       │    │
                    │  └─────────────────────────────────┘    │
  ┌───────┐         │  ┌─────────────────────────────────┐    │
  │ Guru  │─────────┼──┤ Input Nilai Siswa               │    │
  └───────┘         │  └─────────────────────────────────┘    │
      │             │  ┌─────────────────────────────────┐    │
      ├─────────────┼──┤ Kunci Nilai                     │    │
      │             │  └─────────────────────────────────┘    │
      └─────────────┼──┤ Lihat Rekap Nilai Kelas         │    │
                    │  └─────────────────────────────────┘    │
  ┌───────┐         │  ┌─────────────────────────────────┐    │
  │ Siswa │─────────┼──┤ Lihat Nilai Pribadi             │    │
  └───────┘         │  └─────────────────────────────────┘    │
      │             │  ┌─────────────────────────────────┐    │
      └─────────────┼──┤ Lihat Status Kelulusan          │    │
                    │  └─────────────────────────────────┘    │
                    └─────────────────────────────────────────┘
```

> 📊 Lihat diagram lengkap: [`docs/Use Case Diagram.png`](../Use%20Case%20Diagram.png)

---

## 6. Rancangan Antarmuka

### 6.1 Daftar Halaman

| Kode  | Halaman                | Role        | URL                                             |
| ----- | ---------------------- | ----------- | ----------------------------------------------- |
| UI-01 | Halaman Login          | Semua       | `/auth/login`                                   |
| UI-02 | Landing Page           | Logged out  | `/`                                             |
| UI-03 | Dashboard Admin        | Admin       | `/admin/dashboard`                              |
| UI-04 | Dashboard Guru         | Guru        | `/guru/dashboard`                               |
| UI-05 | Dashboard Siswa        | Siswa       | `/siswa/dashboard`                              |
| UI-06 | Daftar Siswa           | Admin       | `/admin/siswa`                                  |
| UI-07 | Form Tambah/Edit Siswa | Admin       | `/admin/siswa/tambah`, `/admin/siswa/edit/<id>` |
| UI-08 | Detail Siswa           | Admin       | `/admin/siswa/<id>`                             |
| UI-09 | Daftar Guru            | Admin       | `/admin/guru`                                   |
| UI-10 | Form Tambah/Edit Guru  | Admin       | `/admin/guru/tambah`, `/admin/guru/edit/<id>`   |
| UI-11 | Input Nilai            | Guru        | `/guru/nilai/input`                             |
| UI-12 | Edit Nilai             | Guru        | `/guru/nilai/edit/<id>`                         |
| UI-13 | Rekap Nilai Kelas      | Guru, Admin | `/guru/nilai/rekap`                             |
| UI-14 | Nilai Pribadi Siswa    | Siswa       | `/siswa/nilai`                                  |
| UI-15 | Detail Nilai Siswa     | Siswa       | `/siswa/nilai/<id>/detail`                      |
| UI-16 | Pilih Laporan          | Admin, Guru | `/laporan/rekap-kelas`                          |
| UI-17 | Daftar User            | Admin       | `/admin/users`                                  |
| UI-18 | Edit User              | Admin       | `/admin/users/edit/<id>`                        |
| UI-19 | Reset Password         | Admin       | `/admin/users/reset-password/<id>`              |
| UI-20 | Audit Log              | Admin       | `/admin/audit`                                  |
| UI-21 | Health Check           | Admin       | `/admin/health`                                 |

### 6.2 Komponen UI Utama

#### Navigasi Global (Navbar)

- Logo/nama sistem (kiri)
- Menu kontekstual per role (admin/guru/siswa)
- Info user + tombol logout (kanan)
- Responsif: hamburger menu di mobile

#### Sidebar (Admin & Guru)

- Menu hierarkis per modul
- Active state untuk halaman aktif
- Collapsible di layar kecil

#### Tabel DataTables

- Search box global
- Sorting per kolom (klik header)
- Pagination (10/25/50/100/All)
- Tombol aksi per baris (Edit, Hapus, Detail)
- Badge status berwarna (hijau/merah)

#### Form Input Nilai

- Dropdown siswa (populate via AJAX)
- Input angka 0-100 dengan validasi real-time
- **Preview Live**: hitung nilai akhir & status lulus via AJAX
- Tombol "Simpan" dengan konfirmasi SweetAlert2

#### Dashboard Chart

- Bar chart: distribusi nilai per kelas
- Doughnut chart: rasio Lulus vs Tidak Lulus
- Card statistik: rata-rata, tertinggi, terendah, % lulus

> 📊 Lihat wireframe: [`docs/Wireframe.png`](../Wireframe.png)

---

## 7. Rancangan Database

### 7.1 ERD (Entity Relationship Diagram)

```
┌──────────────┐       ┌──────────────────┐       ┌──────────────┐
│    users     │       │      nilai       │       │    siswa     │
├──────────────┤       ├──────────────────┤       ├──────────────┤
│ id (PK)      │       │ id (PK)          │       │ id (PK)      │
│ username     │       │ siswa_id (FK)    │◄──────│ nis (UNIQUE) │
│ password_hash│       │ guru_id (FK)     │       │ nama         │
│ role         │       │ mata_pelajaran   │       │ kelas        │
│ is_active    │       │ nilai_tugas      │       │ user_id (FK) │
│ siswa_id(FK) │──────►│ nilai_uts        │       │ created_at   │
│ guru_id (FK) │       │ nilai_uas        │       │ updated_at   │
│ created_at   │       │ nilai_akhir      │       │ deleted_at   │
│ updated_at   │       │ status_lulus     │       └──────────────┘
└──────────────┘       │ is_locked        │
        │              │ created_at       │       ┌──────────────┐
        │              │ updated_at       │       │    guru      │
        │              └──────────────────┘       ├──────────────┤
        │                       ▲                 │ id (PK)      │
        └───────────────────────┴────────────────►│ id_guru (UNQ)│
                                                   │ nama_guru    │
                                                   │ mata_pelajaran│
                                                   │ user_id (FK) │
                                                   │ created_at   │
                                                   │ updated_at   │
                                                   │ deleted_at   │
                                                   └──────────────┘

┌────────────────────────────────┐
│          audit_log             │
├────────────────────────────────┤
│ id (PK)                        │
│ user_id (FK)                   │
│ action (INSERT/UPDATE/DELETE)  │
│ table_name                     │
│ record_id                      │
│ description                    │
│ ip_address                     │
│ created_at                     │
└────────────────────────────────┘
```

> 📊 Lihat diagram lengkap: [`docs/ERD.png`](../ERD.png)

### 7.2 Tabel & Constraint

Lihat [PRD.md §8](../../PRD.md#8-rancangan-database) untuk definisi kolom lengkap. Ringkasan:

| Tabel       | Primary Key | Foreign Key           | Index                                                                    |
| ----------- | ----------- | --------------------- | ------------------------------------------------------------------------ |
| `users`     | id          | siswa_id, guru_id     | username (UNIQUE)                                                        |
| `siswa`     | id          | user_id (via backref) | nis (UNIQUE), kelas                                                      |
| `guru`      | id          | user_id (via backref) | id_guru (UNIQUE)                                                         |
| `nilai`     | id          | siswa_id, guru_id     | siswa_id, guru_id, mata_pelajaran + **UNIQUE(siswa_id, mata_pelajaran)** |
| `audit_log` | id          | user_id               | user_id, created_at                                                      |

### 7.3 Constraint Penting

- **UNIQUE(siswa_id, mata_pelajaran)** pada `nilai` → satu siswa hanya punya satu nilai per mapel (PRD §14 Batasan #1)
- **CHECK (0 ≤ nilai ≤ 100)** pada kolom nilai → defense in depth
- **ON DELETE behavior** → soft delete untuk siswa/guru (pertahankan histori)

### 7.4 DDL Referensi

Lihat [`docs/schema.sql`](../schema.sql) untuk DDL MySQL lengkap.

---

## 8. Batasan Sistem

| No  | Batasan                                                | Catatan                               |
| --- | ------------------------------------------------------ | ------------------------------------- |
| 1   | Satu siswa hanya punya satu nilai per mata pelajaran   | UNIQUE constraint di DB               |
| 2   | Nilai yang sudah dikunci tidak bisa diubah tanpa admin | `is_locked=True`                      |
| 3   | NIS bersifat unik dan immutable                        | `unique=True` + disabled di form edit |
| 4   | Sistem hanya mendukung 3 role: Admin, Guru, Siswa      | ENUM-like field                       |
| 5   | Laporan PDF hanya per kelas (bukan lintas kelas)       | Limitasi WeasyPrint                   |
| 6   | Tidak ada reset password mandiri (harus via admin)     | Backlog BL-010                        |
| 7   | Rentang nilai valid: 0-100 (desimal diperbolehkan)     | CHECK constraint                      |
| 8   | KKM tetap 70 (tidak per-mapel)                         | Backlog BL-006                        |
| 9   | MySQL untuk production; testing pakai SQLite           | Config swap                           |
| 10  | Tidak ada notifikasi email/SMS                         | Backlog BL-002                        |

---

## 9. Rancangan Fungsi Terstruktur

Mengikuti prinsip **Pemrograman Terstruktur** — logika bisnis inti diekspresikan sebagai fungsi/prosedur murni.

### Fungsi 1: `validasi_rentang_nilai(nilai, label)`

**Tujuan:** Memvalidasi tipe data & rentang nilai (0-100).

**Signature:**

```python
def validasi_rentang_nilai(nilai: float, label: str = "Nilai") -> bool:
    """
    Raises:
        ValueError: Jika nilai bukan numerik atau di luar rentang 0-100
    """
```

**Implementasi:** [`app/services/nilai_service.py:23-66`](../../app/services/nilai_service.py)

**Test cases:** `tests/unit/test_nilai_service.py::TestValidasiRentangNilai` (8 tests PASS)

### Fungsi 2: `hitung_nilai_akhir(tugas, uts, uas)`

**Tujuan:** Hitung nilai akhir dengan formula `0.30×T + 0.30×U + 0.40×A`.

**Signature:**

```python
def hitung_nilai_akhir(nilai_tugas: float, nilai_uts: float, nilai_uas: float) -> float:
    """
    Returns:
        float: Nilai akhir dibulatkan 2 desimal
    """
```

**Implementasi:** [`app/services/nilai_service.py:69-115`](../../app/services/nilai_service.py)

**Test cases:** `TestHitungNilaiAkhir` (10 tests PASS)

### Fungsi 3: `tentukan_status_kelulusan(nilai_akhir, kkm)`

**Tujuan:** Tentukan status Lulus/Tidak Lulus berdasarkan KKM.

**Signature:**

```python
def tentukan_status_kelulusan(nilai_akhir: float, kkm: float = 70.0) -> dict:
    """
    Returns:
        dict: {lulus: bool, label: str, badge_class: str, selisih: float}
    """
```

**Implementasi:** [`app/services/nilai_service.py:118-142`](../../app/services/nilai_service.py)

**Test cases:** `TestTentukanStatusKelulusan` (7 tests PASS)

### Fungsi 4: `generate_laporan_pdf(kelas, template)`

**Tujuan:** Generate PDF rekap nilai per kelas via WeasyPrint.

**Signature:**

```python
def generate_laporan_pdf(kelas: str, template: str = 'laporan/rekap_kelas.html') -> bytes:
    """
    Returns:
        bytes: Konten PDF siap-download
    """
```

**Implementasi:** [`app/services/laporan_service.py:54-105`](../../app/services/laporan_service.py)

**Test cases:** `tests/integration/test_laporan.py::TestLaporanPDF` (6 tests PASS)

### Fungsi 5: `hitung_statistik_kelas(data_nilai)`

**Tujuan:** Hitung statistik agregat nilai (total, rata-rata, %, dll).

**Signature:**

```python
def hitung_statistik_kelas(data_nilai: list) -> dict:
    """
    Returns:
        dict: {total, rata_rata, tertinggi, terendah, jumlah_lulus, persen_lulus}
    """
```

**Implementasi:** [`app/services/nilai_service.py:145-187`](../../app/services/nilai_service.py)

**Test cases:** `TestHitungStatistikKelas` (5 tests PASS)

### Fungsi 6: `export_excel(kelas, dicetak_oleh)`

**Tujuan:** Ekspor data nilai ke file `.xlsx` (openpyxl).

**Signature:**

```python
def export_excel(kelas: str = None, dicetak_oleh: str = None) -> bytes:
    """
    Returns:
        bytes: Konten file XLSX
    """
```

**Implementasi:** [`app/services/laporan_service.py:148-269`](../../app/services/laporan_service.py)

**Test cases:** `tests/integration/test_laporan.py::TestLaporanExcel` (4 tests PASS)

### Fungsi 7: `catat_audit_log(user_id, action, table_name, ...)`

**Tujuan:** Catat aktivitas user ke tabel `audit_log`.

**Signature:**

```python
def catat_audit_log(
    user_id: int,
    action: str,
    table_name: str,
    record_id: int = None,
    description: str = None,
    ip_address: str = None,
) -> None:
    """
    Returns:
        None (side-effect: insert ke DB)
    """
```

**Implementasi:** [`app/services/audit_service.py`](../../app/services/audit_service.py)

---

## 10. Rancangan Class OOP

Entitas sistem menggunakan **SQLAlchemy ORM** yang mengimplementasikan prinsip OOP: encapsulation, inheritance, polymorphism.

### Class 1: `User(db.Model, UserMixin)`

**File:** [`app/models/user.py`](../../app/models/user.py)

**Attributes:**

- `id, username, password_hash, role, is_active, siswa_id, guru_id, created_at, updated_at`

**Methods:**

- `set_password(password)` → hash dengan PBKDF2
- `check_password(password)` → verifikasi hash
- `is_admin()`, `is_guru()`, `is_siswa()` → return bool
- `get_id()` → untuk Flask-Login session
- `to_dict()` → serialisasi ke JSON

**Relasi:**

- `siswa` (one-to-one, FK `User.siswa_id`)
- `guru` (one-to-one, FK `User.guru_id`)
- `audit_logs` (one-to-many, backref)

### Class 2: `Siswa(db.Model)`

**File:** [`app/models/siswa.py`](../../app/models/siswa.py)

**Attributes:**

- `id, nis, nama, kelas, created_at, updated_at, deleted_at`

**Methods:**

- `nilai_akhir_all()` → list nilai akhir
- `rata_rata_nilai()` → float
- `status_kelulusan_global()` → 'Lulus'/'Tidak Lulus'/'Belum Ada Nilai'
- `soft_delete()` → set deleted_at
- `cari_by_nis(nis)` (classmethod) → Siswa atau None
- `daftar_kelas()` (classmethod) → list[str]

**Relasi:**

- `nilai` (one-to-many ke Nilai)
- `user` (one-to-one ke User)

### Class 3: `Guru(db.Model)`

**File:** [`app/models/guru.py`](../../app/models/guru.py)

**Attributes:**

- `id, id_guru, nama_guru, mata_pelajaran, created_at, updated_at, deleted_at`

**Methods:**

- `get_siswa_diajar()` → list[Siswa]
- `soft_delete()`

**Relasi:**

- `nilai_diinput` (one-to-many ke Nilai)
- `user` (one-to-one ke User)

### Class 4: `Nilai(db.Model)` — **Titik Integrasi OOP ↔ Terstruktur**

**File:** [`app/models/nilai.py`](../../app/models/nilai.py)

**Attributes:**

- `id, siswa_id, guru_id, mata_pelajaran, nilai_tugas, nilai_uts, nilai_uas, nilai_akhir, status_lulus, is_locked, created_at, updated_at`

**Methods (PENTING):**

- **`hitung_dan_simpan()`** → delegasi ke `hitung_nilai_akhir()` & `tentukan_status_kelulusan()` dari `nilai_service.py` (integrasi OOP ↔ Terstruktur)
- `lock()` → set is_locked=True
- `unlock()` → set is_locked=False (admin only)
- `get_detail_kalkulasi()` → return dict {tugas, uts, uas, nilai_akhir, status_lulus, kkm}
- `to_dict()` → serialisasi JSON

**Constraint:**

- `UNIQUE(siswa_id, mata_pelajaran)` — satu siswa satu nilai per mapel
- `CHECK (0 ≤ nilai ≤ 100)` — defense in depth

**Relasi:**

- `siswa` (many-to-one, backref)
- `guru` (many-to-one, backref)

### Class 5: `AuditLog(db.Model)`

**File:** [`app/models/audit_log.py`](../../app/models/audit_log.py)

**Attributes:**

- `id, user_id, action, table_name, record_id, description, ip_address, created_at`

**Methods:**

- `log(user_id, action, table_name, ...)` (classmethod) → buat entry baru
- `to_dict()` → serialisasi JSON

**Relasi:**

- `user` (many-to-one, lazy='joined')

---

## 📊 Diagram OOP Lengkap

> 📊 Lihat Class Diagram: [`docs/Class Diagram.png`](../Class%20Diagram.png)
> 📊 Lihat Activity Diagram: [`docs/Activity Diagram.png`](../Activity%20Diagram.png)
> 📊 Lihat Sequence Diagram: [`docs/Sequence Diagram.png`](../Sequence%20Diagram.png)

---

## ✅ Checklist Output Fase 1

- [x] `PRD.md` lengkap dan tervalidasi
- [x] `docs/diagrams/` berisi: Use Case, Flowchart, Sequence, Class, Activity Diagram
- [x] `docs/wireframes/` (file: `Wireframe.png`) berisi wireframe semua halaman
- [x] `docs/schema.sql` DDL lengkap
- [x] Rancangan ≥ 3 fungsi terstruktur terdokumentasi (5+ fungsi)
- [x] Rancangan ≥ 2 class OOP terdokumentasi (5 class)

---

_Disusun sesuai PRD.md Fase 1. Versi 1.0.0 — 2026._
