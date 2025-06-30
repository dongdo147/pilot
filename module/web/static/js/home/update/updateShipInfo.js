export function updateShipInfo (center,compassAngle)  {
    console.log(center)
        document.getElementById('lat').textContent = center[0].toFixed(5);
        document.getElementById('lng').textContent = center[1].toFixed(5);
        document.getElementById('speed').textContent = '12.5'; // Simulated
        document.getElementById('heading').textContent = compassAngle.toFixed(0);
        document.getElementById('depth').textContent = '5.2'; // Simulated
        document.getElementById('windSpeed').textContent = '8.0'; // Simulated
        document.getElementById('engineStatus').textContent = 'Running';
        document.getElementById('compassAngle').textContent = `${compassAngle}°`;

        // Rotate compass needle
        const needle = document.getElementById('needle');
        needle.style.transformOrigin = "50% 50%";
        needle.style.transform = `rotate(${compassAngle}deg)`;
    };