from flask import Flask, jsonify, render_template
from threading import Thread
import requests

from alerts import generate_alerts
from log_reader import start_reader
from data_store import ip_counter, logs, alerts
from ml_model import detect_anomaly
from attack_classifier import AttackClassifier
from flask import request
import config

# ✅ Initialize classifier
classifier = AttackClassifier()


# ✅ NEW: Location cache (PERFORMANCE FIX)
location_cache = {}

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)

# ✅ UPDATED: Location function with caching
def get_location(ip):
    # 🔥 RETURN FROM CACHE (FAST)
    if ip in location_cache:
        return location_cache[ip]

    try:
        res = requests.get(f"http://ip-api.com/json/{ip}", timeout=2)
        data = res.json()

        # skip private/local IPs
        if data.get("status") != "success":
            return None

        loc = {
            "ip": ip,
            "lat": data.get("lat"),
            "lon": data.get("lon"),
            "country": data.get("country")
        }

        # 🔥 SAVE TO CACHE
        location_cache[ip] = loc

        return loc

    except:
        return None


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

    generate_alerts(attack_predictions)

    # ✅ GEO LOCATION DATA (NOW FAST)
    locations = []
    for ip in ip_counter.keys():
        loc = get_location(ip)
        if loc:
            locations.append(loc)

    return jsonify({
        "total_requests": total_requests,
        "ip_counts": dict(ip_counter),
        "top_ips": top_ips,
        "status_distribution": status_count,
        "top_endpoints": endpoints,
        "logs": logs[-20:],   # unchanged
        "alerts": alerts,
        "ml_alerts": ml_alerts,
        "attack_predictions": attack_predictions,
        "ml_data": {
            "ips": list(ip_counter.keys()),
            "counts": list(ip_counter.values())
        },

        # ✅ MAP DATA
        "locations": locations
    })

@app.route("/set-log-source", methods=["POST"])
def set_log_source():
    data = request.get_json()
    url = data.get("url")

    if url and url.startswith("http"):
        config.LOG_SOURCE = url
        print("✅ Log source updated to:", config.LOG_SOURCE)
        return {"status": "success"}
    
    return {"status": "error", "message": "Invalid URL"}


if __name__ == "__main__":
    Thread(target=start_reader, daemon=True).start()
    app.run(debug=True)