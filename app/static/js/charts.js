function hitungNilaiAkhir(tugas, uts, uas) {
    return (0.30 * tugas) + (0.30 * uts) + (0.40 * uas);
}

function renderBarChart(canvasId, labels, data) {
    var ctx = document.getElementById(canvasId);
    if (!ctx) return;
    new Chart(ctx.getContext('2d'), {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Rata-rata Nilai',
                data: data,
                backgroundColor: 'rgba(13, 110, 253, 0.6)',
                borderColor: 'rgba(13, 110, 253, 1)',
                borderWidth: 1,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            devicePixelRatio: window.devicePixelRatio || 1,
            scales: {
                y: { beginAtZero: true, max: 100 },
            },
        },
    });
}

function renderDoughnutChart(canvasId, lulus, tidakLulus) {
    var ctx = document.getElementById(canvasId);
    if (!ctx) return;
    new Chart(ctx.getContext('2d'), {
        type: 'doughnut',
        data: {
            labels: ['Lulus', 'Tidak Lulus'],
            datasets: [{
                data: [lulus, tidakLulus],
                backgroundColor: ['rgba(25, 135, 84, 0.8)', 'rgba(220, 53, 69, 0.8)'],
                borderColor: ['#198754', '#dc3545'],
                borderWidth: 1,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            devicePixelRatio: window.devicePixelRatio || 1,
            plugins: {
                legend: { position: 'bottom' },
            },
        },
    });
}

function renderRadarChart(canvasId, labels, data) {
    var ctx = document.getElementById(canvasId);
    if (!ctx) return;
    new Chart(ctx.getContext('2d'), {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Nilai',
                data: data,
                backgroundColor: 'rgba(13, 110, 253, 0.2)',
                borderColor: 'rgba(13, 110, 253, 1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(13, 110, 253, 1)',
            }],
        },
        options: {
            responsive: true,
            scales: {
                r: { beginAtZero: true, max: 100 },
            },
        },
    });
}
