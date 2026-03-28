from flask import Flask, jsonify, render_template
from threading import Thread

from log_reader import start_reader
from data_store import ip_counter, logs, alerts
from ml_model import detect_anomaly
from attack_classifier import AttackClassifier

# ✅ Initialize classifier (NEW)
classifier = AttackClassifier()

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/stats")
def stats():
    total_requests = sum(ip_counter.values())

    top_ips = sorted(ip_counter.items(), key=lambda x: x[1], reverse=True)[:5]

    status_count = {}
    for log in logs:
        status = log["status"]
        status_count[status] = status_count.get(status, 0) + 1

    endpoints = {}
    for log in logs:
        ep = log["endpoint"]
        endpoints[ep] = endpoints.get(ep, 0) + 1

    ml_alerts = detect_anomaly()

    
    attack_predictions = classifier.classify(
        logs,
        dict(ip_counter),
        status_count,
        endpoints
    )

    return jsonify({
        "total_requests": total_requests,
        "ip_counts": dict(ip_counter),
        "top_ips": top_ips,
        "status_distribution": status_count,
        "top_endpoints": endpoints,
        "logs": logs[-20:],
        "alerts": alerts,
        "ml_alerts": ml_alerts,
        "attack_predictions": attack_predictions,
        "ml_data": {
            "ips": list(ip_counter.keys()),
            "counts": list(ip_counter.values())
        }
    })

if __name__ == "__main__":
    Thread(target=start_reader, daemon=True).start()
    app.run(debug=True)