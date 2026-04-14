import requests
import time

from backend.parser import parse_log
from backend.analytics import process_log
from backend.ml_model import detect_anomaly
from backend.data_store import logs, MAX_LOGS
from backend import config 

last_size = 0

def start_reader():
    global last_size

    while True:
        try:
            # 🚨 WAIT UNTIL URL IS SET
            if not config.LOG_SOURCE:
                print("⏳ Waiting for log source...")
                time.sleep(2)
                continue

            print("📡 Fetching from:", config.LOG_SOURCE)

            r = requests.get(config.LOG_SOURCE, timeout=5)

            # 🚨 CHECK STATUS BEFORE PROCESSING
            if r.status_code != 200:
                print("⚠️ Failed to fetch logs:", r.status_code)
                time.sleep(2)
                continue

            lines = r.text.strip().split("\n")

            # 🔥 HANDLE RESET CASE
            if last_size > len(lines):
                last_size = 0

            new_lines = lines[last_size:]

            for line in new_lines:
                if not line.strip():
                    continue

                parsed = parse_log(line)

                if parsed:
                    logs.append(parsed)

                    if len(logs) > MAX_LOGS:
                        logs.pop(0)

                    process_log(parsed)

            # 🔥 UPDATE POINTER
            last_size = len(lines)

            detect_anomaly()

            time.sleep(1)

        except Exception as e:
            print("❌ Log reader error:", e)
            time.sleep(2)
