# Tutorial Deploy SIPNS ke Render + TiDB Cloud (End-to-End)

> **Target:** Deploy aplikasi SIPNS (Flask + MySQL) ke **Render Free Tier** + **TiDB Cloud Serverless (free)** secara production-ready.
> **Estimasi waktu:** 30–40 menit untuk first-time deploy.

---

## Daftar Isi

1. [Arsitektur Target](#1-arsitektur-target)
2. [Prasyarat](#2-prasyarat)
3. [Phase 1 — Setup TiDB Cloud](#3-phase-1--setup-tidb-cloud-510-menit)
4. [Phase 2 — Persiapan & Push Kode ke GitHub](#4-phase-2--persiapan--push-kode-ke-github-5-menit)
5. [Phase 3 — Deploy ke Render](#5-phase-3--deploy-ke-render-1015-menit)
6. [Phase 4 — Verifikasi & Smoke Test](#6-phase-4--verifikasi--smoke-test-5-menit)
7. [Phase 5 — Post-Deploy & Maintenance](#7-phase-5--post-deploy--maintenance)
8. [Troubleshooting](#8-troubleshooting)
9. [Mengurangi Cold Start (Opsional)](#9-mengurangi-cold-start-opsional)

---

## 1. Arsitektur Target

```
┌─────────────────────┐      HTTPS       ┌──────────────────────┐
│  Browser (User)     │ ◄───────────────► │  Render Free Tier    │
│  Admin/Guru/Siswa   │   public URL     │  - Gunicorn 1 worker │
└─────────────────────┘                  │  - Flask 3.1 app     │
                                         │  - WhiteNoise static│
                                         │  - WeasyPrint 61.2   │
                                         │  - libpango/libcairo │
                                         └──────────┬───────────┘
                                                    │ TLS (ssl=True)
                                                    │ mysql+pymysql
                                                    ▼
                                         ┌──────────────────────┐
                                         │  TiDB Cloud Serverless│
                                         │  5 GB free storage   │
                                         │  MySQL 8 compatible  │
                                         └──────────────────────┘
```

**Mengapa kombinasi ini?**
- **Render** = 750 jam/bulan gratis, auto-deploy dari GitHub, region Singapore (dekat Indonesia).
- **TiDB Cloud Serverless** = 5 GB MySQL gratis, MySQL wire-compatible, mendukung TLS.
- **PyMySQL** = pure-Python driver, tidak perlu kompilasi saat build → build Render lebih cepat & reliable.
- **Gunicorn + WhiteNoise** = server production yang ringan; WhiteNoise serve static file langsung dari WSGI (no overhead Flask) → cold start lebih cepat.

---

## 2. Prasyarat

| Tools | Versi | Keterangan |
|-------|-------|------------|
| Git | 2.x | Untuk push ke GitHub |
| Akun GitHub | — | Untuk hosting repo & auto-deploy Render |
| Akun Render | — | Sign up gratis di https://render.com (pakai GitHub) |
| Akun TiDB Cloud | — | Sign up gratis di https://tidbcloud.com |
| Python (lokal) | 3.10+ | Untuk validasi syntax sebelum push |
| **Kode SIPNS sudah production-ready** | — | File `wsgi.py`, `render.yaml`, `Aptfile`, `build.sh`, `runtime.txt` sudah ada di root repo |

> ⚠️ **PENTING:** Semua file deployment (`render.yaml`, `Aptfile`, `build.sh`, `runtime.txt`, `wsgi.py`) **sudah disertakan** di repo ini. Anda TIDAK perlu membuatnya manual.

---

## 3. Phase 1 — Setup TiDB Cloud (5–10 menit)

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
4. (Opsional) Buat user baru dengan privilege terbatas, tapi untuk tutorial ini kita pakai `root`.

### 3.3 Whitelist IP (Opsional)

TiDB Cloud Serverless tier default-nya **allow all IP** (0.0.0.0/0). Tidak perlu whitelist IP Render.

Jika Anda restrict IP, tambahkan range IP Render:
- Render egress IPs berubah-ubah, jadi lebih baik **jangan restrict** untuk setup awal.
- Untuk production serius, gunakan VPC peering atau TiDB Dedicated tier.

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
5. **Connection string format untuk Render (SALIN PERSIS):**
   ```
   mysql+pymysql://root:YOUR_PASSWORD@gateway01.singapore.prod.aws.tidbcloud.com:4000/sipns?charset=utf8mb4
   ```
   Ganti `YOUR_PASSWORD` dengan password Anda (URL-encode karakter spesial jika ada, mis. `@` jadi `%40`).

### 3.5 Buat Database `sipns`

1. Di TiDB Cloud console, klik tab **SQL Editor** (atau **Query** di sidebar).
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

## 4. Phase 2 — Persiapan & Push Kode ke GitHub (5 menit)

### 4.1 Validasi Lokal (Opsional tapi Disarankan)

Sebelum push, pastikan kode production-ready bisa di-import tanpa error:

```bash
# Clone atau extract repo
cd sipns

# Buat virtualenv
python -m venv venv
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Test import (TANPA butuh DB):
python -c "from app import create_app; app = create_app('production'); print('OK:', app)"
```

**Expected output:**
```
OK: <Flask 'app'>
```

Kalau muncul error, fix dulu sebelum lanjut.

### 4.2 Verifikasi File Deployment

Pastikan 6 file ini ada di root repo:

```bash
ls -la    # Linux/macOS
dir       # Windows
```

| File | Tujuan |
|------|--------|
| `render.yaml` | Konfigurasi service Render |
| `Aptfile` | System packages untuk WeasyPrint |
| `build.sh` | Script build (apt + pip) |
| `runtime.txt` | Pin Python 3.12.7 |
| `wsgi.py` | Production entry point |
| `requirements.txt` | Updated dengan gunicorn + whitenoise |

### 4.3 Push ke GitHub

```bash
# Inisialisasi repo (jika belum)
git init
git add .
git commit -m "feat: production-ready for Render + TiDB Cloud deployment"

# Set branch default
git branch -M main

# Tambah remote (ganti <username> dan <repo> dengan punyamu)
git remote add origin https://github.com/<username>/<repo>.git

# Push
git push -u origin main
```

**Verifikasi:** Buka halaman GitHub repo Anda di browser. Pastikan file `render.yaml`, `Aptfile`, `build.sh` muncul di daftar file root.

### 4.4 Pastikan `.env` TIDAK Ter-push

File `.env` berisi secret lokal. **JANGAN** push ke GitHub. Cek `.gitignore`:

```bash
# Cek apakah .env ada di gitignore
cat .gitignore | grep "^\.env$"

# Kalau tidak ada, tambahkan:
echo ".env" >> .gitignore
git add .gitignore
git commit -m "chore: ensure .env is gitignored"
git push
```

---

## 5. Phase 3 — Deploy ke Render (10–15 menit)

### 5.1 Buat Blueprint Instance

1. Login ke https://render.com (pakai akun GitHub yang punya akses ke repo SIPNS).
2. Klik **Dashboard** → **New** → **Blueprint Instance**.
3. **Connect a repository:** pilih repo SIPNS dari dropdown. Klik **Connect**.
4. Render akan auto-detect `render.yaml` di root → preview service muncul:
   ```
   ┌─────────────────────────────────────────────┐
   │  sipns-web                                  │
   │  type: web | plan: free | region: singapore │
   │  ─────────────────────────                  │
   │  Build:  bash build.sh                      │
   │  Start:  flask db upgrade && flask seed &&  │
   │          gunicorn ... wsgi:app              │
   │  Health: /healthz                           │
   └─────────────────────────────────────────────┘
   ```
5. Klik **Apply** → Render mulai provisioning service.

### 5.2 Set Environment Variable DATABASE_URL

Setelah blueprint applied, Anda perlu isi `DATABASE_URL`:

1. Klik service **sipns-web** di dashboard.
2. Tab **Environment** (menu kiri).
3. Cari key `DATABASE_URL` (auto-dari `render.yaml` dengan `sync: false`).
4. Klik **Edit** → paste connection string TiDB Cloud dari [Phase 1.4](#34-dapatkan-connection-string):
   ```
   mysql+pymysql://root:YOUR_PASSWORD@gateway01.singapore.prod.aws.tidbcloud.com:4000/sipns?charset=utf8mb4
   ```
5. Klik **Save Changes** → Render akan **auto-redeploy**.

### 5.3 Monitor Build & Deploy

1. Tab **Logs** (di service detail) — monitor real-time.
2. Anda akan lihat urutan:
   ```
   ==> Cloning repo from GitHub...
   ==> Running build command: bash build.sh
   ==> [1/3] apt-get update...
   ==> [2/3] Install system packages (WeasyPrint)...
   ==> [3/3] Install Python dependencies...
   ==> Build complete.
   ==> Starting service with: flask db upgrade && flask seed && gunicorn --bind 0.0.0.0:$PORT ...
   INFO  [alembic.runtime.migration] Running upgrade  -> 9472af43883e, initial migration
   INFO  [alembic.runtime.migration] Running upgrade 9472af43883e -> 85cddd831f8c, ...
   INFO  [alembic.runtime.migration] Context impl MySQLImpl.
   INFO  [alembic.runtime.migration] Will assume transactional DDL.
   INFO  app.seed:Memulai proses seed data SIPNS...
   INFO  app.seed:Seed master data selesai: 1 admin, 3 guru, 10 siswa.
   INFO  app.seed:Seed nilai selesai: 24 record nilai untuk 10 siswa × 3 mapel.
   [INFO] Starting gunicorn 23.0.0
   [INFO] Booting worker with pid: 42
   [INFO] Listening at: http://0.0.0.0:10000
   ```
   > ⚠️ **CATATAN untuk Free Tier:** Render free tier **tidak mendukung `preDeployCommand`**, jadi `flask db upgrade && flask seed` digabung ke dalam `startCommand`. Keduanya idempotent (Alembic skip jika tidak ada migration baru; seed skip jika User sudah ada) — aman re-run setiap container start. Trade-off: tambah ~2-3 detik ke cold start (yang memang sudah 30-50 detik di free tier).
3. **Build sukses** jika ada `Booting worker` + `Listening at: ...`.
4. **Gagal?** Lihat [Troubleshooting](#8-troubleshooting).

### 5.4 Dapatkan Public URL

Di service detail, header atas menunjukkan:
```
sipns-web   ●   Live   https://sipns-web.onrender.com
```

Klik URL → harus muncul landing page SIPNS. 🎉

---

## 6. Phase 4 — Verifikasi & Smoke Test (5 menit)

Buka URL SIPNS Anda, jalankan test berikut **berurutan**:

| # | Test | Expected | URL |
|---|------|----------|-----|
| 1 | Landing page | Logo + tombol "Login" | `https://<app>.onrender.com/` |
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

**Kalau ada yang gagal**, cek [Troubleshooting](#8-troubleshooting).

---

## 7. Phase 5 — Post-Deploy & Maintenance

### 7.1 Ganti Password Default (WAJIB untuk Production)

Login sebagai admin → menu **Users** → reset password untuk akun yang masih pakai default:

| Akun | Password Lama | Aksi |
|------|---------------|------|
| `admin` | `Admin@123` | Reset ke password kuat baru |
| `GR-001`, `GR-002`, `GR-003` | `Guru@123` | Reset per-guru |
| `2024001` - `2024010` | `<NIS>` | Minta siswa ganti sendiri via... oh, tidak ada self-reset. Admin harus reset manual. |

> 💡 Untuk tugas sekolah/demo, ganti minimal password admin. Kredensial seed lain bisa dibiarkan.

### 7.2 Setup Custom Domain (Opsional, Gratis)

1. Beli domain (Niagahoster, Namecheap, Cloudflare, dll.) — mis. `sipns.sekolah.sch.id`.
2. Di Render → service **sipns-web** → **Settings** → **Custom Domain** → tambahkan domain.
3. Render kasih instruksi DNS (tambahkan CNAME record).
4. Tunggu propagasi DNS (5 menit - 24 jam).
5. Render auto-issue Let's Encrypt SSL → HTTPS aktif.

### 7.3 Monitoring & Logs

| Resource | Lokasi | Keterangan |
|----------|--------|------------|
| App logs | Render → service → **Logs** | Stream real-time, retention 7 hari (free) |
| Request logs | Tab **Metrics** | Request count, latency, error rate |
| DB metrics | TiDB Cloud → cluster → **Monitoring** | Query per second, slow query log, storage |
| App errors | `/healthz/deep` | Cek dari uptime monitor eksternal |

### 7.4 Update Kode → Auto-Redeploy

Setiap `git push` ke branch `main` di GitHub → Render auto-detect → rebuild & redeploy.

Untuk deploy manual: Render dashboard → service → **Manual Deploy** → **Deploy latest commit**.

### 7.5 Schema Baru (Migration Tambahan)

Jika Anda tambah migration baru (`flask db migrate -m "..."` lokal → `flask db upgrade` lokal → commit file di `migrations/versions/`):

```bash
# Lokal
flask db migrate -m "tambah kolom xyz"
flask db upgrade
git add migrations/versions/<file>_xyz.py
git commit -m "feat: migration tambah kolom xyz"
git push
```

`startCommand` di `render.yaml` (`flask db upgrade && flask seed && gunicorn ...`) akan auto-apply migration baru setiap container start. `flask seed` idempotent → aman re-run.

---

## 8. Troubleshooting

### 8.1 Build Gagal: `cannot find -lpango` atau `OSError: cannot load library 'pango'`

**Penyebab:** System package WeasyPrint belum terinstall.

**Fix:**
1. Pastikan `Aptfile` ada di root repo dan isinya benar.
2. Pastikan `buildCommand` di `render.yaml` = `bash build.sh`.
3. Cek tab **Logs** → harusnya ada baris `Install system packages (WeasyPrint)`. Kalau tidak ada, build.sh tidak dijalankan.

### 8.2 `OperationalError: (2003, "Can't connect to MySQL server")`

**Penyebab:** `DATABASE_URL` salah, atau cluster TiDB paused.

**Fix:**
1. Login TiDB Cloud → cek status cluster (harus **Active**, bukan **Paused**).
2. Test koneksi lokal:
   ```bash
   mysql -h gateway01.singapore.prod.aws.tidbcloud.com -P 4000 -u root -p sipns
   ```
3. Kalau connect → cek `DATABASE_URL` di Render environment variables (typo? password salah?).
4. Pastikan tidak ada karakter spesial di password yang perlu URL-encode (`@` → `%40`, `#` → `%23`, dll.).

### 8.3 `OperationalError: (1045, "Access denied for user 'root'@'...'")`

**Penyebab:** Username/password salah.

**Fix:**
1. Reset password di TiDB Cloud → cluster → **Settings** → **User Management**.
2. Update `DATABASE_URL` di Render dengan password baru.
3. Save → auto-redeploy.

### 8.4 `OperationalError: SSL connection error: SSL is required`

**Penyebab:** TiDB Cloud butuh TLS, tapi `connect_args` tidak ada `ssl=True`.

**Fix:** Sudah dihandle otomatis di `app/config.py`:
```python
SQLALCHEMY_ENGINE_OPTIONS = {
    ...
    'connect_args': {
        'connect_timeout': 10,
        'ssl': True,    # ← harus ada
    },
}
```
Pastikan Anda pakai `ProductionConfig` (cek `FLASK_ENV=production` di env vars Render).

### 8.5 Build Gagal: `ERROR: Could not find a version that satisfies the requirement`

**Penyebab:** Versi di `requirements.txt` tidak ada di PyPI (typo?).

**Fix:**
1. Cek PyPI: https://pypi.org/project/<package>/
2. Update versi di `requirements.txt` → commit → push.

### 8.6 Gunicorn Error: `Worker timeout`

**Penyebab:** Request lebih dari `--timeout 60` detik (generate PDF bisa lambat di cold start).

**Fix:** Sudah diset `--timeout 60` di `render.yaml`. Kalau masih timeout, naikkan jadi `--timeout 120`.

### 8.7 `flask seed` Gagal dengan `IntegrityError`

**Penyebab:** Duplikat entry (NIS atau ID guru sudah ada).

**Fix:** Seed sudah idempotent (cek `if User.query.first(): return` di `app/seed.py`). Kalau masih error, cek apakah Anda jalankan seed di database yang sudah punya data.

### 8.8 Static File 404 (CSS/JS tidak load)

**Penyebab:** WhiteNoise belum terinstall atau path salah.

**Fix:**
1. Pastikan `whitenoise==6.8.2` ada di `requirements.txt` (sudah).
2. Cek `app/__init__.py` → `WhiteNoise(app.wsgi_app, root=app.static_folder)`.
3. Test: buka `https://<app>.onrender.com/static/css/custom.css` di browser → harusnya return CSS.

### 8.9 Login Loop / Session Hilang Tiap Refresh

**Penyebab:** Cookie tidak persisten, kemungkinan `SESSION_COOKIE_SECURE=True` tapi diakses via HTTP (bukan HTTPS).

**Fix:** Render default kasih HTTPS → cookie aman. Kalau akses via `http://` (bukan `https://`), cookie ditolak browser.
- Selalu akses via `https://<app>.onrender.com`.
- `PREFERRED_URL_SCHEME='https'` sudah diset di `ProductionConfig` → `url_for(_external=True)` selalu generate URL HTTPS.

### 8.10 TiDB Cluster "Paused" / "Resuming"

**Penyebab:** TiDB Cloud Serverless auto-pause setelah 7 hari tidak ada koneksi (sesuai ToS).

**Fix:**
1. Login TiDB Cloud → klik **Resume**.
2. Tunggu ~30 detik sampai status **Active**.
3. Trigger redeploy di Render (Settings → Manual Deploy) atau ping `/healthz` beberapa kali (Render health check akan auto-retry).

### 8.11 Blueprint Error: "pre-deploy command is not supported for free tier services"

**Penyebab:** Sejak akhir 2024, Render **menonaktifkan `preDeployCommand` di free tier** (fitur hanya untuk Starter+ plan). Jika `render.yaml` Anda masih punya `preDeployCommand:`, Apply akan error.

**Fix:** File `render.yaml` di repo ini **sudah diperbaiki** — `preDeployCommand` dihapus dan `flask db upgrade && flask seed` digabung ke `startCommand`. Pastikan Anda sudah `git pull`/`git fetch` versi terbaru sebelum push.

Verifikasi lokal:
```bash
# Seharusnya TIDAK ada preDeployCommand di output
grep -i "preDeploy" render.yaml
# Output kosong = OK. Kalau ada baris preDeployCommand, berarti file lama.
```

**Kenapa aman digabung ke startCommand?**
- `flask db upgrade` → Alembic track state, no-op jika tidak ada migration baru.
- `flask seed` → guard `if User.query.first(): return` di `app/seed.py`, no-op setelah data pertama.
- Keduanya idempotent → aman re-run setiap container start, termasuk saat wake dari sleep.

**Trade-off:** tambah ~2-3 detik ke cold start (yang memang sudah 30-50 detik di free tier).

### 8.12 Blueprint Error: "Credit card required"

**Penyebab:** Sejak akhir 2024, Render mewambahkan verifikasi credit card untuk semua akun baru (anti-abuse / crypto-mining prevention). Kartu **tidak di-charge** untuk free tier, hanya untuk verifikasi.

**Fix (opsional):**
- Tambahkan debit/credit card ke akun Render → https://dashboard.render.com/billing
- Setelah verifikasi, Anda bisa create Blueprint/Web Service gratis seperti biasa.

**Fix (alternatif tanpa kartu):**
- Pakai Railway.app (sudah tidak dipakai di project ini, tapi opsi valid): $5/bulan credit, no CC untuk usage di bawah credit.
- Pakai PythonAnywhere: 100% free, no CC, tapi paradigma deploy berbeda (WSGI file, bukan container).

---

## 9. Mengurangi Cold Start (Opsional)

Render free tier sleep setelah 15 menit tidak ada request. Request pertama setelah sleep butuh ~30-50 detik (container spin-up + import Python + koneksi DB).

**Strategi mitigasi (opsional, gratis):**

### 9.1 Cron Job Ping `/healthz`

Daftar cron job (cron-job.org / UptimeRobot) untuk ping `/healthz` setiap 10 menit:

```
URL:     https://<app>.onrender.com/healthz
Method:  GET
Interval: every 10 minutes
```

> ✅ **/healthz TIDAK query DB** → super cepat, tidak ada efek samping.
> ✅ Ping setiap 10 menit (di bawah threshold 15 menit) → instance tetap awake.
> ✅ Response time ~50-200ms (sub-1s ideal untuk Render).

### 9.2 Upgrade ke Render Paid (Opsional)

| Plan | Harga | Cold Start | RAM |
|------|-------|------------|-----|
| Free | $0 | 30-50s | 512 MB |
| Starter | $7/mo | ~5-10s | 512 MB |
| Standard | $25/mo | ~5s | 2 GB |
| Pro | $85/mo | ~3s | 4 GB |

Untuk tugas sekolah/demo, free tier sudah cukup. Untuk production beneran, mulai dari Starter.

### 9.3 Optimasi Cold Start yang Sudah Diterapkan di Kode Ini

| Optimasi | Lokasi | Efek |
|----------|--------|------|
| `--workers 1` (bukan 2) | `render.yaml` startCommand | Hindari OOM di free tier 512 MB |
| `--preload` | `render.yaml` startCommand | Load app SEKALI sebelum forking (dengan 1 worker = load lebih awal di startup) |
| WhiteNoise static files | `app/__init__.py` | Serve `/static/*` langsung dari WSGI, no Flask overhead |
| `/healthz` no-DB | `app/__init__.py` | Response < 10ms, cocok untuk Render health check |
| Lazy import WeasyPrint | `app/services/laporan_service.py` | Module weight 50MB tidak di-import saat startup |
| `pool_pre_ping=True` | `app/config.py` | Stale connection auto-detect, no failed request |
| `pool_recycle=3600` | `app/config.py` | Recycle connection sebelum MySQL `wait_timeout` (default 8h di TiDB) |
| `connect_timeout=10` | `app/config.py` | Fail fast kalau DB unreachable (daripada hang) |

---

## 10. Checklist Final

Sebelum menganggap deploy selesai, pastikan SEMUA item di bawah ini ✅:

- [ ] Repo SIPNS ter-push ke GitHub (branch main)
- [ ] `render.yaml`, `Aptfile`, `build.sh`, `runtime.txt`, `wsgi.py` ada di root
- [ ] `whitenoise` & `gunicorn` ada di `requirements.txt`
- [ ] `.env` TIDAK ter-commit (cek `git log -- .env` kosong)
- [ ] TiDB Cloud cluster **Active**, database `sipns` dibuat
- [ ] `DATABASE_URL` di Render env vars = connection string TiDB (dengan `?charset=utf8mb4`)
- [ ] `SECRET_KEY` di-set (auto-generated oleh Render)
- [ ] Build Render sukses (lihat log: `Booting worker with pid: ...`)
- [ ] Pre-deploy sukses (lihat log: `flask db upgrade` + `flask seed` tanpa error)
- [ ] `/healthz` return `{"status":"ok"}` (HTTP 200)
- [ ] `/healthz/deep` return `{"status":"ok","db":"ok"}` (HTTP 200)
- [ ] Login admin berhasil, dashboard muncul
- [ ] Login guru & siswa berhasil
- [ ] Generate PDF kelas berhasil (file ter-download)
- [ ] Generate Excel berhasil (file ter-download)
- [ ] **WAJIB:** Ganti password default `admin` jika production

Kalau semua ✅, **SIPNS Anda sudah LIVE di internet!** 🎉🚀

URL publik: `https://sipns-web.onrender.com` (atau sesuai nama service Anda)
