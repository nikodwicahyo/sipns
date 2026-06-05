"""
Modul: blueprints/laporan/routes.py
Deskripsi: Route handler untuk modul Laporan (PDF & Excel).

Endpoint ringkasan
------------------
Halaman UI:
- ``GET  /laporan/rekap-kelas``          → Halaman filter & preview laporan.

Cetak PDF:
- ``GET  /laporan/pdf/kelas/<kelas>``    → Legacy: PDF rekap satu kelas (backward compat).
- ``GET  /laporan/pdf/filter``           → PDF rekap dengan filter lengkap (guru/mapel/kelas/siswa/status).
- ``GET  /laporan/pdf/transkrip/<id>``   → PDF transkrip personal siswa.

Ekspor Excel:
- ``GET  /laporan/excel``                → Ekspor XLSX dengan filter opsional.

AJAX (cascading dropdown):
- ``GET  /laporan/api/guru``                          → List guru aktif.
- ``GET  /laporan/api/mata-pelajaran?guru_id=X``     → List mapel (filter by guru).
- ``GET  /laporan/api/kelas?guru_id=X&mata_pelajaran=Y`` → List kelas.
- ``GET  /laporan/api/siswa?guru_id=X&mata_pelajaran=Y&kelas=Z`` → List siswa.

Akses:
- Admin & Guru: semua endpoint laporan.
- Siswa: TIDAK boleh akses (403) — di-guard di setiap handler.

Catatan penting:
- HTTPException (404, 403) di-re-raise apa adanya di semua handler
  yang memanggil service. Lihat debugging_log.md Bug #005 untuk
  konteks historis.
- Audit log dicatat SETELAH PDF/Excel berhasil di-generate.
- Filter scope:
  * Admin  → tidak ada auto-scope (akses penuh).
  * Guru   → ``mata_pelajaran`` di-lock ke ``current_user.guru.mata_pelajaran``;
              ``guru_id`` di-lock ke ``current_user.guru.id`` (jika filter guru_id
              tidak diisi atau diisi dengan ID lain, akan di-override ke diri sendiri).

Author : Niko Dwicahyo
Versi  : 1.1.0
"""
import logging
from flask import render_template, Response, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from app.blueprints.laporan import laporan_bp
from app.blueprints.decorators import role_required
from app import db
from app.models import Siswa, Guru, Nilai
from app.services.laporan_service import generate_laporan_pdf, generate_transkrip_pdf, export_excel
from app.services.audit_service import catat_audit_log
from app.services.nilai_service import hitung_statistik_kelas
from app.utils.time import now_jakarta

logger = logging.getLogger(__name__)


# ===========================================================================
# HELPER FUNCTIONS
# ===========================================================================

STATUS_LULUS_CHOICES = ('lulus', 'tidak_lulus')


def _resolve_mata_pelajaran_filter():
    """Tentukan filter mata pelajaran berdasarkan role user yang sedang login.

    Aturan akses (sesuai PRD §14 kontrol akses):
    - Admin  : tidak ada filter mapel (``None``) — akses penuh ke semua mapel.
    - Guru   : filter dikunci ke ``current_user.guru.mata_pelajaran``.
               Guru hanya boleh melihat/mencetak nilai untuk mapel yang
               diampu. Ini adalah authorization filter — bukan fitur
               optional — untuk mencegah guru mapel A mengakses nilai
               mapel B.
    - Siswa  : tidak pernah masuk ke route handler ini (sudah di-block
               via ``abort(403)`` di masing-masing endpoint).

    Returns:
        str | None: Nama mata pelajaran untuk filter query, atau ``None``
        untuk admin (tidak ada filter). Mengembalikan ``None`` juga jika
        user role ``guru`` ternyata tidak memiliki relasi ``guru`` (data
        integrity issue — defensive fallback agar tidak crash).
    """
    if current_user.is_guru() and getattr(current_user, 'guru', None):
        return current_user.guru.mata_pelajaran
    return None


def _resolve_guru_id_scope():
    """Tentukan guru_id scope untuk role guru (defensive).

    Returns:
        int | None: ``current_user.guru.id`` untuk role guru, ``None`` untuk
        admin (akses penuh). ``None`` jika guru tidak punya relasi ``guru``.
    """
    if current_user.is_guru() and getattr(current_user, 'guru', None):
        return current_user.guru.id
    return None


def _parse_filter_args():
    """Parse & normalisasi filter query params dari ``request.args``.

    Mengembalikan dict dengan key yang konsisten (snake_case) dan value
    yang sudah di-normalisasi. Value yang kosong / invalid di-set ke
    ``None`` agar mudah di-handle di query builder.

    Validation rules:
    - ``guru_id`` & ``siswa_id`` di-parse sebagai int (None jika invalid).
    - ``mata_pelajaran`` & ``kelas`` di-strip whitespace, None jika kosong.
    - ``status_lulus`` harus salah satu dari ``STATUS_LULUS_CHOICES``,
      selain itu di-set None (ignored).

    Returns:
        dict: ``{guru_id, mata_pelajaran, kelas, siswa_id, status_lulus}``.
        Semua value bisa ``None`` (artinya "tidak difilter").
    """
    raw_status = (request.args.get('status_lulus') or '').strip().lower()
    status_lulus = raw_status if raw_status in STATUS_LULUS_CHOICES else None

    return {
        'guru_id': _safe_int(request.args.get('guru_id')),
        'mata_pelajaran': (request.args.get('mata_pelajaran') or '').strip() or None,
        'kelas': (request.args.get('kelas') or '').strip() or None,
        'siswa_id': _safe_int(request.args.get('siswa_id')),
        'status_lulus': status_lulus,
    }


def _safe_int(value):
    """Parse string ke int, return None jika kosong atau invalid.

    Digunakan untuk query param ``guru_id`` dan ``siswa_id`` agar
    filter kosong / malformed tidak menyebabkan error 500 di query.
    """
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _filters_active(filters):
    """Cek apakah minimal satu filter aktif (non-None).

    Returns:
        bool: ``True`` jika ada filter yang terisi.
    """
    return any(v is not None for v in filters.values())


def _build_nilai_query(filters, mapel_scope=None, guru_id_scope=None):
    """Build SQLAlchemy query untuk tabel ``Nilai`` sesuai filter.

    Args:
        filters (dict): Output dari ``_parse_filter_args``.
        mapel_scope (str | None): Jika diisi, filter ``Nilai.mata_pelajaran``
            dipaksa ke nilai ini (untuk enforce role guru). Default ``None``.
        guru_id_scope (int | None): Jika diisi, filter ``Nilai.guru_id``
            dipaksa ke nilai ini. Default ``None``.

    Returns:
        Query: SQLAlchemy Query object, belum dieksekusi. Caller bisa
        menambahkan ``.order_by()``, ``.all()``, ``.count()``, dll.
    """
    query = (
        Nilai.query
        .join(Siswa, Nilai.siswa_id == Siswa.id)
        .filter(Siswa.deleted_at.is_(None))
    )
    # Role-based scope (guru: mapel di-lock, guru_id di-lock ke diri sendiri).
    if mapel_scope:
        query = query.filter(Nilai.mata_pelajaran == mapel_scope)
    if guru_id_scope is not None:
        query = query.filter(Nilai.guru_id == guru_id_scope)

    # User-applied filters (skip jika None).
    # Untuk admin yang tidak punya scope, gunakan filter user langsung.
    if not mapel_scope and filters.get('mata_pelajaran'):
        query = query.filter(Nilai.mata_pelajaran == filters['mata_pelajaran'])
    if not guru_id_scope and filters.get('guru_id') is not None:
        query = query.filter(Nilai.guru_id == filters['guru_id'])
    if filters.get('kelas'):
        query = query.filter(Siswa.kelas == filters['kelas'])
    if filters.get('siswa_id') is not None:
        query = query.filter(Nilai.siswa_id == filters['siswa_id'])
    if filters.get('status_lulus') == 'lulus':
        query = query.filter(Nilai.status_lulus.is_(True))
    elif filters.get('status_lulus') == 'tidak_lulus':
        query = query.filter(Nilai.status_lulus.is_(False))
    return query


def _resolve_filter_info(filters):
    """Bangun dict label manusiawi dari filter untuk ditampilkan di header.

    Field None / kosong di-skip agar header PDF/Excel tidak menampilkan
    label yang tidak relevan. Lookup nama guru & siswa dari DB agar
    label yang ditampilkan adalah nama, bukan ID.

    Args:
        filters (dict): Output dari ``_parse_filter_args``.

    Returns:
        dict: ``{guru, siswa, status}`` dengan value string (atau None).
    """
    info = {'guru': None, 'siswa': None, 'status': None}
    if filters.get('guru_id') is not None:
        guru = Guru.query.get(filters['guru_id'])
        if guru and guru.deleted_at is None:
            info['guru'] = f"{guru.nama_guru} ({guru.mata_pelajaran})"
    if filters.get('siswa_id') is not None:
        siswa = Siswa.query.get(filters['siswa_id'])
        if siswa and siswa.deleted_at is None:
            info['siswa'] = f"{siswa.nama} ({siswa.nis})"
    if filters.get('status_lulus') == 'lulus':
        info['status'] = 'Lulus'
    elif filters.get('status_lulus') == 'tidak_lulus':
        info['status'] = 'Tidak Lulus'
    return info


def _validate_filter_ids(filters):
    """Validasi ID yang dipakai sebagai filter — tolak jika tidak valid.

    Untuk filter yang merujuk ke ID (guru_id, siswa_id), cek bahwa:
    1. Record ada di DB.
    2. Tidak soft-deleted.

    Returns:
        tuple[str | None, str | None]: ``(error_message, redirect_url)``.
        Jika valid, kembalikan ``(None, None)``. Jika tidak valid,
        kembalikan ``(error_message, None)`` — caller yang memutuskan
        redirect target (biasanya ke ``laporan.index``).
    """
    if filters.get('guru_id') is not None:
        guru = Guru.query.get(filters['guru_id'])
        if not guru or guru.deleted_at is not None:
            return 'Filter guru tidak valid (guru tidak ditemukan atau sudah dihapus).', None
    if filters.get('siswa_id') is not None:
        siswa = Siswa.query.get(filters['siswa_id'])
        if not siswa or siswa.deleted_at is None:
            return 'Filter siswa tidak valid (siswa tidak ditemukan atau sudah dihapus).', None
    return None, None


# ===========================================================================
# HALAMAN UTAMA LAPORAN
# ===========================================================================

@laporan_bp.route('/rekap-kelas')
@login_required
def index():
    """Halaman UI utama untuk filter, preview, cetak & ekspor laporan.

    Behavior:
    - Saat pertama kali dibuka (tanpa filter): tampilkan 2 kartu legacy
      (PDF per kelas & Export Excel dengan dropdown kelas) + section
      filter kosong di atas.
    - Saat filter diterapkan (query param ada): jalankan query dengan
      filter, tampilkan statistik cards + preview DataTable + tombol
      Cetak PDF / Export Excel yang otomatis pakai filter aktif.

    Akses: Admin & Guru. Siswa di-redirect ke 403 di setiap endpoint
    yang menghasilkan file.
    """
    filters = _parse_filter_args()
    mapel_scope = _resolve_mata_pelajaran_filter()
    guru_id_scope = _resolve_guru_id_scope()

    # Daftar nilai dropdown filter (untuk populate UI).
    # Guru_list hanya untuk admin (guru tidak perlu pilih dirinya sendiri).
    if current_user.is_admin():
        guru_list = Guru.daftar_guru_aktif()
    else:
        guru_list = []

    # Daftar mata pelajaran: distinct dari nilai (bisa di-scope by guru_id).
    # Untuk role guru: otomatis ter-scope ke mapel-nya.
    mapel_list = Nilai.daftar_mata_pelajaran(
        guru_id=filters.get('guru_id') or guru_id_scope,
    )

    # Daftar kelas: distinct dari siswa yang punya nilai (sesuai scope).
    kelas_query = (
        db.session.query(Siswa.kelas)
        .join(Nilai, Nilai.siswa_id == Siswa.id)
        .filter(Siswa.deleted_at.is_(None))
    )
    if mapel_scope:
        kelas_query = kelas_query.filter(Nilai.mata_pelajaran == mapel_scope)
    elif filters.get('mata_pelajaran'):
        kelas_query = kelas_query.filter(Nilai.mata_pelajaran == filters['mata_pelajaran'])
    if filters.get('guru_id') or guru_id_scope:
        kelas_query = kelas_query.filter(
            Nilai.guru_id == (filters.get('guru_id') or guru_id_scope)
        )
    kelas_list = [r[0] for r in kelas_query.distinct().order_by(Siswa.kelas).all()]

    # Legacy: kelas_list untuk kartu PDF per kelas & Export Excel sederhana.
    # Pakai list yang sudah ter-scope agar konsisten dengan section filter.
    legacy_kelas_list = kelas_list

    # Jika ada filter aktif, jalankan query & hitung statistik untuk preview.
    data_nilai = []
    statistik = {
        'rata_rata': 0, 'tertinggi': 0, 'terendah': 0, 'persen_lulus': 0,
        'total': 0, 'jumlah_lulus': 0, 'jumlah_tidak_lulus': 0,
    }
    filters_applied = _filters_active(filters)

    if filters_applied:
        # Guard: siswa tidak boleh akses laporan (tidak perlu di sini karena
        # siswa tidak akan sampai ke sini — sudah di-redirect di setiap
        # endpoint laporan). Tetap defensif: kalau ada yang nyasar, abort.
        if current_user.is_siswa():
            abort(403)
        # Validasi ID filter (guru_id / siswa_id) agar tidak error 500.
        err, _ = _validate_filter_ids(filters)
        if err:
            flash(err, 'warning')
            return redirect(url_for('laporan.index'))

        query = _build_nilai_query(filters, mapel_scope=mapel_scope,
                                   guru_id_scope=guru_id_scope)
        data_nilai = query.order_by(Siswa.kelas, Siswa.nama).all()
        statistik = hitung_statistik_kelas(data_nilai)

    return render_template(
        'laporan/index.html',
        # Data untuk section filter (cascading dropdown).
        guru_list=guru_list,
        mapel_list=mapel_list,
        kelas_list=kelas_list,
        # Filter aktif (untuk pre-select dropdown & hidden input).
        filters=filters,
        mapel_scope=mapel_scope,
        is_guru_role=current_user.is_guru(),
        # Data untuk preview (kosong jika tidak ada filter).
        data_nilai=data_nilai,
        statistik=statistik,
        filters_applied=filters_applied,
        # Legacy cards.
        legacy_kelas_list=legacy_kelas_list,
    )


# ===========================================================================
# PDF REKAP KELAS
# ===========================================================================

@laporan_bp.route('/pdf/kelas/<path:kelas>')
@login_required
def pdf_kelas(kelas):
    """Generate & download PDF rekap nilai satu kelas (LEGACY).

    Endpoint lama — dipertahankan untuk backward compat. Hanya menerima
    parameter ``kelas`` dari URL path. Filter mapel otomatis ter-apply
    sesuai role (admin: None, guru: mapel-nya).

    Untuk filter multi-kriteria (guru/siswa/status), gunakan
    ``/laporan/pdf/filter``.

    Args:
        kelas (str): Nama kelas (path param, support karakter khusus).

    Returns:
        Response: File PDF sebagai attachment, atau redirect + flash
        jika tidak ada data nilai untuk kelas tersebut.

    Raises:
        403: Jika user adalah siswa.
    """
    # Guard: siswa tidak boleh cetak laporan kelas.
    if current_user.is_siswa():
        abort(403)

    mapel_filter = _resolve_mata_pelajaran_filter()

    # Guard: tolak generate PDF jika kelas tidak punya data nilai
    # yang sesuai dengan scope akses user.
    check_query = (
        Nilai.query
        .join(Siswa, Nilai.siswa_id == Siswa.id)
        .filter(Siswa.kelas == kelas, Siswa.deleted_at.is_(None))
    )
    if mapel_filter:
        check_query = check_query.filter(Nilai.mata_pelajaran == mapel_filter)
    if not check_query.first():
        suffix = f' mata pelajaran {mapel_filter}' if mapel_filter else ''
        flash(f'Tidak ada data nilai untuk kelas {kelas}{suffix}.', 'warning')
        return redirect(url_for('laporan.index'))

    try:
        pdf_bytes = generate_laporan_pdf(kelas, mata_pelajaran=mapel_filter)
        tanggal = now_jakarta().strftime('%Y%m%d')

        mapel_desc = f' (mapel: {mapel_filter})' if mapel_filter else ''
        catat_audit_log(
            user_id=current_user.id,
            action='PRINT_PDF',
            table_name='nilai',
            description=f'Cetak PDF rekap nilai kelas {kelas}{mapel_desc}',
            ip_address=request.remote_addr,
        )
        safe_kelas = kelas.replace('/', '_')
        safe_mapel = mapel_filter.replace('/', '_') if mapel_filter else None
        if safe_mapel:
            filename = f'rekap_{safe_kelas}_{safe_mapel}_{tanggal}.pdf'
        else:
            filename = f'rekap_{safe_kelas}_{tanggal}.pdf'
        return Response(
            pdf_bytes,
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename={filename}'
            },
        )
    except Exception as e:
        flash(f'Gagal generate PDF: {str(e)}', 'error')
        return redirect(url_for('laporan.index'))


@laporan_bp.route('/pdf/filter')
@login_required
def pdf_filter():
    """Generate & download PDF rekap nilai dengan filter multi-kriteria.

    Query params (semua optional):
    - ``kelas`` (str): Filter kelas.
    - ``guru_id`` (int): Filter guru penginput.
    - ``mata_pelajaran`` (str): Filter mapel.
    - ``siswa_id`` (int): Filter siswa.
    - ``status_lulus`` (str): ``lulus`` / ``tidak_lulus``.

    Aturan:
    - Minimal satu filter harus diisi (jika tidak, redirect ke index).
    - Untuk role guru: ``mata_pelajaran`` & ``guru_id`` otomatis ter-scope.
    - ``kelas`` WAJIB diisi untuk PDF rekap (PDF butuh scope kelas).

    Returns:
        Response: File PDF sebagai attachment.
    """
    if current_user.is_siswa():
        abort(403)

    filters = _parse_filter_args()
    mapel_scope = _resolve_mata_pelajaran_filter()
    guru_id_scope = _resolve_guru_id_scope()

    # PDF rekap membutuhkan kelas sebagai scope utama.
    kelas = filters.get('kelas')
    if not kelas:
        flash('Pilih kelas terlebih dahulu untuk mencetak PDF rekap.', 'warning')
        return redirect(url_for('laporan.index'))

    # Validasi ID filter.
    err, _ = _validate_filter_ids(filters)
    if err:
        flash(err, 'warning')
        return redirect(url_for('laporan.index'))

    # Guard: cek ada data nilai yang match.
    check_query = _build_nilai_query(filters, mapel_scope=mapel_scope,
                                     guru_id_scope=guru_id_scope)
    if not check_query.first():
        flash('Tidak ada data nilai yang sesuai dengan filter yang dipilih.', 'warning')
        return redirect(url_for('laporan.index'))

    # Resolusi filter info untuk header PDF.
    filter_info = _resolve_filter_info(filters)

    # Effective mapel (untuk diteruskan ke service & filename).
    effective_mapel = mapel_scope or filters.get('mata_pelajaran')
    effective_guru_id = guru_id_scope if guru_id_scope is not None else filters.get('guru_id')

    try:
        pdf_bytes = generate_laporan_pdf(
            kelas,
            mata_pelajaran=effective_mapel,
            guru_id=effective_guru_id,
            siswa_id=filters.get('siswa_id'),
            status_lulus=filters.get('status_lulus'),
            filter_info=filter_info,
        )
        tanggal = now_jakarta().strftime('%Y%m%d')

        # Audit log dengan info filter lengkap.
        filter_desc_parts = [f'kelas={kelas}']
        if effective_mapel:
            filter_desc_parts.append(f'mapel={effective_mapel}')
        if effective_guru_id is not None:
            filter_desc_parts.append(f'guru_id={effective_guru_id}')
        if filters.get('siswa_id') is not None:
            filter_desc_parts.append(f'siswa_id={filters["siswa_id"]}')
        if filters.get('status_lulus'):
            filter_desc_parts.append(f'status={filters["status_lulus"]}')
        catat_audit_log(
            user_id=current_user.id,
            action='PRINT_PDF',
            table_name='nilai',
            description=f'Cetak PDF filter ({", ".join(filter_desc_parts)})',
            ip_address=request.remote_addr,
        )

        # Bangun filename dari filter aktif.
        filename_parts = ['rekap', kelas.replace('/', '_')]
        if effective_mapel:
            filename_parts.append(effective_mapel.replace('/', '_'))
        if filters.get('status_lulus'):
            filename_parts.append(filters['status_lulus'])
        filename_parts.append(tanggal)
        filename = '_'.join(filename_parts) + '.pdf'

        return Response(
            pdf_bytes,
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename={filename}'
            },
        )
    except Exception as e:
        flash(f'Gagal generate PDF: {str(e)}', 'error')
        return redirect(url_for('laporan.index'))


# ===========================================================================
# PDF TRANSKRIP SISWA
# ===========================================================================

@laporan_bp.route('/pdf/transkrip/<int:siswa_id>')
@login_required
def pdf_transkrip(siswa_id):
    """Generate & download PDF transkrip nilai personal satu siswa.

    Siswa hanya boleh akses transkrip MILIKNYA sendiri.

    Args:
        siswa_id (int): Primary key siswa.

    Returns:
        Response: File PDF transkrip (1 halaman).

    Raises:
        403: Jika siswa mencoba akses transkrip siswa lain.
        404: Jika siswa_id tidak ada di database.
    """
    # Guard: siswa hanya boleh akses transkrip sendiri.
    if current_user.is_siswa() and current_user.siswa_id != siswa_id:
        abort(403)

    from werkzeug.exceptions import HTTPException

    try:
        pdf_bytes = generate_transkrip_pdf(siswa_id)
        tanggal = now_jakarta().strftime('%Y%m%d')
        siswa = Siswa.query.get_or_404(siswa_id)
        catat_audit_log(
            user_id=current_user.id,
            action='PRINT_PDF',
            table_name='nilai',
            record_id=siswa_id,
            description=f'Cetak PDF transkrip {siswa.nama}',
            ip_address=request.remote_addr,
        )
        return Response(
            pdf_bytes,
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename=transkrip_{siswa.nis}_{tanggal}.pdf'
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        flash(f'Gagal generate PDF: {str(e)}', 'error')
        return redirect(url_for('laporan.index'))


# ===========================================================================
# EXCEL EXPORT
# ===========================================================================

@laporan_bp.route('/excel')
@login_required
def excel():
    """Generate & download file Excel (.xlsx) rekap nilai.

    Query params (semua optional):
    - ``kelas`` (str): Filter kelas. Kosong = semua kelas.
    - ``guru_id`` (int): Filter guru.
    - ``mata_pelajaran`` (str): Filter mapel.
    - ``siswa_id`` (int): Filter siswa.
    - ``status_lulus`` (str): ``lulus`` / ``tidak_lulus``.

    Untuk user ``guru``, otomatis ter-scope ke mapel & guru_id-nya.
    ``kelas`` di endpoint ini boleh kosong (export semua kelas).

    Returns:
        Response: File XLSX sebagai attachment.

    Raises:
        403: Jika user adalah siswa.
    """
    if current_user.is_siswa():
        abort(403)

    filters = _parse_filter_args()
    mapel_scope = _resolve_mata_pelajaran_filter()
    guru_id_scope = _resolve_guru_id_scope()
    kelas = filters.get('kelas')

    # Validasi ID filter.
    err, _ = _validate_filter_ids(filters)
    if err:
        flash(err, 'warning')
        return redirect(url_for('laporan.index'))

    # Guard: jika kelas diisi, cek ada data yang match.
    if kelas:
        # Untuk check existence: hanya apply mapel_scope (guru bisa export
        # data untuk mapel-nya tanpa peduli guru_id input, selama mapel-nya
        # sesuai — backward compat dengan behavior sebelum filter lanjutan).
        check_query = _build_nilai_query(
            filters, mapel_scope=mapel_scope, guru_id_scope=None,
        )
        if not check_query.first():
            flash(f'Tidak ada data nilai untuk kelas {kelas} dengan filter yang dipilih.', 'warning')
            return redirect(url_for('laporan.index'))

    # Resolusi filter info untuk header Excel.
    filter_info = _resolve_filter_info(filters)
    effective_mapel = mapel_scope or filters.get('mata_pelajaran')
    effective_guru_id = guru_id_scope if guru_id_scope is not None else filters.get('guru_id')

    try:
        dicetak_oleh = current_user.username
        if current_user.is_guru() and current_user.guru:
            dicetak_oleh = current_user.guru.nama_guru
        elif current_user.is_siswa() and current_user.siswa:
            dicetak_oleh = current_user.siswa.nama

        excel_bytes = export_excel(
            kelas,
            dicetak_oleh=dicetak_oleh,
            mata_pelajaran=effective_mapel,
            guru_id=effective_guru_id,
            siswa_id=filters.get('siswa_id'),
            status_lulus=filters.get('status_lulus'),
            filter_info=filter_info,
        )
        tanggal = now_jakarta().strftime('%Y%m%d')

        # Audit log dengan info filter.
        filter_desc_parts = [f'kelas={kelas or "semua"}']
        if effective_mapel:
            filter_desc_parts.append(f'mapel={effective_mapel}')
        if effective_guru_id is not None:
            filter_desc_parts.append(f'guru_id={effective_guru_id}')
        if filters.get('siswa_id') is not None:
            filter_desc_parts.append(f'siswa_id={filters["siswa_id"]}')
        if filters.get('status_lulus'):
            filter_desc_parts.append(f'status={filters["status_lulus"]}')
        catat_audit_log(
            user_id=current_user.id,
            action='EXPORT_EXCEL',
            table_name='nilai',
            description=f'Ekspor Excel ({", ".join(filter_desc_parts)})',
            ip_address=request.remote_addr,
        )

        # Bangun filename dari filter aktif.
        safe_kelas = kelas.replace('/', '_') if kelas else 'semua'
        filename_parts = ['nilai', safe_kelas]
        if effective_mapel:
            filename_parts.append(effective_mapel.replace('/', '_'))
        if filters.get('status_lulus'):
            filename_parts.append(filters['status_lulus'])
        filename_parts.append(tanggal)
        filename = '_'.join(filename_parts) + '.xlsx'

        return Response(
            excel_bytes,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={
                'Content-Disposition': f'attachment; filename={filename}'
            },
        )
    except Exception as e:
        flash(f'Gagal ekspor Excel: {str(e)}', 'error')
        return redirect(url_for('laporan.index'))


# ===========================================================================
# AJAX ENDPOINTS (CASCADING DROPDOWNS)
# ===========================================================================

@laporan_bp.route('/api/guru')
@login_required
def api_guru():
    """API: List guru aktif (untuk dropdown filter).

    Returns:
        Response: JSON array ``[{id, id_guru, nama_guru, mata_pelajaran}, ...]``.
    """
    if current_user.is_siswa():
        abort(403)
    guru_list = Guru.daftar_guru_aktif()
    return jsonify([{
        'id': g.id,
        'id_guru': g.id_guru,
        'nama_guru': g.nama_guru,
        'mata_pelajaran': g.mata_pelajaran,
    } for g in guru_list])


@laporan_bp.route('/api/mata-pelajaran')
@login_required
def api_mata_pelajaran():
    """API: List distinct mata pelajaran (untuk dropdown filter).

    Query params (optional):
    - ``guru_id`` (int): Filter by guru (admin only — guru otomatis
        ter-scope ke mapel-nya dan param ini diabaikan).

    Untuk role guru, otomatis ter-scope ke mapel-nya (query param diabaikan).

    Returns:
        Response: JSON array ``["Matematika", "Bahasa Indonesia", ...]``.
    """
    if current_user.is_siswa():
        abort(403)
    guru_id_scope = _resolve_guru_id_scope()
    # Untuk guru: mapel di-scope ke mapel guru (ignore guru_id param).
    # Untuk admin: gunakan guru_id param jika diisi, jika tidak None.
    if guru_id_scope is not None:
        # Guru: filter by mapel (mapel_scope) - tidak peduli guru_id
        mapel_scope = _resolve_mata_pelajaran_filter()
        # Cari mapel yang punya nilai dengan mapel_scope
        # (tidak peduli guru_id, karena satu mapel bisa diampu banyak guru)
        if mapel_scope:
            mapel_list = [mapel_scope]  # guru hanya boleh lihat mapel-nya
        else:
            mapel_list = Nilai.daftar_mata_pelajaran()
    else:
        # Admin: gunakan guru_id param jika ada
        guru_id_param = _safe_int(request.args.get('guru_id'))
        mapel_list = Nilai.daftar_mata_pelajaran(guru_id=guru_id_param)
    return jsonify(mapel_list)


@laporan_bp.route('/api/kelas')
@login_required
def api_kelas():
    """API: List distinct kelas yang punya data nilai (untuk dropdown filter).

    Query params (optional):
    - ``guru_id`` (int): Filter by guru.
    - ``mata_pelajaran`` (str): Filter by mapel.

    Untuk role guru, otomatis ter-scope ke mapel & guru_id-nya.

    Returns:
        Response: JSON array ``["X-IPA-1", "X-IPA-2", ...]``.
    """
    if current_user.is_siswa():
        abort(403)
    mapel_scope = _resolve_mata_pelajaran_filter()
    guru_id_scope = _resolve_guru_id_scope()

    effective_mapel = mapel_scope or (request.args.get('mata_pelajaran') or '').strip() or None
    effective_guru_id = guru_id_scope if guru_id_scope is not None else _safe_int(request.args.get('guru_id'))

    query = (
        db.session.query(Siswa.kelas)
        .join(Nilai, Nilai.siswa_id == Siswa.id)
        .filter(Siswa.deleted_at.is_(None))
    )
    if effective_mapel:
        query = query.filter(Nilai.mata_pelajaran == effective_mapel)
    if effective_guru_id is not None:
        query = query.filter(Nilai.guru_id == effective_guru_id)
    kelas_list = [r[0] for r in query.distinct().order_by(Siswa.kelas).all()]
    return jsonify(kelas_list)


@laporan_bp.route('/api/siswa')
@login_required
def api_siswa():
    """API: List siswa (untuk dropdown filter) — ter-scope by kelas.

    Query params (optional):
    - ``kelas`` (str): Filter by kelas.
    - ``guru_id`` (int): Filter by guru (hanya siswa yang pernah dinilai guru tsb).
    - ``mata_pelajaran`` (str): Filter by mapel.

    Untuk role guru, otomatis ter-scope ke mapel & guru_id-nya.

    Returns:
        Response: JSON array ``[{id, nis, nama, kelas}, ...]``.
    """
    if current_user.is_siswa():
        abort(403)
    mapel_scope = _resolve_mata_pelajaran_filter()
    guru_id_scope = _resolve_guru_id_scope()

    effective_mapel = mapel_scope or (request.args.get('mata_pelajaran') or '').strip() or None
    effective_guru_id = guru_id_scope if guru_id_scope is not None else _safe_int(request.args.get('guru_id'))
    kelas = (request.args.get('kelas') or '').strip() or None

    # Query siswa yang punya nilai (sesuai filter). Tanpa kelas, return
    # semua siswa yang punya nilai di scope.
    query = (
        db.session.query(Siswa)
        .join(Nilai, Nilai.siswa_id == Siswa.id)
        .filter(Siswa.deleted_at.is_(None))
    )
    if kelas:
        query = query.filter(Siswa.kelas == kelas)
    if effective_mapel:
        query = query.filter(Nilai.mata_pelajaran == effective_mapel)
    if effective_guru_id is not None:
        query = query.filter(Nilai.guru_id == effective_guru_id)
    siswa_list = query.distinct().order_by(Siswa.nama).all()
    return jsonify([{
        'id': s.id,
        'nis': s.nis,
        'nama': s.nama,
        'kelas': s.kelas,
    } for s in siswa_list])
