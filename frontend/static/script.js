let ipChart;
let statusChart;
let trafficChart;
let trafficData = [];
let mlChart;

// INIT
window.onload = () => {
    lucide.createIcons();

    setTimeout(() => {
        document.getElementById("loader").style.display = "none";
    }, 800);
};

// SIDEBAR SWITCH
function showSection(sectionId, btn) {
    document.querySelectorAll(".section").forEach(s => s.classList.add("hidden"));
    document.getElementById(sectionId).classList.remove("hidden");

    document.querySelectorAll(".sidebar button").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
}

// 🚨 NEW: Attack Panel Update Function
function updateAttackPanel(attacks) {
    const container = document.getElementById("attack-container");

    if (!container) return;

    if (!attacks || attacks.length === 0) {
        container.innerHTML = "<p style='color: gray;'>No threats detected</p>";
        return;
    }

    let html = "";

    attacks.forEach(att => {
        let severityClass = "low";
        let blinkClass = "";

        if (att.severity === "HIGH") {
            severityClass = "high";
            blinkClass = "blink";  // 🔴 blinking only
        } else if (att.severity === "MEDIUM") {
            severityClass = "medium";
        }

        html += `
            <div class="attack-item ${severityClass} ${blinkClass}">
                <div class="attack-type">${att.type}</div>
                <div class="attack-desc">${att.description}</div>
                ${att.ip ? `<div style="font-size:12px;">IP: ${att.ip}</div>` : ""}
            </div>
        `;
    });

    container.innerHTML = html;
}

// LOAD DATA
async function loadData() {
    const res = await fetch("/api/stats");
    const data = await res.json();

    // 🚨 NEW: Attack Predictions Integration
    updateAttackPanel(data.attack_predictions);

    document.getElementById("total").innerText = data.total_requests;
    document.getElementById("alertsCount").innerText = data.alerts.length;

    // ALERTS
    const alertBox = document.getElementById("alertBox");
    alertBox.innerHTML = "";
    data.alerts.forEach(a => {
        alertBox.innerHTML += `<div class="alert-item">${a}</div>`;
    });

    // ML
    const mlBox = document.getElementById("mlBox");
    mlBox.innerHTML = "";
    data.ml_alerts.forEach(a => {
        mlBox.innerHTML += `<div class="ml-item">${a}</div>`;
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

// ML GRAPH (Cluster-style visualization)
if (mlChart) mlChart.destroy();

if (!data.ml_data) return;

// safer anomaly extraction
let anomalyIPs = data.ml_alerts.map(a => {
    let parts = a.split(": ");
    return parts.length > 1 ? parts[1].trim() : null;
}).filter(ip => ip);

// better colors
let colors = data.ml_data.ips.map(ip => 
    anomalyIPs.includes(ip) 
        ? "rgba(255, 99, 132, 0.8)" 
        : "rgba(54, 162, 235, 0.6)"
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
}

setInterval(loadData, 1000);
loadData();