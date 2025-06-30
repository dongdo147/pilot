import { updateMap, updateMissionTable, updateShipInfo} from './update/Update.js';

document.addEventListener("DOMContentLoaded", async () => {

    const center = [10.7388542,106.7319975]; // Default center (e.g., Ho Chi Minh City)
    let compassAngle = 45; // Compass angle (degrees)
    let waypoints = []; // List of waypoints for the mission
    let mapMarkers = []; // Store markers for waypoints
    let polyline = null; // Store polyline for waypoints
    let homeMarker = null; // Store home marker
    let translations = {}; 
    // Command mapping for MAVLink commands
    const commandMap = {
        16: "Waypoint", // MAV_CMD_NAV_WAYPOINT
        17: "Loiter", // MAV_CMD_NAV_LOITER_UNLIM
        18: "Loiter Turns", // MAV_CMD_NAV_LOITER_TURNS
        19: "Loiter Time", // MAV_CMD_NAV_LOITER_TIME
        20: "Return to Launch", // MAV_CMD_NAV_RETURN_TO_LAUNCH
        21: "Land", // MAV_CMD_NAV_LAND
        22: "Takeoff" // MAV_CMD_NAV_TAKEOFF
    };

const southWest = L.latLng(9.5, 106.5);
const northEast = L.latLng(11, 108);
const bounds = L.latLngBounds(southWest, northEast);
async function loadTranslations(lang, section) {
    const res = await fetch(`/api/translations?lang=${lang}&section=${section}`);
    return await res.json();
}
const lang = localStorage.getItem('lang') || 'en';
    translations = await loadTranslations(lang, 'home'); // hoặc 'home', hoặc toàn bộ nếu bạn muốn


    // Initialize map
    const map = L.map('map', {
        zoomControl: false,
         minZoom: 3

    }).setView(center, 15);
 L.tileLayer('https://tiles.stadiamaps.com/tiles/alidade_satellite/{z}/{x}/{y}{r}.{ext}', {
	attribution: '&copy; CNES, Distribution Airbus DS, © Airbus DS, © PlanetObserver (Contains Copernicus Data) | &copy; <a href="https://www.stadiamaps.com/" target="_blank">Stadia Maps</a> &copy; <a href="https://openmaptiles.org/" target="_blank">OpenMapTiles</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
	ext: 'jpg'
}).addTo(map);

   // L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      //  attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors | Yacht Control System'
 //   }).addTo(map);

    L.tileLayer('https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png', {
        attribution: '© <a href="https://www.openseamap.org">OpenSeaMap</a> contributors'
    }).addTo(map);
    
    // Boat icon
    const boatIcon = L.divIcon({
        className: "boat-icon",
        html: `
            <svg width="40" height="40" viewBox="0 0 64 64" style="transform: rotate(${compassAngle}deg); transform-origin: center;">
                <path d="M32 2 L12 60 L32 48 L52 60 Z" fill="#1e40af" stroke="#1e3a8a" stroke-width="2"/>
                <circle cx="32" cy="30" r="6" fill="#60a5fa" stroke="#1e3a8a" stroke-width="1"/>
            </svg>
        `,
        iconSize: [40, 40],
        iconAnchor: [20, 30],
    });

    // Home icon (SVG house)
    const homeIcon = L.divIcon({
        className: "home-icon",
        html: `
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M3 12L5 10M5 10L12 3L19 10M5 10V20C5 20.5523 5.44772 21 6 21H9M19 10L21 12M19 10V20C19 20.5523 18.5523 21 18 21H15M9 21C9.55228 21 10 20.5523 10 20V16C10 15.4477 10.4477 15 11 15H13C13.5523 15 14 15.4477 14 16V20C14 20.5523 14.4477 21 15 21M9 21H15" stroke="#1e3a8a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        `,
        iconSize: [40, 40],
        iconAnchor: [20, 20],
    });
    // Add boat marker
    const marker = L.marker(center, { icon: boatIcon }).addTo(map);
    // Update ship info
    updateShipInfo(center,compassAngle)
    // Update mission table
   

    // Update map with waypoints and home marker
    const updateMap = () => {
        // Remove existing waypoint markers and polyline
        mapMarkers.forEach(marker => map.removeLayer(marker));
        if (polyline) map.removeLayer(polyline);
        mapMarkers=[]

        // Add waypoint markers
        waypoints.forEach(wp => {
            const marker = L.marker([wp.x, wp.y]).addTo(map)
                .bindPopup(`Waypoint ${wp.seq}: ${wp.x.toFixed(5)}, ${wp.y.toFixed(5)}, ${wp.z}m`);
            mapMarkers.push(marker);
        });

        // Draw polyline if there are multiple waypoints
        if (waypoints.length > 1) {
            polyline=L.polyline(waypoints.map(w => [w.x, w.y]), { color: '#1e40af' }).addTo(map);

        }
    };

    // Update mission table
    const updateMissionTable = () => {
        const tbody = document.getElementById('missionTableBody');
        tbody.innerHTML = ''; // Clear current table

        waypoints.forEach((wp, index) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="py-2 px-3 border-b"><input type="number" value="${wp.seq}" class="w-16 border rounded px-1" data-index="${index}" data-field="seq"></td>
                <td class="py-2 px-3 border-b"><input type="number" value="${wp.frame}" class="w-16 border rounded px-1" data-index="${index}" data-field="frame"></td>
                <td class="py-2 px-3 border-b">
                    <select class="w-32 border rounded px-1" data-index="${index}" data-field="command">
                        ${Object.entries(commandMap).map(([id, name]) => 
                            `<option value="${id}" ${wp.command == id ? 'selected' : ''}>${name}</option>`
                        ).join('')}
                    </select>
                </td>
                <td class="py-2 px-3 border-b"><input type="number" value="${wp.current}" class="w-16 border rounded px-1" data-index="${index}" data-field="current"></td>
                <td class="py-2 px-3 border-b"><input type="number" value="${wp.autocontinue}" class="w-16 border rounded px-1" data-index="${index}" data-field="autocontinue"></td>
                <td class="py-2 px-3 border-b"><input type="number" value="${wp.param1.toFixed(2)}" step="0.01" class="w-16 border rounded px-1" data-index="${index}" data-field="param1"></td>
                <td class="py-2 px-3 border-b"><input type="number" value="${wp.param2.toFixed(2)}" step="0.01" class="w-16 border rounded px-1" data-index="${index}" data-field="param2"></td>
                <td class="py-2 px-3 border-b"><input type="number" value="${wp.param3.toFixed(2)}" step="0.01" class="w-16 border rounded px-1" data-index="${index}" data-field="param3"></td>
                <td class="py-2 px-3 border-b"><input type="number" value="${wp.param4.toFixed(2)}" step="0.01" class="w-16 border rounded px-1" data-index="${index}" data-field="param4"></td>
                <td class="py-2 px-3 border-b"><input type="number" value="${wp.x.toFixed(5)}" step="0.00001" class="w-24 border rounded px-1" data-index="${index}" data-field="x"></td>
                <td class="py-2 px-3 border-b"><input type="number" value="${wp.y.toFixed(5)}" step="0.00001" class="w-24 border rounded px-1" data-index="${index}" data-field="y"></td>
                <td class="py-2 px-3 border-b"><input type="number" value="${wp.z.toFixed(2)}" step="0.01" class="w-16 border rounded px-1" data-index="${index}" data-field="z"></td>
                <td class="py-2 px-3 border-b"><button class="deleteRow bg-red-600 text-white py-1 px-2 rounded hover:bg-red-700" data-index="${index}"> ${translations.delete || 'Delete'}</button></td>
            `;
            tbody.appendChild(row);
        });

        // Add event listeners for input changes
        document.querySelectorAll('#missionTableBody input').forEach(input => {
            input.addEventListener('change', function () {
                const index = parseInt(this.dataset.index);
                const field = this.dataset.field;
                const value = parseFloat(this.value) || parseInt(this.value) || 0;
                waypoints[index][field] = value;
                
                // Update sequence numbers
                if (field === 'seq') {
                    waypoints.sort((a, b) => a.seq - b.seq);
                    waypoints.forEach((wp, i) => wp.seq = i + 1);
                }
                updateMissionTable(); // Refresh table
                updateMap(); // Update map markers and polyline
            });
        });

        // Add event listeners for delete buttons
        document.querySelectorAll('.deleteRow').forEach(button => {
            button.addEventListener('click', function () {
                console.log("Đã kích hoạt")
                const index = parseInt(this.dataset.index);
                waypoints.splice(index, 1); // Remove waypoint
                waypoints.forEach((wp, i) => wp.seq = i + 1); // Reassign sequence numbers
                updateMissionTable(); // Refresh table
                updateMap(); // Update map
            });
        });
    };
  // Handle createMission button
    document.getElementById('createMission').addEventListener('click', function() {
        alert('Tạo Mission: Click trên bản đồ để thêm waypoint.');
        map.on('click', function(e) {
            const wp = {
                seq: waypoints.length + 1,
                frame: 3, // MAV_FRAME_GLOBAL_RELATIVE_ALT
                command: 16, // MAV_CMD_NAV_WAYPOINT
                current: 0,
                autocontinue: 1,
                param1: 0,
                param2: 0,
                param3: 0,
                param4: 0,
                x: e.latlng.lat,
                y: e.latlng.lng,
                z: 10 // Default altitude
            };
            waypoints.push(wp);
            const marker = L.marker([wp.x, wp.y]).addTo(map)
                .bindPopup(`Waypoint ${wp.seq}: ${wp.x.toFixed(5)}, ${wp.y.toFixed(5)}, ${wp.z}m`).openPopup();
            mapMarkers.push(marker);
            if (waypoints.length > 1) {
                if (polyline) map.removeLayer(polyline);
                polyline = L.polyline(waypoints.map(w => [w.x, w.y]), { color: '#1e40af' }).addTo(map);
            }
            updateMissionTable();
        });
    });

    // Handle setHome button
    document.getElementById('setHome').addEventListener('click', function() {
        alert('Đặt vị trí Home: Click trên bản đồ để chọn vị trí.');
        map.once('click', function(e) {
            // Remove existing home marker if it exists
            if (homeMarker) {
                map.removeLayer(homeMarker);
            }
            // Add new home marker
            homeMarker = L.marker([e.latlng.lat, e.latlng.lng], { icon: homeIcon }).addTo(map)
                .bindPopup(`Home Position: ${e.latlng.lat.toFixed(5)}, ${e.latlng.lng.toFixed(5)}`).openPopup();
        });
    });

    // Create control panel for map buttons
    const ControlPanel = L.Control.extend({
        onAdd: function(map) {
            const container = L.DomUtil.create('div', 'bg-white p-2 rounded-lg shadow-md border border-gray-300');
            container.innerHTML = `
                <div class="flex flex-col space-y-2">
                    <button id="mapCreateMission" class="bg-purple-600 text-white py-1 px-2 rounded hover:bg-purple-700 text-sm">Tạo Mission</button>
                    <button id="mapFetchMission" class="bg-yellow-600 text-white py-1 px-2 rounded hover:bg-yellow-700 text-sm">Lấy Mission</button>
                    <button id="mapSaveMission" class="bg-red-600 text-white py-1 px-2 rounded hover:bg-red-700 text-sm">Lưu Mission</button>
                    <button id="mapSetHome" class="bg-green-600 text-white py-1 px-2 rounded hover:bg-green-700 text-sm">Đặt vị trí Home</button>
                </div>
            `;
            L.DomEvent.disableClickPropagation(container);
            return container;
        }
    });
    map.addControl(new ControlPanel({ position: 'topright' }));

    // Sample mission data for Raspberry Pi
    const sampleMissions = [
        { name: "Mission 1", created: "2025-06-01 10:00:00" },
        { name: "Mission 2", created: "2025-06-01 12:30:00" },
        { name: "Mission 3", created: "2025-06-02 09:15:00" }
    ];

    // Show mission list in popup
    const showMissionList = () => {
        const missionListBody = document.getElementById('missionListBody');
        missionListBody.innerHTML = ''; // Clear current table

        sampleMissions.forEach((mission, index) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="py-2 px-3 border-b">${mission.name}</td>
                <td class="py-2 px-3 border-b">${mission.created}</td>
                <td class="py-2 px-3 border-b">
                    <button class="selectMission bg-blue-600 text-white py-1 px-2 rounded hover:bg-blue-700" data-index="${index}">Chọn</button>
                </td>
            `;
            missionListBody.appendChild(row);
        });

        // Add event listeners for select buttons
        document.querySelectorAll('.selectMission').forEach(button => {
            button.addEventListener('click', async function () {
                const index = parseInt(this.dataset.index);
                try {
                    // Simulate fetching mission data for the selected mission
                    const response = await fetch('/api/fetch-mission', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ missionName: sampleMissions[index].name })
                    });
                    const missionData = await response.json();
                    waypoints = missionData.waypoints || [];
                    waypoints.forEach((wp, i) => wp.seq = i + 1); // Ensure sequence numbers
                    polyline = updateMap(map, waypoints, mapMarkers, polyline);

                    updateMissionTable();
                    document.getElementById('fetchMissionPopup').classList.add('hidden');
                    alert(`Mission ${sampleMissions[index].name} đã được chọn.`);
                } catch (error) {
                    alert('Lỗi khi lấy mission: ' + error.message);
                }
            });
        });

        document.getElementById('missionList').classList.remove('hidden');
    };

    // Handle fetchMission button
    document.getElementById('fetchMission').addEventListener('click', function() {
        // Show popup
        document.getElementById('fetchMissionPopup').classList.remove('hidden');

        // Handle Pixhawk fetch
        document.getElementById('fetchFromPixhawk').addEventListener('click', async function() {
            try {
                const response = await fetch('/api/fetch-mission?source=pixhawk');
                const missionData = await response.json();
                waypoints = missionData.waypoints || [];
                waypoints.forEach((wp, i) => wp.seq = i + 1); // Ensure sequence numbers
                polyline = updateMap(map, waypoints, mapMarkers, polyline);

                updateMissionTable();
                document.getElementById('fetchMissionPopup').classList.add('hidden');
                alert('Đã lấy mission từ Pixhawk thành công.');
            } catch (error) {
                alert('Lỗi khi lấy mission từ Pixhawk: ' + error.message);
            }
        });

        // Handle Raspberry Pi fetch
        document.getElementById('fetchFromRaspberryPi').addEventListener('click', function() {
            showMissionList();
        });

        // Handle close fetch popup
        document.getElementById('closePopup').addEventListener('click', function() {
            document.getElementById('fetchMissionPopup').classList.add('hidden');
            document.getElementById('missionList').classList.add('hidden');
        });
    });

    // Handle saveMission button
    document.getElementById('saveMission').addEventListener('click', function() {
        // Check if waypoints exist
        if (waypoints.length === 0) {
            alert('Không có mission để lưu. Vui lòng tạo mission trước.');
            return;
        }

        // Show save popup
        document.getElementById('saveMissionPopup').classList.remove('hidden');
        // Handle Pixhawk save
        document.getElementById('saveToPixhawk').addEventListener('click', async function() {
            try {
                // const response = await fetch('/api/save-mission?source=pixhawk', {
                //     method: 'POST',
                //     headers: { 'Content-Type': 'application/json' },
                //     body: JSON.stringify({ waypoints })
                // });
                // const result = await response.json();
                document.getElementById('saveMissionPopup').classList.add('hidden');
                alert('Đã lưu mission vào Pixhawk thành công.');
            } catch (error) {
                alert('Lỗi khi lưu mission vào Pixhawk: ' + error.message);
            }
        });

        // Handle Raspberry Pi save
        document.getElementById('saveToRaspberryPi').addEventListener('click', function() {
            document.getElementById('missionNameInput').classList.remove('hidden');
        });

        // Handle confirm save to Raspberry Pi
        document.getElementById('confirmSaveToRaspberryPi').addEventListener('click', async function() {
            const missionName = document.getElementById('missionName').value.trim();
            if (!missionName) {
                alert('Vui lòng nhập tên mission.');
                return;
            }
            try {
                // const response = await fetch('/api/save-mission', {
                //     method: 'POST',
                //     headers: { 'Content-Type': 'application/json' },
                //     body: JSON.stringify({ missionName, waypoints })
                // });
                // const result = await response.json();
                const saveTime = new Date().toLocaleString('vi-VN', { timeZone: 'Asia/Ho_Chi_Minh' });
                document.getElementById('saveMissionPopup').classList.add('hidden');
                document.getElementById('missionNameInput').classList.add('hidden');
                document.getElementById('missionName').value = ''; // Clear input
                alert(`Mission "${missionName}" đã được lưu vào Raspberry Pi lúc ${saveTime}.`);
            } catch (error) {
                alert('Lỗi khi lưu mission vào Raspberry Pi: ' + error.message);
            }
        });

        // Handle close save popup
        document.getElementById('closeSavePopup').addEventListener('click', function() {
            document.getElementById('saveMissionPopup').classList.add('hidden');
            document.getElementById('missionNameInput').classList.add('hidden');
            document.getElementById('missionName').value = ''; // Clear input
        });
    });

  
    // Handle map button events
    L.DomEvent.on(document.getElementById('mapCreateMission'), 'click', function() {
        document.getElementById('createMission').click();
    });
    L.DomEvent.on(document.getElementById('mapFetchMission'), 'click', function() {
        document.getElementById('fetchMission').click();
    });
    L.DomEvent.on(document.getElementById('mapSaveMission'), 'click', function() {
        document.getElementById('saveMission').click();
    });
    L.DomEvent.on(document.getElementById('mapSetHome'), 'click', function() {
        document.getElementById('setHome').click();
    });
    document.getElementById('mapCreateMission').textContent = translations.createMission || 'Tạo Mission';
document.getElementById('mapFetchMission').textContent = translations.fetchMission || 'Lấy Mission';
document.getElementById('mapSaveMission').textContent = translations.saveMission || 'Lưu Mission';
document.getElementById('mapSetHome').textContent = translations.setHome || 'Đặt vị trí Home';

});
