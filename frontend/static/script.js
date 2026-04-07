let ipChart;
let statusChart;
let trafficChart;
let trafficData = [];
let mlChart;
let map;
let markers = [];

// INIT
window.onload = () => {
    lucide.createIcons();

    setTimeout(() => {
        document.getElementById("loader").style.display = "none";
    }, 800);

    // MAP INIT
    map = L.map('map').setView([20, 77], 3);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
};

// SIDEBAR
function showSection(sectionId, btn) {
    document.querySelectorAll(".section").forEach(s => s.classList.add("hidden"));
    document.getElementById(sectionId).classList.remove("hidden");

    document.querySelectorAll(".sidebar button").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");

    // FIX MAP RENDER
    if (sectionId === "mapSection" && map) {
        setTimeout(() => map.invalidateSize(), 200);
    }
}

// 🚨 ATTACK PANEL
function updateAttackPanel(attacks) {
    const container = document.getElementById("attack-container");

    if (!container) return;

    if (!attacks || attacks.length === 0) {
        container.innerHTML = "<p class='sub'>No active threats detected</p>";
        return;
    }

    let html = "";

    attacks.forEach(att => {
        let severityClass = "low";

        if (att.severity === "HIGH") severityClass = "high";
        else if (att.severity === "MEDIUM") severityClass = "medium";

        html += `
            <div class="alert-item ${severityClass}">
                <div style="display:flex; justify-content:space-between;">
                    <strong>${att.type}</strong>
                    <span class="sub">${att.severity}</span>
                </div>
                <div class="sub">${att.description}</div>
                ${att.ip ? `<div class="sub">Source: ${att.ip}</div>` : ""}
            </div>
        `;
    });

    container.innerHTML = html;
}

// 🔥 TOP ATTACKER
function updateTopAttacker(ipCounts) {
    const box = document.getElementById("topAttackerBox");
    if (!box) return;

    let topIP = null;
    let max = 0;

    for (let ip in ipCounts) {
        if (ipCounts[ip] > max) {
            max = ipCounts[ip];
            topIP = ip;
        }
    }

    if (!topIP) {
        box.innerHTML = "<p class='sub'>No activity</p>";
        return;
    }

    box.innerHTML = `
        <strong>${topIP}</strong>
        <div class="sub">${max} requests</div>
    `;
}

// LOAD DATA
async function loadData() {
    try {
        const res = await fetch("/api/stats");
        const data = await res.json();

        updateAttackPanel(data.attack_predictions);
        updateTopAttacker(data.ip_counts);

        // DASHBOARD
        document.getElementById("total").innerText = data.total_requests;
        document.getElementById("alertsCount").innerText = data.alerts.length;

        if (document.getElementById("uniqueIPs")) {
            document.getElementById("uniqueIPs").innerText =
                Object.keys(data.ip_counts).length;
        }

        // ALERTS
        const alertBox = document.getElementById("alertBox");
        alertBox.innerHTML = "";

        data.alerts.forEach(a => {
            let type = "low";
            if (a.includes("[HIGH]")) type = "high";
            else if (a.includes("[MEDIUM]")) type = "medium";

            alertBox.innerHTML += `
                <div class="alert-item ${type}">
                    ${a}
                </div>
            `;
        });

        // LOGS
        const table = document.getElementById("logTable");
        table.innerHTML = "";

        data.logs.forEach(log => {
            table.innerHTML += `
                <tr>
                    <td>${log.ip}</td>
                    <td>${log.endpoint}</td>
                    <td>${log.status}</td>
                </tr>
            `;
        });

        // CHARTS
        if (ipChart) ipChart.destroy();
        ipChart = new Chart(document.getElementById("ipChart"), {
            type: "bar",
            data: {
                labels: Object.keys(data.ip_counts),
                datasets: [{
                    label: "Requests",
                    data: Object.values(data.ip_counts)
                }]
            }
        });

        if (statusChart) statusChart.destroy();
        statusChart = new Chart(document.getElementById("statusChart"), {
            type: "doughnut",
            data: {
                labels: Object.keys(data.status_distribution),
                datasets: [{
                    data: Object.values(data.status_distribution)
                }]
            }
        });

        // ML GRAPH
        if (mlChart) mlChart.destroy();

        let anomalyIPs = data.ml_alerts.map(a => {
            let parts = a.split(": ");
            return parts.length > 1 ? parts[1] : null;
        }).filter(x => x);

        let colors = data.ml_data.ips.map(ip =>
            anomalyIPs.includes(ip)
                ? "rgba(239,68,68,0.85)"
                : "rgba(59,130,246,0.6)"
        );

        mlChart = new Chart(document.getElementById("mlChart"), {
            type: "bar",
            data: {
                labels: data.ml_data.ips,
                datasets: [{
                    label: "ML Traffic Analysis",
                    data: data.ml_data.counts,
                    backgroundColor: colors
                }]
            }
        });

        // 🌍 MAP (AUTO ZOOM FIX INCLUDED)
        if (data.locations && map) {

            markers.forEach(m => map.removeLayer(m));
            markers = [];

            let bounds = [];

            data.locations.forEach(loc => {

                let color = "#3b82f6";

                let attack = data.attack_predictions.find(a => a.ip === loc.ip);

                if (attack) {
                    if (attack.severity === "HIGH") color = "#ef4444";
                    else if (attack.severity === "MEDIUM") color = "#f59e0b";
                }

                let marker = L.circleMarker([loc.lat, loc.lon], {
                    radius: 7,
                    color: color,
                    fillColor: color,
                    fillOpacity: 0.85
                })
                .addTo(map)
                .bindPopup(`
                    <strong>${loc.ip}</strong><br>
                    ${loc.country}<br>
                    ${attack ? attack.type : "Normal Traffic"}
                `);

                markers.push(marker);
                bounds.push([loc.lat, loc.lon]);
            });

            // 🔥 AUTO ZOOM (THIS WAS MISSING BEFORE)
            if (bounds.length > 0) {
                map.fitBounds(bounds, {
                    padding: [50, 50],
                    maxZoom: 6
                });
            }
        }

        // TRAFFIC
        trafficData.push(data.total_requests);
        if (trafficData.length > 10) trafficData.shift();

        if (trafficChart) trafficChart.destroy();
        trafficChart = new Chart(document.getElementById("trafficChart"), {
            type: "line",
            data: {
                labels: trafficData.map((_, i) => i),
                datasets: [{
                    label: "Traffic",
                    data: trafficData,
                    tension: 0.4
                }]
            }
        });

    } catch (err) {
        console.log("UI error:", err);
    }
}

// REFRESH
setInterval(loadData, 2000);
loadData();