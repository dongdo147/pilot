 // Update mission table
    import { updateMap } from "./updateMap.js";
 export function updateMissionTable (map, waypoints, mapMarkers, polyline, commandMap, translations, setPolyline) {
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