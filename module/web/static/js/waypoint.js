async function fetchWaypointList() {
    const res = await fetch("/waypoint-manager");
    const data = await res.json();

    const waypointListDiv = document.getElementById("waypoint-list");
    waypointListDiv.innerHTML = '';

    data.waypoints.forEach(wp => {
        const fileDiv = document.createElement("div");
        fileDiv.classList.add("p-4", "bg-gray-100", "rounded-lg", "shadow");
        fileDiv.innerHTML = `
          <h3 class="text-xl font-semibold">${wp.filename}</h3>
          <p class="text-sm text-gray-500">🕒 ${new Date(wp.created_at).toLocaleString()}</p>
          <button onclick="viewWaypoint('${wp.filename}')" class="mt-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
            Xem
          </button>
          <button onclick="downloadWaypoint('${wp.filename}')" class="mt-2 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700">
            Tải về
          </button>
          <button onclick="deleteWaypoint('${wp.filename}')" class="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700">
            Xóa
          </button>
        `;
        waypointListDiv.appendChild(fileDiv);
    });
    
}

function closeModal() {
    document.getElementById("waypoint-modal").classList.add("hidden");
}

async function viewWaypoint(filename) {
    const res = await fetch(`/waypoint-manager/${filename}`);
    const data = await res.json();

    const container = document.getElementById("waypoint-modal-content");
    container.innerHTML = '';

    // Hiển thị metadata
    const info = data.data;
    const metaHTML = `
        <p><strong>🕒 Thời gian:</strong> ${new Date(info.created_at).toLocaleString()}</p>
        <p><strong>🧭 Số waypoint:</strong> ${info.count}</p>
    `;
    container.innerHTML += metaHTML;

    // Hiển thị bảng tọa độ
    if (info.waypoints && Array.isArray(info.waypoints)) {
        let table = `<table class="table-auto w-full border mt-4">
            <thead class="bg-gray-200">
                <tr>
                    <th class="border px-4 py-2">#</th>
                    <th class="border px-4 py-2">Latitude</th>
                    <th class="border px-4 py-2">Longitude</th>
                </tr>
            </thead><tbody>`;
    
        info.waypoints.forEach((point, idx) => {
            const [lat, lng] = point;
            table += `<tr>
                <td class="border px-4 py-2 text-center">${idx + 1}</td>
                <td class="border px-4 py-2">${lat?.toFixed(6) ?? "?"}</td>
                <td class="border px-4 py-2">${lng?.toFixed(6) ?? "?"}</td>
            </tr>`;
        });
    
        table += `</tbody></table>`;
        container.innerHTML += table;
    } else {
        container.innerHTML += `<p class="text-red-600">Không có dữ liệu waypoint</p>`;
    }
    

    // Hiện modal
    document.getElementById("waypoint-modal").classList.remove("hidden");
}


async function downloadWaypoint(filename) {
    window.location.href = `/waypoint-manager/download/${filename}`;
}

async function deleteWaypoint(filename) {
    const res = await fetch(`/waypoint-manager/${filename}`, {
        method: 'DELETE',
    });
    const data = await res.json();
    alert(data.message);
    fetchWaypointList();
}
setInterval(() => {
    fetch('/camera')
        .then(res => res.json())
        .then(data => {
      
            if (data.image) {
                document.getElementById("camera-feed").src = "data:image/jpeg;base64," + data.image;
              
            }
        });
}, 100);
console.log("dong")
document.addEventListener("DOMContentLoaded", () => {
    fetchWaypointList();
});
