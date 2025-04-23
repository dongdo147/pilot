async function fetchWaypointList() {
    const res = await fetch("/waypoint-manager");
    const data = await res.json();

    const waypointListDiv = document.getElementById("waypoint-list");
    waypointListDiv.innerHTML = '';

    data.waypoints.forEach(wp => {
        const fileDiv = document.createElement("div");
        fileDiv.classList.add("waypoint-card");
        fileDiv.innerHTML = `
          <h3 class="waypoint-title">${wp.filename}</h3>
          <p class="waypoint-meta">🕒 ${new Date(wp.created_at).toLocaleString()}</p>
          <button onclick="viewWaypoint('${wp.filename}')" class="btn btn-view">
            Xem
          </button>
          <button onclick="downloadWaypoint('${wp.filename}')" class="btn btn-download">
            Tải về
          </button>
          <button onclick="deleteWaypoint('${wp.filename}')" class="btn btn-delete">
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
        let table = `<table class="waypoint-table">
            <thead class="table-header">
                <tr>
                    <th class="table-cell">#</th>
                    <th class="table-cell">Latitude</th>
                    <th class="table-cell">Longitude</th>
                </tr>
            </thead><tbody>`;
    
        info.waypoints.forEach((point, idx) => {
            const [lat, lng] = point;
            table += `<tr>
                <td class="table-cell text-center">${idx + 1}</td>
                <td class="table-cell">${lat?.toFixed(6) ?? "?"}</td>
                <td class="table-cell">${lng?.toFixed(6) ?? "?"}</td>
            </tr>`;
        });
    
        table += `</tbody></table>`;
        container.innerHTML += table;
    } else {
        container.innerHTML += `<p class="error-text">Không có dữ liệu waypoint</p>`;
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
<<<<<<< HEAD
=======

>>>>>>> db612be01aea85de6cef57e8917b4cd8ac90e3ac
setInterval(() => {
    fetch('/camera')
        .then(res => res.json())
        .then(data => {
            if (data.image) {
                document.getElementById("camera-feed").src = "data:image/jpeg;base64," + data.image;
            }
        });
}, 100);

console.log("dong");
document.addEventListener("DOMContentLoaded", () => {
    fetchWaypointList();
<<<<<<< HEAD
});
=======
});
>>>>>>> db612be01aea85de6cef57e8917b4cd8ac90e3ac
