const boatIcon = L.divIcon({
    html: `<div id="boat-icon" style="width:40px; height:40px; transform: rotate(0deg);">
             <img src="https://cdn-icons-png.flaticon.com/512/32/32195.png" style="width: 100%; transform-origin: center;">
           </div>`,
    className: "", // bỏ class mặc định
    iconSize: [40, 40],
    iconAnchor: [20, 20], // tâm icon
  });
  
  let map;
  let boatMarker;
  let defaultLat = 10.762622;
  let defaultLon = 106.660172;
  
  // Khởi tạo map
  function initMap(lat, lon) {
    map = L.map("map").setView([lat, lon], 15);
  
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    }).addTo(map);
        boatMarker = L.marker([lat, lon], { icon: boatIcon })
        .addTo(map)
        .bindPopup("🚤 Vị trí tàu")
        .openPopup();
  
  
    initWaypointDrawing(); 
  }
  
  
  async function fetchData() {
    const res = await fetch("/data");
    const { pixhawk_data } = await res.json();
  
    const hasLatLon =  pixhawk_data.lat2  &&   pixhawk_data.lon2;
    const hasYaw = typeof pixhawk_data.yaw === "number";
  
    if (hasLatLon) {
  
      //XÁC ĐỊNH VỊ TRÍ TÀU
      if (!map) {
        initMap(pixhawk_data.lat2, pixhawk_data.lon2);
      } else {
        boatMarker.setLatLng([pixhawk_data.lat2, pixhawk_data.lon2]);
        map.setView([pixhawk_data.lat2, pixhawk_data.lon2]);
      }
  
      //TÍNH TỐC ĐỘ TÀU
      const now = Date.now(); //Thời gian bắt đầu
      if (lastPosition) {
      const dt = (now - lastPosition.time) / 1000;
      const distance = getDistanceKm(
        lastPosition.lat, lastPosition.lon,
        pixhawk_data.lat2, pixhawk_data.lon2
      );
      const speed = (distance / dt) * 1000;
  
      console.log("🌊 Tốc độ tàu:", speed.toFixed(2), "m/s");
  
      if (speed < speedThreshold) {
        stationaryCount++;
      } else {
        stationaryCount = 0;
      }
  
      if (stationaryCount >= stationaryThreshold) {
    
        showStationaryWarning();
      } else {
        hideStationaryWarning();
      }
    }
  
    lastPosition = {
      lat: pixhawk_data.lat2,
      lon: pixhawk_data.lon2,
      time: now,
    };
    } else if (!map) {
      initMap(defaultLat, defaultLon);
    }
  
    if (hasYaw) {
      let headingDeg = (pixhawk_data.yaw * 180) / Math.PI;
      headingDeg = (headingDeg + 360) % 360;
      document.getElementById("boat-icon").style.transform = `rotate(${headingDeg}deg)`;
    }
  }
  
  
  
  setInterval(fetchData, 1000);
  fetchData();
  
// ---------- VẼ WAYPOINT ------------
let waypoints = [];
let line = null;
let markers = [];

function initWaypointDrawing() {
  line = L.polyline([], { color: "blue" }).addTo(map);

  map.on("click", (e) => {
    const { lat, lng } = e.latlng;
    waypoints.push([lat, lng]);

    const marker = L.marker([lat, lng])
      .addTo(map)
      .bindPopup(`📍 Waypoint ${waypoints.length}`)
      .openPopup();

    // Lưu các marker vào một mảng để có thể xóa sau này
    markers.push(marker);

    line.setLatLngs(waypoints);
  });

  document.getElementById("exportBtn").addEventListener("click", async () => {
    if (waypoints.length === 0) {
      alert("Chưa có waypoint nào!");
      return;
    }

    try {
      const res = await fetch('/waypoint', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ waypoints })
      });

      if (res.ok) {
        alert("✅ Waypoint đã được gửi thành công!");
        
        // Sau khi gửi thành công, xóa dữ liệu waypoint
        waypoints = [];
        line.setLatLngs([]); // Xóa polyline

        // Xóa tất cả các marker
        markers.forEach(marker => marker.remove());
        markers = []; // Làm sạch mảng markers
      } else {
        alert("❌ Gửi waypoint thất bại!");
      }
    } catch (err) {
      alert("⚠️ Lỗi khi gửi waypoint: " + err.message);
    }
  });
}


  //---------- TÍNH KHOẢNG CÁCH ĐIỂM BẮT ĐẦU VÀ KẾT THÚC ------------
  let lastPosition = null;  
  let stationaryCount = 0;
  const stationaryThreshold = 5; // số lần fetch liên tiếp
  const speedThreshold = 0.1; // dưới 0.1 m/s coi như đứng yên
  function getDistanceKm(lat1, lon1, lat2, lon2) {
    const R = 6371;
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) ** 2 +
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
      Math.sin(dLon / 2) ** 2;
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  }
  //HÀM HIỆN VÀ ẨN CẢNH BÁO
  function showStationaryWarning() {
    document.getElementById("stationaryWarning").classList.remove("hidden");
  }
  function hideStationaryWarning() {
    document.getElementById("stationaryWarning").classList.add("hidden");
  }