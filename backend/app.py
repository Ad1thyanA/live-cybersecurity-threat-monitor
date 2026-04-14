from flask import Flask, jsonify, render_template, request
from threading import Thread
import requests
import os

from backend.alerts import generate_alerts
from backend.log_reader import start_reader
from backend.data_store import ip_counter, logs, alerts
from backend.ml_model import detect_anomaly
from backend.attack_classifier import AttackClassifier
from backend import config

# ✅ Initialize classifier
classifier = AttackClassifier()

# ✅ Location cache
location_cache = {}

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)

# 🚀 START BACKGROUND THREAD (RENDER SAFE)
reader_started = False

def start_background():
    global reader_started
    if not reader_started:
        print("🚀 Starting log reader thread...")
        Thread(target=start_reader, daemon=True).start()
        reader_started = True

# 🔥 FORCE START (works in Render + Gunicorn)
start_background()


# 🌍 LOCATION FUNCTION
def get_location(ip):
    if ip in location_cache:
        return location_cache[ip]

    try:
        res = requests.get(f"http://ip-api.com/json/{ip}", timeout=2)
        data = res.json()

        if data.get("status") != "success":
            return None

        loc = {
            "ip": ip,
            "lat": data.get("lat"),
            "lon": data.get("lon"),
            "country": data.get("country")
        }

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

    # 🌍 GEO DATA
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
        "logs": logs[-20:],
        "alerts": alerts,
        "ml_alerts": ml_alerts,
        "attack_predictions": attack_predictions,
        "ml_data": {
            "ips": list(ip_counter.keys()),
            "counts": list(ip_counter.values())
        },
        "locations": locations
    })


@app.route("/set-log-source", methods=["POST"])
def set_log_source():
    global reader_started

    data = request.get_json()
    url = data.get("url")

    print("🔥 RECEIVED URL:", url)

    if url and url.startswith("http"):
        config.LOG_SOURCE = url
        print("✅ Log source updated to:", config.LOG_SOURCE)

        # 🚀 START READER HERE (FINAL FIX)
        if not reader_started:
            print("🚀 Starting reader after URL set...")
            Thread(target=start_reader, daemon=True).start()
            reader_started = True

        return {"status": "success"}

    return {"status": "error"}
