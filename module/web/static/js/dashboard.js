// Store latest data
let latestData = {
    attitude: {},
    battery: {},
    gps: {},
    text: []
};

// Format values (show as-is)
const formatNumber = (num, decimals = 2) => num != null ? Number(num).toFixed(decimals) : num;
const toDegrees = (rad) => rad != null ? (rad * 180 / Math.PI).toFixed(2) : null;

function renderAttitude(data) {
    const { roll, pitch, yaw } = data;

    const rollDeg = toDegrees(roll);
    const pitchDeg = toDegrees(pitch);
    const yawDeg = toDegrees(yaw);

    return `
        <div class="card-container">
            <h2 class="card-title">🛩️ Attitude</h2>
            <div class="card-content">
                <div class="flex-row">
                    <span class="label">Roll</span>
                    <div class="value-container">
                        <span class="value">${rollDeg}°</span>
                        <svg width="300" height="40" viewBox="0 0 400 100">
                            <!-- Thanh ngang -->
                            <line x1="-200" y1="50" x2="200" y2="50" stroke="#ccc" stroke-width="10" />
                            <!-- Dấu chấm di chuyển theo roll -->
                            <circle cx="${(rollDeg+180)}" cy="50" r="6" fill="red" />
                        </svg>
                    </div>
                </div>
                <div class="flex-row">
                    <span class="label">Pitch</span>
                    <div class="value-container">
                        <span class="value">${pitchDeg}°</span>
                        <svg width="40" height="200" viewBox="0 0 100 200">
                            <!-- Thanh dọc -->
                            <line x1="50" y1="0" x2="50" y2="200" stroke="#ccc" stroke-width="4"/>
                            <!-- Dấu chấm di chuyển theo giá trị pitch -->
                            <circle cx="50" cy="${100 - (pitchDeg + 90) / 180 * 200}" r="6" fill="red"/>
                        </svg>
                    </div>
                </div>
                <div class="flex-row">
                    <span class="label">Yaw</span>
                    <div class="value-container">
                        <span class="value">${yawDeg}°</span>
                        <svg width="40" height="40" viewBox="0 0 100 100">
                            <!-- Draw Compass (Yaw) -->
                            <circle cx="50" cy="50" r="48" stroke="#ccc" stroke-width="4" fill="white"/>
                            <g transform="rotate(${yawDeg}, 50, 50)">
                                <polygon points="50,10 45,30 55,30" fill="red"/>
                                <polygon points="50,90 45,70 55,70" fill="#999"/>
                            </g>
                            <circle cx="50" cy="50" r="4" fill="#333"/>
                        </svg>
                    </div>
                </div>
            </div>
        </div>`;
}

function renderBattery(data) {
    const { voltage, current, remaining } = data;
    return `
        <div class="card-container">
            <h2 class="card-title">🔋 Battery</h2>
            <div class="card-content">
                <div class="flex-row">
                    <span class="label">Voltage</span>
                    <span class="value">${formatNumber(voltage)} V</span>
                </div>
                <div class="flex-row">
                    <span class="label">Current</span>
                    <span class="value">${formatNumber(current)} A</span>
                </div>
                <div class="flex-row">
                    <span class="label">Remaining</span>
                    <span class="value">${formatNumber(remaining, 0)}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${remaining || 0}%"></div>
                </div>
            </div>
        </div>`;
}

function renderGPS(data) {
    const { lat2, lon2, alt2, satellites, fix_type, timestamp, armed, mode } = data;

    return `
        <div class="card-container">
            <h2 class="card-title">📍 GPS</h2>
            <div class="card-content">
                <div class="flex-row">
                    <span class="label">Latitude</span>
                    <span class="value">${formatNumber(lat2, 6)}</span>
                </div>
                <div class="flex-row">
                    <span class="label">Longitude</span>
                    <span class="value">${formatNumber(lon2, 6)}</span>
                </div>
                <div class="flex-row">
                    <span class="label">Altitude</span>
                    <span class="value">${formatNumber(alt2)} m</span>
                </div>
                <div class="flex-row">
                    <span class="label">Satellites</span>
                    <span class="value">${satellites}</span>
                </div>
                <div class="flex-row">
                    <span class="label">Armed</span>
                    <span class="value">${armed}</span>
                </div>
                <div class="flex-row">
                    <span class="label">Mode</span>
                    <span class="value">${mode}</span>
                </div>
                <div class="flex-row">
                    <span class="label">Fix Type</span>
                    <span class="value">${fix_type}</span>
                </div>
                <div class="flex-row">
                    <span class="label">Timestamp</span>
                    <span class="value">${formatNumber(timestamp, 3)}</span>
                </div>
            </div>
        </div>`;
}

function renderTextMessages(text) {
    return `
        <div class="card-container">
            <h2 class="card-title">📜 Messages</h2>
            <div class="messages-container">
                <p class="message-text">${text || ''}</p>
            </div>
        </div>`;
}

async function fetchData() {
    try {
        const res = await fetch('/data');
        const { pixhawk_data } = await res.json();

        // Update data
        latestData.attitude = {
            roll: pixhawk_data.roll,
            pitch: pixhawk_data.pitch,
            yaw: pixhawk_data.yaw
        };
        latestData.battery = {
            voltage: pixhawk_data.voltage,
            current: pixhawk_data.current,
            remaining: pixhawk_data.remaining
        };
        latestData.gps = {
            lat2: pixhawk_data.lat2,
            lon2: pixhawk_data.lon2,
            alt2: pixhawk_data.alt2,
            satellites: pixhawk_data.satellites,
            fix_type: pixhawk_data.fix_type,
            timestamp: pixhawk_data.timestamp,
            armed: pixhawk_data.armed,
            mode: pixhawk_data.mode,
        };
        latestData.text = [pixhawk_data.text]; // Treat as single message

        // Render everything
        document.getElementById('telemetry').innerHTML = `
            <div class="telemetry-grid">
                ${renderAttitude(latestData.attitude)}
                ${renderBattery(latestData.battery)}
                ${renderGPS(latestData.gps)}
                ${renderTextMessages(latestData.text[0])}
            </div>
        `;
    } catch (error) {
        console.error('Fetch error:', error);
        // Redraw with last data
        document.getElementById('telemetry').innerHTML = `
            <div class="telemetry-grid">
                ${renderAttitude(latestData.attitude)}
                ${renderBattery(latestData.battery)}
                ${renderGPS(latestData.gps)}
                ${renderTextMessages(latestData.text[0])}
            </div>
        `;
    }
}

// Run immediately and every second
fetchData();
setInterval(fetchData, 100);