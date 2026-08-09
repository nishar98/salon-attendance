/**
 * Geofence configuration page — map preview + settings form.
 */

let map, marker, circle;

// Load current settings
loadGeofence();

async function loadGeofence() {
    try {
        const res = await fetch('/api/admin/geofence');
        if (!res.ok) return;
        const data = await res.json();

        document.getElementById('geo-lat').value = data.latitude;
        document.getElementById('geo-lon').value = data.longitude;
        document.getElementById('geo-radius').value = data.radius_m;
        document.getElementById('radius-label').textContent = data.radius_m;

        initMap(data.latitude, data.longitude, data.radius_m);
    } catch (err) {
        console.error('Failed to load geofence:', err);
    }
}

function initMap(lat, lon, radius) {
    map = L.map('map').setView([lat, lon], 18);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 20,
    }).addTo(map);

    marker = L.marker([lat, lon]).addTo(map);
    circle = L.circle([lat, lon], {
        radius: radius,
        color: '#6366f1',
        fillColor: '#6366f1',
        fillOpacity: 0.15,
    }).addTo(map);

    // Allow clicking on map to set position
    map.on('click', (e) => {
        document.getElementById('geo-lat').value = e.latlng.lat.toFixed(7);
        document.getElementById('geo-lon').value = e.latlng.lng.toFixed(7);
        updateMap();
    });
}

function updateMap() {
    const lat = parseFloat(document.getElementById('geo-lat').value);
    const lon = parseFloat(document.getElementById('geo-lon').value);
    const radius = parseInt(document.getElementById('geo-radius').value);

    if (isNaN(lat) || isNaN(lon) || !map) return;

    marker.setLatLng([lat, lon]);
    circle.setLatLng([lat, lon]);
    circle.setRadius(radius);
    map.setView([lat, lon]);
}

// Save form
document.getElementById('geofence-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const msg = document.getElementById('geo-msg');

    const latitude = parseFloat(document.getElementById('geo-lat').value);
    const longitude = parseFloat(document.getElementById('geo-lon').value);
    const radius_m = parseInt(document.getElementById('geo-radius').value);

    try {
        const res = await fetch('/api/admin/geofence', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ latitude, longitude, radius_m }),
        });

        msg.style.display = 'block';
        if (res.ok) {
            msg.className = 'mt-3 text-sm text-green-600 font-medium';
            msg.textContent = '✓ Geofence updated successfully!';
        } else {
            const data = await res.json();
            msg.className = 'mt-3 text-sm text-red-600 font-medium';
            msg.textContent = data.detail || 'Failed to save.';
        }
    } catch (err) {
        msg.style.display = 'block';
        msg.className = 'mt-3 text-sm text-red-600 font-medium';
        msg.textContent = 'Network error. Please try again.';
    }
});
