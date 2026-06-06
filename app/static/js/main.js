$(document).ready(function() {
    var flashData = $('#flash-messages').data('messages');
    if (flashData) {
        flashData.forEach(function(msg) {
            var category = msg[0];
            var message = msg[1];
            var icon = 'info';
            var bgColor = '#0d6efd';

            if (category === 'success') {
                icon = 'success';
                bgColor = '#198754';
            } else if (category === 'error') {
                icon = 'error';
                bgColor = '#dc3545';
            } else if (category === 'warning') {
                icon = 'warning';
                bgColor = '#ffc107';
            }

            Swal.fire({
                toast: true,
                position: 'top-end',
                icon: icon,
                title: message,
                showConfirmButton: false,
                timer: 3000,
                timerProgressBar: true,
                background: bgColor,
                color: '#fff',
            });
        });
    }
});

function confirmLogout(event) {
    event.preventDefault();
    Swal.fire({
        title: 'Yakin ingin logout?',
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: 'Ya, Logout',
        cancelButtonText: 'Batal',
    }).then((result) => {
        if (result.isConfirmed) {
            window.location.href = '/auth/logout';
        }
    });
}

function getCSRFToken() {
    var meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
}

function confirmHapus(url, nama) {
    Swal.fire({
        title: 'Hapus ' + nama + '?',
        text: 'Data akan dihapus secara soft-delete.',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#dc3545',
        confirmButtonText: 'Ya, Hapus',
        cancelButtonText: 'Batal',
    }).then((result) => {
        if (result.isConfirmed) {
            var form = document.createElement('form');
            form.method = 'POST';
            form.action = url;
            var csrfInput = document.createElement('input');
            csrfInput.type = 'hidden';
            csrfInput.name = 'csrf_token';
            csrfInput.value = getCSRFToken();
            form.appendChild(csrfInput);
            document.body.appendChild(form);
            form.submit();
        }
    });
    return false;
}

// SweetAlert: konfirmasi aktivasi / nonaktivasi user.
// Dipakai dari admin/users/index.html. isActive = true => Nonaktifkan
// (user sedang aktif); isActive = false => Aktifkan (user nonaktif).
function confirmToggleAktif(url, username, isActive) {
    var action = isActive ? 'Nonaktifkan' : 'Aktifkan';
    var confirmText = isActive ? 'Ya, Nonaktifkan' : 'Ya, Aktifkan';
    var color = isActive ? '#dc3545' : '#198754';
    Swal.fire({
        title: action + ' user ' + username + '?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: color,
        confirmButtonText: confirmText,
        cancelButtonText: 'Batal',
    }).then((result) => {
        if (result.isConfirmed) {
            var form = document.createElement('form');
            form.method = 'POST';
            form.action = url;
            var csrfInput = document.createElement('input');
            csrfInput.type = 'hidden';
            csrfInput.name = 'csrf_token';
            csrfInput.value = getCSRFToken();
            form.appendChild(csrfInput);
            document.body.appendChild(form);
            form.submit();
        }
    });
    return false;
}

// SweetAlert: konfirmasi kunci nilai. Dipakai dari guru/nilai/rekap.html.
// Menerima elemen form, lalu submit form tsb jika user konfirmasi.
function confirmKunciNilai(form) {
    Swal.fire({
        title: 'Kunci nilai ini?',
        text: 'Nilai tidak dapat diubah setelah dikunci.',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#198754',
        confirmButtonText: 'Ya, Kunci',
        cancelButtonText: 'Batal',
    }).then((result) => {
        if (result.isConfirmed) {
            form.submit();
        }
    });
    return false;
}

document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.forEach(function(el) {
        new bootstrap.Tooltip(el);
    });

    if (typeof $.fn.DataTable !== 'undefined') {
        $.fn.DataTable.ext.pager.numbers_length = 5;
    }
});
