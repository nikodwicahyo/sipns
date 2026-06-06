# SIPNS — Sistem Informasi Pengolahan Nilai Siswa

> 🌐 **Live Demo:** [https://nikodwicahyo-sipns.hf.space](https://nikodwicahyo-sipns.hf.space)

> 📖 **Tutorial Deploy:** Lihat [`docs/DEPLOY_HUGGINGFACE_TIDB.md`](docs/DEPLOY_HUGGINGFACE_TIDB.md) untuk panduan lengkap step-by-step.

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-152%2F152%20PASS-brightgreen)](tests/)
[![Coverage](https://img.shields.io/badge/Coverage-77%25-yellow)](docs/laporan_tugas3.md)

Aplikasi web berbasis **Python/Flask** untuk mengelola data nilai siswa secara digital, terstruktur, dan efisien. Mendukung tiga peran pengguna: **Admin**, **Guru**, dan **Siswa**.

Dikembangkan sebagai implementasi nyata **dua paradigma pemrograman** yang saling melengkapi:

| Paradigma                                | Lokasi          | Deskripsi                                                                             |
| ---------------------------------------- | --------------- | ------------------------------------------------------------------------------------- |
| **Pemrograman Terstruktur**              | `app/services/` | Fungsi/prosedur murni untuk logika bisnis (kalkulasi nilai, generate laporan, audit). |
| **Pemrograman Berorientasi Objek (OOP)** | `app/models/`   | Class SQLAlchemy ORM untuk entitas sistem (User, Siswa, Guru, Nilai, AuditLog).       |

Lihat [PRD.md](PRD.md) untuk spesifikasi lengkap dan [docs/laporan_tugas1.md](docs/laporan_tugas1.md) untuk analisis & perancangan.

---

## 📑 Daftar Isi

1. [Tech Stack](#-tech-stack)
2. [Fitur Utama](#-fitur-utama)
3. [Prasyarat](#-prasyarat)
4. [Instalasi](#-instalasi)
5. [Kredensial Default](#-kredensial-default)
6. [Struktur Proyek](#-struktur-proyek)
7. [Implementasi Pemrograman Terstruktur](#-implementasi-pemrograman-terstruktur)
8. [Implementasi OOP](#-implementasi-oop)
9. [Testing](#-testing)
10. [Screenshot](#-screenshot)
11. [Dokumentasi](#-dokumentasi)
12. [Kontribusi](#-kontribusi)
13. [Lisensi](#-lisensi)

---

## 🛠️ Tech Stack

| Layer               | Teknologi       | Versi | Keterangan                                           |
| ------------------- | --------------- | ----- | ---------------------------------------------------- |
| **Language**        | Python          | 3.12  | Bahasa pemrograman utama                             |
| **Backend**         | Flask           | 3.x   | Web framework micro                                  |
| **ORM**             | SQLAlchemy      | 2.x   | Database abstraction layer                           |
| **Migration**       | Flask-Migrate   | 4.x   | Database schema versioning (Alembic)                 |
| **Authentication**  | Flask-Login     | 0.6.x | Session management & login                           |
| **Form Validation** | Flask-WTF       | 1.x   | WTForms + CSRF protection                            |
| **Database**        | MySQL           | 8.x   | RDBMS production (SQLite untuk testing)              |
| **Frontend**        | HTML5 + Jinja2  | 3.x   | Server-side rendering                                |
| **Styling**         | Bootstrap       | 5.3   | CSS framework responsif                              |
| **Table**           | DataTables      | 1.13  | Tabel interaktif (sort, search, pagination)          |
| **Alert**           | SweetAlert2     | 11.x  | Dialog konfirmasi & notifikasi toast                 |
| **Icons**           | Bootstrap Icons | 1.11  | Icon library                                         |
| **Charts**          | Chart.js        | 4.x   | Visualisasi data (bar, doughnut)                     |
| **PDF**             | WeasyPrint      | 61.x  | Generate laporan PDF (perlu GTK3 runtime di Windows) |
| **Excel**           | openpyxl        | 3.x   | Ekspor data ke `.xlsx`                               |
| **Password**        | Werkzeug        | 3.x   | PBKDF2-SHA256 hashing                                |
| **Testing**         | Pytest          | 8.x   | Unit + integration test suite                        |
| **Env Config**      | python-dotenv   | 1.x   | Manajemen environment variable                       |

Lihat [`requirements.txt`](requirements.txt) untuk daftar dependency lengkap dengan versi terkunci.

---

## ✨ Fitur Utama

### 👨‍💼 Admin

- ✅ Login dengan kredensial admin
- ✅ CRUD data siswa (tambah, lihat, edit, **soft-delete**)
- ✅ CRUD data guru (tambah, lihat, edit, soft-delete dengan validasi ketergantungan)
- ✅ Manajemen user (toggle aktif/nonaktif, reset password)
- ✅ Audit log viewer (filter by user, action, date)
- ✅ Lihat & cetak laporan PDF per kelas
- ✅ Ekspor data nilai ke Excel
- ✅ Dashboard dengan chart (Chart.js) & statistik agregat
- ✅ Health check endpoint (cek koneksi DB)

### 👨‍🏫 Guru

- ✅ Login dengan kredensial guru
- ✅ Input nilai siswa (Tugas, UTS, UAS) per mata pelajaran yang diampu
- ✅ **Preview kalkulasi nilai akhir real-time** (AJAX)
- ✅ Edit nilai sebelum dikunci
- ✅ **Kunci nilai** (lock) agar tidak dapat diubah
- ✅ Lihat rekap nilai seluruh siswa di kelasnya
- ✅ Generate PDF rekap nilai kelas yang diampu
- ✅ Generate PDF transkrip siswa

### 👨‍🎓 Siswa

- ✅ Login dengan **NIS sebagai username** (password = NIS)
- ✅ Lihat nilai pribadi per mata pelajaran
- ✅ Lihat **rincian kalkulasi** nilai (bobot 30%/30%/40%)
- ✅ Lihat status kelulusan global
- ✅ Unduh transkrip PDF pribadi
- ✅ Akses ditolak ke halaman admin/guru (403 Forbidden)

### 🔒 Keamanan

- ✅ Password di-hash dengan **PBKDF2-SHA256** (Werkzeug)
- ✅ CSRF protection via **Flask-WTF** (token di setiap form)
- ✅ SQL injection prevention via **SQLAlchemy ORM** (no raw queries)
- ✅ XSS protection via **Jinja2 auto-escape**
- ✅ Role-Based Access Control (RBAC) dengan decorator `@role_required`
- ✅ Soft delete siswa/guru (data nilai historis tetap terjaga)

---

## 📋 Prasyarat

Pastikan sistem Anda memiliki:

| Software               | Versi Minimum | Keterangan                                                                                                               |
| ---------------------- | ------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Python                 | 3.10+         | Disarankan 3.12 (versi pengembangan)                                                                                     |
| MySQL Server           | 8.x           | Untuk dev/production. Testing pakai SQLite (built-in).                                                                   |
| pip                    | 21+           | Package manager Python                                                                                                   |
| Git                    | 2.x           | Version control                                                                                                          |
| **WeasyPrint runtime** | —             | **Wajib di Windows:** install [GTK3 Runtime](https://github.com/nickvdyck/weasyprint-win/releases) dan tambahkan ke PATH |

### Verifikasi Prasyarat

```bash
python --version    # >= 3.10
mysql --version     # >= 8.0
pip --version
```

---

## 🚀 Instalasi

### 1. Clone Repository

```bash
git clone <repository-url> sipns
cd sipns
```

### 2. Buat Virtual Environment

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux/macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Konfigurasi Environment

```bash
cp .env.example .env
```

Edit `.env` dan sesuaikan kredensial MySQL Anda:

```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=ganti-dengan-random-string-yang-kuat
DATABASE_URL=mysql+pymysql://root:password_anda@localhost:3306/sipns_dev?charset=utf8mb4
```

> ⚠️ **PENTING:** Jangan gunakan SECRET_KEY default di production!

### 5. Buat Database MySQL

```bash
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS sipns_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

### 6. Migrasi Schema

```bash
flask db upgrade
```

### 7. Seed Data Awal

```bash
flask seed
```

Output yang diharapkan:

```
INFO:app.seed:Memulai proses seed data SIPNS...
INFO:app.seed:Seed master data selesai: 1 admin, 3 guru, 10 siswa.
INFO:app.seed:Seed nilai selesai: 24 record nilai untuk 10 siswa × 3 mapel.
INFO:app.seed:Seed data SIPNS berhasil!
```

### 8. Jalankan Aplikasi

```bash
flask run
```

Atau dengan mode debug:

```bash
flask run --debug
```

Buka browser dan akses: **http://localhost:5000**

---

## 🔑 Kredensial Default

| Role                      | Username                | Password                    | Akses                      |
| ------------------------- | ----------------------- | --------------------------- | -------------------------- |
| **Admin**                 | `admin`                 | `Admin@123`                 | Semua menu admin           |
| **Guru Matematika**       | `GR-001`                | `Guru@123`                  | Input nilai Matematika     |
| **Guru Bahasa Indonesia** | `GR-002`                | `Guru@123`                  | Input nilai Bhs. Indonesia |
| **Guru IPA**              | `GR-003`                | `Guru@123`                  | Input nilai IPA            |
| **Siswa**                 | `2024001` s/d `2024010` | `<NIS>` (sama dgn username) | Lihat nilai pribadi        |

> ⚠️ **WAJIB ganti semua password default di production!**

Lihat [`docs/seed_credentials.md`](docs/seed_credentials.md) untuk daftar lengkap siswa & guru.

---

## 📁 Struktur Proyek

```
sipns/
├── app/                                # Application package
│   ├── __init__.py                    # Application factory (create_app)
│   ├── config.py                      # Konfigurasi (Development, Production, Testing)
│   ├── seed.py                        # CLI command `flask seed`
│   │
│   ├── models/                        # ── OOP: SQLAlchemy ORM ──
│   │   ├── __init__.py
│   │   ├── user.py                    # class User (autentikasi)
│   │   ├── siswa.py                   # class Siswa (data siswa)
│   │   ├── guru.py                    # class Guru (data guru)
│   │   ├── nilai.py                   # class Nilai (data nilai)
│   │   └── audit_log.py               # class AuditLog
│   │
│   ├── services/                      # ── Pemrograman Terstruktur ──
│   │   ├── __init__.py
│   │   ├── nilai_service.py           # Kalkulasi, validasi, statistik
│   │   ├── laporan_service.py         # Generate PDF & Excel
│   │   └── audit_service.py           # Logging audit
│   │
│   ├── forms/                         # WTForms (validasi & CSRF)
│   │   ├── auth_forms.py              # LoginForm
│   │   ├── siswa_forms.py             # SiswaForm
│   │   ├── guru_forms.py              # GuruForm
│   │   ├── nilai_forms.py             # NilaiForm
│   │   └── user_forms.py              # TambahUserForm, EditUserForm, ResetPasswordForm
│   │
│   ├── blueprints/                    # Modular routing per role
│   │   ├── __init__.py
│   │   ├── decorators.py              # @role_required
│   │   ├── auth/                      # /auth/login, /auth/logout
│   │   ├── admin/                     # /admin/dashboard, /admin/siswa, dll
│   │   ├── guru/                      # /guru/dashboard, /guru/nilai/*
│   │   ├── siswa/                     # /siswa/dashboard, /siswa/nilai
│   │   └── laporan/                   # /laporan/pdf/*, /laporan/excel
│   │
│   ├── templates/                     # Jinja2 templates
│   │   ├── base.html                  # Layout utama
│   │   ├── landing.html               # Halaman landing (logged out)
│   │   ├── partials/                  # navbar, sidebar, flash_messages
│   │   ├── auth/                      # login.html
│   │   ├── admin/                     # dashboard, siswa/, guru/, users/, audit/
│   │   ├── guru/                      # dashboard, nilai/input, nilai/rekap
│   │   ├── siswa/                     # dashboard, nilai, nilai_detail
│   │   ├── laporan/                   # index, rekap_kelas, transkrip_siswa
│   │   └── errors/                    # 403, 404, 500
│   │
│   ├── static/                        # Assets statis
│   │   ├── css/                       # custom.css, print.css
│   │   ├── js/                        # main.js, charts.js, nilai-preview.js
│   │   ├── fonts/
│   │   └── img/                       # favicon.svg, logo.svg
│   │
│   └── utils/                         # Helper bersama
│       ├── __init__.py
│       ├── constants.py               # KKM, BOBOT_TUGAS/UTS/UAS, dll (F7-013)
│       └── time.py                    # Zona waktu Jakarta
│
├── tests/                             # Pytest test suite (152 tests)
│   ├── conftest.py                    # Shared fixtures
│   ├── unit/                          # Unit tests (services, models)
│   │   ├── test_nilai_service.py      # 30 tests
│   │   └── test_models.py             # 34 tests
│   └── integration/                   # Integration tests (routes, DB)
│       ├── test_auth.py
│       ├── test_siswa.py
│       ├── test_nilai.py
│       ├── test_laporan.py
│       └── test_security.py
│
├── docs/                              # Dokumentasi
│   ├── PRD.md                         # Product Requirements Document
│   ├── seed_credentials.md            # Kredensial seed data
│   ├── test_cases.md                  # Test case manual (25 skenario)
│   ├── debugging_log.md               # Log bug yang ditemukan & fix
│   ├── schema.sql                     # DDL MySQL lengkap
│   ├── ERD.png                        # Entity Relationship Diagram
│   ├── Use Case Diagram.png
│   ├── Activity Diagram.png
│   ├── Sequence Diagram.png
│   ├── Class Diagram.png
│   ├── Flowchart alur login.png
│   ├── Flowchart alur input nilai.png
│   ├── Flowchart generate laporan.png
│   ├── Wireframe.png
│   ├── screenshots/                   # Screenshot UI (lihat instruksi)
│   ├── laporan_tugas1.md              # Laporan Tugas 1 (Analisis)
│   ├── laporan_tugas2.md              # Laporan Tugas 2 (Implementasi)
│   └── laporan_tugas3.md              # Laporan Tugas 3 (Pengujian)
│
├── migrations/                        # Flask-Migrate (Alembic)
│
├── .env.example                       # Template environment variables
├── .gitignore                         # File yang di-exclude dari Git
├── pytest.ini                         # Konfigurasi pytest
├── requirements.txt                   # Dependency Python
├── run.py                             # Entry point aplikasi
└── README.md                          # File ini
```

---

## 🧩 Implementasi Pemrograman Terstruktur

Logika bisnis inti diisolasi sebagai **fungsi/prosedur murni** di `app/services/`. Tujuannya: memudahkan unit testing tanpa Flask app context.

### Fungsi Utama

| #   | Fungsi                                        | Modul                | Deskripsi                                                                             |
| --- | --------------------------------------------- | -------------------- | ------------------------------------------------------------------------------------- |
| 1   | `validasi_rentang_nilai(nilai, label)`        | `nilai_service.py`   | Validasi numerik & rentang 0-100. Raise `ValueError` jika invalid.                    |
| 2   | `hitung_nilai_akhir(tugas, uts, uas)`         | `nilai_service.py`   | Hitung `(0.30 × T) + (0.30 × U) + (0.40 × A)`, round 2 desimal.                       |
| 3   | `tentukan_status_kelulusan(nilai_akhir, kkm)` | `nilai_service.py`   | Lulus jika `>= KKM` (default 70). Return dict `{lulus, label, badge_class, selisih}`. |
| 4   | `hitung_statistik_kelas(data_nilai)`          | `nilai_service.py`   | Agregat: total, rata-rata, tertinggi, terendah, % lulus.                              |
| 5   | `generate_laporan_pdf(kelas, template)`       | `laporan_service.py` | Generate PDF rekap kelas via WeasyPrint.                                              |
| 6   | `generate_transkrip_pdf(siswa_id)`            | `laporan_service.py` | Generate PDF transkrip siswa.                                                         |
| 7   | `export_excel(kelas, dicetak_oleh)`           | `laporan_service.py` | Ekspor data nilai ke `.xlsx` (openpyxl).                                              |
| 8   | `catat_audit_log(user_id, action, ...)`       | `audit_service.py`   | Catat aktivitas user ke `audit_log` table.                                            |

### Konstanta Terpusat

Semua "magic numbers" (KKM, bobot, rentang) didefinisikan di [`app/utils/constants.py`](app/utils/constants.py):

```python
KKM = 70.0
BOBOT_TUGAS = 0.30
BOBOT_UTS = 0.30
BOBOT_UAS = 0.40
RENTANG_NILAI_MIN = 0
RENTANG_NILAI_MAX = 100
PEMBULATAN_DESIMAL = 2
```

---

## 🎯 Implementasi OOP

Entitas sistem dimodelkan sebagai **class SQLAlchemy** di `app/models/`. Setiap class memiliki atribut, relasi, dan method bisnis.

### Class Utama

| Class                       | File           | Deskripsi                                                                                                                                                                                   |
| --------------------------- | -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `User(db.Model, UserMixin)` | `user.py`      | Akun login (admin/guru/siswa). Method: `set_password()`, `check_password()`, `is_admin()`, `is_guru()`, `is_siswa()`.                                                                       |
| `Siswa(db.Model)`           | `siswa.py`     | Data siswa. Method: `nilai_akhir_all()`, `rata_rata_nilai()`, `status_kelulusan_global()`, `soft_delete()`. Classmethod: `cari_by_nis()`, `daftar_kelas()`.                                 |
| `Guru(db.Model)`            | `guru.py`      | Data guru. Method: `get_siswa_diajar()`, `soft_delete()`.                                                                                                                                   |
| `Nilai(db.Model)`           | `nilai.py`     | Record nilai siswa per mapel. **Titik integrasi OOP ↔ Terstruktur**: method `hitung_dan_simpan()` memanggil fungsi `hitung_nilai_akhir` & `tentukan_status_kelulusan` dari `nilai_service`. |
| `AuditLog(db.Model)`        | `audit_log.py` | Jejak aktivitas user. Classmethod: `log(...)`.                                                                                                                                              |

### Integrasi OOP ↔ Pemrograman Terstruktur

Contoh pada class `Nilai`:

```python
# app/models/nilai.py
class Nilai(db.Model):
    def hitung_dan_simpan(self):
        """Integrasi: delegasi kalkulasi ke fungsi terstruktur murni."""
        self.nilai_akhir = hitung_nilai_akhir(
            float(self.nilai_tugas),
            float(self.nilai_uts),
            float(self.nilai_uas),
        )
        status = tentukan_status_kelulusan(float(self.nilai_akhir))
        self.status_lulus = status['lulus']
```

**Keuntungan pola ini:**

- Logika bisnis terpusat di service (mudah di-unit-test)
- Model OOP tetap tipis (hanya menyimpan data + delegasi)
- Perubahan formula → edit 1 file (`nilai_service.py`)

---

## ✅ Testing

SIPNS memiliki **152 test** (30 unit service + 34 unit model + 88 integration) yang seluruhnya PASS.

### Menjalankan Test

```bash
# Semua test
pytest tests/ -v

# Hanya unit test
pytest tests/unit/ -v

# Hanya integration test
pytest tests/integration/ -v

# Dengan coverage report
pytest tests/ --cov=app --cov-report=term-missing

# Test spesifik (by name pattern)
pytest tests/ -v -k "nilai"
```

### Coverage

| Area              | Coverage |
| ----------------- | -------- |
| **Total project** | ~77%     |
| `app/services/`   | ~97%     |
| `app/models/`     | ~94%     |
| `app/blueprints/` | ~75%     |

Lihat [`docs/laporan_tugas3.md`](docs/laporan_tugas3.md) untuk detail hasil pengujian.

### Test Markers

Tersedia marker pytest:

- `unit` — Unit tests individual function/method
- `integration` — Integration tests (route + DB)
- `functional` — Functional tests (end-to-end)
- `security` — Security tests (CSRF, XSS, role isolation)
- `slow` — Test yang lambat (generate PDF/Excel)

```bash
pytest -m "unit" -v          # hanya unit tests
pytest -m "not slow" -v      # skip slow tests
```

---

## 📸 Screenshot

Lihat folder [`docs/screenshots/`](docs/screenshots/) untuk screenshot aplikasi. Template nama file dan instruksi tersedia di [`docs/screenshots/README.md`](docs/screenshots/README.md).

Screenshot yang tersedia/direncanakan:

| #   | File                     | Halaman                                   |
| --- | ------------------------ | ----------------------------------------- |
| 1   | `01_login.png`           | Halaman login                             |
| 2   | `02_dashboard_admin.png` | Dashboard admin dengan chart              |
| 3   | `03_dashboard_guru.png`  | Dashboard guru                            |
| 4   | `04_dashboard_siswa.png` | Dashboard siswa                           |
| 5   | `05_input_nilai.png`     | Form input nilai dengan preview live      |
| 6   | `06_rekap_nilai.png`     | Rekap nilai kelas dengan badge status     |
| 7   | `07_pdf_kelas.png`       | PDF laporan kelas (browser)               |
| 8   | `08_transkrip_pdf.png`   | PDF transkrip siswa                       |
| 9   | `09_excel_export.png`    | File Excel yang di-generate               |
| 10  | `10_pytest_output.png`   | Output pytest menunjukkan semua test PASS |
| 11  | `11_mysql_tables.png`    | Tabel database MySQL (≥3 tabel)           |

---

## 📚 Dokumentasi

Dokumen lengkap tersedia di folder `docs/`:

| Dokumen                                                    | Deskripsi                                           |
| ---------------------------------------------------------- | --------------------------------------------------- |
| [PRD.md](PRD.md)                                           | Product Requirements Document (spesifikasi lengkap) |
| [docs/laporan_tugas1.md](docs/laporan_tugas1.md)           | Laporan Tugas 1: Analisis & Perancangan             |
| [docs/laporan_tugas2.md](docs/laporan_tugas2.md)           | Laporan Tugas 2: Implementasi Program               |
| [docs/laporan_tugas3.md](docs/laporan_tugas3.md)           | Laporan Tugas 3: Pengujian & Dokumentasi            |
| [docs/seed_credentials.md](docs/seed_credentials.md)       | Daftar lengkap kredensial seed data                 |
| [docs/test_cases.md](docs/test_cases.md)                   | 25 skenario pengujian manual                        |
| [docs/debugging_log.md](docs/debugging_log.md)             | Log 5 bug yang ditemukan & diperbaiki               |
| [docs/schema.sql](docs/schema.sql)                         | DDL MySQL lengkap (referensi)                       |
| [docs/ERD.png](docs/ERD.png)                               | Entity Relationship Diagram                         |
| [docs/Use Case Diagram.png](docs/Use%20Case%20Diagram.png) | Use Case Diagram (3 aktor)                          |
| [docs/Class Diagram.png](docs/Class%20Diagram.png)         | Class Diagram OOP                                   |
| [docs/Wireframe.png](docs/Wireframe.png)                   | Wireframe UI                                        |

---

## 🤝 Kontribusi

Untuk kontribusi (pull request):

1. Fork repository
2. Buat branch fitur: `git checkout -b feature/nama-fitur`
3. Commit perubahan: `git commit -m "feat: tambah fitur X"`
4. Push branch: `git push origin feature/nama-fitur`
5. Buat Pull Request ke branch `develop`

Pastikan:

- ✅ Semua test pass (`pytest tests/ -v`)
- ✅ Tambahkan test untuk fitur baru
- ✅ Ikuti PEP 8 style guide
- ✅ Update dokumentasi jika perlu

---

## 📄 Lisensi

MIT License — Bebas digunakan untuk keperluan edukasi & non-komersial.

Lihat [LICENSE](LICENSE) untuk detail lengkap.

---

## 👥 Tim Pengembang

Dikembangkan sebagai bagian dari tugas **LSP (Lembaga Sertifikasi Profesi)** untuk sertifikasi pemrograman.

**Pemilik:** Niko Dwicahyo Widiyanto  
**Versi:** 1.0.0  
**Tahun:** 2026  
**Status:** Production-ready ✅

---

<p align="center">
  Created by Niko Dwicahyo Widiyanto and Made with Flask, SQLAlchemy, Bootstrap, and a lot of ☕
</p>
