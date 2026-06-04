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
            document.body.appendChild(form);
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
