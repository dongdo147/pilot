// update/Update.js

import { updateMap } from './updateMap.js';
import { updateShipInfo } from './updateShipInfo.js';
import { updateMissionTable } from './updateMissionTable.js';

// Function to handle createMission button
export function createMission(map, waypoints, mapMarkers, polyline, commandMap, translations, updateMissionTable) {
    let creatingMission = false;
    const btn = document.getElementById('createMission');

    btn.addEventListener('click', function () {
        creatingMission = !creatingMission;

        if (creatingMission) {
            // Update button class for active state
            btn.className = "createMission bg-yellow-400 text-black py-2 px-4 rounded-lg shadow-lg hover:bg-yellow-500 transition";
        } else {
            // Revert button class
            btn.className = "createMission bg-purple-600 text-white py-2 px-4 rounded-lg hover:bg-purple-700 transition";
        }

        if (creatingMission) {
            map.on('click', function (e) {
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
                polyline = updateMap(map, waypoints, mapMarkers, polyline);
                updateMissionTable(map, waypoints, mapMarkers, polyline, commandMap, translations, (newVal) => polyline = newVal);
            });
        } else {
            map.off('click'); // Remove map click listener when mission creation is toggled off
        }
    });

    return polyline; // Return updated polyline for the main file
}

// Function to handle setHome button
export function setHome(map, homeMarker, homeIcon) {
    const btn = document.getElementById('setHome');

    btn.addEventListener('click', function () {
        alert('Đặt vị trí Home: Click trên bản đồ để chọn vị trí.');
        map.once('click', function (e) {
            // Remove existing home marker if it exists
            if (homeMarker) {
                map.removeLayer(homeMarker);
            }
            // Add new home marker
            homeMarker = L.marker([e.latlng.lat, e.latlng.lng], { icon: homeIcon }).addTo(map)
                .bindPopup(`Home Position: ${e.latlng.lat.toFixed(5)}, ${e.latlng.lng.toFixed(5)}`).openPopup();
            return homeMarker; // Return updated homeMarker
        });
    });

    return homeMarker; // Return homeMarker for the main file
}

// Re-export existing functions
export {
    updateMap,
    updateShipInfo,
    updateMissionTable
};