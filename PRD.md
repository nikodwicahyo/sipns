# Product Requirements Document (PRD)
## Sistem Informasi Pengolahan Nilai Siswa (SIPNS)
**Versi:** 1.0.0  
**Tanggal:** 2025  
**Status:** Draft  
**Penulis:** Tim Pengembang

---

## Daftar Isi

1. [Ringkasan Eksekutif](#1-ringkasan-eksekutif)
2. [Latar Belakang & Tujuan](#2-latar-belakang--tujuan)
3. [Ruang Lingkup Sistem](#3-ruang-lingkup-sistem)
4. [Analisis Kebutuhan Pengguna](#4-analisis-kebutuhan-pengguna)
5. [Spesifikasi Fungsional](#5-spesifikasi-fungsional)
6. [Spesifikasi Non-Fungsional](#6-spesifikasi-non-fungsional)
7. [Arsitektur & Tech Stack](#7-arsitektur--tech-stack)
8. [Rancangan Database](#8-rancangan-database)
9. [Rancangan Antarmuka (UI)](#9-rancangan-antarmuka-ui)
10. [Alur Kerja Sistem (Flowchart / UML)](#10-alur-kerja-sistem-flowchart--uml)
11. [Implementasi Pemrograman Terstruktur](#11-implementasi-pemrograman-terstruktur)
12. [Implementasi OOP](#12-implementasi-oop)
13. [Rencana Pengujian](#13-rencana-pengujian)
14. [Batasan Sistem](#14-batasan-sistem)
15. [Risiko & Mitigasi](#15-risiko--mitigasi)
16. [Milestone & Timeline](#16-milestone--timeline)

---

## 1. Ringkasan Eksekutif

**SIPNS** (Sistem Informasi Pengolahan Nilai Siswa) adalah aplikasi web berbasis Python/Flask yang dirancang untuk membantu institusi pendidikan dalam mengelola data nilai siswa secara digital, terstruktur, dan efisien. Sistem ini menggantikan proses manual berbasis kertas atau spreadsheet dengan platform terintegrasi yang mendukung tiga peran pengguna: **Admin**, **Guru**, dan **Siswa**.

Aplikasi ini dikembangkan sebagai implementasi nyata dua paradigma pemrograman — **Pemrograman Terstruktur** dan **Pemrograman Berorientasi Objek (OOP)** — yang saling melengkapi dalam satu ekosistem perangkat lunak.

---

## 2. Latar Belakang & Tujuan

### 2.1 Latar Belakang

Pengelolaan nilai siswa di banyak institusi pendidikan masih dilakukan secara manual, rentan terhadap kesalahan perhitungan, sulit diakses secara real-time, dan tidak memiliki sistem audit yang memadai. Kebutuhan akan sistem yang terotomasi menjadi urgensi bagi institusi yang ingin meningkatkan akurasi, transparansi, dan efisiensi administrasi akademik.

### 2.2 Tujuan Sistem

| No | Tujuan |
|----|--------|
| 1 | Menyimpan dan mengelola data siswa secara terpusat dan aman |
| 2 | Mengotomasi perhitungan nilai akhir berdasarkan formula baku |
| 3 | Menentukan status kelulusan siswa secara otomatis |
| 4 | Menyajikan laporan nilai dalam format yang dapat dicetak (PDF) |
| 5 | Menerapkan kontrol akses berbasis peran (Role-Based Access Control) |
| 6 | Mendemonstrasikan implementasi Pemrograman Terstruktur dan OOP |

### 2.3 Sasaran Pengguna

- Staf administrasi / Admin sekolah
- Guru mata pelajaran
- Siswa

---

## 3. Ruang Lingkup Sistem

### 3.1 Dalam Ruang Lingkup (In-Scope)

- Manajemen pengguna (Admin, Guru, Siswa)
- Autentikasi dan otorisasi berbasis peran
- CRUD data siswa dan guru
- Input nilai (Tugas, UTS, UAS) per mata pelajaran
- Perhitungan otomatis nilai akhir: `(30% × Tugas) + (30% × UTS) + (40% × UAS)`
- Penentuan status kelulusan (Lulus / Tidak Lulus, KKM ≥ 70)
- Dashboard statistik per kelas
- Laporan nilai dalam format PDF (WeasyPrint)
- Ekspor data ke Excel (openpyxl)
- Audit log aktivitas pengguna
- Visualisasi data dengan Chart.js

### 3.2 Di Luar Ruang Lingkup (Out-of-Scope)

- Manajemen jadwal pelajaran
- Sistem absensi
- Komunikasi pesan antar pengguna
- Integrasi dengan sistem eksternal (Dapodik, dll.)
- Aplikasi mobile native

---

## 4. Analisis Kebutuhan Pengguna

### 4.1 Admin

| Kebutuhan | Prioritas |
|-----------|-----------|
| Login ke sistem dengan kredensial admin | Wajib |
| Menambah, melihat, mengubah, menghapus data siswa (CRUD) | Wajib |
| Menambah, melihat, mengubah, menghapus data guru (CRUD) | Wajib |
| Mengelola akun pengguna (reset password, aktivasi) | Wajib |
| Melihat laporan nilai seluruh siswa | Wajib |
| Mencetak/mengunduh laporan PDF | Wajib |
| Melihat audit log aktivitas sistem | Penting |
| Melihat dashboard statistik akademik | Penting |
| Mengekspor data ke Excel | Penting |

### 4.2 Guru

| Kebutuhan | Prioritas |
|-----------|-----------|
| Login ke sistem dengan kredensial guru | Wajib |
| Menginput nilai siswa (Tugas, UTS, UAS) sesuai mata pelajaran yang diampu | Wajib |
| Mengubah nilai siswa sebelum dikunci | Wajib |
| Melihat rekap nilai seluruh siswa di kelasnya | Wajib |
| Memvalidasi dan mengunci nilai | Penting |
| Melihat status kelulusan siswa | Penting |
| Mencetak rekap nilai kelas | Penting |

### 4.3 Siswa

| Kebutuhan | Prioritas |
|-----------|-----------|
| Login ke sistem dengan NIS sebagai username | Wajib |
| Melihat nilai pribadi (Tugas, UTS, UAS, Nilai Akhir) | Wajib |
| Melihat status kelulusan pribadi | Wajib |
| Melihat rincian perhitungan nilai akhir | Penting |
| Mencetak/mengunduh transkrip nilai pribadi | Opsional |

---

## 5. Spesifikasi Fungsional

### 5.1 Modul Autentikasi (AUTH)

| Kode | Fitur | Deskripsi |
|------|-------|-----------|
| AUTH-01 | Login | Form login dengan username & password; validasi kredensial; redirect berdasarkan role |
| AUTH-02 | Logout | Terminasi sesi pengguna yang aman |
| AUTH-03 | Session Management | Sesi kedaluwarsa setelah 2 jam tidak aktif |
| AUTH-04 | Password Hashing | Password disimpan dengan Werkzeug `generate_password_hash` (PBKDF2-SHA256) |
| AUTH-05 | Flash Message | Notifikasi sukses/gagal login menggunakan SweetAlert2 |

### 5.2 Modul Manajemen Siswa (SISWA)

| Kode | Fitur | Deskripsi |
|------|-------|-----------|
| SISWA-01 | Tambah Siswa | Form input NIS, Nama, Kelas; NIS harus unik |
| SISWA-02 | Lihat Daftar Siswa | Tabel dengan DataTables (sorting, search, pagination) |
| SISWA-03 | Edit Data Siswa | Ubah nama dan kelas; NIS tidak dapat diubah |
| SISWA-04 | Hapus Siswa | Soft delete dengan konfirmasi SweetAlert2 |
| SISWA-05 | Profil Siswa | Halaman detail siswa dengan riwayat nilai |

### 5.3 Modul Manajemen Guru (GURU)

| Kode | Fitur | Deskripsi |
|------|-------|-----------|
| GURU-01 | Tambah Guru | Form input ID Guru, Nama Guru, Mata Pelajaran |
| GURU-02 | Lihat Daftar Guru | Tabel DataTables dengan filter mata pelajaran |
| GURU-03 | Edit Data Guru | Ubah nama dan mata pelajaran |
| GURU-04 | Hapus Guru | Soft delete dengan validasi ketergantungan data nilai |

### 5.4 Modul Nilai (NILAI)

| Kode | Fitur | Deskripsi |
|------|-------|-----------|
| NILAI-01 | Input Nilai | Form input Nilai Tugas, UTS, UAS; rentang valid 0–100 |
| NILAI-02 | Validasi Nilai | Server-side & client-side validation; nilai di luar rentang ditolak |
| NILAI-03 | Hitung Nilai Akhir | Otomatis: `(0.30 × Tugas) + (0.30 × UTS) + (0.40 × UAS)` |
| NILAI-04 | Penentuan Status | Lulus jika Nilai Akhir ≥ 70; Tidak Lulus jika < 70 |
| NILAI-05 | Edit Nilai | Ubah nilai selama belum dikunci oleh guru |
| NILAI-06 | Kunci Nilai | Guru mengunci nilai agar tidak dapat diubah kembali |
| NILAI-07 | Rekap Nilai | Tampilan tabel rekap nilai satu kelas |

### 5.5 Modul Laporan (LAPORAN)

| Kode | Fitur | Deskripsi |
|------|-------|-----------|
| LAPORAN-01 | Laporan Per Kelas | Cetak/unduh PDF rekap nilai seluruh siswa satu kelas |
| LAPORAN-02 | Transkrip Siswa | PDF nilai pribadi siswa (1 halaman) |
| LAPORAN-03 | Ekspor Excel | Ekspor data nilai ke .xlsx menggunakan openpyxl |
| LAPORAN-04 | Dashboard Chart | Grafik distribusi nilai kelas dengan Chart.js |
| LAPORAN-05 | Statistik | Rata-rata kelas, nilai tertinggi/terendah, persentase kelulusan |

### 5.6 Modul Dashboard

| Kode | Fitur | Deskripsi |
|------|-------|-----------|
| DASH-01 | Dashboard Admin | Ringkasan: total siswa, guru, persentase kelulusan, chart distribusi |
| DASH-02 | Dashboard Guru | Rekap kelas yang diampu, status input nilai |
| DASH-03 | Dashboard Siswa | Nilai pribadi, status kelulusan, grafik nilai per komponen |

### 5.7 Modul Audit Log

| Kode | Fitur | Deskripsi |
|------|-------|-----------|
| AUDIT-01 | Log Aktivitas | Catat semua aksi CRUD beserta timestamp, user, dan IP address |
| AUDIT-02 | Lihat Log | Admin dapat melihat riwayat aktivitas sistem |

---

## 6. Spesifikasi Non-Fungsional

| Kategori | Ketentuan |
|----------|-----------|
| **Performa** | Halaman utama load < 3 detik; query database < 1 detik untuk data ≤ 1000 siswa |
| **Keamanan** | Password di-hash (PBKDF2-SHA256); CSRF protection via Flask-WTF; SQL Injection prevention via SQLAlchemy ORM; XSS protection via Jinja2 auto-escape |
| **Reliabilitas** | Sistem dapat menangani 50 pengguna konkuren |
| **Usability** | Antarmuka responsif (mobile-friendly via Bootstrap 5.3); waktu belajar pengguna baru < 30 menit |
| **Maintainability** | Kode mengikuti PEP 8; komentar pada setiap fungsi utama; dokumentasi README.md |
| **Skalabilitas** | Arsitektur modular (Blueprint); mudah ditambah modul baru |
| **Kompatibilitas** | Browser: Chrome 100+, Firefox 100+, Edge 100+; OS: Windows 10+, Linux |
| **Aksesibilitas** | Mendukung navigasi keyboard; label form lengkap |

---

## 7. Arsitektur & Tech Stack

### 7.1 Tech Stack Utama

| Layer | Teknologi | Versi | Keterangan |
|-------|-----------|-------|------------|
| **Language** | Python | 3.12 | Bahasa pemrograman utama |
| **Backend** | Flask | 3.x | Web framework micro |
| **ORM** | SQLAlchemy | 2.x | Database abstraction layer |
| **Migration** | Flask-Migrate | 4.x | Database schema versioning (Alembic) |
| **Authentication** | Flask-Login | 0.6.x | Session management & login |
| **Form Validation** | Flask-WTF | 1.x | WTForms + CSRF protection |
| **Database** | MySQL | 8.x | RDBMS production-ready |
| **Frontend** | HTML5 | — | Markup |
| **Styling** | Bootstrap | 5.3 | CSS framework responsif |
| **Template** | Jinja2 | 3.x | Server-side rendering |
| **JavaScript** | Vanilla JS | ES6+ | Logika frontend |
| **Table** | DataTables | 1.13 | Tabel interaktif (sorting, search, pagination) |
| **Alert** | SweetAlert2 | 11.x | Dialog konfirmasi & notifikasi |
| **Icons** | Bootstrap Icons | 1.11 | Icon library |
| **Charts** | Chart.js | 4.x | Visualisasi data |
| **PDF** | WeasyPrint | 62.x | Generate laporan PDF |
| **Excel** | openpyxl | 3.x | Ekspor data ke .xlsx *(tambahan)* |
| **Password** | Werkzeug | 3.x | Password hashing (sudah termasuk Flask) |
| **Testing** | Pytest | 8.x | Unit & integration testing |
| **Test Client** | Flask Testing | — | Testing HTTP request Flask |
| **Env Config** | python-dotenv | 1.x | Manajemen environment variable |
| **IDE** | VS Code | Latest | Editor utama |
| **VCS** | Git + GitHub | — | Version control |

### 7.2 Arsitektur Aplikasi

```
sipns/
├── app/
│   ├── __init__.py          # Application factory
│   ├── config.py            # Konfigurasi (Dev, Prod, Test)
│   ├── models/              # OOP: Model SQLAlchemy
│   │   ├── __init__.py
│   │   ├── user.py          # class User
│   │   ├── siswa.py         # class Siswa
│   │   ├── guru.py          # class Guru
│   │   ├── nilai.py         # class Nilai
│   │   └── audit_log.py     # class AuditLog
│   ├── blueprints/          # Modular routing
│   │   ├── auth/            # Blueprint autentikasi
│   │   ├── admin/           # Blueprint admin
│   │   ├── guru/            # Blueprint guru
│   │   ├── siswa/           # Blueprint siswa
│   │   └── laporan/         # Blueprint laporan
│   ├── services/            # Pemrograman Terstruktur: fungsi logika bisnis
│   │   ├── nilai_service.py # Kalkulasi & validasi nilai
│   │   ├── laporan_service.py # Generate laporan PDF/Excel
│   │   └── audit_service.py # Logging audit
│   ├── forms/               # WTForms
│   │   ├── auth_forms.py
│   │   ├── siswa_forms.py
│   │   ├── guru_forms.py
│   │   └── nilai_forms.py
│   ├── templates/           # Jinja2 templates
│   │   ├── base.html
│   │   ├── auth/
│   │   ├── admin/
│   │   ├── guru/
│   │   ├── siswa/
│   │   └── laporan/
│   └── static/              # Assets statis
│       ├── css/
│       ├── js/
│       └── img/
├── migrations/              # Flask-Migrate files
├── tests/                   # Pytest test suite
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_nilai.py
│   └── test_laporan.py
├── .env                     # Environment variables (tidak di-commit)
├── .env.example
├── .gitignore
├── requirements.txt
├── run.py                   # Entry point
└── README.md
```

### 7.3 Pola Arsitektur

- **Application Factory Pattern** — `create_app()` untuk fleksibilitas konfigurasi
- **Blueprint Pattern** — Modularisasi routing berdasarkan fitur/role
- **Service Layer Pattern** — Logika bisnis dipisahkan dari route handler
- **Repository Pattern** (via SQLAlchemy) — Abstraksi akses data

---

## 8. Rancangan Database

### 8.1 ERD (Entity Relationship Diagram)

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
                       │ created_at       │       ┌──────────────┐
       │               │ updated_at       │       │    guru      │
       │               └──────────────────┘       ├──────────────┤
       │                        ▲                 │ id (PK)      │
       └────────────────────────┘────────────────►│ id_guru (UNQ)│
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

### 8.2 Definisi Tabel

#### Tabel: `users`

| Kolom | Tipe | Constraint | Keterangan |
|-------|------|------------|------------|
| id | INT | PK, AUTO_INCREMENT | Primary key |
| username | VARCHAR(50) | UNIQUE, NOT NULL | Username login |
| password_hash | VARCHAR(255) | NOT NULL | Hash password (PBKDF2) |
| role | ENUM('admin','guru','siswa') | NOT NULL | Peran pengguna |
| is_active | BOOLEAN | DEFAULT TRUE | Status akun aktif |
| siswa_id | INT | FK → siswa.id, NULL | Relasi ke data siswa |
| guru_id | INT | FK → guru.id, NULL | Relasi ke data guru |
| created_at | DATETIME | DEFAULT NOW() | Waktu dibuat |
| updated_at | DATETIME | ON UPDATE NOW() | Waktu diperbarui |

#### Tabel: `siswa`

| Kolom | Tipe | Constraint | Keterangan |
|-------|------|------------|------------|
| id | INT | PK, AUTO_INCREMENT | Primary key |
| nis | VARCHAR(20) | UNIQUE, NOT NULL | Nomor Induk Siswa |
| nama | VARCHAR(100) | NOT NULL | Nama lengkap siswa |
| kelas | VARCHAR(20) | NOT NULL | Kelas (contoh: X-IPA-1) |
| created_at | DATETIME | DEFAULT NOW() | Waktu dibuat |
| updated_at | DATETIME | ON UPDATE NOW() | Waktu diperbarui |
| deleted_at | DATETIME | NULL | Soft delete timestamp |

#### Tabel: `guru`

| Kolom | Tipe | Constraint | Keterangan |
|-------|------|------------|------------|
| id | INT | PK, AUTO_INCREMENT | Primary key |
| id_guru | VARCHAR(20) | UNIQUE, NOT NULL | ID Guru |
| nama_guru | VARCHAR(100) | NOT NULL | Nama lengkap guru |
| mata_pelajaran | VARCHAR(100) | NOT NULL | Mata pelajaran yang diampu |
| created_at | DATETIME | DEFAULT NOW() | Waktu dibuat |
| updated_at | DATETIME | ON UPDATE NOW() | Waktu diperbarui |
| deleted_at | DATETIME | NULL | Soft delete timestamp |

#### Tabel: `nilai`

| Kolom | Tipe | Constraint | Keterangan |
|-------|------|------------|------------|
| id | INT | PK, AUTO_INCREMENT | Primary key |
| siswa_id | INT | FK → siswa.id, NOT NULL | Relasi ke siswa |
| guru_id | INT | FK → guru.id, NOT NULL | Guru penginput |
| mata_pelajaran | VARCHAR(100) | NOT NULL | Nama mata pelajaran |
| nilai_tugas | DECIMAL(5,2) | NOT NULL, CHECK(0-100) | Nilai tugas |
| nilai_uts | DECIMAL(5,2) | NOT NULL, CHECK(0-100) | Nilai UTS |
| nilai_uas | DECIMAL(5,2) | NOT NULL, CHECK(0-100) | Nilai UAS |
| nilai_akhir | DECIMAL(5,2) | NOT NULL | Hasil kalkulasi otomatis |
| status_lulus | BOOLEAN | NOT NULL | TRUE = Lulus, FALSE = Tidak Lulus |
| is_locked | BOOLEAN | DEFAULT FALSE | Status kunci nilai |
| created_at | DATETIME | DEFAULT NOW() | Waktu input |
| updated_at | DATETIME | ON UPDATE NOW() | Waktu pembaruan |

#### Tabel: `audit_log`

| Kolom | Tipe | Constraint | Keterangan |
|-------|------|------------|------------|
| id | INT | PK, AUTO_INCREMENT | Primary key |
| user_id | INT | FK → users.id | Pengguna yang beraksi |
| action | VARCHAR(50) | NOT NULL | Jenis aksi |
| table_name | VARCHAR(50) | NOT NULL | Tabel yang terpengaruh |
| record_id | INT | NULL | ID record yang diubah |
| description | TEXT | NULL | Deskripsi aksi |
| ip_address | VARCHAR(45) | NULL | IP pengguna |
| created_at | DATETIME | DEFAULT NOW() | Waktu aksi |

### 8.3 Index

```sql
-- Performance index
CREATE INDEX idx_nilai_siswa ON nilai(siswa_id);
CREATE INDEX idx_nilai_guru ON nilai(guru_id);
CREATE INDEX idx_nilai_mapel ON nilai(mata_pelajaran);
CREATE INDEX idx_siswa_kelas ON siswa(kelas);
CREATE INDEX idx_audit_user ON audit_log(user_id);
CREATE INDEX idx_audit_created ON audit_log(created_at);
```

---

## 9. Rancangan Antarmuka (UI)

### 9.1 Daftar Halaman

| Kode | Halaman | Role Akses | URL |
|------|---------|------------|-----|
| UI-01 | Halaman Login | Semua | `/auth/login` |
| UI-02 | Dashboard Admin | Admin | `/admin/dashboard` |
| UI-03 | Dashboard Guru | Guru | `/guru/dashboard` |
| UI-04 | Dashboard Siswa | Siswa | `/siswa/dashboard` |
| UI-05 | Daftar Siswa | Admin | `/admin/siswa` |
| UI-06 | Form Tambah/Edit Siswa | Admin | `/admin/siswa/tambah` |
| UI-07 | Profil Siswa | Admin, Guru | `/admin/siswa/<id>` |
| UI-08 | Daftar Guru | Admin | `/admin/guru` |
| UI-09 | Form Tambah/Edit Guru | Admin | `/admin/guru/tambah` |
| UI-10 | Input Nilai | Guru | `/guru/nilai/input` |
| UI-11 | Rekap Nilai Kelas | Guru, Admin | `/guru/nilai/rekap` |
| UI-12 | Nilai Pribadi Siswa | Siswa | `/siswa/nilai` |
| UI-13 | Laporan PDF | Admin, Guru | `/laporan/pdf/<kelas>` |
| UI-14 | Ekspor Excel | Admin | `/laporan/excel` |
| UI-15 | Audit Log | Admin | `/admin/audit` |
| UI-16 | Manajemen User | Admin | `/admin/users` |

### 9.2 Deskripsi Komponen UI

#### Navigasi Global (Navbar)
- Logo/nama sistem kiri
- Menu navigasi kontekstual (berbeda per role)
- Info pengguna + tombol logout kanan
- Responsif (hamburger menu mobile)

#### Sidebar (Admin/Guru)
- Menu hierarkis per modul
- Indikator halaman aktif
- Collapsible di layar kecil

#### Halaman Login
- Card terpusat dengan logo sekolah
- Field: Username, Password (dengan toggle show/hide)
- Tombol Login dengan loading state
- Flash message error (SweetAlert2 toast)

#### Tabel Data (DataTables)
- Search box global
- Sorting per kolom
- Pagination (10/25/50/All per halaman)
- Tombol aksi (Edit/Hapus) per baris
- Badge status (Lulus/Tidak Lulus) berwarna

#### Form Input Nilai
- Dropdown pemilih siswa & mata pelajaran
- Field angka dengan validasi real-time
- Preview kalkulasi nilai akhir live (JavaScript)
- Indikator status lulus/tidak lulus live

#### Dashboard Chart
- Bar chart: distribusi nilai per kelas
- Doughnut chart: persentase lulus/tidak lulus
- Card statistik: rata-rata, tertinggi, terendah

---

## 10. Alur Kerja Sistem (Flowchart / UML)

### 10.1 Alur Login

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
[Validasi Form?] ──TIDAK──► [Tampilkan Error Validasi]
   │                                    │
   YA                                   └──► [Kembali ke Form]
   │
   ▼
[Cek Kredensial di DB]
   │
   ├── GAGAL ──► [Flash: "Kredensial salah"] ──► [Kembali ke Form]
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

### 10.2 Alur Input & Kalkulasi Nilai

```
[Guru: Halaman Input Nilai]
   │
   ▼
[Pilih Siswa & Mata Pelajaran]
   │
   ▼
[Input Nilai Tugas, UTS, UAS]
   │
   ▼
[Validasi Client-side]
   │── GAGAL ──► [Tampilkan error inline]
   │
   YA ──► [Preview Nilai Akhir Live]
   │
   ▼
[Submit Form]
   │
   ▼
[Validasi Server-side]
   │── GAGAL ──► [Return JSON error 422]
   │
   YA
   │
   ▼
[Hitung Nilai Akhir]
nilai_akhir = (0.30 × tugas) + (0.30 × uts) + (0.40 × uas)
   │
   ▼
[Tentukan Status]
nilai_akhir >= 70 ? Lulus : Tidak Lulus
   │
   ▼
[Simpan ke Database]
   │
   ▼
[Catat Audit Log]
   │
   ▼
[SweetAlert2: "Nilai berhasil disimpan"]
```

### 10.3 Use Case Diagram

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

### 10.4 Class Diagram (OOP)

```
┌──────────────────────────┐
│         User             │
├──────────────────────────┤
│ - id: int                │
│ - username: str          │
│ - password_hash: str     │
│ - role: str              │
│ - is_active: bool        │
├──────────────────────────┤
│ + set_password(pwd)      │
│ + check_password(pwd)    │
│ + is_admin(): bool       │
│ + is_guru(): bool        │
│ + is_siswa(): bool       │
│ + get_id(): str          │  ← Flask-Login mixin
└──────────────────────────┘
           ▲
           │ inherits
    ┌──────┴──────┐
    │             │
┌───────┐   ┌──────────┐
│ Siswa │   │   Guru   │
├───────┤   ├──────────┤
│- nis  │   │- id_guru │
│- nama │   │- nama_   │
│- kelas│   │  guru    │
├───────┤   │- mata_   │
│+to_   │   │  pelajar │
│ dict()│   ├──────────┤
│+nilai_│   │+get_mata_│
│ akhir │   │ pelajaran│
│ _all()│   └──────────┘
└───────┘
    │ 1         * │
    └─────────────┘
            │
        ┌───────┐
        │ Nilai │
        ├───────┤
        │- siswa_id     │
        │- guru_id      │
        │- mata_pelajar │
        │- nilai_tugas  │
        │- nilai_uts    │
        │- nilai_uas    │
        │- nilai_akhir  │
        │- status_lulus │
        │- is_locked    │
        ├───────────────┤
        │+ hitung_nilai_akhir()    │
        │+ tentukan_status_lulus() │
        │+ lock()                  │
        │+ to_dict()               │
        └──────────────────────────┘
```

---

## 11. Implementasi Pemrograman Terstruktur

Minimal 3 fungsi/prosedur yang diimplementasikan di `app/services/`:

### Fungsi 1: `hitung_nilai_akhir(tugas, uts, uas)`

```python
# app/services/nilai_service.py

def hitung_nilai_akhir(nilai_tugas: float, nilai_uts: float, nilai_uas: float) -> float:
    """
    Menghitung nilai akhir siswa berdasarkan bobot komponen nilai.
    
    Formula: (30% × Tugas) + (30% × UTS) + (40% × UAS)
    
    Args:
        nilai_tugas (float): Nilai tugas harian (0-100)
        nilai_uts (float): Nilai Ujian Tengah Semester (0-100)
        nilai_uas (float): Nilai Ujian Akhir Semester (0-100)
    
    Returns:
        float: Nilai akhir dibulatkan 2 desimal
    
    Raises:
        ValueError: Jika salah satu nilai di luar rentang 0-100
    """
    validasi_rentang_nilai(nilai_tugas, "Tugas")
    validasi_rentang_nilai(nilai_uts, "UTS")
    validasi_rentang_nilai(nilai_uas, "UAS")
    
    nilai_akhir = (0.30 * nilai_tugas) + (0.30 * nilai_uts) + (0.40 * nilai_uas)
    return round(nilai_akhir, 2)
```

### Fungsi 2: `validasi_rentang_nilai(nilai, label)`

```python
def validasi_rentang_nilai(nilai: float, label: str = "Nilai") -> bool:
    """
    Memvalidasi apakah nilai berada dalam rentang valid 0–100.
    
    Args:
        nilai (float): Nilai yang akan divalidasi
        label (str): Label komponen nilai untuk pesan error
    
    Returns:
        bool: True jika valid
    
    Raises:
        ValueError: Jika nilai di luar rentang 0-100 atau bukan numerik
    """
    if not isinstance(nilai, (int, float)):
        raise ValueError(f"{label} harus berupa angka.")
    if not (0 <= nilai <= 100):
        raise ValueError(f"{label} harus berada di antara 0 dan 100. Nilai '{nilai}' tidak valid.")
    return True
```

### Fungsi 3: `tentukan_status_kelulusan(nilai_akhir, kkm=70)`

```python
def tentukan_status_kelulusan(nilai_akhir: float, kkm: float = 70.0) -> dict:
    """
    Menentukan status kelulusan siswa berdasarkan nilai akhir dan KKM.
    
    Args:
        nilai_akhir (float): Nilai akhir hasil kalkulasi
        kkm (float): Kriteria Ketuntasan Minimal, default 70
    
    Returns:
        dict: {
            'lulus': bool,
            'label': str ('Lulus' | 'Tidak Lulus'),
            'badge_class': str (Bootstrap badge class),
            'selisih': float
        }
    """
    lulus = nilai_akhir >= kkm
    return {
        'lulus': lulus,
        'label': 'Lulus' if lulus else 'Tidak Lulus',
        'badge_class': 'bg-success' if lulus else 'bg-danger',
        'selisih': round(nilai_akhir - kkm, 2)
    }
```

### Fungsi 4 (Tambahan): `generate_laporan_pdf(kelas, template)`

```python
def generate_laporan_pdf(kelas: str, template: str = 'laporan/rekap_kelas.html') -> bytes:
    """
    Menghasilkan file PDF laporan rekap nilai siswa untuk satu kelas.
    
    Args:
        kelas (str): Nama kelas yang akan dicetak
        template (str): Path template Jinja2 untuk PDF
    
    Returns:
        bytes: Konten file PDF dalam format bytes
    """
    from app.models.nilai import Nilai
    from app.models.siswa import Siswa
    from flask import render_template
    import weasyprint

    data_nilai = (
        Nilai.query
        .join(Siswa)
        .filter(Siswa.kelas == kelas, Siswa.deleted_at.is_(None))
        .order_by(Siswa.nama)
        .all()
    )
    
    statistik = hitung_statistik_kelas(data_nilai)
    html_content = render_template(template, data=data_nilai, statistik=statistik, kelas=kelas)
    
    return weasyprint.HTML(string=html_content).write_pdf()
```

### Fungsi 5 (Tambahan): `hitung_statistik_kelas(data_nilai)`

```python
def hitung_statistik_kelas(data_nilai: list) -> dict:
    """
    Menghitung statistik agregat nilai untuk satu kelas/kelompok.
    
    Args:
        data_nilai (list): List objek Nilai
    
    Returns:
        dict: Statistik meliputi rata-rata, tertinggi, terendah, dan persentase lulus
    """
    if not data_nilai:
        return {'rata_rata': 0, 'tertinggi': 0, 'terendah': 0, 'persen_lulus': 0, 'total': 0}
    
    nilai_list = [n.nilai_akhir for n in data_nilai]
    lulus_count = sum(1 for n in data_nilai if n.status_lulus)
    
    return {
        'total': len(nilai_list),
        'rata_rata': round(sum(nilai_list) / len(nilai_list), 2),
        'tertinggi': max(nilai_list),
        'terendah': min(nilai_list),
        'jumlah_lulus': lulus_count,
        'jumlah_tidak_lulus': len(nilai_list) - lulus_count,
        'persen_lulus': round((lulus_count / len(nilai_list)) * 100, 1)
    }
```

---

## 12. Implementasi OOP

### Class 1: `Siswa` (Model SQLAlchemy)

```python
# app/models/siswa.py

from app import db
from datetime import datetime

class Siswa(db.Model):
    """
    Model OOP merepresentasikan entitas Siswa dalam sistem.
    
    Attributes:
        id (int): Primary key
        nis (str): Nomor Induk Siswa, unik
        nama (str): Nama lengkap siswa
        kelas (str): Kelas siswa
        created_at (datetime): Timestamp pembuatan record
        updated_at (datetime): Timestamp pembaruan record
        deleted_at (datetime): Soft delete timestamp
    """
    
    __tablename__ = 'siswa'
    
    id = db.Column(db.Integer, primary_key=True)
    nis = db.Column(db.String(20), unique=True, nullable=False, index=True)
    nama = db.Column(db.String(100), nullable=False)
    kelas = db.Column(db.String(20), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    # Relasi
    nilai = db.relationship('Nilai', backref='siswa', lazy='dynamic',
                            foreign_keys='Nilai.siswa_id')
    user = db.relationship('User', backref='siswa', uselist=False,
                           foreign_keys='User.siswa_id')
    
    def __repr__(self):
        return f'<Siswa {self.nis}: {self.nama}>'
    
    def nilai_akhir_all(self) -> list:
        """Mengambil semua nilai akhir siswa lintas mata pelajaran."""
        return [n.nilai_akhir for n in self.nilai if n.nilai_akhir is not None]
    
    def rata_rata_nilai(self) -> float:
        """Menghitung rata-rata nilai akhir siswa dari semua mata pelajaran."""
        nilai_list = self.nilai_akhir_all()
        return round(sum(nilai_list) / len(nilai_list), 2) if nilai_list else 0.0
    
    def status_kelulusan_global(self) -> str:
        """
        Menentukan status kelulusan siswa secara global (semua mapel lulus).
        Returns 'Lulus' jika semua mata pelajaran lulus, sebaliknya 'Tidak Lulus'.
        """
        nilai_records = self.nilai.filter_by(is_locked=True).all()
        if not nilai_records:
            return 'Belum Ada Nilai'
        return 'Lulus' if all(n.status_lulus for n in nilai_records) else 'Tidak Lulus'
    
    def soft_delete(self):
        """Melakukan soft delete dengan menandai deleted_at."""
        self.deleted_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Mengkonversi objek Siswa ke dictionary untuk JSON response."""
        return {
            'id': self.id,
            'nis': self.nis,
            'nama': self.nama,
            'kelas': self.kelas,
            'rata_rata': self.rata_rata_nilai(),
            'status': self.status_kelulusan_global(),
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def cari_by_nis(cls, nis: str):
        """Mencari siswa berdasarkan NIS (class method)."""
        return cls.query.filter_by(nis=nis, deleted_at=None).first()
    
    @classmethod
    def daftar_kelas(cls) -> list:
        """Mengambil daftar kelas unik yang tersedia."""
        result = db.session.query(cls.kelas).filter(
            cls.deleted_at.is_(None)
        ).distinct().order_by(cls.kelas).all()
        return [r[0] for r in result]
```

### Class 2: `Nilai` (Model SQLAlchemy)

```python
# app/models/nilai.py

from app import db
from datetime import datetime
from app.services.nilai_service import hitung_nilai_akhir, tentukan_status_kelulusan

class Nilai(db.Model):
    """
    Model OOP merepresentasikan entitas Nilai dalam sistem.
    Mengintegrasikan pemrograman terstruktur (fungsi kalkulasi) ke dalam OOP.
    
    Attributes:
        id (int): Primary key
        siswa_id (int): FK ke tabel siswa
        guru_id (int): FK ke tabel guru
        mata_pelajaran (str): Nama mata pelajaran
        nilai_tugas (Decimal): Nilai tugas harian (0-100)
        nilai_uts (Decimal): Nilai UTS (0-100)
        nilai_uas (Decimal): Nilai UAS (0-100)
        nilai_akhir (Decimal): Hasil kalkulasi otomatis
        status_lulus (bool): True jika lulus (nilai_akhir >= 70)
        is_locked (bool): Status kunci nilai oleh guru
    """
    
    __tablename__ = 'nilai'
    
    id = db.Column(db.Integer, primary_key=True)
    siswa_id = db.Column(db.Integer, db.ForeignKey('siswa.id'), nullable=False)
    guru_id = db.Column(db.Integer, db.ForeignKey('guru.id'), nullable=False)
    mata_pelajaran = db.Column(db.String(100), nullable=False)
    nilai_tugas = db.Column(db.Numeric(5, 2), nullable=False)
    nilai_uts = db.Column(db.Numeric(5, 2), nullable=False)
    nilai_uas = db.Column(db.Numeric(5, 2), nullable=False)
    nilai_akhir = db.Column(db.Numeric(5, 2), nullable=True)
    status_lulus = db.Column(db.Boolean, nullable=True)
    is_locked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Nilai siswa_id={self.siswa_id} mapel={self.mata_pelajaran} akhir={self.nilai_akhir}>'
    
    def hitung_dan_simpan(self):
        """
        Memanggil fungsi terstruktur untuk kalkulasi nilai akhir dan
        status kelulusan, kemudian menyimpan hasilnya ke atribut objek.
        Integrasi OOP + Pemrograman Terstruktur.
        """
        # Memanggil fungsi terstruktur dari nilai_service
        self.nilai_akhir = hitung_nilai_akhir(
            float(self.nilai_tugas),
            float(self.nilai_uts),
            float(self.nilai_uas)
        )
        status = tentukan_status_kelulusan(float(self.nilai_akhir))
        self.status_lulus = status['lulus']
    
    def lock(self):
        """Mengunci nilai sehingga tidak dapat diubah kembali."""
        if not self.is_locked:
            self.is_locked = True
    
    def unlock(self):
        """Membuka kunci nilai (hanya admin)."""
        self.is_locked = False
    
    def get_detail_kalkulasi(self) -> dict:
        """Mengembalikan rincian perhitungan nilai akhir untuk ditampilkan."""
        return {
            'tugas': {'nilai': float(self.nilai_tugas), 'bobot': 30, 'kontribusi': round(float(self.nilai_tugas) * 0.30, 2)},
            'uts': {'nilai': float(self.nilai_uts), 'bobot': 30, 'kontribusi': round(float(self.nilai_uts) * 0.30, 2)},
            'uas': {'nilai': float(self.nilai_uas), 'bobot': 40, 'kontribusi': round(float(self.nilai_uas) * 0.40, 2)},
            'nilai_akhir': float(self.nilai_akhir),
            'status_lulus': self.status_lulus,
            'kkm': 70
        }
    
    def to_dict(self) -> dict:
        """Mengkonversi objek Nilai ke dictionary untuk JSON response."""
        return {
            'id': self.id,
            'mata_pelajaran': self.mata_pelajaran,
            'nilai_tugas': float(self.nilai_tugas),
            'nilai_uts': float(self.nilai_uts),
            'nilai_uas': float(self.nilai_uas),
            'nilai_akhir': float(self.nilai_akhir) if self.nilai_akhir else None,
            'status_lulus': self.status_lulus,
            'is_locked': self.is_locked
        }
```

### Class 3 (Tambahan): `Guru` (Model SQLAlchemy)

```python
# app/models/guru.py

class Guru(db.Model):
    """Model OOP merepresentasikan entitas Guru dalam sistem."""
    
    __tablename__ = 'guru'
    
    id = db.Column(db.Integer, primary_key=True)
    id_guru = db.Column(db.String(20), unique=True, nullable=False)
    nama_guru = db.Column(db.String(100), nullable=False)
    mata_pelajaran = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    # Relasi
    nilai_diinput = db.relationship('Nilai', backref='guru', lazy='dynamic',
                                     foreign_keys='Nilai.guru_id')
    
    def get_siswa_diajar(self) -> list:
        """Mengambil daftar siswa yang pernah diberi nilai oleh guru ini."""
        from app.models.siswa import Siswa
        siswa_ids = db.session.query(Nilai.siswa_id).filter_by(
            guru_id=self.id
        ).distinct().all()
        return Siswa.query.filter(
            Siswa.id.in_([s[0] for s in siswa_ids])
        ).all()
    
    def soft_delete(self):
        self.deleted_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'id_guru': self.id_guru,
            'nama_guru': self.nama_guru,
            'mata_pelajaran': self.mata_pelajaran
        }
```

---

## 13. Rencana Pengujian

### 13.1 Strategi Pengujian

| Level | Metode | Tool |
|-------|--------|------|
| Unit Testing | Fungsi & method individual | Pytest |
| Integration Testing | Alur antar modul (route → service → DB) | Pytest + Flask Test Client |
| Functional Testing | Pengujian fitur end-to-end | Manual / Pytest |
| Regression Testing | Setelah setiap perbaikan bug | Pytest |

### 13.2 Test Case Utama

| TC-ID | Modul | Skenario | Input | Expected Output | Prioritas |
|-------|-------|----------|-------|-----------------|-----------|
| TC-01 | AUTH | Login admin valid | username: admin, pass: admin123 | Redirect ke /admin/dashboard | Wajib |
| TC-02 | AUTH | Login password salah | username: admin, pass: salah | Flash error "Kredensial salah" | Wajib |
| TC-03 | AUTH | Login dengan role siswa | NIS valid | Redirect ke /siswa/dashboard | Wajib |
| TC-04 | NILAI | Kalkulasi nilai normal | T=80, U=75, A=85 | NA = 80.5 | Wajib |
| TC-05 | NILAI | Nilai tepat KKM | T=70, U=70, A=70 | NA = 70.0, Lulus | Wajib |
| TC-06 | NILAI | Nilai di bawah KKM | T=50, U=60, A=65 | NA = 59.0, Tidak Lulus | Wajib |
| TC-07 | NILAI | Input nilai di luar rentang | T=101 | Error validasi | Wajib |
| TC-08 | NILAI | Input nilai negatif | T=-5 | Error validasi | Wajib |
| TC-09 | SISWA | Tambah siswa NIS duplikat | NIS yang sudah ada | Error: NIS sudah terdaftar | Wajib |
| TC-10 | LAPORAN | Generate PDF laporan kelas | kelas=X-IPA-1 | File PDF berhasil dibuat | Penting |
| TC-11 | DB | Koneksi database | — | Connection berhasil | Wajib |
| TC-12 | AKSES | Siswa akses halaman admin | URL: /admin/dashboard | Redirect 403/login | Wajib |

### 13.3 Formula Kalkulasi Uji

```
TC-04: NA = (0.30 × 80) + (0.30 × 75) + (0.40 × 85)
            = 24 + 22.5 + 34
            = 80.5 ✓ (Lulus, karena 80.5 ≥ 70)

TC-06: NA = (0.30 × 50) + (0.30 × 60) + (0.40 × 65)
            = 15 + 18 + 26
            = 59.0 ✓ (Tidak Lulus, karena 59.0 < 70)
```

---

## 14. Batasan Sistem

| No | Batasan |
|----|---------|
| 1 | Satu siswa hanya memiliki satu nilai per mata pelajaran |
| 2 | Nilai yang sudah dikunci oleh guru tidak dapat diubah tanpa intervensi admin |
| 3 | NIS bersifat unik dan tidak dapat diubah setelah didaftarkan |
| 4 | Sistem hanya mendukung tiga role pengguna: Admin, Guru, Siswa |
| 5 | Laporan PDF hanya tersedia per kelas, bukan lintas kelas dalam satu dokumen |
| 6 | Sistem tidak memiliki fitur reset password mandiri; harus melalui admin |
| 7 | Rentang nilai valid: 0 sampai 100 (desimal diperbolehkan) |
| 8 | KKM bersifat tetap (70) dan tidak dapat dikonfigurasi per mata pelajaran |
| 9 | Sistem menggunakan MySQL sebagai database utama; memerlukan MySQL server terinstall |
| 10 | Tidak ada notifikasi email/SMS |

---

## 15. Risiko & Mitigasi

| Risiko | Probabilitas | Dampak | Mitigasi |
|--------|-------------|--------|----------|
| Konflik versi library Python | Sedang | Tinggi | Gunakan `requirements.txt` dengan versi terkunci; virtual environment |
| WeasyPrint kesulitan rendering font | Sedang | Sedang | Gunakan font web-safe; test PDF di awal development |
| MySQL connection timeout | Rendah | Sedang | Gunakan connection pooling; set pool_recycle di SQLAlchemy |
| SQL Injection melalui form input | Rendah | Sangat Tinggi | Selalu gunakan SQLAlchemy ORM; tidak pernah raw query dari input user |
| Data nilai terhapus tidak sengaja | Rendah | Sangat Tinggi | Implementasi soft delete; audit log semua operasi DELETE |
| Performa lambat untuk data besar | Rendah | Sedang | Gunakan pagination DataTables; tambahkan database index |

---

## 16. Milestone & Timeline

| Fase | Tugas | Deliverable | Estimasi |
|------|-------|-------------|----------|
| **Fase 1** | Analisis & Perancangan (Tugas 1) | PRD.md, ERD, Wireframe, Rancangan Fungsi & Class | Minggu 1–2 |
| **Fase 2** | Setup Proyek | Struktur direktori, konfigurasi DB, env setup, init Flask | Minggu 2 |
| **Fase 3** | Implementasi Backend (Tugas 2) | Models, Services, Blueprints, Forms | Minggu 3–4 |
| **Fase 4** | Implementasi Frontend | Templates Jinja2, integrasi Bootstrap, DataTables, Chart.js | Minggu 4–5 |
| **Fase 5** | Fitur Laporan | PDF WeasyPrint, Ekspor Excel | Minggu 5 |
| **Fase 6** | Pengujian & Debugging (Tugas 3) | Test suite Pytest, bug fixes, dokumentasi | Minggu 6 |
| **Fase 7** | Dokumentasi Final | README.md, komentar kode, laporan akhir | Minggu 6 |

---

## Lampiran

### A. Contoh Data Uji (Seed Data)

```
Admin   : username=admin,       password=Admin@123
Guru    : username=guru_mat,    password=Guru@123   | Mapel: Matematika
Siswa   : NIS=2024001,          password=2024001    | Nama: Budi Santoso | Kelas: X-IPA-1

Contoh Nilai Budi di Matematika:
  Tugas : 85
  UTS   : 78
  UAS   : 82
  Nilai Akhir: (0.30×85) + (0.30×78) + (0.40×82) = 25.5 + 23.4 + 32.8 = 81.7 → LULUS
```

### B. Environment Variables (`.env.example`)

```
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=mysql+pymysql://root:@localhost:3306/sipns_dev
DATABASE_URL_TEST=mysql+pymysql://root:@localhost:3306/sipns_test
```

### C. Perintah Setup Awal

```bash
# Clone repository
git clone https://github.com/username/sipns.git && cd sipns

# Buat virtual environment
python -m venv venv && source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env  # Edit sesuai konfigurasi lokal (sesuaikan user/password MySQL)

# Buat database MySQL
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS sipns_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Inisialisasi database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Jalankan seed data
flask seed

# Jalankan aplikasi
flask run
```

---

*Dokumen ini merupakan acuan pengembangan SIPNS. Setiap perubahan signifikan terhadap spesifikasi harus didokumentasikan dalam changelog dan dikomunikasikan kepada seluruh anggota tim.*

**Versi:** 1.0.0 | **Status:** Draft | **Terakhir diperbarui:** 2025
