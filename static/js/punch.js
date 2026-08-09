/**
 * Punch In/Out logic — gets GPS, sends to server, updates UI.
 */

const punchBtn = document.getElementById('punch-btn');
const statusText = document.getElementById('status-text');
const elapsedTime = document.getElementById('elapsed-time');
const messageDiv = document.getElementById('message');
const gpsStatus = document.getElementById('gps-status');

let currentStatus = null; // 'on_duty' or 'off_duty'
let elapsedInterval = null;

// Load initial status
loadStatus();

async function loadStatus() {
    try {
        const res = await fetch('/api/punch/status');
        const data = await res.json();
        currentStatus = data.status;
        updateUI(data);
    } catch (err) {
        statusText.textContent = 'Unable to load status';
    }
}

function updateUI(data) {
    if (data.status === 'on_duty') {
        statusText.textContent = 'On Duty';
        statusText.className = 'text-green-600 text-lg font-medium';
        punchBtn.textContent = 'Punch Out';
        punchBtn.className = 'w-48 h-48 rounded-full text-white text-xl font-bold shadow-lg transition-all transform hover:scale-105 active:scale-95 punch-btn-out';
        punchBtn.disabled = false;
        startElapsedTimer(data.since);
    } else {
        statusText.textContent = 'Off Duty';
        statusText.className = 'text-gray-500 text-lg';
        punchBtn.textContent = 'Punch In';
        punchBtn.className = 'w-48 h-48 rounded-full text-white text-xl font-bold shadow-lg transition-all transform hover:scale-105 active:scale-95 punch-btn-in';
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
        const hours = Math.floor(diff / 3600000);
        const mins = Math.floor((diff % 3600000) / 60000);
        elapsedTime.textContent = `Since ${sinceDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} (${hours}h ${mins}m)`;
    }

    update();
    elapsedInterval = setInterval(update, 60000); // update every minute
}

async function doPunch() {
    const action = currentStatus === 'on_duty' ? 'out' : 'in';
    showMessage('', ''); // clear previous

    punchBtn.disabled = true;
    punchBtn.textContent = 'Getting GPS...';
    gpsStatus.textContent = 'Requesting location...';

    try {
        const position = await getGPS();
        const { latitude, longitude, accuracy } = position.coords;
        gpsStatus.textContent = `GPS: ±${Math.round(accuracy)}m accuracy`;

        punchBtn.textContent = 'Sending...';

        const res = await fetch(`/api/punch/${action}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ latitude, longitude, accuracy }),
        });

        const data = await res.json();

        if (res.ok) {
            showMessage(data.message, 'success');
            await loadStatus(); // refresh UI
        } else {
            showMessage(data.detail || 'Punch failed.', 'error');
            punchBtn.disabled = false;
            punchBtn.textContent = action === 'in' ? 'Punch In' : 'Punch Out';
        }
    } catch (err) {
        if (err.code === 1) {
            showMessage('Location permission denied. Please enable location in your browser settings.', 'error');
        } else if (err.code === 2) {
            showMessage('Location unavailable. Move near a window or outside.', 'error');
        } else if (err.code === 3) {
            showMessage('GPS timed out. Please try again.', 'error');
        } else {
            showMessage('Network error. Check your connection.', 'error');
        }
        punchBtn.disabled = false;
        punchBtn.textContent = action === 'in' ? 'Punch In' : 'Punch Out';
        gpsStatus.textContent = '';
    }
}

function getGPS() {
    return new Promise((resolve, reject) => {
        if (!navigator.geolocation) {
            reject({ code: 2, message: 'Geolocation not supported' });
            return;
        }
        navigator.geolocation.getCurrentPosition(resolve, reject, {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0,
        });
    });
}

function showMessage(text, type) {
    if (!text) {
        messageDiv.classList.add('hidden');
        return;
    }
    messageDiv.classList.remove('hidden');
    if (type === 'success') {
        messageDiv.className = 'mt-6 px-4 py-3 rounded-lg text-sm max-w-sm mx-auto bg-green-50 border border-green-200 text-green-700';
    } else {
        messageDiv.className = 'mt-6 px-4 py-3 rounded-lg text-sm max-w-sm mx-auto bg-red-50 border border-red-200 text-red-700';
    }
    messageDiv.textContent = text;
}
