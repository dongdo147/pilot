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
        <div class="bg-white rounded-xl shadow p-6 border border-gray-200">
            <h2 class="text-lg font-semibold text-gray-700 mb-4">🛩️ Attitude</h2>
                                    <div class="space-y-3">
                                        <div class="flex justify-between items-center">
                            <span class="font-medium text-gray-600">Roll</span>
                            <div class="flex items-center space-x-2">
                                <span class="text-gray-800 mr-16 ml-8">${rollDeg}°</span>
                                <svg width="300" height="40" viewBox="0 0 400 100">
                                    <!-- Thanh ngang -->
                                    <line x1="-200" y1="50" x2="200" y2="50" stroke="#ccc" stroke-width="10" />
                                    
                                    <!-- Dấu chấm di chuyển theo roll -->
                                    <circle cx="${(rollDeg+180) }" cy="50" r="6" fill="red" />
                                </svg>
                            </div>
                        </div>

                            <div class="flex justify-between items-center">
                <span class="font-medium text-gray-600">Pitch</span>
                <div class="flex items-center space-x-2">
                    <span class="text-gray-800 ">${pitchDeg}°</span>
                    <svg width="40" height="200" viewBox="0 0 100 200">
                        <!-- Thanh dọc -->
                        <line x1="50" y1="0" x2="50" y2="200" stroke="#ccc" stroke-width="4"/>
                        
                        <!-- Dấu chấm di chuyển theo giá trị pitch -->
                        <circle cx="50" cy="${100 - (pitchDeg + 90) / 180 * 200}" r="6" fill="red"/>
                    </svg>
                </div>
            </div>

               <div class="flex justify-between items-center">
                    <span class="font-medium text-gray-600">Yaw</span>
                    <div class="flex items-center space-x-2">
                        <span class="text-gray-800">${yawDeg}°</span>
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
        <div class="bg-white rounded-xl shadow p-6 border border-gray-200">
            <h2 class="text-lg font-semibold text-gray-700 mb-4">🔋 Battery</h2>
            <div class="space-y-2">
                <div class="flex justify-between">
                    <span class="font-medium text-gray-600">Voltage</span>
                    <span class="text-gray-800">${formatNumber(voltage)} V</span>
                </div>
                <div class="flex justify-between">
                    <span class="font-medium text-gray-600">Current</span>
                    <span class="text-gray-800">${formatNumber(current)} A</span>
                </div>
                <div class="flex justify-between">
                    <span class="font-medium text-gray-600">Remaining</span>
                    <span class="text-gray-800">${formatNumber(remaining, 0)}%</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2.5 mt-1">
                    <div class="bg-blue-500 h-2.5 rounded-full" style="width: ${remaining || 0}%"></div>
                </div>
            </div>
        </div>`;
}

function renderGPS(data) {
    const { lat2, lon2, alt2, satellites, fix_type, timestamp } = data;
    return `
        <div class="bg-white rounded-xl shadow p-6 border border-gray-200">
            <h2 class="text-lg font-semibold text-gray-700 mb-4">📍 GPS</h2>
            <div class="space-y-2">
                <div class="flex justify-between">
                    <span class="font-medium text-gray-600">Latitude</span>
                    <span class="text-gray-800">${formatNumber(lat2, 6)}</span>
                </div>
                <div class="flex justify-between">
                    <span class="font-medium text-gray-600">Longitude</span>
                    <span class="text-gray-800">${formatNumber(lon2, 6)}</span>
                </div>
                <div class="flex justify-between">
                    <span class="font-medium text-gray-600">Altitude</span>
                    <span class="text-gray-800">${formatNumber(alt2)} m</span>
                </div>
                <div class="flex justify-between">
                    <span class="font-medium text-gray-600">Satellites</span>
                    <span class="text-gray-800">${satellites}</span>
                </div>
                <div class="flex justify-between">
                    <span class="font-medium text-gray-600">Fix Type</span>
                    <span class="text-gray-800">${fix_type}</span>
                </div>
                <div class="flex justify-between">
                    <span class="font-medium text-gray-600">Timestamp</span>
                    <span class="text-gray-800">${formatNumber(timestamp, 3)}</span>
                </div>
            </div>
        </div>`
    ;
}

function renderTextMessages(text) {
    return `
       <div class="bg-white rounded-xl shadow p-6 border border-gray-200">
            <h2 class="text-lg font-semibold text-gray-700 mb-4">📜 Messages</h2>
            <div class="max-h-40 overflow-y-auto space-y-2">
                <p class="text-gray-800">${text || ''}</p>
            </div>
        </div>`
    ;
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
            timestamp: pixhawk_data.timestamp
        };
        latestData.text = [pixhawk_data.text]; // Treat as single message

        // Render everything
        document.getElementById('telemetry').innerHTML = `
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
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
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
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
setInterval(fetchData, 1000);