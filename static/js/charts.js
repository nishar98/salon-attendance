/**
 * Admin dashboard — load data and render Chart.js charts.
 */

loadDashboard();

async function loadDashboard() {
    try {
        const res = await fetch('/api/admin/dashboard');
        if (!res.ok) return;
        const data = await res.json();

        // Summary cards
        document.getElementById('present-count').textContent = data.present_today || 0;
        document.getElementById('absent-count').textContent = data.absent_today || 0;
        document.getElementById('active-count').textContent = data.active_now || 0;

        // Weekly chart
        renderWeeklyChart(data.weekly || []);

        // Today's table
        renderTodayTable(data.today_details || []);
    } catch (err) {
        console.error('Dashboard load error:', err);
    }

    // Set up export link
    setupExport();
}

function renderWeeklyChart(weeklyData) {
    const ctx = document.getElementById('weekly-chart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: weeklyData.map(d => d.day),
            datasets: [{
                label: 'Present',
                data: weeklyData.map(d => d.present),
                backgroundColor: '#10b981',
                borderRadius: 4,
            }, {
                label: 'Absent',
                data: weeklyData.map(d => d.absent),
                backgroundColor: '#ef4444',
                borderRadius: 4,
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true, ticks: { stepSize: 1 } }
            },
            plugins: { legend: { position: 'bottom' } }
        }
    });
}

function renderTodayTable(details) {
    const container = document.getElementById('today-table');
    if (!details.length) {
        container.innerHTML = '<p class="text-gray-500 text-center py-4">No data yet today.</p>';
        return;
    }
    let html = `
        <table class="w-full text-sm">
            <thead>
                <tr class="border-b text-left text-gray-500">
                    <th class="py-2">Name</th>
                    <th class="py-2">Status</th>
                    <th class="py-2">Punch In</th>
                    <th class="py-2">Hours</th>
                </tr>
            </thead>
            <tbody>`;

    for (const row of details) {
        const statusClass = row.status === 'Present' ? 'text-green-600' : 'text-red-500';
        html += `
            <tr class="border-b last:border-0">
                <td class="py-2">${row.name}</td>
                <td class="py-2 ${statusClass} font-medium">${row.status}</td>
                <td class="py-2">${row.punch_in || '-'}</td>
                <td class="py-2">${row.hours || '-'}</td>
            </tr>`;
    }

    html += '</tbody></table>';
    container.innerHTML = html;
}

function setupExport() {
    const startInput = document.getElementById('export-start');
    const endInput = document.getElementById('export-end');
    const link = document.getElementById('export-link');

    // Default: last 7 days
    const today = new Date();
    const weekAgo = new Date(today);
    weekAgo.setDate(weekAgo.getDate() - 7);
    startInput.value = weekAgo.toISOString().split('T')[0];
    endInput.value = today.toISOString().split('T')[0];

    function updateLink() {
        link.href = `/api/reports/export?start=${startInput.value}&end=${endInput.value}`;
    }

    startInput.addEventListener('change', updateLink);
    endInput.addEventListener('change', updateLink);
    updateLink();
}
