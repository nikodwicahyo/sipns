# Laporan Tugas 2 — Implementasi Program SIPNS

**Sistem Informasi Pengolahan Nilai Siswa**
**Versi:** 1.0.0 | **Tahun:** 2026 | **Fase:** 2 (Tugas 2)
**Referensi:** [PRD.md](../../PRD.md) v1.0.0

---

## Daftar Isi

1. [Pendahuluan](#1-pendahuluan)
2. [Library & Framework yang Digunakan](#2-library--framework-yang-digunakan)
3. [Struktur Kode Program](#3-struktur-kode-program)
4. [Implementasi Fungsi Terstruktur](#4-implementasi-fungsi-terstruktur)
5. [Implementasi Class OOP](#5-implementasi-class-oop)
6. [Implementasi Antarmuka Pengguna](#6-implementasi-antarmuka-pengguna)
7. [Before/After Refactoring (Snippet Kode)](#7-beforeafter-refactoring-snippet-kode)
8. [Screenshot Antarmuka](#8-screenshot-antarmuka)

---

## 1. Pendahuluan

Tugas 2 membahas **implementasi teknis** SIPNS berdasarkan rancangan yang telah disusun di Tugas 1. Dokumen ini menjelaskan:

- Library & framework yang digunakan beserta justifikasinya
- Struktur direktori kode program
- Implementasi fungsi terstruktur inti (modul `services/`)
- Implementasi class OOP (modul `models/`)
- Implementasi antarmuka (modul `blueprints/` + `templates/` + `static/`)
- Contoh refactoring kode (sebelum & sesudah) untuk menunjukkan evolusi kualitas

**Konteks:**

- Total baris kode: **~5.800 baris** Python (estimasi)
- Total file Python: **35 file** (models, services, forms, blueprints, utils, config)
- Total test: **152 tests** (semua PASSING)
- Total halaman HTML: **24 templates** (Jinja2)
- Total endpoint: **45+ routes** (auth, admin, guru, siswa, laporan, API)

---

## 2. Library & Framework yang Digunakan

### 2.1 Tabel Dependensi (dari `requirements.txt`)

| Library              | Versi  | Fungsi                       | Justifikasi                                |
| -------------------- | ------ | ---------------------------- | ------------------------------------------ |
| **Flask**            | 3.1.0  | Web framework utama          | Ringan, mature, dokumentasi lengkap        |
| **Flask-Login**      | 0.6.3  | Manajemen session user       | Standar industri untuk Flask auth          |
| **Flask-WTF**        | 1.2.2  | Integrasi WTForms + CSRF     | CSRF protection built-in                   |
| **Flask-SQLAlchemy** | 3.1.1  | ORM untuk database           | Abstraksi DB, query Pythonic               |
| **SQLAlchemy**       | 2.0.36 | Core ORM                     | Dipakai langsung untuk query kompleks      |
| **WTForms**          | 3.2.1  | Validasi & rendering form    | Validasi server-side yang kuat             |
| **PyMySQL**          | 1.1.1  | MySQL driver (pure-Python)   | Tidak perlu kompilasi C di Windows         |
| **WeasyPrint**       | 61.2   | HTML → PDF generator         | CSS Paged Media support                    |
| **openpyxl**         | 3.1.5  | Generator file Excel (.xlsx) | Standar industri, ringan                   |
| **Jinja2**           | 3.1.5  | Template engine (built-in)   | Renderer HTML dinamis                      |
| **Werkzeug**         | 3.1.3  | WSGI utility (built-in)      | Password hashing, request handling         |
| **pytest**           | 8.3.4  | Framework testing            | Standar Python untuk unit/integration test |
| **pytest-flask**     | 1.3.0  | Plugin pytest untuk Flask    | Test client + fixtures                     |
| **python-dotenv**    | 1.0.1  | Load .env file               | Konfigurasi terpisah dari kode             |
| **cryptography**     | 44.0.0 | Dependensi transitif         | Untuk secure connection                    |

### 2.2 Frontend (CDN)

| Library             | Versi   | Fungsi                             | Sumber                                                    |
| ------------------- | ------- | ---------------------------------- | --------------------------------------------------------- |
| **Bootstrap**       | 5.3.2   | CSS framework                      | [getbootstrap.com](https://getbootstrap.com/)             |
| **Bootstrap Icons** | 1.11.3  | Icon set                           | [icons.getbootstrap.com](https://icons.getbootstrap.com/) |
| **jQuery**          | 3.7.1   | DOM manipulation (DataTables dep)  | [jquery.com](https://jquery.com/)                         |
| **DataTables**      | 2.1.8   | Tabel interaktif (sorting, paging) | [datatables.net](https://datatables.net/)                 |
| **Chart.js**        | 4.4.4   | Visualisasi chart (bar, doughnut)  | [chartjs.org](https://www.chartjs.org/)                   |
| **SweetAlert2**     | 11.10.5 | Notifikasi popup interaktif        | [sweetalert2.github.io](https://sweetalert2.github.io/)   |

> 📸 **Bukti screenshot library**: `![Library](screenshots/lib.png)`

### 2.3 Mengapa Flask dan Bukan Django?

| Aspek            | Flask                          | Django                      |
| ---------------- | ------------------------------ | --------------------------- |
| Kompleksitas     | **Mikro-framework** (modular)  | Full-stack (monolitik)      |
| ORM              | SQLAlchemy (mature, fleksibel) | Django ORM (kaku)           |
| Pembelajaran     | Lebih landai                   | Konvensi ketat              |
| Ukuran komunitas | Besar                          | Besar                       |
| Cocok untuk      | API + app kecil-menengah       | App besar (CMS, e-commerce) |
| Kebutuhan SIPNS  | ✅ Modular, ringan, mudah      | ❌ Overkill                 |

**Kesimpulan:** Flask dipilih karena SIPNS relatif kecil (5 tabel, 3 role) dan membutuhkan fleksibilitas tinggi.

---

## 3. Struktur Kode Program

### 3.1 Pohon Direktori

```
SIPNS/
├── app/
│   ├── __init__.py                  # Application factory
│   ├── config.py                    # Config class (dev/test/prod)
│   ├── seed.py                      # CLI seeder (flask seed)
│   ├── models/                      # ORM models
│   │   ├── __init__.py
│   │   ├── user.py                  # User
│   │   ├── siswa.py                 # Siswa
│   │   ├── guru.py                  # Guru
│   │   ├── nilai.py                 # Nilai (integrasi OOP↔terstruktur)
│   │   └── audit_log.py             # AuditLog
│   ├── services/                    # Business logic (TERSTRUKTUR)
│   │   ├── __init__.py
│   │   ├── nilai_service.py         # 5 fungsi inti
│   │   ├── audit_service.py         # Pencatatan log
│   │   └── laporan_service.py       # PDF + Excel generator
│   ├── forms/                       # WTForms classes
│   │   ├── __init__.py
│   │   ├── auth_forms.py            # LoginForm
│   │   ├── siswa_forms.py           # SiswaForm
│   │   ├── guru_forms.py            # GuruForm
│   │   ├── nilai_forms.py           # NilaiForm
│   │   └── user_forms.py            # 3 form manajemen user
│   ├── blueprints/                  # Route handlers (MVC Controller)
│   │   ├── __init__.py
│   │   ├── decorators.py            # @role_required
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   └── routes.py            # login, logout
│   │   ├── admin/
│   │   │   ├── __init__.py
│   │   │   └── routes.py            # 16 routes + 3 API
│   │   ├── guru/
│   │   │   ├── __init__.py
│   │   │   └── routes.py            # 5 routes
│   │   ├── siswa/
│   │   │   ├── __init__.py
│   │   │   └── routes.py            # 3 routes
│   │   └── laporan/
│   │       ├── __init__.py
│   │       └── routes.py            # 4 routes
│   ├── utils/                       # Utilities
│   │   ├── __init__.py
│   │   ├── constants.py             # KKM, BOBOT, RENTANG, PASSWORD
│   │   └── time.py                  # timestamp_now(), format_id()
│   ├── templates/                   # Jinja2 templates
│   │   ├── base.html
│   │   ├── auth/
│   │   │   └── login.html
│   │   ├── admin/                   # 12 templates
│   │   ├── guru/                    # 4 templates
│   │   ├── siswa/                   # 3 templates
│   │   └── laporan/                 # 2 templates (HTML+PDF)
│   └── static/
│       ├── css/
│       │   └── custom.css
│       ├── js/
│       │   └── main.js
│       └── img/
├── tests/                           # 152 tests
│   ├── conftest.py
│   ├── unit/
│   │   ├── test_nilai_service.py    # 30 tests
│   │   ├── test_models.py           # 34 tests
│   │   └── test_laporan.py          # 14 tests
│   └── integration/
│       ├── test_auth.py
│       ├── test_siswa.py
│       ├── test_nilai.py
│       ├── test_security.py         # 30 tests
│       └── test_laporan.py
├── docs/                            # Dokumentasi
│   ├── PRD.md
│   ├── schema.sql
│   ├── debugging_log.md
│   ├── test_cases.md
│   ├── seed_credentials.md
│   ├── laporan_tugas1.md
│   ├── laporan_tugas2.md
│   └── laporan_tugas3.md
├── venv/                            # Python virtual env
├── requirements.txt
├── pytest.ini
├── run.py                           # Entry point
├── .env.example
├── .gitignore
└── README.md
```

### 3.2 Diagram Arsitektur 3-Layer

```
┌─────────────────────────────────────────────────────────────┐
│                  PRESENTATION LAYER                          │
│  - Templates (Jinja2): base.html + per-bp                   │
│  - Static (CSS/JS): Bootstrap 5, DataTables, Chart.js       │
│  - Client-side: input validation, AJAX preview              │
└─────────────────────────────────────────────────────────────┘
                          ▲   ▼
┌─────────────────────────────────────────────────────────────┐
│                  APPLICATION LAYER                           │
│  - Blueprints (routes): auth, admin, guru, siswa, laporan   │
│  - Forms (WTForms): validasi server-side + CSRF token       │
│  - Decorators: @login_required, @role_required              │
└─────────────────────────────────────────────────────────────┘
                          ▲   ▼
┌─────────────────────────────────────────────────────────────┐
│                  BUSINESS LOGIC LAYER                        │
│  - Services (fungsi terstruktur):                           │
│      • nilai_service: hitung, status, statistik            │
│      • laporan_service: PDF, Excel                          │
│      • audit_service: catat_audit_log                       │
│  - Models (class OOP): User, Siswa, Guru, Nilai, AuditLog  │
└─────────────────────────────────────────────────────────────┘
                          ▲   ▼
┌─────────────────────────────────────────────────────────────┐
│                  DATA ACCESS LAYER                           │
│  - SQLAlchemy ORM (db.session)                              │
│  - DB: SQLite (test) / MySQL (production)                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Implementasi Fungsi Terstruktur

> **Prinsip:** Fungsi murni, single-responsibility, input → output deterministik.

### 4.1 Modul `app/services/nilai_service.py`

#### Fungsi: `validasi_rentang_nilai()`

**Kegunaan:** Memvalidasi tipe data dan rentang nilai (0-100).

**Lokasi:** [`app/services/nilai_service.py:23-66`](../../app/services/nilai_service.py)

```python
def validasi_rentang_nilai(nilai: float, label: str = "Nilai") -> bool:
    """
    Validasi tipe data dan rentang nilai (0-100).

    Args:
        nilai: Nilai yang akan divalidasi (numerik).
        label: Label field untuk pesan error (default: "Nilai").

    Returns:
        True jika nilai valid.

    Raises:
        TypeError: Jika nilai bukan numerik.
        ValueError: Jika nilai di luar rentang 0-100.

    Example:
        >>> validasi_rentang_nilai(85.0, "Tugas")
        True
        >>> validasi_rentang_nilai(120, "UTS")
        ValueError: UTS harus berada di rentang 0-100. Diberikan: 120
    """
    # 1. Tipe data harus numerik (bukan string / None)
    if not isinstance(nilai, (int, float)):
        raise TypeError(
            f"{label} harus berupa angka. Diberikan: {type(nilai).__name__}"
        )

    # 2. Tidak boleh NaN
    if isinstance(nilai, float) and math.isnan(nilai):
        raise ValueError(f"{label} tidak boleh NaN")

    # 3. Harus dalam rentang 0-100 (inklusif)
    if not (RENTANG_NILAI_MIN <= nilai <= RENTANG_NILAI_MAX):
        raise ValueError(
            f"{label} harus berada di rentang "
            f"{RENTANG_NILAI_MIN}-{RENTANG_NILAI_MAX}. "
            f"Diberikan: {nilai}"
        )

    return True
```

**Tes terkait:** `tests/unit/test_nilai_service.py::TestValidasiRentangNilai` (8 test PASS)

#### Fungsi: `hitung_nilai_akhir()`

**Kegunaan:** Hitung nilai akhir dengan formula `0.30×Tugas + 0.30×UTS + 0.40×UAS`.

**Lokasi:** [`app/services/nilai_service.py:69-115`](../../app/services/nilai_service.py)

```python
def hitung_nilai_akhir(
    nilai_tugas: float,
    nilai_uts: float,
    nilai_uas: float,
) -> float:
    """
    Hitung nilai akhir siswa berdasarkan bobot komponen.

    Formula: NA = 0.30 × Tugas + 0.30 × UTS + 0.40 × UAS

    Args:
        nilai_tugas: Nilai tugas (0-100).
        nilai_uts: Nilai UTS (0-100).
        nilai_uas: Nilai UAS (0-100).

    Returns:
        Nilai akhir (float), dibulatkan ke 2 desimal (PEMBULATAN_DESIMAL).

    Raises:
        TypeError: Jika input bukan numerik.
        ValueError: Jika input di luar rentang 0-100.

    Example:
        >>> hitung_nilai_akhir(80, 75, 90)
        82.5
    """
    # Validasi semua komponen sebelum kalkulasi
    validasi_rentang_nilai(nilai_tugas, "Nilai Tugas")
    validasi_rentang_nilai(nilai_uts, "Nilai UTS")
    validasi_rentang_nilai(nilai_uas, "Nilai UAS")

    # Hitung nilai akhir dengan bobot (konstanta dari utils/constants.py)
    nilai_akhir_raw = (
        (BOBOT_TUGAS * nilai_tugas)
        + (BOBOT_UTS * nilai_uts)
        + (BOBOT_UAS * nilai_uas)
    )

    # Bulatkan sesuai aturan (PEMBULATAN_DESIMAL = 2)
    return round(nilai_akhir_raw, PEMBULATAN_DESIMAL)
```

**Tes terkait:** `TestHitungNilaiAkhir` (10 test PASS)

#### Fungsi: `tentukan_status_kelulusan()`

**Kegunaan:** Tentukan status Lulus/Tidak Lulus berdasarkan KKM (default 70).

**Lokasi:** [`app/services/nilai_service.py:118-142`](../../app/services/nilai_service.py)

```python
def tentukan_status_kelulusan(
    nilai_akhir: float,
    kkm: float = KKM,  # Default 70
) -> dict:
    """
    Tentukan status kelulusan siswa berdasarkan KKM.

    Args:
        nilai_akhir: Nilai akhir siswa (0-100).
        kkm: Kriteria Ketuntasan Minimal (default dari konstanta KKM=70).

    Returns:
        dict: {
            'lulus': bool,
            'label': str ('LULUS' / 'TIDAK LULUS'),
            'badge_class': str (Bootstrap class),
            'selisih': float (nilai_akhir - kkm)
        }

    Example:
        >>> tentukan_status_kelulusan(85.0)
        {'lulus': True, 'label': 'LULUS', 'badge_class': 'bg-success', 'selisih': 15.0}
    """
    # Hitung selisih (positif = di atas KKM)
    selisih = round(nilai_akhir - kkm, PEMBULATAN_DESIMAL)
    lulus = nilai_akhir >= kkm

    return {
        'lulus': lulus,
        'label': 'LULUS' if lulus else 'TIDAK LULUS',
        'badge_class': 'bg-success' if lulus else 'bg-danger',
        'selisih': selisih,
    }
```

**Tes terkait:** `TestTentukanStatusKelulusan` (7 test PASS)

#### Fungsi: `generate_laporan_pdf()`

**Kegunaan:** Generate PDF rekap nilai per kelas via WeasyPrint.

**Lokasi:** [`app/services/laporan_service.py:54-105`](../../app/services/laporan_service.py)

```python
def generate_laporan_pdf(
    kelas: str,
    template: str = 'laporan/rekap_kelas.html',
) -> bytes:
    """
    Generate PDF rekap nilai per kelas.

    Args:
        kelas: Nama kelas (mis. 'X-IPA-1').
        template: Path template Jinja2 (default laporan/rekap_kelas.html).

    Returns:
        bytes: Konten file PDF.

    Raises:
        ValueError: Jika kelas kosong atau tidak ada data.
    """
    if not kelas:
        raise ValueError("Kelas tidak boleh kosong")

    # Lazy import untuk menghindari circular dependency
    from app.models.nilai import Nilai
    from app.models.siswa import Siswa

    # 1. Query data nilai JOIN siswa, filter kelas & not deleted
    data_nilai = (
        Nilai.query
        .join(Siswa, Nilai.siswa_id == Siswa.id)
        .filter(Siswa.kelas == kelas, Siswa.deleted_at.is_(None))
        .all()
    )

    if not data_nilai:
        raise ValueError(f"Tidak ada data nilai untuk kelas {kelas}")

    # 2. Hitung statistik
    statistik = hitung_statistik_kelas([n.to_dict() for n in data_nilai])

    # 3. Render template ke HTML string
    html_string = render_template(
        template,
        kelas=kelas,
        data_nilai=data_nilai,
        statistik=statistik,
        tanggal_cetak=datetime.now().strftime("%d %B %Y"),
    )

    # 4. Convert HTML ke PDF
    pdf_bytes = HTML(string=html_string).write_pdf()

    logger.info(f"PDF rekap kelas {kelas} di-generate ({len(pdf_bytes)} bytes)")
    return pdf_bytes
```

**Tes terkait:** `tests/integration/test_laporan.py::TestLaporanPDF` (6 test PASS)

#### Fungsi: `hitung_statistik_kelas()`

**Kegunaan:** Hitung statistik agregat nilai kelas (total, rata-rata, %, dll).

**Lokasi:** [`app/services/nilai_service.py:145-187`](../../app/services/nilai_service.py)

```python
def hitung_statistik_kelas(data_nilai: list) -> dict:
    """
    Hitung statistik agregat nilai dari list data nilai.

    Args:
        data_nilai: List of dict nilai (setiap dict harus punya 'nilai_akhir').

    Returns:
        dict: {
            'total_siswa': int,
            'rata_rata': float,
            'tertinggi': float,
            'terendah': float,
            'jumlah_lulus': int,
            'jumlah_tidak_lulus': int,
            'persen_lulus': float,
            'persen_tidak_lulus': float
        }
    """
    if not data_nilai:
        return {
            'total_siswa': 0,
            'rata_rata': 0.0,
            'tertinggi': 0.0,
            'terendah': 0.0,
            'jumlah_lulus': 0,
            'jumlah_tidak_lulus': 0,
            'persen_lulus': 0.0,
            'persen_tidak_lulus': 0.0,
        }

    nilai_akhir_list = [d['nilai_akhir'] for d in data_nilai]
    jumlah_lulus = sum(1 for n in nilai_akhir_list if n >= KKM)
    total = len(nilai_akhir_list)

    return {
        'total_siswa': total,
        'rata_rata': round(sum(nilai_akhir_list) / total, PEMBULATAN_DESIMAL),
        'tertinggi': max(nilai_akhir_list),
        'terendah': min(nilai_akhir_list),
        'jumlah_lulus': jumlah_lulus,
        'jumlah_tidak_lulus': total - jumlah_lulus,
        'persen_lulus': round((jumlah_lulus / total) * 100, PEMBULATAN_DESIMAL),
        'persen_tidak_lulus': round(((total - jumlah_lulus) / total) * 100, PEMBULATAN_DESIMAL),
    }
```

**Tes terkait:** `TestHitungStatistikKelas` (5 test PASS)

### 4.2 Modul `app/services/audit_service.py`

#### Fungsi: `catat_audit_log()`

**Kegunaan:** Catat aktivitas user ke tabel `audit_log` (INSERT).

**Lokasi:** [`app/services/audit_service.py`](../../app/services/audit_service.py)

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
    Catat aktivitas user ke tabel audit_log (side-effect: INSERT ke DB).

    Args:
        user_id: ID user yang melakukan aksi.
        action: Jenis aksi (INSERT/UPDATE/DELETE/LOGIN/LOGOUT/PRINT_PDF/EXPORT_EXCEL).
        table_name: Nama tabel yang terkait (atau 'auth'/'system').
        record_id: ID record (opsional).
        description: Deskripsi tambahan (opsional).
        ip_address: IP address user (opsional, akan terisi otomatis dari request).
    """
    # Validasi action sesuai ENUM
    valid_actions = ['INSERT', 'UPDATE', 'DELETE', 'LOGIN', 'LOGOUT',
                     'PRINT_PDF', 'EXPORT_EXCEL']
    if action not in valid_actions:
        raise ValueError(f"Action tidak valid: {action}")

    # Auto-detect IP address jika tidak diisi
    if ip_address is None:
        from flask import request
        try:
            ip_address = request.remote_addr
        except RuntimeError:
            ip_address = 'system'  # CLI context (mis. seed)

    # Buat entry baru
    log = AuditLog(
        user_id=user_id,
        action=action,
        table_name=table_name,
        record_id=record_id,
        description=description,
        ip_address=ip_address,
    )
    db.session.add(log)
    db.session.commit()
    logger.info(f"Audit: user={user_id} action={action} table={table_name}")
```

---

## 5. Implementasi Class OOP

> **Prinsip:** SQLAlchemy ORM, encapsulation via properties/methods, inheritance dari `db.Model` dan `UserMixin`.

### 5.1 Class `Nilai` — Titik Integrasi OOP ↔ Terstruktur

**Lokasi:** [`app/models/nilai.py`](../../app/models/nilai.py)

```python
class Nilai(db.Model):
    """
    Model ORM untuk tabel `nilai`.

    Attributes:
        id (int): Primary key auto-increment.
        siswa_id (int): FK ke tabel siswa.
        guru_id (int): FK ke tabel guru.
        mata_pelajaran (str): Nama mata pelajaran (mis. 'Matematika').
        nilai_tugas (float): Nilai tugas (0-100).
        nilai_uts (float): Nilai UTS (0-100).
        nilai_uas (float): Nilai UAS (0-100).
        nilai_akhir (float): Nilai akhir terhitung (0-100).
        status_lulus (bool): True jika >= KKM.
        is_locked (bool): True jika nilai sudah dikunci guru.
        created_at (datetime): Timestamp dibuat.
        updated_at (datetime): Timestamp diubah.

    Constraints:
        UNIQUE(siswa_id, mata_pelajaran): Satu siswa satu nilai per mapel.
        CHECK (0 <= nilai_xxx <= 100): Defense in depth (server + DB).

    Relasi:
        siswa: many-to-one ke Siswa (lazy='joined').
        guru: many-to-one ke Guru (lazy='joined').
    """

    __tablename__ = 'nilai'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    siswa_id = db.Column(
        db.Integer,
        db.ForeignKey('siswa.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    guru_id = db.Column(
        db.Integer,
        db.ForeignKey('guru.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    mata_pelajaran = db.Column(db.String(100), nullable=False, index=True)

    # Kolom nilai (range 0-100, desimal diperbolehkan)
    nilai_tugas = db.Column(db.Float, nullable=False)
    nilai_uts = db.Column(db.Float, nullable=False)
    nilai_uas = db.Column(db.Float, nullable=False)
    nilai_akhir = db.Column(db.Float, nullable=False)
    status_lulus = db.Column(db.Boolean, nullable=False, default=False)
    is_locked = db.Column(db.Boolean, nullable=False, default=False)

    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )

    # Relasi
    siswa = db.relationship('Siswa', backref=db.backref('nilai', lazy='dynamic'))
    guru = db.relationship('Guru', backref=db.backref('nilai_diinput', lazy='dynamic'))

    # Constraint: satu siswa satu nilai per mata pelajaran
    __table_args__ = (
        db.UniqueConstraint('siswa_id', 'mata_pelajaran', name='uq_siswa_mapel'),
    )

    def hitung_dan_simpan(self) -> None:
        """
        Hitung nilai akhir & status kelulusan, lalu simpan ke instance.

        **INTEGRASI OOP ↔ TERSTRUKTUR:**
        Metode ini mendemonstrasikan **Titik Integrasi** antara class OOP
        dan fungsi terstruktur. Logika kalkulasi murni didelegasikan ke
        `nilai_service.hitung_nilai_akhir()` dan `nilai_service.tentukan_status_kelulusan()`.

        Side-effect: mengubah self.nilai_akhir dan self.status_lulus.
        """
        # Delegasi ke fungsi terstruktur (PEMROGRAMAN TERSTRUKTUR)
        self.nilai_akhir = hitung_nilai_akhir(
            self.nilai_tugas, self.nilai_uts, self.nilai_uas
        )
        status = tentukan_status_kelulusan(self.nilai_akhir)
        self.status_lulus = status['lulus']

    def lock(self) -> None:
        """Kunci nilai agar tidak bisa diedit."""
        self.is_locked = True

    def unlock(self) -> None:
        """Buka kunci nilai (admin only)."""
        self.is_locked = False

    def get_detail_kalkulasi(self) -> dict:
        """
        Kembalikan detail kalkulasi nilai untuk ditampilkan ke siswa.

        Returns:
            dict: {tugas, uts, uas, nilai_akhir, status_lulus, kkm, selisih}
        """
        return {
            'tugas': self.nilai_tugas,
            'uts': self.nilai_uts,
            'uas': self.nilai_uas,
            'nilai_akhir': self.nilai_akhir,
            'status_lulus': 'LULUS' if self.status_lulus else 'TIDAK LULUS',
            'kkm': KKM,
            'selisih': round(self.nilai_akhir - KKM, PEMBULATAN_DESIMAL),
        }

    def to_dict(self) -> dict:
        """Serialisasi objek ke dict (untuk JSON response)."""
        return {
            'id': self.id,
            'siswa_id': self.siswa_id,
            'guru_id': self.guru_id,
            'mata_pelajaran': self.mata_pelajaran,
            'nilai_tugas': self.nilai_tugas,
            'nilai_uts': self.nilai_uts,
            'nilai_uas': self.nilai_uas,
            'nilai_akhir': self.nilai_akhir,
            'status_lulus': self.status_lulus,
            'is_locked': self.is_locked,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return (
            f"<Nilai id={self.id} siswa_id={self.siswa_id} "
            f"mapel='{self.mata_pelajaran}' akhir={self.nilai_akhir}>"
        )
```

### 5.2 Class `Siswa`

**Lokasi:** [`app/models/siswa.py`](../../app/models/siswa.py)

```python
class Siswa(db.Model):
    """
    Model ORM untuk tabel `siswa` (data siswa).

    Attributes:
        id (int): Primary key.
        nis (str): Nomor Induk Siswa (UNIQUE, immutable).
        nama (str): Nama lengkap siswa.
        kelas (str): Kelas siswa (mis. 'X-IPA-1').
        user_id (int): FK ke User (one-to-one untuk login).
        deleted_at (datetime): Soft-delete timestamp.

    Methods:
        - status_kelulusan_global(): 'Lulus'/'Tidak Lulus'/'Belum Ada Nilai'
        - soft_delete(): Tandai siswa sebagai dihapus.
        - cari_by_nis(nis) (classmethod): Cari siswa by NIS.
    """

    __tablename__ = 'siswa'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nis = db.Column(db.String(20), unique=True, nullable=False, index=True)
    nama = db.Column(db.String(100), nullable=False)
    kelas = db.Column(db.String(20), nullable=False, index=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
    )

    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )
    deleted_at = db.Column(db.DateTime, nullable=True)  # Soft delete

    def status_kelulusan_global(self) -> str:
        """
        Tentukan status kelulusan GLOBAL siswa (rata-rata semua mapel).

        Returns:
            'Lulus' / 'Tidak Lulus' / 'Belum Ada Nilai'
        """
        # Lazy import untuk hindari circular import
        from app.models.nilai import Nilai

        # Filter nilai yang tidak di-soft-delete (semuanya, karena nilai belum ada soft-delete)
        nilai_list = Nilai.query.filter(
            Nilai.siswa_id == self.id
        ).all()

        if not nilai_list:
            return 'Belum Ada Nilai'

        # Hitung rata-rata nilai akhir
        rata_rata = sum(n.nilai_akhir for n in nilai_list) / len(nilai_list)

        # Tentukan status
        return 'Lulus' if rata_rata >= KKM else 'Tidak Lulus'

    def soft_delete(self) -> None:
        """Tandai siswa sebagai dihapus (soft delete)."""
        self.deleted_at = datetime.now()

    @classmethod
    def cari_by_nis(cls, nis: str) -> Optional['Siswa']:
        """Cari siswa berdasarkan NIS (return None jika tidak ada / dihapus)."""
        return cls.query.filter(
            cls.nis == nis, cls.deleted_at.is_(None)
        ).first()

    @classmethod
    def daftar_kelas(cls) -> list:
        """Kembalikan daftar kelas unik (distinct)."""
        result = db.session.query(cls.kelas).filter(
            cls.deleted_at.is_(None)
        ).distinct().order_by(cls.kelas).all()
        return [r[0] for r in result]

    def __repr__(self) -> str:
        return f"<Siswa id={self.id} nis='{self.nis}' nama='{self.nama}' kelas='{self.kelas}'>"
```

### 5.3 Diagram Class Sederhana

```
                  ┌──────────────────────┐
                  │     User             │
                  ├──────────────────────┤
                  │ +id, username        │
                  │ +role, is_active     │
                  │ +siswa_id, guru_id   │
                  ├──────────────────────┤
                  │ +set_password()      │
                  │ +check_password()    │
                  │ +is_admin()          │
                  └──────────┬───────────┘
                             │ 1
                             │
        ┌────────────────────┼────────────────────┐
        │ 1                  │ 1                  │ *
        ▼                    ▼                    ▼
┌────────────────┐   ┌────────────────┐   ┌────────────────┐
│     Siswa      │   │     Guru       │   │   AuditLog     │
├────────────────┤   ├────────────────┤   ├────────────────┤
│ +id, nis       │   │ +id, id_guru   │   │ +id, user_id   │
│ +nama, kelas   │   │ +nama_guru     │   │ +action        │
│ +user_id       │   │ +mata_pelajaran│   │ +table_name    │
├────────────────┤   ├────────────────┤   ├────────────────┤
│ +soft_delete() │   │ +soft_delete() │   │ +log()         │
│ +cari_by_nis() │   └────────┬───────┘   └────────────────┘
│ +status_lulus()│            │ 1
└───────┬────────┘            │
        │ *                   │ *
        │                     │
        │       ┌─────────────┴───────────┐
        └──────►│         Nilai           │◄────────┐
                ├─────────────────────────┤         │
                │ +id, siswa_id, guru_id  │         │
                │ +mata_pelajaran         │         │
                │ +nilai_tugas/uts/uas    │         │
                │ +nilai_akhir            │         │
                │ +status_lulus, is_locked│         │
                ├─────────────────────────┤         │
                │ +hitung_dan_simpan() ★  │         │
                │ +lock(), unlock()       │         │
                │ +get_detail_kalkulasi() │         │
                └─────────────────────────┘         │
                                                    │
        ★ = Titik Integrasi OOP ↔ Terstruktur     │
            (delegasi ke nilai_service.py)         │
```

> 📊 Lihat Class Diagram lengkap: [`docs/Class Diagram.png`](../Class%20Diagram.png)

---

## 6. Implementasi Antarmuka Pengguna

### 6.1 Template Engine (Jinja2)

**Base template (`app/templates/base.html`):**

```html
<!DOCTYPE html>
<html lang="id">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{% block title %}SIPNS{% endblock %} - SIPNS</title>

    <!-- Bootstrap 5.3 -->
    <link
      href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css"
      rel="stylesheet"
    />
    <link
      href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css"
      rel="stylesheet"
    />

    <!-- DataTables -->
    <link
      href="https://cdn.datatables.net/2.1.8/css/dataTables.bootstrap5.css"
      rel="stylesheet"
    />

    {% block extra_css %}{% endblock %}
  </head>
  <body>
    {% include 'partials/navbar.html' %}

    <main class="container py-4">
      <!-- Flash messages -->
      {% with messages = get_flashed_messages(with_categories=true) %} {% if
      messages %} {% for category, message in messages %}
      <div class="alert alert-{{ category }} alert-dismissible fade show">
        {{ message }}
        <button
          type="button"
          class="btn-close"
          data-bs-dismiss="alert"
        ></button>
      </div>
      {% endfor %} {% endif %} {% endwith %} {% block content %}{% endblock %}
    </main>

    <!-- Scripts -->
    <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.datatables.net/2.1.8/js/dataTables.js"></script>
    <script src="https://cdn.datatables.net/2.1.8/js/dataTables.bootstrap5.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11.10.5/dist/sweetalert2.all.min.js"></script>
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>

    {% block extra_js %}{% endblock %}
  </body>
</html>
```

### 6.2 Contoh Halaman: Login (`app/templates/auth/login.html`)

```html
{% extends "base.html" %} {% block title %}Login{% endblock %} {% block content
%}
<div class="row justify-content-center mt-5">
  <div class="col-md-5">
    <div class="card shadow">
      <div class="card-body p-5">
        <h2 class="text-center mb-4">
          <i class="bi bi-mortarboard-fill text-primary"></i>
          SIPNS
        </h2>
        <p class="text-center text-muted">
          Sistem Informasi Pengolahan Nilai Siswa
        </p>

        <form method="POST" action="{{ url_for('auth.login') }}" novalidate>
          {{ form.hidden_tag() }}
          <!-- CSRF token -->

          <div class="mb-3">
            {{ form.username.label(class="form-label") }} {{
            form.username(class="form-control form-control-lg",
            placeholder="Username / NIS / ID Guru") }} {% for err in
            form.username.errors %}
            <small class="text-danger">{{ err }}</small>
            {% endfor %}
          </div>

          <div class="mb-3">
            {{ form.password.label(class="form-label") }} {{
            form.password(class="form-control form-control-lg",
            placeholder="Password") }} {% for err in form.password.errors %}
            <small class="text-danger">{{ err }}</small>
            {% endfor %}
          </div>

          <div class="d-grid">
            {{ form.submit(class="btn btn-primary btn-lg") }}
          </div>
        </form>

        <div class="mt-4 text-muted small">
          <strong>Akun Default (dev):</strong><br />
          Admin: <code>admin</code> / <code>admin123</code><br />
          Guru: <code>GR-001</code> / <code>guru123</code><br />
          Siswa: <code>2024001</code> / <code>2024001</code>
        </div>
      </div>
    </div>
  </div>
</div>
{% endblock %}
```

### 6.3 Contoh Halaman: Input Nilai (AJAX Live Preview)

**Halaman:** `app/templates/guru/input_nilai.html`

```html
<form method="POST" id="formNilai" action="{{ url_for('guru.input_nilai') }}">
  {{ form.hidden_tag() }}

  <div class="row">
    <div class="col-md-6">
      {{ form.siswa_id.label(class="form-label") }} {{
      form.siswa_id(class="form-select") }}
    </div>
    <div class="col-md-6">
      <label class="form-label">Mata Pelajaran</label>
      <input
        type="text"
        class="form-control"
        value="{{ current_user.guru.mata_pelajaran }}"
        readonly
      />
    </div>
  </div>

  <div class="row mt-3">
    <div class="col-md-4">
      {{ form.nilai_tugas.label(class="form-label") }} {{
      form.nilai_tugas(class="form-control nilai-input", min=0, max=100,
      step=0.01) }}
    </div>
    <div class="col-md-4">
      {{ form.nilai_uts.label(class="form-label") }} {{
      form.nilai_uts(class="form-control nilai-input", min=0, max=100,
      step=0.01) }}
    </div>
    <div class="col-md-4">
      {{ form.nilai_uas.label(class="form-label") }} {{
      form.nilai_uas(class="form-control nilai-input", min=0, max=100,
      step=0.01) }}
    </div>
  </div>

  <!-- Live Preview -->
  <div class="card mt-4 bg-light">
    <div class="card-body">
      <h6>Preview Kalkulasi</h6>
      <div class="row text-center">
        <div class="col-md-4">
          <small class="text-muted">Nilai Akhir</small>
          <h3 id="previewNilaiAkhir" class="text-primary">-</h3>
        </div>
        <div class="col-md-4">
          <small class="text-muted">KKM</small>
          <h3 class="text-muted">70</h3>
        </div>
        <div class="col-md-4">
          <small class="text-muted">Status</small>
          <h3 id="previewStatus"><span class="badge bg-secondary">-</span></h3>
        </div>
      </div>
    </div>
  </div>

  <div class="mt-4 d-flex justify-content-end">
    <a href="{{ url_for('guru.dashboard') }}" class="btn btn-secondary me-2"
      >Batal</a
    >
    {{ form.submit(class="btn btn-primary") }}
  </div>
</form>

{% block extra_js %}
<script>
  // Live preview via AJAX
  const inputs = document.querySelectorAll(".nilai-input");
  inputs.forEach((input) => {
    input.addEventListener("input", updatePreview);
  });

  function updatePreview() {
    const t = parseFloat(document.getElementById("nilai_tugas").value) || 0;
    const u = parseFloat(document.getElementById("nilai_uts").value) || 0;
    const a = parseFloat(document.getElementById("nilai_uas").value) || 0;

    if (t === 0 && u === 0 && a === 0) {
      document.getElementById("previewNilaiAkhir").textContent = "-";
      document.getElementById("previewStatus").innerHTML =
        '<span class="badge bg-secondary">-</span>';
      return;
    }

    // Validasi range
    if (t < 0 || t > 100 || u < 0 || u > 100 || a < 0 || a > 100) {
      document.getElementById("previewNilaiAkhir").textContent = "Invalid";
      document.getElementById("previewStatus").innerHTML =
        '<span class="badge bg-danger">Invalid</span>';
      return;
    }

    // Hitung di client
    const akhir = (0.3 * t + 0.3 * u + 0.4 * a).toFixed(2);
    const status = akhir >= 70 ? "LULUS" : "TIDAK LULUS";
    const cls = akhir >= 70 ? "bg-success" : "bg-danger";

    document.getElementById("previewNilaiAkhir").textContent = akhir;
    document.getElementById("previewStatus").innerHTML =
      `<span class="badge ${cls}">${status}</span>`;
  }
</script>
{% endblock %}
```

---

## 7. Before/After Refactoring (Snippet Kode)

### 7.1 Refactor #1: Menghilangkan Magic Numbers

**❌ SEBELUM** (`app/services/nilai_service.py` — versi awal):

```python
def hitung_nilai_akhir(nilai_tugas, nilai_uts, nilai_uas):
    if not (0 <= nilai_tugas <= 100):
        raise ValueError("Nilai tugas harus 0-100")
    if not (0 <= nilai_uts <= 100):
        raise ValueError("Nilai UTS harus 0-100")
    if not (0 <= nilai_uas <= 100):
        raise ValueError("Nilai UAS harus 0-100")

    # Magic numbers!
    akhir = (0.30 * nilai_tugas) + (0.30 * nilai_uts) + (0.40 * nilai_uas)
    return round(akhir, 2)


def tentukan_status_kelulusan(nilai_akhir):
    # Magic number 70!
    if nilai_akhir >= 70:
        return {'lulus': True, 'label': 'LULUS'}
    else:
        return {'lulus': False, 'label': 'TIDAK LULUS'}
```

**✅ SESUDAH** (menggunakan `app/utils/constants.py`):

```python
from app.utils.constants import (
    KKM, BOBOT_TUGAS, BOBOT_UTS, BOBOT_UAS,
    RENTANG_NILAI_MIN, RENTANG_NILAI_MAX, PEMBULATAN_DESIMAL
)

def hitung_nilai_akhir(nilai_tugas, nilai_uts, nilai_uas):
    # Reuse validasi
    validasi_rentang_nilai(nilai_tugas, "Nilai Tugas")
    validasi_rentang_nilai(nilai_uts, "Nilai UTS")
    validasi_rentang_nilai(nilai_uas, "Nilai UAS")

    # Konstanta dari utils/constants.py
    akhir = (BOBOT_TUGAS * nilai_tugas) + (BOBOT_UTS * nilai_uts) + (BOBOT_UAS * nilai_uas)
    return round(akhir, PEMBULATAN_DESIMAL)


def tentukan_status_kelulusan(nilai_akhir, kkm=KKM):
    # Pakai konstanta KKM
    lulus = nilai_akhir >= kkm
    return {
        'lulus': lulus,
        'label': 'LULUS' if lulus else 'TIDAK LULUS',
        'badge_class': 'bg-success' if lulus else 'bg-danger',
        'selisih': round(nilai_akhir - kkm, PEMBULATAN_DESIMAL),
    }
```

**Keuntungan:**

- ✅ Single source of truth (KKM, bobot, rentang) di `constants.py`
- ✅ Perubahan 1 tempat untuk semua aturan bisnis
- ✅ Self-documenting (BOBOT_TUGAS jelas maknanya)
- ✅ Mudah testing (bisa override di test)

### 7.2 Refactor #2: Mengganti `print()` dengan `logger`

**❌ SEBELUM** (`app/models/audit_log.py`):

```python
def log(user_id, action, table_name):
    log_entry = AuditLog(user_id=user_id, action=action, table_name=table_name)
    db.session.add(log_entry)
    db.session.commit()
    print(f"[AUDIT] user={user_id} action={action}")  # ← Masalah: print ke stdout
```

**✅ SESUDAH**:

```python
import logging
logger = logging.getLogger(__name__)

def log(user_id, action, table_name):
    log_entry = AuditLog(user_id=user_id, action=action, table_name=table_name)
    db.session.add(log_entry)
    db.session.commit()
    logger.info(f"Audit: user={user_id} action={action} table={table_name}")  # ← Best practice
```

**Keuntungan:**

- ✅ Bisa diset level (DEBUG/INFO/WARNING/ERROR)
- ✅ Otomatis muncul timestamp & level
- ✅ Bisa diarahkan ke file log
- ✅ Bisa difilter sesuai environment (dev vs prod)

### 7.3 Refactor #3: Lazy Import untuk Circular Dependency

**❌ SEBELUM** (`app/services/laporan_service.py`):

```python
from app.models.nilai import Nilai  # ← Import di top-level
from app.models.siswa import Siswa  # ← Import di top-level

def generate_laporan_pdf(kelas):
    data = Nilai.query.join(Siswa).filter(...).all()  # ← ImportError di app startup
```

**Penyebab error:** `app/models/nilai.py` mengimpor `nilai_service` di top-level, sehingga ketika `app/models/__init__.py` memuat `Nilai`, modul `nilai_service` (yang memuat `laporan_service`) sedang di-load → partial module → `ImportError`.

**✅ SESUDAH**:

```python
def generate_laporan_pdf(kelas):
    # Lazy import HANYA saat fungsi dipanggil (bukan saat modul di-load)
    from app.models.nilai import Nilai
    from app.models.siswa import Siswa

    data = Nilai.query.join(Siswa).filter(...).all()
```

**Keuntungan:**

- ✅ Menghindari circular import 100%
- ✅ Startup time lebih cepat (import ditunda)
- ✅ Test independence meningkat

---

## 8. Screenshot Antarmuka

> **Catatan:** Semua screenshot di bawah ini adalah **placeholder** yang akan diisi secara manual oleh pengguna dengan tangkapan layar aplikasi SIPNS yang sedang berjalan.

### 8.1 Halaman Login

![Screenshots: Halaman Login SIPNS](screenshots/01_login.png)

> Tampilan halaman login dengan form username & password. Terdapat 3 akun default yang ditampilkan di bagian bawah untuk memudahkan testing (admin/admin123, GR-001/guru123, 2024001/2024001).

### 8.2 Dashboard Admin

![Screenshots: Dashboard Admin dengan Chart.js](screenshots/02_dashboard_admin.png)

> Dashboard admin menampilkan: 4 card statistik (Total Siswa, Total Guru, Total Mapel, % Kelulusan), bar chart distribusi nilai per kelas, dan doughnut chart rasio Lulus/Tidak Lulus.

### 8.3 Halaman Manajemen Siswa (DataTables)

![Screenshots: Daftar Siswa dengan DataTables](screenshots/03_daftar_siswa.png)

> Tabel interaktif menggunakan DataTables: search box, sorting per kolom, pagination, dan tombol aksi per baris (Edit/Hapus/Detail).

### 8.4 Form Input Nilai (Live Preview)

![Screenshots: Form Input Nilai dengan Live Preview](screenshots/04_input_nilai.png)

> Form input nilai dengan 3 field (Tugas, UTS, UAS) dan live preview kalkulasi real-time. Preview menghitung `0.30×T + 0.30×U + 0.40×A` via JavaScript oninput.

### 8.5 Halaman Nilai Siswa

![Screenshots: Halaman Nilai Pribadi Siswa](screenshots/05_nilai_siswa.png)

> Halaman nilai siswa menampilkan DataTable semua nilai per mata pelajaran, dengan badge berwarna (hijau = LULUS, merah = TIDAK LULUS) dan link "Detail" untuk melihat rincian kalkulasi.

### 8.6 Modal Detail Kalkulasi

![Screenshots: Modal Detail Kalkulasi Nilai](screenshots/06_detail_kalkulasi.png)

> Modal SweetAlert2 yang menampilkan rincian kalkulasi nilai: input nilai (Tugas/UTS/UAS), nilai akhir, KKM, dan selisih dari KKM.

### 8.7 Halaman Laporan (Pilih Kelas)

![Screenshots: Halaman Pilih Laporan](screenshots/07_pilih_laporan.png)

> Halaman untuk memilih kelas dan aksi: Cetak PDF (WeasyPrint) atau Ekspor Excel (openpyxl).

### 8.8 Preview Laporan PDF (di Browser)

![Screenshots: Preview Laporan PDF di Browser](screenshots/08_preview_laporan_pdf.png)

> Tampilan laporan PDF yang di-generate oleh WeasyPrint, dengan header sekolah, statistik kelas (total siswa, rata-rata, tertinggi, terendah, % lulus), dan tabel nilai per siswa.

### 8.9 Audit Log

![Screenshots: Halaman Audit Log](screenshots/09_audit_log.png)

> Halaman audit log yang menampilkan semua aktivitas user: timestamp, user, action (INSERT/UPDATE/DELETE/LOGIN), table_name, description, dan IP address.

### 8.10 Ekspor Excel

![Screenshots: File Excel Hasil Ekspor](screenshots/10_export_excel.png)

> File Excel hasil ekspor, dengan header yang diformat (bold + background biru), border, dan freeze pane untuk header.

---

## ✅ Checklist Output Fase 2

- [x] Penjelasan library & framework lengkap (tabel + justifikasi)
- [x] Struktur kode program (pohon direktori)
- [x] Implementasi fungsi terstruktur (5+ fungsi, semua dengan docstring)
- [x] Implementasi class OOP (5+ class, semua dengan docstring)
- [x] Implementasi antarmuka (snippet base.html, login.html, input_nilai.html)
- [x] Before/after refactoring (3 contoh: magic numbers, print→logger, lazy import)
- [x] Screenshot referensi (10 placeholder untuk diisi manual)

---

_Disusun sesuai PRD.md Fase 2. Versi 1.0.0 — 2026._
