import { updateMissionTable } from "../update/updateMissionTable.js";

export function setupMissionCreation(map, waypoints, mapMarkers, polyline, commandMap, translations, setPolyline) {
    let creatingMission = false;
    const createBtn = document.getElementById('createMission');

    createBtn.addEventListener('click', function () {
        creatingMission = !creatingMission;

        // Toggle button style
        createBtn.className = creatingMission
            ? "createMission bg-yellow-400 text-black py-2 px-4 rounded-lg shadow-lg hover:bg-yellow-500 transition"
            : "createMission bg-purple-600 text-white py-2 px-4 rounded-lg hover:bg-purple-700 transition";

        if (creatingMission) {
            // Attach map click handler
            map.on('click', handleMapClick);
        } else {
            // Remove map click handler
            map.off('click', handleMapClick);
        }
    });

    function handleMapClick(e) {
        const wp = {
            seq: waypoints.length + 1,
            frame: 3,
            command: 16,
            current: 0,
            autocontinue: 1,
            param1: 0,
            param2: 0,
            param3: 0,
            param4: 0,
            x: e.latlng.lat,
            y: e.latlng.lng,
            z: 10
        };

        waypoints.push(wp);

        const marker = L.marker([wp.x, wp.y]).addTo(map)
            .bindPopup(`Waypoint ${wp.seq}: ${wp.x.toFixed(5)}, ${wp.y.toFixed(5)}, ${wp.z}m`).openPopup();
        mapMarkers.push(marker);

        if (waypoints.length > 1) {
            if (polyline) map.removeLayer(polyline);
            polyline = L.polyline(waypoints.map(w => [w.x, w.y]), { color: '#1e40af' }).addTo(map);
        }
    
        updateMissionTable(map, waypoints, mapMarkers, polyline, commandMap, translations, setPolyline);
        setPolyline(polyline); // Update polyline reference in parent
    }
}
