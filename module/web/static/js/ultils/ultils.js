// utils.js
export function isTooClose(newPoint, waypoints, minDistanceMeters = 5) {
    const newLatLng = L.latLng(newPoint.x, newPoint.y);
    return waypoints.some(wp => {
        const existingLatLng = L.latLng(wp.x, wp.y);
        const distance = newLatLng.distanceTo(existingLatLng); // Distance in meters
        return distance < minDistanceMeters;
    });
}
// utils.js
export function debounce(func, wait) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}