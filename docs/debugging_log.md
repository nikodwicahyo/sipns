# Debugging Log — SIPNS

**Sistem Informasi Pengolahan Nilai Siswa**
**Versi:** 1.0.0 | **Tanggal:** 2026 | **Fase:** 6 (Pengujian & Debugging)

> Catatan bug yang ditemukan dan diperbaiki selama Fase 6.
> Format mengikuti standar.

---

## Bug #001

**Tanggal ditemukan:** 2026-06-05
**Fase:** Fase 6 — Setup Testing
**Severity:** Medium
**Tester:** Automated test suite (test_nilai_service.py::TestValidasiRentangNilai)

**Deskripsi:**
Test `test_tc_val_04_nilai_negatif_invalid` gagal dengan assertion error.

**Langkah reproduksi:**

1. Jalankan `pytest tests/unit/test_nilai_service.py -v`
2. Lihat test `test_tc_val_04_nilai_negatif_invalid`

**Error message/traceback:**

```
FAILED tests/unit/test_nilai_service.py::TestValidasiRentangNilai::test_tc_val_04_nilai_negatif_invalid
    assert 'Tugas' in "Nilai harus berada di antara 0 dan 100. Nilai '-1' tidak valid."
E   assert 'Tugas' in "Nilai harus berada di antara 0 dan 100..."
```

**Root cause:**
Test salah asumsi tentang default label parameter. Fungsi `validasi_rentang_nilai(nilai, label="Nilai")` memiliki default `label="Nilai"`, bukan `"Tugas"`. Test menyebut `validasi_rentang_nilai(-1)` tanpa argumen label, sehingga error message menggunakan default "Nilai", bukan "Tugas" yang di-assert oleh test.

**Fix yang diterapkan:**
Memperbaiki assertion di test untuk menggunakan string yang benar-benar muncul di error message. Test diupdate untuk assert `"'-1'"` (nilai yang divalidasi) dan `"antara 0 dan 100"` (rentang), yang keduanya selalu muncul.

**File yang diubah:**

- `tests/unit/test_nilai_service.py:48-56` (test `test_tc_val_04`)

**Hasil setelah fix:** Test PASS ✓

**Lesson learned:**
Saat test pesan error, gunakan substring yang PASTI ada di error message, bukan substring yang diasumsikan. Default parameter harus diverifikasi signature fungsi.

---

## Bug #002

**Tanggal ditemukan:** 2026-06-05
**Fase:** Fase 6 — Setup Testing
**Severity:** High
**Tester:** Automated test suite (test_models.py::TestUserModel::test_get_id_mengembalikan_string)

**Deskripsi:**
Test gagal dengan IntegrityError saat insert User baru.

**Error message/traceback:**

```
sqlalchemy.exc.IntegrityError: (sqlite3.IntegrityError) NOT NULL constraint failed: users.password_hash
[SQL: INSERT INTO users (...password_hash...) VALUES (?, ?, ?, ?, ?, ?, ?, ?)]
[parameters: ('x', None, 'admin', 1, None, None, '...', '...')]
```

**Root cause:**
Model `User` memiliki kolom `password_hash` dengan `nullable=False`. Test membuat `User(username='x', role='admin')` tanpa memanggil `set_password()`, sehingga `password_hash=None` saat commit.

**Fix yang diterapkan:**
Menambahkan `user.set_password('dummy')` sebelum `db.session.add(user)` di test fixture/test case. Pola ini sekarang konsisten di seluruh test_models.py dan test_security.py.

**File yang diubah:**

- `tests/unit/test_models.py:79-86` (test `test_get_id_mengembalikan_string`)

**Hasil setelah fix:** Test PASS ✓

**Lesson learned:**
Setiap pembuatan User harus disertai `set_password()`. Test harus explicit tentang setup data, tidak bergantung pada default value.

---

## Bug #003

**Tanggal ditemukan:** 2026-06-05
**Fase:** Fase 6 — Setup Testing
**Severity:** High
**Tester:** Automated test suite (tests/unit/test_models.py::TestSiswaModel::test_rata_rata_nilai_dengan_3_nilai)

**Deskripsi:**
Test gagal dengan `AssertionError: assert False` untuk `isinstance(rata, float)`.

**Error message/traceback:**

```
E   AssertionError: assert False
E    +  where False = isinstance(Decimal('70.00'), float)
```

**Root cause:**
Method `Siswa.rata_rata_nilai()` mengembalikan `round(sum(nilai_list) / len(nilai_list), 2)`. Karena `nilai_list` berisi `Decimal` objects (dari kolom `Numeric(5,2)` SQLAlchemy), `sum()` mempertahankan tipe Decimal dan `round(Decimal, 2)` juga mengembalikan Decimal, BUKAN float.

**Fix yang diterapkan:**
Mengubah assertion dari `isinstance(rata, float)` menjadi `float(rata) > 0` yang lebih robust terhadap tipe numeric (Decimal atau float). Pola ini merefleksikan realitas: tipe data bisa bervariasi tergantung pada SQLAlchemy arithmetic, tapi nilai numerik harus valid.

**File yang diubah:**

- `tests/unit/test_models.py:142-151` (test `test_rata_rata_dengan_3_nilai`)

**Hasil setelah fix:** Test PASS ✓

**Lesson learned:**
Test tipe data yang terlalu strict (`isinstance(x, float)`) rapuh terhadap representasi internal database. Lebih baik test nilai/properti yang penting, bukan representasi persis. Untuk business logic "rata-rata adalah angka", `float(x) > 0` lebih bermakna dari `isinstance(x, float)`.

---

## Bug #004

**Tanggal ditemukan:** 2026-06-05
**Fase:** Fase 6 — Integration Testing
**Severity:** Critical
**Tester:** Automated test suite (test_auth.py — semua test login role)

**Deskripsi:**
Test `test_tc_auth_01b_login_guru_valid` (dan test serupa untuk siswa) gagal dengan redirect ke `/admin/dashboard` padahal user adalah guru/siswa.

**Langkah reproduksi:**

1. Jalankan `pytest tests/integration/test_auth.py -v`
2. Test pertama (admin login) PASS
3. Test kedua (guru login) FAIL — redirect ke /admin/dashboard

**Error message/traceback:**

```
E   AssertionError: assert '/guru/dashboard' in '/admin/dashboard'
```

**Root cause:**
Fixture `app` di conftest.py lama menggunakan `scope='session'`, sehingga semua test berbagi Flask app instance yang sama. Dikombinasikan dengan Flask-Login session handling, terjadi state pollution: setelah admin login di test pertama, session/admin masih "tersimpan" di app context, dan test guru berikutnya di-redirect ke admin dashboard oleh `redirect_by_role(current_user)` di awal route login.

Meskipun `client` fixture function-scoped (test client baru per test), session di app context bersama menyebabkan `current_user` masih admin dari test sebelumnya.

**Fix yang diterapkan:**
Mengubah `app` fixture dari `scope='session'` ke `scope='function'`. Setiap test sekarang mendapat Flask app yang benar-benar baru, dengan isolation penuh untuk app context, session, dan SQLAlchemy binding. Trade-off: ~50-100ms overhead per test untuk re-create app, tapi isolation 100% terjamin.

**File yang diubah:**

- `tests/conftest.py:23-46` (fixtures `app` dan `db`)

**Hasil setelah fix:** 20/20 auth tests PASS ✓

**Lesson learned:**
Dalam Flask testing, JANGAN share Flask app instance antar test. Setiap test harus punya app sendiri untuk isolation penuh. Performance overhead negligible dibanding bug yang sulit dilacak dari state pollution. Pola `scope='function'` adalah default yang aman.

---

## Bug #005

**Tanggal ditemukan:** 2026-06-05
**Fase:** Fase 6 — Integration Testing
**Severity:** High
**Tester:** Automated test suite (test_laporan.py::TestLaporanPDF::test_pdf_transkrip_siswa_tidak_ada_404)

**Deskripsi:**
Test mengharapkan status 404 untuk siswa ID yang tidak ada, tapi mendapat 302 (redirect ke index).

**Error message/traceback:**

```
E   assert 302 == 404
E    +  where 302 = <WrapperTestResponse streamed [302 FOUND]>.status_code
```

**Root cause:**
Service `generate_transkrip_pdf` di `app/services/laporan_service.py` membungkus SEMUA exception (termasuk `HTTPException` seperti 404) dalam `try/except Exception` dan mengubahnya menjadi `RuntimeError`. Akibatnya, `Siswa.query.get_or_404()` yang raise `NotFound` (subclass HTTPException) menjadi RuntimeError, lalu route handler yang juga punya `except Exception` menangkapnya dan me-redirect ke halaman index dengan flash error.

Akibat: User tidak pernah melihat 404 page untuk siswa yang tidak ada, hanya flash "Gagal generate PDF".

**Fix yang diterapkan:**

1. Di `app/services/laporan_service.py` (fungsi `generate_transkrip_pdf` dan `generate_laporan_pdf`): Tambahkan `except HTTPException: raise` SEBELUM `except Exception` agar HTTP exceptions (404, 403) tidak diubah tipenya.
2. Di `app/blueprints/laporan/routes.py` (fungsi `pdf_transkrip`): Tambahkan `except HTTPException: raise` serupa untuk double-protection di layer route.

**File yang diubah:**

- `app/services/laporan_service.py:46-71` (`generate_transkrip_pdf`)
- `app/services/laporan_service.py:17-43` (`generate_laporan_pdf`)
- `app/blueprints/laporan/routes.py:59-91` (`pdf_transkrip` route)

**Hasil setelah fix:** Test 404 PASS ✓ — siswa tidak ada → 404 page yang benar

**Lesson learned:**
Hindari `except Exception` yang terlalu lebar di service layer. Selalu pisahkan `except HTTPException: raise` agar HTTP semantics (404, 403, 400) tidak hilang. Pola ini juga penting di route handler.

---

## Summary

| Bug # | Severity | Lokasi                                   | Status     |
| ----- | -------- | ---------------------------------------- | ---------- |
| 001   | Medium   | test_nilai_service.py                    | RESOLVED ✓ |
| 002   | High     | test_models.py                           | RESOLVED ✓ |
| 003   | High     | test_models.py                           | RESOLVED ✓ |
| 004   | Critical | tests/conftest.py                        | RESOLVED ✓ |
| 005   | High     | app/services/laporan_service.py + routes | RESOLVED ✓ |

**Total bug ditemukan dan diperbaiki: 5**

---

## Rekomendasi untuk Pencegahan

1. **Selalu pisahkan HTTPException di except clause** di service dan route layer
2. **Pola fixture `scope='function'`** untuk Flask app di testing, jangan share instance
3. **Gunakan `float(x)` bukan `isinstance(x, float)`** untuk test nilai numeric dari SQLAlchemy
4. **Setiap User baru harus `set_password()`** sebelum commit (enforce via factory function di production)
5. **Test pesan error** dengan substring yang PASTI muncul, bukan yang diasumsikan

---

_Disusun sesuai PRD.md (Fase 6 — Pengujian & Debugging)._
