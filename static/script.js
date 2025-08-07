function startStream() {
    document.getElementById('video').src = '/video_feed';
}

function clickPixel(event) {
    const img = event.target;
    const rect = img.getBoundingClientRect();
    const x = Math.floor(event.clientX - rect.left);
    const y = Math.floor(event.clientY - rect.top);
    fetch(`/click_point/?x=${x}&y=${y}`, { method: 'POST' })
        .then(response => response.json())
        .then(data => updatePointList());
}

function updatePointList() {
    fetch('/get_points/')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('points-list');
            container.innerHTML = '<h3>Captured Points (x, y, z):</h3>';
            data.forEach((pt, i) => {
                container.innerHTML += `<p>${i+1}. (${pt.world.join(', ')})</p>`;
            });
        });
}

function sendData() {
    fetch('/send/', { method: 'POST' })
        .then(response => response.json())
        .then(data => alert("Data sent to server!"));
}

function clearData() {
    fetch('/clear/', { method: 'POST' })
        .then(() => {
            document.getElementById('points-list').innerHTML = '';
        });
}

function exitStream() {
    fetch('/exit/', { method: 'POST' })
        .then(() => {
            document.getElementById('video').src = '';
            alert("Stream stopped.");
        });
}