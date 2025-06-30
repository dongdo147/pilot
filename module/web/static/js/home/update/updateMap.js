export const updateMap = (map, waypoints, mapMarkers, polyline) => {
  
    // Xóa markers cũ
    mapMarkers.forEach(marker => map.removeLayer(marker));
    mapMarkers.length = 0;

    // Xóa polyline cũ nếu tồn tại
    if (polyline) {
        map.removeLayer(polyline);
    }

    // Thêm markers mới
    const validWaypoints = waypoints.filter(wp => 
        wp && typeof wp.x === 'number' && !isNaN(wp.x) && typeof wp.y === 'number' && !isNaN(wp.y)
    );

    validWaypoints.forEach(wp => {
        const marker = L.marker([wp.x, wp.y]).addTo(map)
            .bindPopup(`Waypoint ${wp.seq}: ${wp.x.toFixed(5)}, ${wp.y.toFixed(5)}, ${wp.z}m`);
        mapMarkers.push(marker);
    });

    // Tạo polyline mới nếu đủ waypoint
    let newPolyline = undefined;
    if (validWaypoints.length > 1) {
        newPolyline = L.polyline(validWaypoints.map(w => [w.x, w.y]), {
            color: '#1e40af'
        }).addTo(map);
    }

    // Điều chỉnh view của map để hiển thị tất cả markers
    if (validWaypoints.length > 0) {
        const bounds = L.latLngBounds(validWaypoints.map(wp => [wp.x, wp.y]));
        // map.fitBounds(bounds, { padding: [50, 50] });
    }

    // Gọi invalidateSize để đảm bảo map render đúng
    map.invalidateSize();

    return newPolyline;
};