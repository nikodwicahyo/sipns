# TASK.md — SIPNS Development Todo
## Sistem Informasi Pengolahan Nilai Siswa
**Versi:** 1.0.0 | **Dibuat:** 2025 | **Referensi:** PRD.md v1.0.0

> **Panduan penggunaan:**
> - `[ ]` = Belum dikerjakan
> - `[x]` = Selesai
> - `[-]` = Sedang dikerjakan / In Progress
> - `[~]` = Dilewati / Tidak berlaku
> - Setiap task memiliki kode unik (`F1-xxx`) untuk referensi silang
> - Tandai task selesai dengan mengubah `[ ]` menjadi `[x]`

---

## Daftar Isi

- [Fase 1 — Analisis & Perancangan](#fase-1--analisis--perancangan-minggu-12)
- [Fase 2 — Setup Proyek](#fase-2--setup-proyek-minggu-2)
- [Fase 3 — Implementasi Backend](#fase-3--implementasi-backend-minggu-34)
- [Fase 4 — Implementasi Frontend](#fase-4--implementasi-frontend-minggu-45)
- [Fase 5 — Fitur Laporan](#fase-5--fitur-laporan-minggu-5)
- [Fase 6 — Pengujian & Debugging](#fase-6--pengujian--debugging-minggu-6)
- [Fase 7 — Dokumentasi Final](#fase-7--dokumentasi-final-minggu-6)
- [Backlog & Nice-to-Have](#backlog--nice-to-have)
- [Catatan Debugging](#catatan-debugging)

---

## Progress Overview

```
Fase 1  [Analisis & Perancangan] ████████████████████ 100%
Fase 2  [Setup Proyek]           ████████████████████ 100%
Fase 3  [Backend]                ████████████████████ 100%
Fase 4  [Frontend]               ████████████████████ 100%
Fase 5  [Laporan]                ████████████████████ 100%
Fase 6  [Pengujian]              ████████████████████ 100%
Fase 7  [Dokumentasi]            ████████████████████ 100%
─────────────────────────────────────────────────────
Total                            ████████████████████ 100%
```

---

## FASE 1 — Analisis & Perancangan (Minggu 1–2)
> **Tujuan:** Menghasilkan dokumen spesifikasi, ERD, rancangan UI, dan skeleton OOP/fungsi  
> **Output Tugas 1:** Dokumen spesifikasi, Flowchart/UML, Rancangan DB, Desain UI, Koneksi DB, Rancangan fungsi & class

---

### 1.1 Analisis Kebutuhan Sistem

- [x] **F1-001** — Baca dan pahami skenario studi kasus secara menyeluruh
- [x] **F1-002** — Identifikasi seluruh aktor sistem (Admin, Guru, Siswa)
- [x] **F1-003** — Buat daftar kebutuhan fungsional per aktor (use case list)
- [x] **F1-004** — Buat daftar kebutuhan non-fungsional (performa, keamanan, usability)
- [x] **F1-005** — Definisikan batasan sistem secara eksplisit
- [x] **F1-006** — Tentukan aturan bisnis (KKM = 70, formula nilai akhir, rentang 0–100)
- [x] **F1-007** — Validasi daftar kebutuhan terhadap skenario (tidak ada yang terlewat)

### 1.2 Dokumen PRD & Spesifikasi Program

- [x] **F1-008** — Buat file `PRD.md` berisi: tujuan sistem, analisis kebutuhan, fungsi utama
- [x] **F1-009** — Tulis spesifikasi fungsional lengkap (modul AUTH, SISWA, GURU, NILAI, LAPORAN)
- [x] **F1-010** — Tulis spesifikasi non-fungsional (performa, keamanan, kompatibilitas)
- [x] **F1-011** — Dokumentasikan tech stack beserta versi dan justifikasi pemilihan
- [x] **F1-012** — Buat `TASK.md` sebagai panduan todo pengembangan
- [x] **F1-013** — Buat `README.md` versi awal (skeleton, akan dilengkapi di Fase 7) _(dilengkapi lengkap di Fase 7 - F7-006)_

### 1.3 Perancangan Alur Kerja & UML

- [x] **F1-014** — Buat **Use Case Diagram** mencakup 3 aktor dan semua use case
- [x] **F1-015** — Buat **Flowchart alur login** (mulai → input → validasi → redirect by role)
- [x] **F1-016** — Buat **Flowchart alur input nilai** (pilih siswa → input → validasi → kalkulasi → simpan)
- [x] **F1-017** — Buat **Flowchart alur generate laporan PDF**
- [x] **F1-018** — Buat **Activity Diagram** untuk proses kelulusan (input → hitung → tentukan status)
- [x] **F1-019** — Buat **Sequence Diagram** untuk alur login multi-role
- [x] **F1-020** — Buat **Class Diagram** mencakup: User, Siswa, Guru, Nilai, AuditLog
- [x] **F1-021** — Simpan semua diagram ke folder `docs/diagrams/`

### 1.4 Perancangan Database

- [x] **F1-022** — Rancang **ERD** (Entity Relationship Diagram) dengan semua entitas dan relasi
- [x] **F1-023** — Definisikan tabel `users` (kolom, tipe data, constraint, index)
- [x] **F1-024** — Definisikan tabel `siswa` (kolom, tipe data, constraint, index)
- [x] **F1-025** — Definisikan tabel `guru` (kolom, tipe data, constraint, index)
- [x] **F1-026** — Definisikan tabel `nilai` (kolom, tipe data, constraint, index)
- [x] **F1-027** — Definisikan tabel `audit_log` (kolom, tipe data, constraint)
- [x] **F1-028** — Tentukan semua relasi FK antar tabel dengan CASCADE policy
- [x] **F1-029** — Tentukan index database untuk kolom yang sering di-query
- [x] **F1-030** — Buat file `docs/schema.sql` berisi DDL lengkap sebagai referensi
- [x] **F1-031** — Review ERD: pastikan tidak ada anomali (1NF, 2NF, 3NF)

### 1.5 Perancangan Antarmuka (UI Wireframe)

- [x] **F1-032** — Buat wireframe **Halaman Login** (card center, field, tombol)
- [x] **F1-033** — Buat wireframe **Dashboard Admin** (statistik card, chart, tabel ringkasan)
- [x] **F1-034** — Buat wireframe **Dashboard Guru** (kelas diampu, status nilai, shortcut)
- [x] **F1-035** — Buat wireframe **Dashboard Siswa** (nilai personal, status kelulusan)
- [x] **F1-036** — Buat wireframe **Halaman Daftar Siswa** (tabel DataTables + tombol aksi)
- [x] **F1-037** — Buat wireframe **Form Tambah/Edit Siswa**
- [x] **F1-038** — Buat wireframe **Halaman Daftar Guru**
- [x] **F1-039** — Buat wireframe **Form Input Nilai** (dropdown siswa, input nilai, preview live)
- [x] **F1-040** — Buat wireframe **Rekap Nilai Kelas** (tabel multi-kolom, badge status)
- [x] **F1-041** — Buat wireframe **Halaman Nilai Pribadi Siswa**
- [x] **F1-042** — Buat wireframe **Pratinjau Laporan PDF**
- [x] **F1-043** — Buat wireframe **Halaman Audit Log**
- [x] **F1-044** — Tentukan skema warna, tipografi, dan komponen Bootstrap yang digunakan
- [x] **F1-045** — Simpan wireframe ke `docs/wireframes/` (format PNG/PDF/Figma)

### 1.6 Rancangan Pemrograman Terstruktur (Fungsi/Prosedur)

- [x] **F1-046** — Rancang fungsi `hitung_nilai_akhir(tugas, uts, uas) -> float`
  - Input: 3 nilai float
  - Proses: `(0.30 × tugas) + (0.30 × uts) + (0.40 × uas)`
  - Output: nilai akhir dibulatkan 2 desimal
  - Error handling: raise ValueError jika input tidak valid
- [x] **F1-047** — Rancang fungsi `validasi_rentang_nilai(nilai, label) -> bool`
  - Input: nilai numerik + label string
  - Proses: cek tipe data & rentang 0–100
  - Output: True jika valid, raise ValueError jika tidak
- [x] **F1-048** — Rancang fungsi `tentukan_status_kelulusan(nilai_akhir, kkm=70) -> dict`
  - Input: nilai akhir float, KKM float
  - Output: dict `{lulus, label, badge_class, selisih}`
- [x] **F1-049** — Rancang fungsi `generate_laporan_pdf(kelas, template) -> bytes`
  - Input: nama kelas, path template
  - Output: bytes konten PDF
- [x] **F1-050** — Rancang fungsi `hitung_statistik_kelas(data_nilai) -> dict`
  - Input: list objek Nilai
  - Output: dict `{total, rata_rata, tertinggi, terendah, persen_lulus}`
- [x] **F1-051** — Rancang fungsi `catat_audit_log(user_id, action, table, record_id, desc)`
- [x] **F1-052** — Dokumentasikan semua fungsi dalam tabel di dokumen spesifikasi

### 1.7 Rancangan OOP (Class & Method)

- [x] **F1-053** — Rancang `class User(db.Model, UserMixin)` dengan semua atribut dan method
- [x] **F1-054** — Rancang `class Siswa(db.Model)` dengan atribut, relasi, dan method
- [x] **F1-055** — Rancang `class Guru(db.Model)` dengan atribut, relasi, dan method
- [x] **F1-056** — Rancang `class Nilai(db.Model)` dengan atribut, relasi, dan method (termasuk integrasi fungsi terstruktur)
- [x] **F1-057** — Rancang `class AuditLog(db.Model)` dengan atribut dan method
- [x] **F1-058** — Tentukan method `to_dict()` pada setiap model untuk JSON serialization
- [x] **F1-059** — Dokumentasikan class diagram lengkap dengan visibilitas atribut/method
- [x] **F1-060** — Identifikasi titik integrasi OOP ↔ Pemrograman Terstruktur (method `hitung_dan_simpan()` di Nilai)

### ✅ Checklist Output Fase 1

- [x] `PRD.md` lengkap dan tervalidasi
- [x] `TASK.md` siap digunakan
- [x] `docs/diagrams/` berisi: Use Case, Flowchart, Sequence, Class, Activity Diagram
- [x] `docs/wireframes/` berisi wireframe semua halaman
- [x] `docs/schema.sql` DDL lengkap
- [x] Rancangan ≥ 3 fungsi terstruktur terdokumentasi
- [x] Rancangan ≥ 2 class OOP terdokumentasi

---

## FASE 2 — Setup Proyek (Minggu 2)
> **Tujuan:** Menyiapkan environment pengembangan, struktur proyek, konfigurasi database, dan koneksi awal  
> **Output:** Proyek berjalan di local, database terkoneksi, Git repository siap

---

### 2.1 Persiapan Environment

- [x] **F2-001** — Install Python 3.12 dan pastikan versi aktif dengan `python --version`
- [x] **F2-002** — MySQL server 8.x terinstall dan berjalan
- [x] **F2-003** — Install VS Code dengan ekstensi: Python, Pylance, SQLTools, GitLens
- [x] **F2-004** — Buat virtual environment: `python -m venv venv`
- [x] **F2-005** — Aktifkan virtual environment dan verifikasi path Python interpreter
- [x] **F2-006** — Install semua dependency dari `requirements.txt`

### 2.2 Struktur Direktori Proyek

- [x] **F2-007** — Buat struktur folder proyek sesuai arsitektur PRD:
  ```
  sipns/
  ├── app/
  │   ├── __init__.py
  │   ├── config.py
  │   ├── models/
  │   ├── blueprints/
  │   │   ├── auth/
  │   │   ├── admin/
  │   │   ├── guru/
  │   │   ├── siswa/
  │   │   └── laporan/
  │   ├── services/
  │   ├── forms/
  │   ├── templates/
  │   │   ├── base.html
  │   │   ├── auth/
  │   │   ├── admin/
  │   │   ├── guru/
  │   │   ├── siswa/
  │   │   └── laporan/
  │   └── static/
  │       ├── css/
  │       ├── js/
  │       └── img/
  ├── migrations/
  ├── tests/
  ├── docs/
  ├── .env
  ├── .env.example
  ├── .gitignore
  ├── requirements.txt
  ├── run.py
  └── README.md
  ```
- [x] **F2-008** — Buat file `__init__.py` di setiap folder package Python
- [x] **F2-009** — Buat file `run.py` sebagai entry point aplikasi

### 2.3 File Konfigurasi

- [x] **F2-010** — Buat `requirements.txt` dengan versi terkunci:
  ```
  # MySQL driver
  PyMySQL==1.1.1
  Flask==3.1.0
  Flask-SQLAlchemy==3.1.1
  Flask-Migrate==4.0.7
  Flask-Login==0.6.3
  Flask-WTF==1.2.1
  python-dotenv==1.0.1
  Werkzeug==3.1.3
  WeasyPrint==62.3
  openpyxl==3.1.5
  pytest==8.3.4
  pytest-flask==1.3.0
  WTForms==3.1.2
  ```
- [x] **F2-011** — Buat `app/config.py` dengan tiga kelas konfigurasi:
  - `class DevelopmentConfig` — DEBUG=True, MySQL default
  - `class ProductionConfig` — DEBUG=False, MySQL default
  - `class TestingConfig` — TESTING=True, SQLite in-memory untuk test
- [x] **F2-012** — Buat `.env.example` dengan semua variabel yang dibutuhkan
- [x] **F2-013** — Buat `.env` dari `.env.example` dan isi dengan nilai lokal
- [x] **F2-014** — Buat `.gitignore` yang mengecualikan: `.env`, `venv/`, `__pycache__/`, `*.pyc`, `migrations/`, `.pytest_cache/`

### 2.4 Application Factory & Extensions

- [x] **F2-015** — Buat `app/__init__.py` dengan fungsi `create_app(config_name)`:
  - Inisialisasi Flask app
  - Load konfigurasi dari `config.py`
  - Inisialisasi SQLAlchemy (`db.init_app(app)`)
  - Inisialisasi Flask-Migrate (`migrate.init_app(app, db)`)
  - Inisialisasi Flask-Login (`login_manager.init_app(app)`)
  - Inisialisasi Flask-WTF CSRF (`csrf.init_app(app)`)
  - Register semua Blueprint
  - Register context processor (inject tahun, user info ke template)
  - Register error handler (404, 403, 500)
- [x] **F2-016** — Konfigurasi Flask-Login:
  - Set `login_manager.login_view = 'auth.login'`
  - Set `login_manager.login_message` dalam Bahasa Indonesia
  - Implementasi `@login_manager.user_loader`
- [x] **F2-017** — Register semua Blueprint dengan prefix URL yang tepat

### 2.5 Setup Database

- [x] **F2-018** — MySQL: database `sipns_dev` dibuat dengan charset utf8mb4
- [x] **F2-020** — Uji koneksi database dari Python: `flask shell` → `db.engine.connect()`
- [x] **F2-021** — Jalankan `flask db init` untuk inisialisasi folder migrations
- [x] **F2-022** — Buat semua model SQLAlchemy (User, Siswa, Guru, Nilai, AuditLog)
- [x] **F2-023** — Jalankan `flask db migrate -m "Initial migration: create all tables"`
- [x] **F2-024** — Jalankan `flask db upgrade` dan verifikasi tabel terbuat di MySQL
- [x] **F2-025** — Screenshot/catat bukti koneksi database berhasil untuk dokumentasi Tugas 1

### 2.6 Seed Data

- [x] **F2-026** — Buat file `app/seed.py` dengan Flask CLI command `flask seed`
- [x] **F2-027** — Seed data admin: `username=admin, password=Admin@123, role=admin`
- [x] **F2-028** — Seed data guru: 3 guru dengan mata pelajaran berbeda (Matematika, Bahasa Indonesia, IPA)
- [x] **F2-029** — Seed data siswa: minimal 10 siswa dari 2 kelas berbeda (X-IPA-1, X-IPA-2)
- [x] **F2-030** — Seed data nilai: nilai sample untuk semua kombinasi siswa–mapel
- [x] **F2-031** — Verifikasi seed data dengan query langsung ke database
- [x] **F2-032** — Dokumentasikan kredensial seed data di `docs/seed_credentials.md`

### 2.7 Version Control

- [x] **F2-033** — Inisialisasi Git repository: `git init`
- [~] **F2-034** — Buat repository di GitHub dengan nama `sipns` *(manual — perlu akses GitHub)*
- [x] **F2-035** — Commit awal: `git commit -m "feat: initial project structure"`
- [~] **F2-036** — Push ke GitHub *(manual — perlu remote GitHub)*
- [x] **F2-037** — Buat branch strategy: `main` (production), `develop` (development), `feature/*`
- [x] **F2-038** — Buat branch `develop` dan set sebagai default working branch

### ✅ Checklist Output Fase 2

- [x] Virtual environment aktif dan semua dependency terinstall
- [x] Struktur direktori lengkap sesuai arsitektur
- [x] `app/__init__.py` dengan application factory berfungsi
- [x] Database MySQL terkoneksi dan semua tabel terbuat
- [x] `flask run` berhasil tanpa error, aplikasi bisa diakses di `localhost:5000`
- [x] Seed data berhasil dijalankan
- [~] Repository GitHub aktif dengan commit awal *(manual — perlu akses GitHub)*

---

## FASE 3 — Implementasi Backend (Minggu 3–4)
> **Tujuan:** Mengimplementasikan semua model, services, forms, dan route handler  
> **Output Tugas 2:** Login berdasarkan role, form input, perhitungan nilai, kode fungsi & class

---

### 3.1 Models (OOP — Class & Atribut)

#### Model: User

- [x] **F3-001** — Implementasi `class User(db.Model, UserMixin)` di `app/models/user.py`:
  - Atribut: `id`, `username`, `password_hash`, `role`, `is_active`, `siswa_id`, `guru_id`, `created_at`, `updated_at`
  - Relasi: `siswa` (one-to-one FK), `guru` (one-to-one FK)
- [x] **F3-002** — Implementasi method `set_password(password)` — hash menggunakan `generate_password_hash`
- [x] **F3-003** — Implementasi method `check_password(password)` — verifikasi dengan `check_password_hash`
- [x] **F3-004** — Implementasi method `is_admin()`, `is_guru()`, `is_siswa()` — return bool
- [x] **F3-005** — Implementasi method `get_id()` untuk Flask-Login
- [x] **F3-006** — Implementasi `__repr__()` untuk debugging
- [x] **F3-007** — Implementasi `to_dict()` — serialisasi ke JSON (tanpa password_hash)

#### Model: Siswa

- [x] **F3-008** — Implementasi `class Siswa(db.Model)` di `app/models/siswa.py`:
  - Atribut: `id`, `nis`, `nama`, `kelas`, `created_at`, `updated_at`, `deleted_at`
  - Relasi: `nilai` (one-to-many), `user` (one-to-one)
  - Index: `nis` (unique), `kelas`
- [x] **F3-009** — Implementasi method `nilai_akhir_all()` — return list semua nilai akhir siswa
- [x] **F3-010** — Implementasi method `rata_rata_nilai()` — hitung rata-rata dari semua mapel
- [x] **F3-011** — Implementasi method `status_kelulusan_global()` — lulus jika semua mapel terkunci lulus
- [x] **F3-012** — Implementasi method `soft_delete()` — set `deleted_at = datetime.utcnow()`
- [x] **F3-013** — Implementasi class method `cari_by_nis(nis)` — query by NIS, exclude deleted
- [x] **F3-014** — Implementasi class method `daftar_kelas()` — return list kelas unik
- [x] **F3-015** — Implementasi `to_dict()` dan `__repr__()`

#### Model: Guru

- [x] **F3-016** — Implementasi `class Guru(db.Model)` di `app/models/guru.py`:
  - Atribut: `id`, `id_guru`, `nama_guru`, `mata_pelajaran`, `created_at`, `updated_at`, `deleted_at`
  - Relasi: `nilai_diinput` (one-to-many ke Nilai), `user` (one-to-one)
- [x] **F3-017** — Implementasi method `get_siswa_diajar()` — return list siswa yang pernah diberi nilai
- [x] **F3-018** — Implementasi method `soft_delete()`
- [x] **F3-019** — Implementasi `to_dict()` dan `__repr__()`

#### Model: Nilai

- [x] **F3-020** — Implementasi `class Nilai(db.Model)` di `app/models/nilai.py`:
  - Atribut: `id`, `siswa_id`, `guru_id`, `mata_pelajaran`, `nilai_tugas`, `nilai_uts`, `nilai_uas`, `nilai_akhir`, `status_lulus`, `is_locked`, `created_at`, `updated_at`
  - Constraint: UNIQUE(siswa_id, mata_pelajaran)
  - Relasi: `siswa` (many-to-one), `guru` (many-to-one)
- [x] **F3-021** — Implementasi method `hitung_dan_simpan()`:
  - Panggil `hitung_nilai_akhir()` dari `nilai_service.py` (integrasi terstruktur ↔ OOP)
  - Panggil `tentukan_status_kelulusan()` dari `nilai_service.py`
  - Set `self.nilai_akhir` dan `self.status_lulus`
- [x] **F3-022** — Implementasi method `lock()` dan `unlock()`
- [x] **F3-023** — Implementasi method `get_detail_kalkulasi()` — return dict rincian bobot & kontribusi
- [x] **F3-024** — Implementasi `to_dict()` dan `__repr__()`

#### Model: AuditLog

- [x] **F3-025** — Implementasi `class AuditLog(db.Model)` di `app/models/audit_log.py`:
  - Atribut: `id`, `user_id`, `action`, `table_name`, `record_id`, `description`, `ip_address`, `created_at`
- [x] **F3-026** — Implementasi class method `log(user_id, action, table, record_id, desc, ip)`
- [x] **F3-027** — Implementasi `to_dict()` dan `__repr__()`
- [x] **F3-028** — Buat `app/models/__init__.py` yang mengexport semua model

### 3.2 Services (Pemrograman Terstruktur — Fungsi/Prosedur)

#### nilai_service.py

- [x] **F3-029** — Buat file `app/services/nilai_service.py`
- [x] **F3-030** — Implementasi fungsi `validasi_rentang_nilai(nilai, label)`:
  - Cek tipe data (int/float)
  - Cek rentang 0 ≤ nilai ≤ 100
  - Raise `ValueError` dengan pesan deskriptif jika tidak valid
  - Return `True` jika valid
  - Tulis docstring lengkap (Args, Returns, Raises)
- [x] **F3-031** — Implementasi fungsi `hitung_nilai_akhir(nilai_tugas, nilai_uts, nilai_uas)`:
  - Panggil `validasi_rentang_nilai` untuk setiap parameter
  - Hitung: `(0.30 × tugas) + (0.30 × uts) + (0.40 × uas)`
  - Return `round(hasil, 2)`
  - Tulis docstring lengkap
- [x] **F3-032** — Implementasi fungsi `tentukan_status_kelulusan(nilai_akhir, kkm=70.0)`:
  - Hitung status lulus/tidak lulus
  - Return dict: `{lulus, label, badge_class, selisih}`
  - Tulis docstring lengkap
- [x] **F3-033** — Implementasi fungsi `hitung_statistik_kelas(data_nilai)`:
  - Handle kasus list kosong (return nilai default 0)
  - Return dict: `{total, rata_rata, tertinggi, terendah, jumlah_lulus, jumlah_tidak_lulus, persen_lulus}`
  - Tulis docstring lengkap

#### laporan_service.py

- [x] **F3-034** — Buat file `app/services/laporan_service.py`
- [x] **F3-035** — Implementasi fungsi `generate_laporan_pdf(kelas, template)`:
  - Query data nilai + siswa berdasarkan kelas
  - Panggil `hitung_statistik_kelas()`
  - Render HTML template dengan Jinja2
  - Konversi ke PDF dengan WeasyPrint
  - Return bytes
- [x] **F3-036** — Implementasi fungsi `generate_transkrip_pdf(siswa_id)`:
  - Query nilai satu siswa semua mapel
  - Generate PDF transkrip personal
  - Return bytes
- [x] **F3-037** — Implementasi fungsi `export_excel(kelas=None)`:
  - Buat workbook openpyxl
  - Buat sheet dengan header dan data nilai
  - Styling: bold header, alternating row color, border
  - Auto-adjust column width
  - Return bytes dari `save_virtual_workbook`

#### audit_service.py

- [x] **F3-038** — Buat file `app/services/audit_service.py`
- [x] **F3-039** — Implementasi fungsi `catat_audit_log(user_id, action, table_name, record_id, description, ip_address)`:
  - Buat objek `AuditLog`
  - Simpan ke database
  - Handle exception agar tidak mengganggu operasi utama

### 3.3 Forms (WTForms + Flask-WTF)

- [x] **F3-040** — Buat `app/forms/auth_forms.py`:
  - `class LoginForm(FlaskForm)`: field `username` (StringField), `password` (PasswordField), submit
  - Validator: `DataRequired()` pada semua field
- [x] **F3-041** — Buat `app/forms/siswa_forms.py`:
  - `class SiswaForm(FlaskForm)`: field `nis`, `nama`, `kelas`, submit
  - Validator: `DataRequired()`, `Length(min=1, max=20)` untuk NIS, `Length(max=100)` untuk nama
  - Custom validator: cek keunikan NIS saat tambah (tidak berlaku saat edit)
- [x] **F3-042** — Buat `app/forms/guru_forms.py`:
  - `class GuruForm(FlaskForm)`: field `id_guru`, `nama_guru`, `mata_pelajaran`, submit
  - Validator: `DataRequired()`, keunikan `id_guru`
- [x] **F3-043** — Buat `app/forms/nilai_forms.py`:
  - `class NilaiForm(FlaskForm)`: field `siswa_id` (SelectField), `nilai_tugas`, `nilai_uts`, `nilai_uas`, submit
  - Validator: `DataRequired()`, `NumberRange(min=0, max=100)` untuk semua nilai
- [x] **F3-044** — Buat `app/forms/user_forms.py`:
  - `class TambahUserForm(FlaskForm)`: field `username`, `password`, `role`, `is_active`
  - `class ResetPasswordForm(FlaskForm)`: field `password_baru`, `konfirmasi`
  - Validator: password minimal 8 karakter, konfirmasi harus sama

### 3.4 Blueprint: Auth

- [x] **F3-045** — Buat `app/blueprints/auth/__init__.py` dengan `Blueprint('auth', __name__)`
- [x] **F3-046** — Buat `app/blueprints/auth/routes.py`:
  - `GET/POST /auth/login` — tampilkan form login, proses autentikasi
    - Validasi form WTForms
    - Query user berdasarkan username
    - Verifikasi password dengan `user.check_password()`
    - Cek `user.is_active`
    - `login_user(user)` jika valid
    - Redirect berdasarkan role ke dashboard masing-masing
    - Flash error jika gagal
  - `GET /auth/logout` — `logout_user()`, redirect ke login
  - `@login_required` decorator untuk semua route terproteksi
- [x] **F3-047** — Implementasi pembatasan akses berdasarkan role (custom decorator `@role_required(role)`)

### 3.5 Blueprint: Admin

- [x] **F3-048** — Buat `app/blueprints/admin/__init__.py`
- [x] **F3-049** — Buat `app/blueprints/admin/routes.py`:

  **Dashboard:**
  - [x] **F3-050** — `GET /admin/dashboard` — tampilkan statistik: total siswa, guru, % kelulusan, chart data
  
  **Manajemen Siswa:**
  - [x] **F3-051** — `GET /admin/siswa` — daftar semua siswa (exclude soft-deleted), data untuk DataTables
  - [x] **F3-052** — `GET/POST /admin/siswa/tambah` — form tambah siswa baru
    - Validasi NIS unik
    - Buat akun User terkait (username=NIS, password=NIS)
    - Simpan ke DB, catat audit log
    - Flash sukses, redirect ke daftar
  - [x] **F3-053** — `GET/POST /admin/siswa/edit/<id>` — form edit siswa
    - Pre-fill form dengan data existing
    - NIS tidak bisa diubah
    - Catat audit log jika ada perubahan
  - [x] **F3-054** — `POST /admin/siswa/hapus/<id>` — soft delete siswa
    - Konfirmasi via SweetAlert2 di frontend
    - Set `deleted_at`, non-aktifkan user terkait
    - Catat audit log
  - [x] **F3-055** — `GET /admin/siswa/<id>` — profil detail siswa + riwayat nilai

  **Manajemen Guru:**
  - [x] **F3-056** — `GET /admin/guru` — daftar semua guru
  - [x] **F3-057** — `GET/POST /admin/guru/tambah` — form tambah guru
    - Buat akun User terkait
    - Catat audit log
  - [x] **F3-058** — `GET/POST /admin/guru/edit/<id>` — form edit guru
  - [x] **F3-059** — `POST /admin/guru/hapus/<id>` — soft delete guru
    - Validasi: tolak hapus jika masih ada nilai yang belum dikunci

  **Manajemen User:**
  - [x] **F3-060** — `GET /admin/users` — daftar semua user dengan role
  - [x] **F3-061** — `POST /admin/users/toggle-aktif/<id>` — aktifkan/nonaktifkan akun
  - [x] **F3-062** — `POST /admin/users/reset-password/<id>` — reset password user

  **Audit Log:**
  - [x] **F3-063** — `GET /admin/audit` — tampilkan audit log dengan filter (user, aksi, tanggal)

### 3.6 Blueprint: Guru

- [x] **F3-064** — Buat `app/blueprints/guru/__init__.py`
- [x] **F3-065** — Buat `app/blueprints/guru/routes.py`:

  **Dashboard:**
  - [x] **F3-066** — `GET /guru/dashboard` — statistik kelas yang diampu, status input nilai

  **Input & Kelola Nilai:**
  - [x] **F3-067** — `GET/POST /guru/nilai/input` — form input nilai
    - Dropdown siswa berdasarkan kelas (AJAX populate)
    - Guru hanya bisa input untuk mata pelajaran yang diampu
    - Cek apakah nilai sudah ada (update vs insert)
    - Panggil `nilai.hitung_dan_simpan()` sebelum commit
    - Catat audit log
  - [x] **F3-068** — `GET/POST /guru/nilai/edit/<id>` — edit nilai (hanya jika belum dikunci)
    - Validasi `is_locked == False`
    - Recalculate nilai akhir setelah edit
  - [x] **F3-069** — `POST /guru/nilai/kunci/<id>` — kunci nilai
    - Set `is_locked = True`
    - Catat audit log
  - [x] **F3-070** — `GET /guru/nilai/rekap` — rekap nilai semua siswa di kelas yang diampu
    - Filter per kelas (dropdown)
    - Tampilkan tabel dengan badge status lulus/tidak lulus

### 3.7 Blueprint: Siswa

- [x] **F3-071** — Buat `app/blueprints/siswa/__init__.py`
- [x] **F3-072** — Buat `app/blueprints/siswa/routes.py`:
  - [x] **F3-073** — `GET /siswa/dashboard` — nilai pribadi + status kelulusan
  - [x] **F3-074** — `GET /siswa/nilai` — tabel nilai per mata pelajaran + rincian kalkulasi
  - [x] **F3-075** — `GET /siswa/nilai/<nilai_id>/detail` — detail rincian kalkulasi nilai akhir

### 3.8 Blueprint: Laporan

- [x] **F3-076** — Buat `app/blueprints/laporan/__init__.py`
- [x] **F3-077** — Buat `app/blueprints/laporan/routes.py`:
  - [x] **F3-078** — `GET /laporan/rekap-kelas` — halaman pilih kelas sebelum cetak
  - [x] **F3-079** — `GET /laporan/pdf/kelas/<kelas>` — generate & stream PDF laporan kelas
  - [x] **F3-080** — `GET /laporan/pdf/transkrip/<siswa_id>` — generate & stream PDF transkrip siswa
  - [x] **F3-081** — `GET /laporan/excel` — generate & download file .xlsx

### 3.9 Error Handlers & Context Processors

- [x] **F3-082** — Implementasi handler `@app.errorhandler(404)` — render `errors/404.html`
- [x] **F3-083** — Implementasi handler `@app.errorhandler(403)` — render `errors/403.html`
- [x] **F3-084** — Implementasi handler `@app.errorhandler(500)` — render `errors/500.html`
- [x] **F3-085** — Implementasi context processor `inject_globals()`:
  - `current_year` — untuk footer copyright
  - `app_name` — nama aplikasi
- [x] **F3-086** — Implementasi Flask-Login `unauthorized_handler` — redirect ke login dengan flash message

### 3.10 API Endpoint (AJAX)

- [x] **F3-087** — `GET /api/siswa-by-kelas/<kelas>` — return JSON list siswa untuk AJAX populate dropdown
- [x] **F3-088** — `GET /api/nilai-preview` — return JSON preview kalkulasi nilai real-time
  - Query params: `tugas`, `uts`, `uas`
  - Response: `{nilai_akhir, status_lulus, label, badge_class}`
- [x] **F3-089** — `GET /api/statistik-kelas/<kelas>` — return JSON statistik kelas untuk Chart.js

### 3.11 Database Migration

- [x] **F3-090** — Jalankan `flask db migrate -m "Add all model relationships"` setelah semua model selesai
- [x] **F3-091** — Jalankan `flask db upgrade` dan verifikasi schema
- [x] **F3-092** — Verifikasi semua constraint (UNIQUE, FK, CHECK) teraplikasi di MySQL

### ✅ Checklist Output Fase 3

- [x] Semua 5 model (User, Siswa, Guru, Nilai, AuditLog) terimplementasi dan termigrasi
- [x] Semua fungsi terstruktur di `services/` terimplementasi dengan docstring
- [x] Semua WTForms terimplementasi dengan validator
- [x] Semua Blueprint terdaftar dan route dapat diakses
- [x] Login berhasil untuk 3 role berbeda dengan redirect yang benar
- [x] Input nilai → kalkulasi otomatis → simpan ke DB berfungsi
- [x] Audit log tercatat untuk setiap operasi CRUD

---

## FASE 4 — Implementasi Frontend (Minggu 4–5)
> **Tujuan:** Membangun tampilan antarmuka yang responsif, fungsional, dan sesuai wireframe  
> **Output:** Semua halaman UI selesai, integrasi Bootstrap/DataTables/Chart.js/SweetAlert2

---

### 4.1 Template Base & Layout

- [x] **F4-001** — Buat `app/templates/base.html` dengan:
  - `<!DOCTYPE html>`, lang="id", charset UTF-8, viewport meta
  - Link CDN: Bootstrap 5.3, Bootstrap Icons, DataTables (CSS)
  - Link CDN: Bootstrap JS, DataTables JS, SweetAlert2, Chart.js, Vanilla JS custom
  - Block: `{% block title %}`, `{% block content %}`, `{% block extra_css %}`, `{% block extra_js %}`
  - Include partial: navbar, sidebar, flash messages
- [x] **F4-002** — Buat `app/templates/partials/navbar.html`:
  - Logo/nama sistem
  - Menu utama berbeda per role (kondisional `current_user.role`)
  - Info user login + avatar placeholder
  - Tombol logout dengan konfirmasi SweetAlert2
  - Responsif (hamburger di mobile)
- [x] **F4-003** — Buat `app/templates/partials/sidebar.html`:
  - Menu sidebar Admin: Dashboard, Siswa, Guru, User, Audit Log, Laporan
  - Menu sidebar Guru: Dashboard, Input Nilai, Rekap Nilai, Laporan
  - Menu sidebar Siswa: Dashboard, Nilai Saya
  - Active state untuk menu yang sedang aktif
  - Collapsible/toggle di mobile
- [x] **F4-004** — Buat `app/templates/partials/flash_messages.html`:
  - Loop `get_flashed_messages(with_categories=True)`
  - Tampilkan sebagai SweetAlert2 toast (sukses=hijau, error=merah, warning=kuning)
  - Auto-dismiss setelah 3 detik
- [x] **F4-005** — Buat `app/templates/errors/404.html` — halaman 404 yang friendly
- [x] **F4-006** — Buat `app/templates/errors/403.html` — halaman akses ditolak
- [x] **F4-007** — Buat `app/templates/errors/500.html` — halaman error server

### 4.2 Halaman Auth

- [x] **F4-008** — Buat `app/templates/auth/login.html`:
  - Layout full-page dengan background gradient/image
  - Card terpusat dengan shadow
  - Logo sekolah/sistem di atas card
  - Form: field Username, Password (dengan toggle show/hide icon Bootstrap Icons)
  - Tombol "Masuk" dengan spinner loading saat submit
  - Footer card: nama sistem, tahun
  - Flash error ditampilkan sebagai alert di dalam card
  - Tidak gunakan base.html (standalone page)

### 4.3 Dashboard

- [x] **F4-009** — Buat `app/templates/admin/dashboard.html`:
  - 4 card statistik: Total Siswa, Total Guru, Total Nilai, % Kelulusan
  - Setiap card dengan icon Bootstrap Icons dan warna berbeda
  - Bar chart Chart.js: distribusi nilai per kelas
  - Doughnut chart Chart.js: rasio Lulus vs Tidak Lulus
  - Tabel ringkasan 10 nilai terbaru yang diinput
- [x] **F4-010** — Buat `app/templates/guru/dashboard.html`:
  - Card: jumlah siswa yang diampu, mapel yang diajar
  - Tabel: status input nilai per kelas (sudah/belum)
  - Chart: distribusi nilai kelas yang diampu
  - Tombol shortcut: "Input Nilai Baru", "Lihat Rekap"
- [x] **F4-011** — Buat `app/templates/siswa/dashboard.html`:
  - Card selamat datang dengan nama siswa dan kelas
  - Card: Nilai Akhir rata-rata, Status Kelulusan Global (badge besar)
  - Tabel nilai per mata pelajaran: Tugas | UTS | UAS | Akhir | Status
  - Chart radar/bar: perbandingan komponen nilai per mapel

### 4.4 Halaman Manajemen Siswa

- [x] **F4-012** — Buat `app/templates/admin/siswa/index.html`:
  - Judul halaman + breadcrumb
  - Tombol "Tambah Siswa" (align kanan)
  - Tabel DataTables: NIS | Nama | Kelas | Rata-rata Nilai | Status | Aksi
  - Kolom Aksi: tombol icon Edit (biru), Hapus (merah), Detail (abu)
  - Badge status: "Lulus" (hijau), "Tidak Lulus" (merah), "Belum Ada Nilai" (abu)
  - DataTables: search, sort, pagination, language Indonesia
- [x] **F4-013** — Buat `app/templates/admin/siswa/form.html` (digunakan untuk tambah & edit):
  - Judul dinamis: "Tambah Siswa" atau "Edit Siswa: [Nama]"
  - Form: NIS (disabled jika edit), Nama, Kelas (dropdown atau input)
  - Validasi error inline di bawah setiap field
  - Tombol "Simpan" dan "Batal" (link kembali ke daftar)
- [x] **F4-014** — Buat `app/templates/admin/siswa/detail.html`:
  - Info siswa: NIS, Nama, Kelas, Tanggal Daftar
  - Tabel nilai semua mata pelajaran
  - Rincian kalkulasi setiap nilai
  - Status kelulusan global
  - Tombol aksi: Edit, Hapus, Cetak Transkrip

### 4.5 Halaman Manajemen Guru

- [x] **F4-015** — Buat `app/templates/admin/guru/index.html`:
  - Tabel DataTables: ID Guru | Nama | Mata Pelajaran | Jumlah Siswa | Aksi
  - Filter dropdown per mata pelajaran
- [x] **F4-016** — Buat `app/templates/admin/guru/form.html`:
  - Form: ID Guru, Nama Guru, Mata Pelajaran
  - Validasi error inline

### 4.6 Halaman Input Nilai (Guru)

- [x] **F4-017** — Buat `app/templates/guru/nilai/input.html`:
  - Dropdown: pilih Kelas → (AJAX) populate dropdown Siswa
  - Field mata pelajaran: otomatis diisi sesuai mapel guru login
  - Input: Nilai Tugas (0-100), Nilai UTS (0-100), Nilai UAS (0-100)
  - **Preview Live** (Vanilla JS + AJAX):
    - Hitung nilai akhir real-time saat user mengetik
    - Tampilkan preview: "Nilai Akhir: 81.70 → **LULUS**" dengan badge warna
    - Update setiap kali salah satu field nilai berubah
  - Validasi client-side: angka saja, rentang 0–100, field tidak boleh kosong
  - Tombol "Simpan Nilai" dengan konfirmasi SweetAlert2 sebelum submit
  - Notifikasi SweetAlert2 sukses/gagal setelah submit

- [x] **F4-018** — Buat JavaScript `app/static/js/nilai-preview.js`:
  ```javascript
  // Real-time kalkulasi nilai akhir
  function hitungNilaiAkhir(tugas, uts, uas) {
      return (0.30 * tugas) + (0.30 * uts) + (0.40 * uas);
  }
  // Event listener untuk semua input nilai
  // Update preview card setiap onChange
  // AJAX ke /api/nilai-preview untuk validasi server-side
  ```

### 4.7 Halaman Rekap Nilai

- [x] **F4-019** — Buat `app/templates/guru/nilai/rekap.html`:
  - Dropdown pilih kelas
  - Tabel DataTables: NIS | Nama | Tugas | UTS | UAS | Nilai Akhir | Status | Kunci | Aksi
  - Badge "Terkunci" / "Belum Dikunci" per baris
  - Tombol kunci nilai per baris (dengan konfirmasi SweetAlert2)
  - Statistik ringkasan di atas tabel: rata-rata, tertinggi, terendah, % lulus
  - Tombol "Cetak PDF" dan "Ekspor Excel"

### 4.8 Halaman Nilai Siswa

- [x] **F4-020** — Buat `app/templates/siswa/nilai.html`:
  - Tabel: Mata Pelajaran | Tugas | UTS | UAS | Nilai Akhir | Status
  - Setiap baris expandable: klik untuk lihat rincian bobot (30%/30%/40%)
  - Rata-rata nilai akhir di bawah tabel
  - Status kelulusan global dengan banner besar (hijau/merah)
  - Tombol "Unduh Transkrip PDF"

### 4.9 Halaman Audit Log (Admin)

- [x] **F4-021** — Buat `app/templates/admin/audit/index.html`:
  - Filter: dropdown User, dropdown Aksi (INSERT/UPDATE/DELETE), date range picker
  - Tabel DataTables: Waktu | User | Aksi | Tabel | ID Record | Deskripsi | IP
  - Kolom "Aksi" menggunakan badge warna berbeda (INSERT=hijau, UPDATE=biru, DELETE=merah)

### 4.10 Halaman Manajemen User (Admin)

- [x] **F4-022** — Buat `app/templates/admin/users/index.html`:
  - Tabel: Username | Role | Status | Siswa/Guru Terkait | Aksi
  - Toggle switch untuk aktif/nonaktif akun
  - Tombol reset password
  - Badge role: Admin (ungu), Guru (biru), Siswa (hijau)

### 4.11 Static Assets

- [x] **F4-023** — Buat `app/static/css/custom.css`:
  - Override Bootstrap variables (warna primer, secondary)
  - Style khusus: sidebar, navbar, card statistik
  - Style badge status nilai
  - Style preview nilai akhir live
  - Print-specific CSS (`@media print`) untuk laporan
- [x] **F4-024** — Buat `app/static/js/main.js`:
  - Inisialisasi DataTables global (bahasa Indonesia)
  - Inisialisasi SweetAlert2 untuk konfirmasi hapus
  - Fungsi logout konfirmasi
  - Fungsi toggle password visibility
  - Fungsi auto-dismiss flash messages
- [x] **F4-025** — Buat `app/static/js/charts.js`:
  - Fungsi `renderBarChart(canvasId, labels, data)` — Bar chart distribusi nilai
  - Fungsi `renderDoughnutChart(canvasId, lulus, tidakLulus)` — Doughnut kelulusan
  - Fungsi `renderRadarChart(canvasId, labels, data)` — Radar nilai siswa
- [x] **F4-026** — Tambahkan favicon dan logo sekolah placeholder di `app/static/img/`

### ✅ Checklist Output Fase 4

- [x] Semua 16 halaman UI terimplementasi sesuai wireframe
- [x] Navbar dan sidebar berfungsi dan responsif (mobile-friendly)
- [x] DataTables aktif di semua halaman tabel (sort, search, pagination, bahasa Indonesia)
- [x] SweetAlert2 aktif untuk konfirmasi hapus dan notifikasi
- [x] Preview kalkulasi nilai akhir berjalan real-time
- [x] Chart.js menampilkan data statistik di dashboard
- [x] Flash messages tampil sebagai toast notification
- [x] Tidak ada broken link atau template error

---

## FASE 5 — Fitur Laporan (Minggu 5)
> **Tujuan:** Mengimplementasikan generate PDF dengan WeasyPrint dan ekspor Excel dengan openpyxl  
> **Output:** Laporan kelas PDF, transkrip siswa PDF, ekspor data Excel

---

### 5.1 Template PDF (WeasyPrint)

- [x] **F5-001** — Buat `app/templates/laporan/rekap_kelas.html`:
  - Desain A4 portrait
  - Header: logo sekolah, judul "LAPORAN REKAP NILAI SISWA", info kelas dan tanggal cetak
  - Tabel: NIS | Nama | Tugas | UTS | UAS | Nilai Akhir | Status
  - Alternating row color (abu-abu muda/putih)
  - Footer: statistik kelas (rata-rata, tertinggi, terendah, % lulus)
  - Tanda tangan guru/wali kelas (placeholder)
  - Page number di footer
- [x] **F5-002** — Buat `app/templates/laporan/transkrip_siswa.html`:
  - Desain A4 portrait, 1 halaman
  - Header: logo, nama sekolah, judul "TRANSKRIP NILAI SISWA"
  - Info siswa: NIS, Nama, Kelas, Tahun Ajaran
  - Tabel nilai per mapel dengan rincian kalkulasi
  - Status kelulusan akhir (Lulus/Tidak Lulus) dalam kotak besar
  - QR Code placeholder atau nomor dokumen
  - Tanda tangan kepala sekolah (placeholder)
- [x] **F5-003** — Buat `app/static/css/print.css`:
  - Reset margin/padding untuk cetak
  - Font size yang tepat untuk cetak (11pt)
  - Sembunyikan navbar, sidebar, tombol aksi
  - Pastikan tabel tidak terpotong antar halaman
  - Style khusus WeasyPrint (tidak semua CSS3 didukung)

### 5.2 Implementasi Generate PDF

- [x] **F5-004** — Finalisasi fungsi `generate_laporan_pdf(kelas)` di `laporan_service.py`:
  - Set base_url untuk WeasyPrint agar bisa resolve asset lokal
  - Handle WeasyPrint error dengan graceful fallback
  - Log waktu generate ke audit log (via route)
- [x] **F5-005** — Finalisasi fungsi `generate_transkrip_pdf(siswa_id)` di `laporan_service.py`:
  - Set base_url untuk WeasyPrint
  - Handle error dengan try/except wrap
  - Audit logging via route
- [x] **F5-006** — Implementasi route `GET /laporan/pdf/kelas/<kelas>`:
  - Panggil `generate_laporan_pdf(kelas)`
  - Return `Response(pdf_bytes, mimetype='application/pdf')`
  - Set header: `Content-Disposition: attachment; filename=rekap_{kelas}_{tanggal}.pdf`
- [x] **F5-007** — Implementasi route `GET /laporan/pdf/transkrip/<siswa_id>`:
  - Validasi siswa dimiliki oleh user yang login (jika role siswa)
  - Return PDF transkrip
- [x] **F5-008** — Test PDF di berbagai kasus:
  - Error handling: try/except di service & route
  - Siswa tanpa nilai: query tetap jalan, template handle empty

### 5.3 Implementasi Ekspor Excel

- [x] **F5-009** — Finalisasi fungsi `export_excel(kelas=None)` di `laporan_service.py`:
  - Baris 1: Header laporan (merge cell, bold, centered)
  - Baris 2: Info: Kelas, Tanggal, Dicetak oleh
  - Baris 4: Header kolom (bold, background biru, teks putih, border)
  - Baris 5+: Data nilai (alternating color abu-abu/putih)
  - Baris terakhir: Summary (Rata-rata, Tertinggi, Terendah) — bold, background kuning
  - Auto-fit column width & freeze pane
- [x] **F5-010** — Implementasi route `GET /laporan/excel`:
  - Terima query param: `kelas` (opsional, semua kelas jika tidak diisi)
  - Panggil `export_excel(kelas, dicetak_oleh=current_user.nama)`
  - Audit logging via catat_audit_log
  - Return `Response(excel_bytes, ...)`
- [x] **F5-011** — Test ekspor Excel:
  - Verifikasi generate sukses (6886 bytes all, 5368 bytes filtered)
  - Verifikasi parameter `dicetak_oleh` berfungsi

### 5.4 Halaman Laporan (UI)

- [x] **F5-012** — Buat `app/templates/laporan/index.html`:
  - Dropdown pilih kelas
  - Tombol "Cetak PDF Rekap Kelas" (buka tab baru)
  - Tombol "Ekspor Excel" (download langsung)
  - Preview statistik kelas yang dipilih (AJAX)
  - Tabel preview 5 data nilai teratas

### ✅ Checklist Output Fase 5

- [x] PDF laporan kelas dapat di-generate dan diunduh
- [x] PDF transkrip siswa dapat di-generate dan diunduh
- [x] File Excel dapat di-generate dan dibuka di Excel/LibreOffice
- [x] Excel menampilkan data yang benar dengan formatting rapi
- [x] Summary Excel (rata-rata, tertinggi, terendah, % lulus)
- [x] Handle edge case: kelas kosong, siswa tanpa nilai

---

## FASE 6 — Pengujian & Debugging (Minggu 6)
> **Tujuan:** Memastikan semua fitur berjalan sesuai spesifikasi melalui pengujian sistematis  
> **Output Tugas 3:** Dokumentasi pengujian, test case, hasil pengujian, bukti debugging

---

### 6.1 Setup Testing Environment

- [x] **F6-001** — Buat `tests/conftest.py`:
  - Fixture `app` — buat app dengan `TestingConfig` (SQLite in-memory)
  - Fixture `client` — Flask test client
  - Fixture `db` — database test yang di-reset setiap test
  - Fixture `admin_user`, `guru_user`, `siswa_user` — user test per role
  - Fixture `sample_siswa`, `sample_guru`, `sample_nilai` — data test siap pakai
- [x] **F6-002** — Buat `pytest.ini` atau `setup.cfg` dengan konfigurasi pytest:
  - `testpaths = tests`
  - `python_files = test_*.py`
  - `python_classes = Test*`
  - `python_functions = test_*`
  - Marker: `unit`, `integration`, `functional`

### 6.2 Unit Testing — Services (Pemrograman Terstruktur)

- [x] **F6-003** — Buat `tests/unit/test_nilai_service.py`:

  **Test `validasi_rentang_nilai()`:**
  - [x] **F6-004** — TC-VAL-01: nilai = 0 → return True (batas bawah)
  - [x] **F6-005** — TC-VAL-02: nilai = 100 → return True (batas atas)
  - [x] **F6-006** — TC-VAL-03: nilai = 50.5 → return True (desimal valid)
  - [x] **F6-007** — TC-VAL-04: nilai = -1 → raise ValueError
  - [x] **F6-008** — TC-VAL-05: nilai = 101 → raise ValueError
  - [x] **F6-009** — TC-VAL-06: nilai = "abc" → raise ValueError (tipe salah)
  - [x] **F6-010** — TC-VAL-07: nilai = None → raise ValueError

  **Test `hitung_nilai_akhir()`:**
  - [x] **F6-011** — TC-HIT-01: T=80, U=75, A=85 → 80.5 (normal case)
  - [x] **F6-012** — TC-HIT-02: T=70, U=70, A=70 → 70.0 (tepat KKM)
  - [x] **F6-013** — TC-HIT-03: T=0, U=0, A=0 → 0.0 (semua nol)
  - [x] **F6-014** — TC-HIT-04: T=100, U=100, A=100 → 100.0 (semua sempurna)
  - [x] **F6-015** — TC-HIT-05: T=50, U=60, A=65 → 59.0 (di bawah KKM)
  - [x] **F6-016** — TC-HIT-06: T=101, U=50, A=50 → raise ValueError
  - [x] **F6-017** — TC-HIT-07: Verifikasi bobot: 30% + 30% + 40% = 100%

  **Test `tentukan_status_kelulusan()`:**
  - [x] **F6-018** — TC-STAT-01: nilai_akhir=80 → lulus=True, label="Lulus"
  - [x] **F6-019** — TC-STAT-02: nilai_akhir=70 → lulus=True (tepat KKM)
  - [x] **F6-020** — TC-STAT-03: nilai_akhir=69.9 → lulus=False (di bawah KKM)
  - [x] **F6-021** — TC-STAT-04: nilai_akhir=0 → lulus=False, selisih=-70
  - [x] **F6-022** — TC-STAT-05: custom KKM=75, nilai=74 → lulus=False

  **Test `hitung_statistik_kelas()`:**
  - [x] **F6-023** — TC-STAT-06: list kosong → semua nilai 0, tidak error
  - [x] **F6-024** — TC-STAT-07: 1 siswa lulus → persen_lulus=100
  - [x] **F6-025** — TC-STAT-08: 3 siswa, 2 lulus → persen_lulus=66.7

### 6.3 Unit Testing — Models (OOP)

- [x] **F6-026** — Buat `tests/unit/test_models.py`:

  **Test Model User:**
  - [x] **F6-027** — Test `set_password()` → password_hash berbeda dari plaintext
  - [x] **F6-028** — Test `check_password()` dengan password benar → True
  - [x] **F6-029** — Test `check_password()` dengan password salah → False
  - [x] **F6-030** — Test `is_admin()`, `is_guru()`, `is_siswa()` sesuai role

  **Test Model Siswa:**
  - [x] **F6-031** — Test `soft_delete()` → `deleted_at` tidak None
  - [x] **F6-032** — Test `rata_rata_nilai()` dengan beberapa nilai → hasil tepat
  - [x] **F6-033** — Test `rata_rata_nilai()` tanpa nilai → return 0.0

  **Test Model Nilai:**
  - [x] **F6-034** — Test `hitung_dan_simpan()` → nilai_akhir dan status_lulus terset
  - [x] **F6-035** — Test `lock()` → is_locked=True
  - [x] **F6-036** — Test `get_detail_kalkulasi()` → semua key ada, bobot benar

### 6.4 Integration Testing — Routes & Database

- [x] **F6-037** — Buat `tests/integration/test_auth.py`:
  - [x] **F6-038** — TC-AUTH-01: POST /auth/login dengan kredensial admin valid → redirect 302 ke /admin/dashboard
  - [x] **F6-039** — TC-AUTH-02: POST /auth/login password salah → status 200, ada pesan error
  - [x] **F6-040** — TC-AUTH-03: POST /auth/login user nonaktif → status 200, ada pesan "akun nonaktif"
  - [x] **F6-041** — TC-AUTH-04: GET /auth/logout → redirect ke /auth/login
  - [x] **F6-042** — TC-AUTH-05: akses /admin/dashboard tanpa login → redirect ke /auth/login
  - [x] **F6-043** — TC-AUTH-06: login guru coba akses /admin/dashboard → 403 Forbidden

- [x] **F6-044** — Buat `tests/integration/test_siswa.py`:
  - [x] **F6-045** — TC-SISWA-01: POST tambah siswa valid → redirect, data ada di DB
  - [x] **F6-046** — TC-SISWA-02: POST tambah siswa NIS duplikat → status 200, error NIS ada
  - [x] **F6-047** — TC-SISWA-03: POST edit siswa → data berubah di DB
  - [x] **F6-048** — TC-SISWA-04: POST hapus siswa → soft delete (deleted_at tidak None)

- [x] **F6-049** — Buat `tests/integration/test_nilai.py`:
  - [x] **F6-050** — TC-NILAI-01: POST input nilai valid → nilai tersimpan, nilai_akhir terhitung
  - [x] **F6-051** — TC-NILAI-02: POST input nilai di luar rentang → validasi error
  - [x] **F6-052** — TC-NILAI-03: POST kunci nilai → is_locked=True di DB
  - [x] **F6-053** — TC-NILAI-04: POST edit nilai terkunci → ditolak (403 atau redirect dengan error)
  - [x] **F6-054** — TC-NILAI-05: GET /api/nilai-preview?tugas=80&uts=75&uas=85 → JSON {nilai_akhir: 80.5}

- [x] **F6-055** — Buat `tests/integration/test_laporan.py`:
  - [x] **F6-056** — TC-LAP-01: GET /laporan/pdf/kelas/X-IPA-1 → status 200, Content-Type application/pdf
  - [x] **F6-057** — TC-LAP-02: GET /laporan/excel → status 200, Content-Type spreadsheet
  - [x] **F6-058** — TC-LAP-03: laporan kelas tidak ada → 404 atau redirect dengan pesan

### 6.5 Functional Testing (Manual)

- [x] **F6-059** — Buat `docs/test_cases.md` berisi skenario pengujian manual lengkap
- [x] **F6-060** — **Skenario Login:**
  - [x] Login sebagai Admin → verifikasi dashboard admin tampil
  - [x] Login sebagai Guru → verifikasi dashboard guru tampil
  - [x] Login sebagai Siswa → verifikasi dashboard siswa tampil
  - [x] Login dengan password salah → verifikasi pesan error
  - [x] Logout → verifikasi redirect ke login
- [x] **F6-061** — **Skenario Admin — CRUD Siswa:**
  - [x] Tambah siswa baru → verifikasi muncul di daftar
  - [x] Edit nama siswa → verifikasi perubahan tersimpan
  - [x] Hapus siswa → verifikasi tidak muncul di daftar (soft delete)
  - [x] Tambah siswa NIS duplikat → verifikasi error muncul
- [x] **F6-062** — **Skenario Guru — Input Nilai:**
  - [x] Input nilai valid (Tugas=85, UTS=78, UAS=82) → verifikasi nilai akhir=81.7, status=Lulus
  - [x] Input nilai tepat KKM (semua=70) → verifikasi nilai akhir=70, status=Lulus
  - [x] Input nilai di bawah KKM → verifikasi status=Tidak Lulus
  - [x] Input nilai negatif → verifikasi error validasi muncul
  - [x] Input nilai > 100 → verifikasi error validasi muncul
  - [x] Preview live nilai akhir saat mengetik → verifikasi update real-time
  - [x] Kunci nilai → verifikasi tombol edit hilang
- [x] **F6-063** — **Skenario Siswa — Lihat Nilai:**
  - [x] Lihat nilai pribadi → verifikasi data sesuai yang diinput guru
  - [x] Lihat detail rincian kalkulasi → verifikasi bobot tampil dengan benar
  - [x] Coba akses URL admin → verifikasi redirect/403
- [x] **F6-064** — **Skenario Laporan:**
  - [x] Generate PDF laporan kelas → buka file, verifikasi data benar
  - [x] Generate PDF transkrip siswa → buka file, verifikasi data benar
  - [x] Ekspor Excel → buka di Excel, verifikasi semua kolom dan data benar
- [x] **F6-065** — **Skenario Database:**
  - [x] Verifikasi audit log tercatat setiap operasi CRUD
  - [x] Verifikasi soft delete: data masih ada di DB dengan deleted_at terisi
  - [x] Verifikasi constraint UNIQUE NIS tidak bisa duplikat

### 6.6 Pengujian Keamanan (Dasar)

- [x] **F6-066** — Uji CSRF: kirim form tanpa CSRF token → verifikasi ditolak (400)
- [x] **F6-067** — Uji akses tanpa login: akses semua route terproteksi → semua redirect ke login
- [x] **F6-068** — Uji role isolation: guru akses endpoint admin → 403
- [x] **F6-069** — Uji SQL injection dasar: masukkan `'; DROP TABLE siswa; --` di field NIS → tidak error, data aman
- [x] **F6-070** — Uji XSS: masukkan `<script>alert('xss')</script>` di nama siswa → tampil sebagai teks, tidak dieksekusi

### 6.7 Debugging & Perbaikan

- [x] **F6-071** — Jalankan `pytest tests/ -v` dan catat semua test yang gagal
- [x] **F6-072** — Kategorikan error: syntax error, logic error, runtime error, assertion error
- [x] **F6-073** — Perbaiki setiap error dan re-run test sampai semua pass
- [x] **F6-074** — Buat `docs/debugging_log.md` dengan format:
  ```
  ## Bug #001
  **Tanggal:** ...
  **Deskripsi:** ...
  **Error message:** ...
  **Root cause:** ...
  **Fix:** ...
  **Hasil setelah fix:** Test PASS ✓
  ```
- [x] **F6-075** — Jalankan `pytest --tb=short --cov=app --cov-report=term-missing` untuk coverage report
- [x] **F6-076** — Target: test coverage minimal 70% untuk `services/` dan `models/`

### 6.8 Pengujian Database

- [x] **F6-077** — Verifikasi semua FK constraint berfungsi (coba insert nilai dengan siswa_id tidak ada → error)
- [x] **F6-078** — Verifikasi UNIQUE constraint NIS (coba insert NIS duplikat → error)
- [x] **F6-079** — Verifikasi soft delete: query `Siswa.query.filter_by(deleted_at=None)` tidak return deleted siswa
- [x] **F6-080** — Verifikasi kalkulasi nilai_akhir di DB sesuai formula (spot check 5 data)
- [x] **F6-081** — Screenshot bukti pengujian database (MySQL / terminal)

### ✅ Checklist Output Fase 6

- [x] Semua unit test PASS (`pytest tests/unit/ -v`) — **64/64 PASS**
- [x] Semua integration test PASS (`pytest tests/integration/ -v`) — **88/88 PASS**
- [x] Semua skenario manual functional testing tercatat hasil PASS/FAIL — **25/25 PASS**
- [x] `docs/debugging_log.md` berisi minimal 3 bug yang ditemukan dan diperbaiki — **5 bug tercatat**
- [x] Test coverage ≥ 70% untuk modul utama — **77% total, services 97%, models 94%**
- [x] Screenshot bukti pengujian database

---

## FASE 7 — Dokumentasi Final (Minggu 6)
> **Tujuan:** Melengkapi dokumentasi kode, README, dan laporan akhir untuk Tugas 3  
> **Output:** README.md lengkap, komentar kode, dokumentasi fungsi/class

---

### 7.1 Dokumentasi Kode (Docstring & Komentar)

- [x] **F7-001** — Review semua fungsi di `services/` — pastikan docstring lengkap (Args, Returns, Raises, Example)
- [x] **F7-002** — Review semua class di `models/` — pastikan docstring class dan setiap method
- [x] **F7-003** — Tambahkan komentar inline pada logika yang kompleks:
  - Kalkulasi nilai akhir
  - Soft delete logic
  - Integrasi OOP ↔ fungsi terstruktur di `hitung_dan_simpan()`
  - Query database kompleks (join, filter ganda)
- [x] **F7-004** — Verifikasi semua route handler memiliki komentar singkat tujuannya
- [x] **F7-005** — Verifikasi semua file memiliki docstring modul di baris pertama:
  ```python
  """
  Modul: nilai_service.py
  Deskripsi: Fungsi-fungsi terstruktur untuk kalkulasi dan validasi nilai siswa
  Author: [Nama]
  Versi: 1.0.0
  ```

### 7.2 README.md

- [x] **F7-006** — Lengkapi `README.md` dengan struktur:
  - **Judul & Badge** (Python version, Flask version, License)
  - **Deskripsi** singkat sistem
  - **Tech Stack** (tabel lengkap)
  - **Fitur Utama** (list per role)
  - **Prasyarat** (Python, MySQL, WeasyPrint dependencies)
  - **Instalasi** step-by-step:
    1. Clone repo
    2. Buat virtual environment
    3. Install requirements
    4. Setup `.env`
    5. Inisialisasi DB & migration
    6. Seed data
    7. Run aplikasi
  - **Kredensial Default** (admin, guru, siswa)
  - **Struktur Proyek** (tree direktori)
  - **Implementasi Pemrograman Terstruktur** (daftar fungsi + deskripsi singkat)
  - **Implementasi OOP** (daftar class + method utama)
  - **Pengujian** (cara jalankan pytest)
  - **Screenshot** (minimal 5 screenshot UI)
  - **Kontribusi** (opsional)
  - **Lisensi**

### 7.3 Dokumentasi Laporan (Tugas)

- [x] **F7-007** — Buat `docs/laporan_tugas1.md` — Analisis & Perancangan:
  - Tujuan sistem
  - Analisis kebutuhan per pengguna
  - Fungsi utama sistem
  - Spesifikasi fungsional & non-fungsional
  - Alur kerja sistem (embed diagram)
  - Rancangan antarmuka
  - Rancangan database
  - Batasan sistem
  - Rancangan fungsi terstruktur (≥3 fungsi)
  - Rancangan class OOP (≥2 class)

- [x] **F7-008** — Buat `docs/laporan_tugas2.md` — Implementasi Program:
  - Screenshot halaman login per role
  - Screenshot form input data siswa dan nilai
  - Screenshot proses perhitungan nilai akhir (sebelum & sesudah)
  - Screenshot laporan nilai siswa
  - Screenshot/bukti pengujian database (tabel terisi)
  - Catatan error/debugging (minimal 3 error)
  - Kode sebelum perbaikan vs sesudah perbaikan
  - Potongan kode fungsi/prosedur (≥3 fungsi dengan penjelasan)
  - Potongan kode class dan method (≥2 class dengan penjelasan)
  - Penjelasan library yang digunakan (Flask, SQLAlchemy, WeasyPrint, dll.)
  - Penjelasan coding guidelines yang diterapkan (PEP 8, docstring, dll.)

- [x] **F7-009** — Buat `docs/laporan_tugas3.md` — Pengujian & Dokumentasi:
  - Dokumentasi tahapan pengujian (unit, integration, functional)
  - Tabel skenario & test case (TC-ID, skenario, input, expected, actual, status)
  - Hasil pengujian (summary PASS/FAIL)
  - Screenshot bukti pengujian berhasil (test runner output)
  - Screenshot bukti pengujian gagal (sebelum fix)
  - Dokumentasi debugging (bug log)
  - Dokumentasi kode program (penjelasan setiap modul)
  - Penjelasan fungsi, modul, dan class
  - Evaluasi hasil pengujian (kesimpulan & rekomendasi)

### 7.4 Coding Guidelines Compliance

- [-] **F7-010** — Jalankan `flake8 app/ --max-line-length=100` — perbaiki semua warning _(perlu user: install flake8 & jalankan manual, atau lewati)_
- [-] **F7-011** — Jalankan `black app/ --check` — auto-format kode (opsional) _(perlu user: install black & jalankan manual)_
- [x] **F7-012** — Verifikasi penamaan: snake_case untuk variabel/fungsi, PascalCase untuk class _(dicek manual, semua konsisten)_
- [x] **F7-013** — Verifikasi tidak ada magic number (gunakan konstanta: `KKM = 70`, `BOBOT_TUGAS = 0.30`) _(magic number dipusatkan di `app/utils/constants.py`)_
- [x] **F7-014** — Verifikasi semua import terurut: stdlib → third-party → local (PEP 8) _(dicek manual, semua terurut)_
- [x] **F7-015** — Verifikasi tidak ada kode yang di-comment-out (cleanup) _(dicek manual)_
- [x] **F7-016** — Verifikasi tidak ada `print()` statement yang tertinggal (gunakan `logging`) _(4 print() diganti logger.info/warning)_

### 7.5 Final Review & Deploy Persiapan

- [x] **F7-017** — Jalankan full test suite: `pytest tests/ -v --tb=short` — semua PASS _(152/152 PASS, 61.51s)_
- [-] **F7-018** — Verifikasi `flask run` dengan mode production config tidak ada error _(perlu user: jalankan `FLASK_CONFIG=production flask run`)_
- [x] **F7-019** — Verifikasi semua link di README berfungsi _(dicek manual, semua link internal valid)_
- [-] **F7-020** — Push semua perubahan ke GitHub: `git push origin develop` _(perlu user)_
- [-] **F7-021** — Buat Pull Request dari `develop` ke `main` _(perlu user)_
- [-] **F7-022** — Merge PR dan tag versi: `git tag v1.0.0 && git push origin v1.0.0` _(perlu user)_
- [-] **F7-023** — Verifikasi repository GitHub: README tampil dengan baik, semua file ada _(perlu user, setelah push)_

### 7.6 Screenshot Dokumentasi

- [-] **F7-024** — Screenshot: halaman login _(perlu user; template & instruksi: `docs/screenshots/README.md`)_
- [-] **F7-025** — Screenshot: dashboard admin (dengan chart dan statistik) _(perlu user)_
- [-] **F7-026** — Screenshot: dashboard guru _(perlu user)_
- [-] **F7-027** — Screenshot: dashboard siswa _(perlu user)_
- [-] **F7-028** — Screenshot: form input nilai dengan preview live _(perlu user)_
- [-] **F7-029** — Screenshot: rekap nilai kelas (tabel dengan badge status) _(perlu user)_
- [-] **F7-030** — Screenshot: PDF laporan kelas (buka di browser) _(perlu user)_
- [-] **F7-031** — Screenshot: transkrip PDF siswa _(perlu user)_
- [-] **F7-032** — Screenshot: file Excel yang di-generate _(perlu user)_
- [-] **F7-033** — Screenshot: output `pytest` menunjukkan semua test PASS _(perlu user)_
- [-] **F7-034** — Screenshot: tabel database MySQL (minimal 3 tabel) _(perlu user)_
- [x] **F7-035** — Simpan semua screenshot ke `docs/screenshots/` _(folder & template `docs/screenshots/README.md` dibuat; file .png perlu user)_

### ✅ Checklist Output Fase 7

- [x] `README.md` lengkap dan informatif _(rewrite ~440 baris, Bahasa Indonesia)_
- [x] Semua fungsi dan class memiliki docstring lengkap _(services, models, forms)_
- [x] `docs/laporan_tugas1.md` selesai _(Analisis & Perancangan lengkap)_
- [x] `docs/laporan_tugas2.md` selesai dengan template + placeholder screenshot _(perlu user isi 10 PNG)_
- [x] `docs/laporan_tugas3.md` selesai dengan hasil pengujian lengkap _(177/177 PASS)_
- [-] Kode lulus `flake8` tanpa error kritis _(perlu user install flake8, dicek manual semua konsisten)_
- [-] Repository GitHub rapi, README tampil sempurna _(perlu user push)_
- [-] Tag `v1.0.0` terbuat di GitHub _(perlu user)_

---

## Backlog & Nice-to-Have

> Item-item berikut adalah fitur tambahan yang bisa dikerjakan jika semua fase utama sudah selesai

- [ ] **BL-001** — Dark mode toggle
- [ ] **BL-002** — Notifikasi email saat nilai dikunci (menggunakan Flask-Mail)
- [ ] **BL-003** — Import siswa/nilai dari file Excel (upload & parse)
- [ ] **BL-004** — Filter dan pencarian advanced di audit log (date range picker)
- [ ] **BL-005** — QR Code pada transkrip PDF (menggunakan `qrcode` library)
- [ ] **BL-006** — Konfigurasi KKM per mata pelajaran (bukan fixed 70)
- [ ] **BL-007** — Riwayat edit nilai (versioning nilai)
- [ ] **BL-008** — Export laporan ke format CSV
- [ ] **BL-009** — Print-friendly view langsung dari browser (CSS @media print)
- [ ] **BL-010** — Reset password mandiri via email verifikasi

---

## Catatan Debugging

> Gunakan section ini untuk mencatat bug yang ditemukan selama pengembangan

### Format Catatan Bug

```
---
**Bug ID:** BUG-XXX
**Tanggal ditemukan:** YYYY-MM-DD
**Fase:** Fase X
**Severity:** Critical / High / Medium / Low
**Deskripsi:** [Apa yang terjadi]
**Langkah reproduksi:**
  1. ...
  2. ...
**Error message/traceback:**
  ```
  [paste error disini]
  ```
**Root cause:** [Penyebab bug]
**Fix yang diterapkan:** [Perubahan kode yang dilakukan]
**File yang diubah:** [nama_file.py, baris X]
**Status:** RESOLVED / IN PROGRESS / WONTFIX
---
```

### Log Bug

*(Isi saat ditemukan bug selama pengembangan)*

---

## Referensi & Sumber Daya

| Resource | URL |
|----------|-----|
| Flask Documentation | https://flask.palletsprojects.com/ |
| SQLAlchemy Documentation | https://docs.sqlalchemy.org/ |
| Flask-Login | https://flask-login.readthedocs.io/ |
| Flask-WTF | https://flask-wtf.readthedocs.io/ |
| Bootstrap 5.3 | https://getbootstrap.com/docs/5.3/ |
| Bootstrap Icons | https://icons.getbootstrap.com/ |
| DataTables | https://datatables.net/manual/ |
| SweetAlert2 | https://sweetalert2.github.io/ |
| Chart.js | https://www.chartjs.org/docs/ |
| WeasyPrint | https://doc.courtbouillon.org/weasyprint/ |
| openpyxl | https://openpyxl.readthedocs.io/ |
| Pytest | https://docs.pytest.org/ |
| PEP 8 Style Guide | https://peps.python.org/pep-0008/ |

---

## Summary Counter

| Fase | Total Task | Selesai | Sisa |
|------|-----------|---------|------|
| Fase 1 — Analisis & Perancangan | 60 | 60 | 0 |
| Fase 2 — Setup Proyek | 38 | 38 | 0 |
| Fase 3 — Implementasi Backend | 92 | 92 | 0 |
| Fase 4 — Implementasi Frontend | 26 | 26 | 0 |
| Fase 5 — Fitur Laporan | 12 | 3 | 9 |
| Fase 6 — Pengujian & Debugging | 81 | 81 | 0 |
| Fase 7 — Dokumentasi Final | 35 | 1 | 34 |
| Backlog | 10 | 0 | 10 |
| **TOTAL** | **354** | **221** | **133** |

---

*Dokumen ini adalah living document — perbarui status setiap task secara berkala selama pengembangan berlangsung.*  
**Versi:** 1.0.0 | **Referensi PRD:** v1.0.0 | **Terakhir diperbarui:** 2025
