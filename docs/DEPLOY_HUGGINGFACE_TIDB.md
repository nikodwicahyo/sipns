# Tutorial Deploy SIPNS ke Hugging Face Spaces + TiDB Cloud (End-to-End)

> **Target:** Deploy aplikasi SIPNS (Flask + MySQL) ke **Hugging Face Spaces (free CPU)** + **TiDB Cloud Serverless (free)** secara production-ready.
> **Estimasi waktu:** 25–35 menit untuk first-time deploy.
> **Biaya:** $0/bulan (kedua platform punya free tier tanpa credit card).

---

## Daftar Isi

1. [Arsitektur Target](#1-arsitektur-target)
2. [Prasyarat](#2-prasyarat)
3. [Phase 1 — Setup TiDB Cloud](#3-phase-1--setup-tidb-cloud-510-menit)
4. [Phase 2 — Persiapan Project Lokal](#4-phase-2--persiapan-project-lokal-5-menit)
5. [Phase 3 — Buat Hugging Face Space](#5-phase-3--buat-hugging-face-space-3-menit)
6. [Phase 4 — Push Kode ke Space](#6-phase-4--push-kode-ke-space-5-menit)
7. [Phase 5 — Setup Environment Variables](#7-phase-5--setup-environment-variables-5-menit)
8. [Phase 6 — Monitor Build & Deploy](#8-phase-6--monitor-build--deploy-510-menit)
9. [Phase 7 — Verifikasi & Smoke Test](#9-phase-7--verifikasi--smoke-test-5-menit)
10. [Phase 8 — Post-Deploy & Maintenance](#10-phase-8--post-deploy--maintenance)
11. [Troubleshooting](#11-troubleshooting)
12. [Cold Start & Cost Optimization](#12-cold-start--cost-optimization)

---

## 1. Arsitektur Target

```
┌─────────────────────┐      HTTPS       ┌──────────────────────────────┐
│  Browser (User)     │ ◄───────────────► │  Hugging Face Spaces (Free)  │
│  Admin/Guru/Siswa   │   *.hf.space     │  - Docker container          │
└─────────────────────┘                  │  - 2 vCPU, 16 GB RAM (!)     │
                                         │  - 50 GB ephemeral storage   │
                                         │  - Sleep setelah 48 jam idle │
                                         │  - Port 7860 (Docker SDK)    │
                                         │  - Gunicorn 1 worker         │
                                         │  - WeasyPrint + libpango     │
                                         └──────────┬───────────────────┘
                                                    │ TLS (ssl=True)
                                                    │ mysql+pymysql
                                                    ▼
                                         ┌──────────────────────────────┐
                                         │  TiDB Cloud Serverless       │
                                         │  - 5 GB free storage         │
                                         │  - MySQL 8 compatible        │
                                         │  - Auto-pause setelah 7 hari │
                                         └──────────────────────────────┘
```

**Mengapa kombinasi ini?**
- **Hugging Face Spaces (Free CPU basic)** = $0/bulan, **2 vCPU + 16 GB RAM** (jauh lebih besar dari Render free 512 MB), **sleep setelah 48 jam** (bukan 15 menit seperti Render), tidak butuh credit card.
- **TiDB Cloud Serverless** = MySQL-compatible, 5 GB gratis, mendukung TLS, region Singapore.
- **PyMySQL** = pure-Python driver, tidak perlu kompilasi → build Docker image lebih cepat & reliable.
- **Gunicorn + WhiteNoise** = server production ringan; WhiteNoise serve static file langsung dari WSGI (no overhead Flask) → cold start lebih cepat.

---

## 2. Prasyarat

| Tools | Keterangan |
|-------|------------|
| Git 2.x | Untuk push ke Hugging Face |
| Akun Hugging Face | Sign up gratis di https://huggingface.co/join (pakai GitHub/Google/email) |
| Akun TiDB Cloud | Sign up gratis di https://tidbcloud.com |
| Python 3.10+ (lokal, opsional) | Untuk validasi syntax sebelum push |
| Kode SIPNS | File `Dockerfile`, `.dockerignore`, `wsgi.py`, `README.md` (dengan HF frontmatter) sudah ada di root |

> ✅ **PENTING:** Semua file deployment (`Dockerfile`, `.dockerignore`, `wsgi.py`) **sudah disertakan** di repo ini. Anda TIDAK perlu membuatnya manual. Cukup push ke Hugging Face Space baru.

---

## 3. Phase 1 — Setup TiDB Cloud (5–10 menit)

> 💡 **Skip jika Anda sudah pernah setup TiDB Cloud** (mis. dari percobaan Render sebelumnya). Anda bisa langsung pakai cluster & database yang sama.

### 3.1 Buat Akun & Cluster

1. Buka https://tidbcloud.com → klik **Sign Up** (pakai Google / GitHub / email).
2. Setelah login, Anda akan diminta setup Organization. Isi nama bebas → **Continue**.
3. Pilih region: **Singapore (AWS)** (paling dekat dengan Indonesia).
4. Pilih plan: **Serverless Tier** (gratis, 5 GB).
5. Klik **Create Cluster** → tunggu ~1 menit sampai status **Active**.

### 3.2 Setup User & Password

1. Di sidebar → **Clusters** → klik nama cluster Anda.
2. Tab **Settings** → **User Management** → klik user `root` → **Change Password**.
3. Set password kuat (min 8 char, kombinasi huruf besar + kecil + angka). **SIMPAN PASSWORD INI** — tidak akan ditampilkan lagi.

### 3.3 Whitelist IP (Opsional)

TiDB Cloud Serverless tier default-nya **allow all IP** (0.0.0.0/0). Hugging Face Spaces egress IP berubah-ubah, jadi **jangan restrict** untuk setup awal.

### 3.4 Dapatkan Connection String

1. Di cluster overview, klik tombol **Connect** (pojok kanan atas).
2. Pilih **General** → **Endpoint Type: Public**.
3. Pilih **Connect With: MySQL CLI** atau **Standard Connection**.
4. Catat informasi ini (jangan di-share):
   ```
   Host:     gateway01.singapore.prod.aws.tidbcloud.com
   Port:     4000
   User:     root
   Password: <yang Anda set di 3.2>
   Database: sipns
   ```
5. **Connection string format untuk HF Spaces (SALIN PERSIS):**
   ```
   mysql+pymysql://root:YOUR_PASSWORD@gateway01.singapore.prod.aws.tidbcloud.com:4000/sipns?charset=utf8mb4
   ```
   Ganti `YOUR_PASSWORD` dengan password Anda (URL-encode karakter spesial jika ada, mis. `@` jadi `%40`).

### 3.5 Buat Database `sipns`

1. Di TiDB Cloud console, klik tab **SQL Editor**.
2. Pilih cluster Anda di dropdown.
3. Paste & run:
   ```sql
   CREATE DATABASE IF NOT EXISTS sipns
     CHARACTER SET utf8mb4
     COLLATE utf8mb4_unicode_ci;
   ```
4. Pastikan output `OK` (1 row affected). Database `sipns` siap menerima migration.

> 💡 **Tips:** TiDB Cloud Serverless bisa **auto-pause** setelah 7 hari tidak ada koneksi. Saat deploy pertama, atau setelah pause, koneksi pertama akan retry beberapa kali — sabar, akan connect.

---

## 4. Phase 2 — Persiapan Project Lokal (5 menit)

### 4.1 Verifikasi File Deployment

Pastikan 4 file ini ada di root repo:

| File | Tujuan |
|------|--------|
| `Dockerfile` | Image build untuk HF Spaces |
| `.dockerignore` | Exclude file tidak perlu dari image |
| `wsgi.py` | Production entry point (`gunicorn wsgi:app`) |
| `README.md` | Wajib ada YAML frontmatter HF di paling atas |

Cek:
```bash
# Windows PowerShell:
dir Dockerfile, .dockerignore, wsgi.py, README.md

# Linux/macOS:
ls -la Dockerfile .dockerignore wsgi.py README.md
```

### 4.2 Validasi Lokal (Opsional tapi Disarankan)

Sebelum push, pastikan kode production-ready bisa di-import tanpa error:

```bash
# Install dependencies
pip install -r requirements.txt

# Test import (TANPA butuh DB):
python -c "from app import create_app; app = create_app('production'); print('OK:', app)"
```

**Expected output:**
```
OK: <Flask 'app'>
```

Atau jalankan validation script lengkap:
```bash
python validate.py
```

**Expected output:**
```
[1] create_app('production') = Flask OK
[2] /healthz = ['GET'] OK
[3] wsgi_app = WhiteNoise OK
[4] ProductionConfig flags OK
[5] Dockerfile base image: python:3.12 OK
[6] .dockerignore OK
[7] README.md HF Spaces frontmatter OK
[8] wsgi.py loadable OK
[9] No Render residue OK
ALL CHECKS PASSED
```

### 4.3 (Opsional) Test Build Docker Image Lokal

Kalau Anda punya Docker Desktop terinstall, bisa test build image lokal:

```bash
# Build image
docker build -t sipns-test .

# Run dengan env vars dummy
docker run -p 7860:7860 \
  -e FLASK_APP=wsgi.py \
  -e FLASK_ENV=production \
  -e SECRET_KEY=test-secret \
  -e DATABASE_URL='mysql+pymysql://invalid@localhost:3306/sipns' \
  sipns-test

# Container akan crash karena DB invalid, tapi pastikan:
# - Build sukses (image terbentuk)
# - Error log menunjukkan flask db upgrade mencoba konek DB (artinya env var sampai)
```

**Skip step ini kalau tidak punya Docker** — HF akan build untuk Anda.

### 4.4 Pastikan `.env` TIDAK Ter-commit

File `.env` berisi secret lokal. **JANGAN** push ke Hugging Face. Cek `.gitignore`:

```bash
# Cek apakah .env ada di gitignore
cat .gitignore | grep "^\.env$"
```

Kalau tidak ada, tambahkan:
```bash
echo ".env" >> .gitignore
```

`Dockerfile` di repo ini sudah exclude `.env` via `.dockerignore`, tapi `.gitignore` tetap penting untuk Git history.

---

## 5. Phase 3 — Buat Hugging Face Space (3 menit)

### 5.1 Login ke Hugging Face

1. Buka https://huggingface.co → klik **Sign In** (pakai GitHub/Google/email).
2. Setelah login, klik avatar Anda (pojok kanan atas) → **Settings** (opsional, set display name).

### 5.2 Buat Space Baru

1. Buka https://huggingface.co/new-space
2. Isi form:
   | Field | Value | Catatan |
   |-------|-------|---------|
   | **Owner** | `<username>` Anda | Otomatis terisi |
   | **Space name** | `sipns` | Akan jadi URL: `https://huggingface.co/spaces/<user>/sipns` |
   | **License** | `mit` | Sesuai LICENSE repo |
   | **SDK** | **Docker** | ⚠️ PENTING! Bukan Gradio/Streamlit |
   | **Space hardware** | **CPU basic** | Free tier ($0/bulan, 2 vCPU + 16 GB RAM) |
   | **Visibility** | **Public** | Siapapun bisa akses via URL (tidak bisa edit) |
3. Klik **Create Space**.
4. Anda akan di-redirect ke halaman Space baru. Status: **Building** (initial Docker build).

> 💡 **Catatan:** "Public" artinya URL Space bisa diakses siapapun. Cocok untuk demo sekolah. "Private" hanya bisa diakses owner (perlu login HF). Pilih "Public" untuk tugas/demo.

### 5.3 (Opsional) Ganti SDK Setelah Buat

Kalau Anda salah pilih SDK, bisa ganti nanti: Space → **Settings** → **SDK** (di section "Space settings"). Pilih **Docker** lalu Save.

---

## 6. Phase 4 — Push Kode ke Space (5 menit)

### 6.1 Clone Space Repo

Hugging Face Spaces punya Git repo sendiri. Clone ke folder terpisah (BUKAN di folder project SIPNS lokal Anda):

```bash
# Ganti <username> dengan username HF Anda
git clone https://huggingface.co/spaces/<username>/sipns
cd sipns
```

Anda akan dapat pesan:
```
Cloning into 'sipns'...
warning: You appear to have cloned an empty repository.
```

Itu normal — Space baru memang kosong. HF menyediakan README.md default yang akan kita overwrite.

### 6.2 Copy File Project ke Space

Dari folder project SIPNS lokal Anda, copy SEMUA file dan folder **KECUALI** yang di-exclude `.dockerignore`:

**Windows PowerShell:**
```powershell
# Path ke project SIPNS lokal (parent folder dari folder Space)
$source = "E:\Proyek LSP\LSP 2\SIPNS"
$dest = "E:\Proyek LSP\LSP 2\sipns-space"  # folder Space hasil clone

# Copy semua file yang dibutuhkan
Copy-Item -Path "$source\app" -Destination "$dest\" -Recurse -Force
Copy-Item -Path "$source\migrations" -Destination "$dest\" -Recurse -Force
Copy-Item -Path "$source\docs" -Destination "$dest\" -Recurse -Force
Copy-Item -Path "$source\wsgi.py" -Destination "$dest\" -Force
Copy-Item -Path "$source\Dockerfile" -Destination "$dest\" -Force
Copy-Item -Path "$source\.dockerignore" -Destination "$dest\" -Force
Copy-Item -Path "$source\README.md" -Destination "$dest\" -Force
Copy-Item -Path "$source\requirements.txt" -Destination "$dest\" -Force
Copy-Item -Path "$source\.gitignore" -Destination "$dest\" -Force
```

**Linux/macOS:**
```bash
# Path ke project SIPNS lokal
SOURCE="/path/to/sipns"
DEST="/path/to/sipns-space"  # folder Space hasil clone

# Copy semua yang dibutuhkan (exclude Render file, venv, cache, dll — .dockerignore handle)
cp -r $SOURCE/app $DEST/
cp -r $SOURCE/migrations $DEST/
cp -r $SOURCE/docs $DEST/
cp $SOURCE/wsgi.py $DEST/
cp $SOURCE/Dockerfile $DEST/
cp $SOURCE/.dockerignore $DEST/
cp $SOURCE/README.md $DEST/
cp $SOURCE/requirements.txt $DEST/
cp $SOURCE/.gitignore $DEST/
```

**Atau lebih simpel** (Linux/macOS):
```bash
# rsync exclude file/folder tertentu
rsync -av --exclude='.git' --exclude='venv' --exclude='__pycache__' \
          --exclude='render.yaml' --exclude='Aptfile' --exclude='build.sh' \
          --exclude='runtime.txt' --exclude='PRD.md' --exclude='tests' \
          --exclude='htmlcov' --exclude='.pytest_cache' --exclude='logs' \
          --exclude='validate.py' --exclude='docs/PRD.md' \
          $SOURCE/ $DEST/
```

### 6.3 Verify Struktur File

Pastikan struktur folder Space Anda seperti ini:
```
sipns-space/                  ← hasil clone HF Space
├── .dockerignore
├── .gitignore
├── Dockerfile
├── README.md                 ← sudah ada YAML frontmatter HF di atas
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── seed.py
│   ├── models/
│   ├── services/
│   ├── blueprints/
│   ├── forms/
│   ├── templates/
│   ├── static/
│   └── utils/
├── docs/
│   └── DEPLOY_HUGGINGFACE_TIDB.md
├── migrations/
│   ├── alembic.ini
│   ├── env.py
│   └── versions/
│       ├── 9472af43883e_*.py
│       └── 85cddd831f8c_*.py
├── requirements.txt
└── wsgi.py
```

### 6.4 (Opsional) Tambahkan License File

Kalau repo lokal punya `LICENSE`:
```bash
cp $SOURCE/LICENSE $DEST/  # Linux/macOS
```

### 6.5 Push ke Hugging Face

```bash
cd sipns-space

# Verify perubahan
git status
# Akan muncul daftar file baru (modified/new)

# Add semua file
git add .

# Commit
git commit -m "deploy: initial SIPNS on Hugging Face Spaces"

# Push ke HF (pertama kali akan minta username + password HF)
git push
```

**Jika muncul error autentikasi:**
- HF pakai HTTPS Git, butuh username + password (atau token).
- **Saran:** pakai **Access Token** (lebih aman dari password):
  1. HF → Settings → **Access Tokens** → **New token**
  2. Name: `sipns-deploy`, Type: **Write**
  3. Copy token
  4. Saat `git push`, masukkan:
     - Username: username HF Anda
     - Password: paste token (bukan password akun)

Untuk menyimpan token supaya tidak ditanya tiap push:
```bash
git config --global credential.helper store
# Push sekali, masukkan token,下次 tidak ditanya lagi
```

### 6.6 Monitor Build Pertama

Setelah push, kembali ke browser → halaman Space Anda:
- Tab **Logs** → monitor real-time Docker build:
  ```
  ==> Building Docker image...
  ==> [1/4] FROM python:3.12-slim
  ==> [2/4] RUN apt-get install (WeasyPrint deps)
  ==> [3/4] RUN pip install -r requirements.txt
  ==> [4/4] COPY . .
  ==> Build successful
  ==> Starting container...
  ==> Running: flask db upgrade && flask seed && gunicorn ...
  INFO  [alembic.runtime.migration] Running upgrade  -> 9472af43883e, ...
  INFO  app.seed:Memulai proses seed data SIPNS...
  [INFO] Starting gunicorn 23.0.0
  [INFO] Booting worker with pid: 42
  [INFO] Listening at: http://0.0.0.0:7860
  ```
- **Build sukses** jika ada `Booting worker` + `Listening at: 0.0.0.0:7860`.
- Build time pertama: **5-10 menit** (download Python base image + install WeasyPrint deps).

> ⚠️ **JANGAN push env vars DATABASE_URL dulu sebelum build sukses tanpa DB.** Tanpa env vars, container akan start dan crash di `flask db upgrade` (DB unreachable), tapi Gunicorn tidak akan start. **Lanjut ke Phase 5 untuk set env vars.**

---

## 7. Phase 5 — Setup Environment Variables (5 menit)

### 7.1 Buka Settings Space

1. Buka halaman Space Anda di HF.
2. Tab **Settings** (menu atas / sidebar).
3. Scroll ke section **"Variables and secrets"**.

### 7.2 Tambah Secrets (Encrypted — untuk data sensitif)

Klik **"New secret"** untuk tiap entry di bawah:

| # | Name | Value | Keterangan |
|---|------|-------|------------|
| 1 | `SECRET_KEY` | *(generate random 64-char string)* | Untuk Flask session signing. Bisa pakai: `python -c "import secrets; print(secrets.token_hex(32))"` |
| 2 | `DATABASE_URL` | `mysql+pymysql://root:YOUR_PASSWORD@gateway01.singapore.prod.aws.tidbcloud.com:4000/sipns?charset=utf8mb4` | Connection string TiDB Cloud (lihat Phase 1.4) |

**Cara tambah:**
1. Klik "New secret"
2. Name: `SECRET_KEY`
3. Secret value: paste value
4. Klik **Add**
5. Ulangi untuk `DATABASE_URL`

> 🔒 **Secrets vs Variables:** Secrets ter-encrypt di-rest dan tidak muncul di logs. Variables visible (untuk hal non-rahasia). Gunakan **Secrets** untuk password dan data sensitif.

### 7.3 Tambah Variables (Visible — untuk config biasa)

Klik **"New variable"** untuk tiap entry di bawah:

| # | Name | Value |
|---|------|-------|
| 1 | `FLASK_APP` | `wsgi.py` |
| 2 | `FLASK_ENV` | `production` |
| 3 | `DB_POOL_SIZE` | `5` |
| 4 | `DB_MAX_OVERFLOW` | `10` |
| 5 | `DB_CONNECT_TIMEOUT` | `10` |
| 6 | `LOG_LEVEL` | `INFO` |
| 7 | `PYTHONUNBUFFERED` | `1` |

**Cara tambah:**
1. Klik "New variable"
2. Name + Value
3. Klik **Add**
4. Ulangi untuk semua 7 entries

### 7.4 Trigger Redeploy

Setelah semua env vars ditambah, Space akan **otomatis restart** dengan env vars baru. Monitor di tab **Logs**:
```
==> Restarting container with new environment...
==> Running: flask db upgrade && flask seed && gunicorn ...
INFO  [alembic.runtime.migration] Running upgrade  -> 9472af43883e, initial migration
INFO  [alembic.runtime.migration] Running upgrade 9472af43883e -> 85cddd831f8c, ...
INFO  app.seed:Memulai proses seed data SIPNS...
INFO  app.seed:Seed master data selesai: 1 admin, 3 guru, 10 siswa.
[INFO] Listening at: http://0.0.0.0:7860
```

**Sukses** jika:
- `flask db upgrade` apply migration tanpa error
- `flask seed` insert data tanpa error
- Gunicorn listen di 0.0.0.0:7860

---

## 8. Phase 6 — Monitor Build & Deploy (5–10 menit)

### 8.1 Tab-Tab Penting di HF Space

| Tab | Fungsi |
|-----|--------|
| **App** | Preview iframe Space (kalau Web App — Gradio/Streamlit) — untuk Docker SDK biasanya kosong/tidak dipakai |
| **Logs** | Real-time log Docker container (gunicorn, request, error) |
| **Files** | List file di repo Space (Git tree) |
| **Community** | Discussion, issues, pull requests (kalau di-enable) |
| **Settings** | Env vars, hardware, secrets, members |

### 8.2 Indikator Status

Di header Space, ada status indicator:
- 🟡 **Building** — Docker image sedang di-build (push baru / perubahan Dockerfile)
- 🟡 **Starting** — Container starting up (importing Python modules, running migrations)
- 🟢 **Running** — Container running normal, gunicorn listening
- 🔴 **Runtime error** — Container crash, cek Logs
- ⚪ **Sleeping** — Container idle > 48 jam, akan wake saat request pertama

### 8.3 Cek Container Up via `/healthz`

Buka di browser:
```
https://<username>-sipns.hf.space/healthz
```

Expected response:
```json
{"status": "ok"}
```

**Jika muncul 502/503:** container belum ready atau ada error. Cek Logs.

### 8.4 Cek Koneksi DB via `/healthz/deep`

Buka di browser:
```
https://<username>-sipns.hf.space/healthz/deep
```

Expected response:
```json
{"status": "ok", "db": "ok"}
```

**Jika `db: "error"`:** DATABASE_URL salah atau TiDB cluster paused.

---

## 9. Phase 7 — Verifikasi & Smoke Test (5 menit)

Buka URL SIPNS Anda: **https://\<username\>-sipns.hf.space**

Jalankan test berikut **berurutan**:

| # | Test | Expected | URL / Cara |
|---|------|----------|------------|
| 1 | Landing page | Logo + tombol "Login" | `/` |
| 2 | Login admin | Redirect ke dashboard admin (stat cards muncul) | `/auth/login` → `admin` / `Admin@123` |
| 3 | Health check | JSON `{"status":"ok"}` | `/healthz` |
| 4 | Deep health | JSON `{"status":"ok","db":"ok"}` | `/healthz/deep` |
| 5 | List siswa | 10 siswa (dari seed) | `/admin/siswa` |
| 6 | List guru | 3 guru (dari seed) | `/admin/guru` |
| 7 | Audit log | Minimal ada log login | `/admin/audit` |
| 8 | Login guru GR-001 | Redirect ke dashboard guru | `/auth/login` → `GR-001` / `Guru@123` |
| 9 | Rekap nilai | 24 record nilai | `/guru/nilai/rekap` |
| 10 | Generate PDF kelas | PDF ter-download (~50-200 KB) | `/laporan/pdf/X-IPA-1` |
| 11 | Login siswa 2024001 | Lihat nilai pribadi | `/auth/login` → `2024001` / `2024001` |
| 12 | Transkrip PDF | PDF 1 halaman | `/laporan/transkrip/<id>` (lihat ID di /siswa/nilai) |
| 13 | Ekspor Excel | File `.xlsx` ter-download | `/laporan/excel` |
| 14 | Static file CSS | Load cepat (cek DevTools Network) | `/static/css/custom.css` |
| 15 | Logout | Redirect ke /auth/login | Tombol logout di navbar |

**Kalau ada yang gagal**, cek [Troubleshooting](#11-troubleshooting).

---

## 10. Phase 8 — Post-Deploy & Maintenance

### 10.1 Ganti Password Default (WAJIB untuk Production)

Login sebagai admin → menu **Users** → reset password untuk akun yang masih pakai default:

| Akun | Password Lama | Aksi |
|------|---------------|------|
| `admin` | `Admin@123` | Reset ke password kuat baru |
| `GR-001`, `GR-002`, `GR-003` | `Guru@123` | Reset per-guru |
| `2024001` - `2024010` | `<NIS>` | Admin harus reset manual (tidak ada self-reset) |

> 💡 Untuk tugas sekolah/demo, ganti minimal password admin. Kredensial seed lain bisa dibiarkan.

### 10.2 Update Kode → Auto-Redeploy

Setiap perubahan kode → commit & push → HF auto-rebuild & redeploy.

```bash
# Dari folder Space lokal (sipns-space/)
git add .
git commit -m "feat: tambah fitur X"
git push
```

HF akan:
1. Re-build Docker image (5-10 menit kalau ada perubahan dependency)
2. Stop container lama
3. Start container baru dengan image baru
4. Run `flask db upgrade && flask seed` (di CMD)
5. Start gunicorn

> ⚠️ **Downtime:** ada gap ~10-30 detik antara container lama mati dan baru hidup. Untuk production serius, pakai blue-green deploy. Untuk free tier/demo, acceptable.

### 10.3 Schema Baru (Migration Tambahan)

Jika Anda tambah migration baru (`flask db migrate -m "..."` lokal → `flask db upgrade` lokal → commit file di `migrations/versions/`):

```bash
# Di project SIPNS lokal
flask db migrate -m "tambah kolom xyz"
flask db upgrade
git add migrations/versions/<file>_xyz.py
git commit -m "feat: migration tambah kolom xyz"

# Push ke Space
git push
```

`CMD` di Dockerfile (`flask db upgrade && flask seed && gunicorn ...`) akan auto-apply migration baru setiap container start. `flask seed` idempotent → aman re-run.

### 10.4 Update Environment Variables

1. HF → Space → **Settings** → **Variables and secrets**
2. Edit value → **Save** → container restart otomatis

### 10.5 Custom Domain (Opsional, Gratis)

1. Beli domain (Niagahoster, Namecheap, Cloudflare) — mis. `sipns.sekolah.sch.id`.
2. HF → Space → **Settings** → **Custom domain**
3. Masukkan domain → HF kasih instruksi DNS (CNAME record ke `username-sipns.hf.space`).
4. Tunggu propagasi DNS (5 menit - 24 jam).
5. HF auto-issue SSL via Let's Encrypt → HTTPS aktif di custom domain.

### 10.6 Monitoring

| Resource | Lokasi | Keterangan |
|----------|--------|------------|
| Container logs | HF Space → **Logs** | Real-time, retention 30 hari |
| Container metrics | HF Space → **Settings** → **Usage** | CPU, RAM, network usage |
| DB metrics | TiDB Cloud → cluster → **Monitoring** | Query per second, slow query log, storage |
| App errors | `/healthz/deep` | Cek dari uptime monitor eksternal |

### 10.7 Pause & Resume

HF Space **auto-pause setelah 48 jam** tidak ada request. Saat pause:
- Container dimatikan (no compute cost)
- Data di TiDB Cloud tetap aman
- Request berikutnya akan **trigger wake-up** (~30-50 detik)

Untuk manual pause: Space → **Settings** → **Pause Space**.
Untuk resume: klik **"Restart Space"** atau akses URL publik.

---

## 11. Troubleshooting

### 11.1 Build Gagal: `ERROR: failed to solve: process "/bin/sh -c apt-get update" did not complete successfully`

**Penyebab:** Koneksi internet ke apt repo gagal saat build.

**Fix:**
- Tunggu 5-10 menit lalu push lagi (HF biasanya rate-limit retry).
- Cek di HF Space → **Logs** untuk detail error.

### 11.2 Build Gagal: `OSError: cannot load library 'pango'`

**Penyebab:** Package WeasyPrint belum terinstall dengan benar.

**Fix:**
1. Pastikan `Dockerfile` punya section `RUN apt-get install ... libpango-1.0-0 libpangoft2-1.0-0 libcairo2 ...`
2. Cek juga `libgdk-pixbuf-2.0-0`, `libffi-dev`, `fonts-dejavu-core`.
3. Push lagi.

### 11.3 Container Start Tapi Crash: `OperationalError: (2003, "Can't connect to MySQL server")`

**Penyebab:** DATABASE_URL salah, atau TiDB cluster paused.

**Fix:**
1. Login TiDB Cloud → cek status cluster (harus **Active**, bukan **Paused**).
2. Cek Secrets di HF Space Settings → DATABASE_URL harus persis sama dengan TiDB connection string.
3. Pastikan password di-URL-encode kalau ada karakter spesial.

### 11.4 Container Start Tapi Crash: `OperationalError: (1045, "Access denied for user 'root'@'...'")`

**Penyebab:** Username/password TiDB salah.

**Fix:**
1. Reset password di TiDB Cloud → cluster → **Settings** → **User Management**.
2. Update secret `DATABASE_URL` di HF Space Settings.
3. Tunggu auto-restart.

### 11.5 Container Start Tapi Crash: `SSL connection error: SSL is required`

**Penyebab:** TiDB Cloud butuh TLS, tapi `connect_args` tidak ada `ssl=True`.

**Fix:** Sudah dihandle otomatis di `app/config.py` ProductionConfig. Pastikan:
- Anda pakai `ProductionConfig` (cek `FLASK_ENV=production` di HF Variables)
- File `app/config.py` punya `connect_args={'connect_timeout': 10, 'ssl': True}`

### 11.6 Build Gagal: `ERROR: failed to compute cache key: "/requirements.txt": not found`

**Penyebab:** `requirements.txt` tidak ada di root Space, atau `.dockerignore` exclude.

**Fix:** Pastikan `requirements.txt` ada di root Space repo dan TIDAK di-exclude `.dockerignore`.

### 11.7 Container Sleep Terlalu Sering / Cold Start Lama

**Penyebab:** Free tier sleep setelah 48 jam. Container butuh ~30-50 detik untuk wake.

**Mitigasi (opsional):**
- Daftar cron job di https://cron-job.org untuk ping `/healthz` setiap 24 jam (di bawah threshold 48 jam).
- Atau upgrade ke paid HF hardware (~$0.05/jam untuk CPU upgrade).

### 11.8 `flask seed` Gagal dengan `IntegrityError`

**Penyebab:** Duplikat entry (NIS atau ID guru sudah ada).

**Fix:** Seed sudah idempotent (cek `if User.query.first(): return` di `app/seed.py:48`). Kalau masih error, cek apakah Anda sudah pernah seed sebelumnya.

### 11.9 Static File 404 (CSS/JS tidak load)

**Penyebab:** WhiteNoise belum terinstall atau path salah.

**Fix:**
1. Pastikan `whitenoise==6.8.2` ada di `requirements.txt` (sudah).
2. Cek `app/__init__.py` → `WhiteNoise(app.wsgi_app, root=app.static_folder)`.
3. Test: buka `https://<username>-sipns.hf.space/static/css/custom.css` di browser → harusnya return CSS.

### 11.10 Login Loop / Session Hilang Tiap Refresh

**Penyebab:** Cookie tidak persisten — `SESSION_COOKIE_SECURE=True` tapi diakses via HTTP.

**Fix:**
- HF Spaces default kasih HTTPS → cookie aman.
- Selalu akses via `https://` (bukan `http://`).
- `PREFERRED_URL_SCHEME='https'` sudah diset di `ProductionConfig` → `url_for(_external=True)` selalu generate URL HTTPS.

### 11.11 TiDB Cluster "Paused"

**Penyebab:** TiDB Cloud Serverless auto-pause setelah 7 hari tidak ada koneksi.

**Fix:**
1. Login TiDB Cloud → klik **Resume**.
2. Tunggu ~30 detik sampai status **Active**.
3. Trigger redeploy di HF Space (Settings → **Restart Space**) atau akses URL publik.

### 11.12 Image Build Sangat Lama (> 15 menit)

**Penyebab:** Koneksi lambat atau image base perlu di-pull dari awal.

**Fix:**
- Tunggu sabar. Image Python 3.12-slim ~150 MB, butuh waktu.
- Cek Logs untuk progress.
- Kalau > 30 menit, kemungkinan error — cek log untuk detail.

---

## 12. Cold Start & Cost Optimization

### 12.1 Cold Start Reality

HF Spaces free tier **sleep setelah 48 jam tidak ada request**. Request pertama setelah sleep butuh ~30-50 detik (container spin-up + import Python + koneksi DB ke TiDB).

**Komponen cold start:**
| Komponen | Lama | Bisa dioptimasi? |
|----------|------|------------------|
| Container provisioning | ~5-10s | ❌ (HF-internal) |
| Docker image pull (cached setelah build pertama) | ~5-10s (cached) / ~30s (cold) | ⚠️ Sebagian |
| Python interpreter start | ~1s | ❌ |
| Import Flask + SQLAlchemy + extensions | ~2-3s | ⚠️ Minimal (lazy load) |
| WeasyPrint import (lazy) | 0s (tidak di-import saat startup) | ✅ |
| Gunicorn fork + bind | ~0.5s | ❌ |
| DB connection (TLS handshake ke TiDB) | ~1-2s | ⚠️ Minimal |
| `flask db upgrade` + `flask seed` | ~2-3s | ✅ Idempotent |
| **Total** | **~30-50s** | |

### 12.2 Optimasi yang Sudah Diterapkan

| Optimasi | Lokasi | Efek |
|----------|--------|------|
| `python:3.12-slim` (bukan full) | Dockerfile | Image lebih kecil (~150MB vs 900MB) |
| `pip install --no-cache-dir` | Dockerfile | Layer lebih kecil |
| `rm -rf /var/lib/apt/lists/*` | Dockerfile | Hapus apt cache, image lebih kecil |
| `--workers 1` | Dockerfile CMD | 1 worker cukup untuk free tier |
| `--preload` | Dockerfile CMD | Load app SEKALI di startup |
| WhiteNoise static files | `app/__init__.py` | Serve `/static/*` dari WSGI, no Flask overhead |
| `/healthz` no-DB | `app/__init__.py` | Response < 10ms |
| Lazy import WeasyPrint | `app/services/laporan_service.py` | Modul 50MB tidak di-import saat startup |
| `pool_pre_ping=True` | `app/config.py` | Stale connection auto-detect |
| `pool_recycle=3600` | `app/config.py` | Recycle sebelum MySQL `wait_timeout` (8h di TiDB) |
| `connect_timeout=10` | `app/config.py` | Fail fast kalau DB unreachable |
| `.dockerignore` | root repo | Exclude `venv/`, `tests/`, `docs/PRD.md`, dll → image lebih lean |

### 12.3 Cron Job Anti-Cold-Start (Opsional)

Kalau Anda ingin container **tidak pernah sleep** (zero cold start), daftar cron job:

```
URL:     https://<username>-sipns.hf.space/healthz
Method:  GET
Interval: every 24 hours
```

Daftar di:
- https://cron-job.org (gratis, no signup)
- https://uptimerobot.com (gratis, dengan monitoring dashboard)
- https://www.statuscake.com (gratis)

> ✅ **/healthz TIDAK query DB** → sangat cepat (~10-50ms), tidak ada efek samping.

### 12.4 Biaya Detail

| Resource | Free Tier | Paid Tier |
|----------|-----------|-----------|
| **HF Spaces (CPU basic)** | $0/bulan (sleep setelah 48 jam) | $0.05/jam (~$36/bulan terus nyala) |
| **TiDB Cloud Serverless** | $0/bulan (5 GB storage, 50M request units/bulan) | $0.10/GB storage/bulan |
| **Total untuk SIPNS** | **$0/bulan** ✅ | ~$36/bulan |

Untuk tugas sekolah / demo, **free tier sudah lebih dari cukup**.

---

## 13. Checklist Final

Sebelum menganggap deploy selesai, pastikan SEMUA item di bawah ini ✅:

- [ ] Akun Hugging Face dibuat
- [ ] Akun TiDB Cloud dibuat
- [ ] TiDB Cloud cluster **Active**, database `sipns` dibuat
- [ ] HF Space dibuat dengan SDK = **Docker**, hardware = **CPU basic**, visibility = **Public**
- [ ] `Dockerfile`, `.dockerignore`, `wsgi.py`, `README.md` (HF frontmatter) ada di root
- [ ] Code di-push ke HF Space repo (commit + push sukses)
- [ ] Secret `SECRET_KEY` diset (random 64-char string)
- [ ] Secret `DATABASE_URL` diset (connection string TiDB, URL-encoded)
- [ ] Variable `FLASK_APP=wsgi.py` diset
- [ ] Variable `FLASK_ENV=production` diset
- [ ] Variable `DB_POOL_SIZE=5`, `DB_MAX_OVERFLOW=10`, `DB_CONNECT_TIMEOUT=10` diset
- [ ] Variable `LOG_LEVEL=INFO`, `PYTHONUNBUFFERED=1` diset
- [ ] Build HF sukses (lihat log: `Booting worker with pid: ...`)
- [ ] Container start sukses (lihat log: `flask db upgrade` + `flask seed` tanpa error)
- [ ] `/healthz` return `{"status":"ok"}` (HTTP 200)
- [ ] `/healthz/deep` return `{"status":"ok","db":"ok"}` (HTTP 200)
- [ ] Login admin berhasil, dashboard muncul
- [ ] Login guru & siswa berhasil
- [ ] Generate PDF kelas berhasil (file ter-download)
- [ ] Generate Excel berhasil (file ter-download)
- [ ] **WAJIB:** Ganti password default `admin` jika production

Kalau semua ✅, **SIPNS Anda sudah LIVE di internet!** 🎉🚀

URL publik: `https://<username>-sipns.hf.space`

---

## 14. Referensi Tambahan

- **HF Spaces Docs**: https://huggingface.co/docs/hub/spaces
- **HF Docker SDK**: https://huggingface.co/docs/hub/spaces-sdks-docker
- **TiDB Cloud Docs**: https://docs.pingcap.com/tidbcloud
- **TiDB TLS Connection**: https://docs.pingcap.com/tidbcloud/connect-to-tidb-cluster
- **WeasyPrint System Deps**: https://doc.courtbouillon.org/weasyprint/stable/first_steps.html
- **Gunicorn Settings**: https://docs.gunicorn.org/en/stable/settings.html

---

_Tutorial ini untuk SIPNS versi 1.0.0. Update tutorial jika ada perubahan konfigurasi deployment._
