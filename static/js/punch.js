const punchBtn = document.getElementById('punch-btn');
const punchLabel = document.getElementById('punch-label');
const statusText = document.getElementById('status-text');
const statusIcon = document.getElementById('status-icon');
const elapsedTime = document.getElementById('elapsed-time');
const messageDiv = document.getElementById('message');
const gpsStatus = document.getElementById('gps-status');

let currentStatus = null;
let elapsedInterval = null;

loadStatus();

async function loadStatus() {
    try {
        const res = await fetch('/api/punch/status');
        const data = await res.json();
        currentStatus = data.status;
        updateUI(data);
    } catch (err) { statusText.textContent = 'Unable to load status'; }
}

function updateUI(data) {
    if (data.status === 'on_duty') {
        statusText.textContent = 'On Duty';
        statusText.className = 'text-lg font-semibold text-green-600';
        statusIcon.className = 'w-12 h-12 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-3';
        statusIcon.innerHTML = '<span class="w-3 h-3 bg-green-500 rounded-full animate-pulse"></span>';
        punchLabel.textContent = 'Punch Out';
        punchBtn.className = 'w-44 h-44 rounded-full text-white text-xl font-bold shadow-xl transition-all transform hover:scale-105 active:scale-95 flex items-center justify-center punch-btn-out';
        punchBtn.disabled = false;
        startElapsedTimer(data.since);
    } else {
        statusText.textContent = 'Off Duty';
        statusText.className = 'text-lg font-semibold text-gray-500';
        statusIcon.className = 'w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-3';
        statusIcon.innerHTML = '<svg class="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>';
        punchLabel.textContent = 'Punch In';
        punchBtn.className = 'w-44 h-44 rounded-full text-white text-xl font-bold shadow-xl transition-all transform hover:scale-105 active:scale-95 flex items-center justify-center punch-btn-in';
        punchBtn.disabled = false;
        elapsedTime.textContent = '';
        clearInterval(elapsedInterval);
    }
}

function startElapsedTimer(since) {
    clearInterval(elapsedInterval);
    const sinceDate = new Date(since);
    function update() {
        const diff = Date.now() - sinceDate.getTime();
        const h = Math.floor(diff / 3600000);
        const m = Math.floor((diff % 3600000) / 60000);
        elapsedTime.textContent = `Since ${sinceDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} · ${h}h ${m}m`;
    }
    update();
    elapsedInterval = setInterval(update, 30000);
}

async function doPunch() {
    const action = currentStatus === 'on_duty' ? 'out' : 'in';
    showMessage('', '');
    punchBtn.disabled = true;
    punchLabel.textContent = 'Getting GPS...';
    gpsStatus.textContent = 'Requesting location...';

    try {
        const position = await getGPS();
        const { latitude, longitude, accuracy } = position.coords;
        gpsStatus.textContent = `GPS: ±${Math.round(accuracy)}m`;
        punchLabel.textContent = 'Sending...';

        const res = await fetch(`/api/punch/${action}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ latitude, longitude, accuracy }),
        });
        const data = await res.json();

        if (res.ok) {
            showMessage(data.message, 'success');
            await loadStatus();
        } else {
            showMessage(data.detail || 'Punch failed.', 'error');
            punchBtn.disabled = false;
            punchLabel.textContent = action === 'in' ? 'Punch In' : 'Punch Out';
        }
    } catch (err) {
        const msgs = { 1: 'Location permission denied. Enable it in browser settings.', 2: 'Location unavailable. Move near a window.', 3: 'GPS timed out. Try again.' };
        showMessage(msgs[err.code] || 'Network error. Check your connection.', 'error');
        punchBtn.disabled = false;
        punchLabel.textContent = action === 'in' ? 'Punch In' : 'Punch Out';
        gpsStatus.textContent = '';
    }
}

function getGPS() {
    return new Promise((resolve, reject) => {
        if (!navigator.geolocation) { reject({ code: 2 }); return; }
        navigator.geolocation.getCurrentPosition(resolve, reject, { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 });
    });
}

function showMessage(text, type) {
    if (!text) { messageDiv.classList.add('hidden'); return; }
    messageDiv.classList.remove('hidden');
    const styles = {
        success: 'bg-green-50 border border-green-200 text-green-700',
        error: 'bg-red-50 border border-red-200 text-red-700'
    };
    messageDiv.className = `rounded-xl text-sm px-4 py-3 mb-4 ${styles[type] || ''}`;
    messageDiv.textContent = text;
}
