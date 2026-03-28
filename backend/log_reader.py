import requests
import time

from parser import parse_log
from analytics import process_log
from alerts import check_alerts
from ml_model import detect_anomaly
from data_store import logs, MAX_LOGS

URL = "http://localhost:9000/live.log"

seen = 0
MAX_LINES = 200  

def start_reader():
    global seen

    while True:
        try:
            r = requests.get(URL)
            lines = r.text.split("\n")

            # 🔥 Take only last part of file
            if len(lines) > MAX_LINES:
                lines = lines[-MAX_LINES:]
                seen = min(seen, len(lines))

            # 🔥 Handle reset
            if seen > len(lines):
                seen = 0

            new_lines = lines[seen:]

            for line in new_lines:
                if not line.strip():
                    continue

                parsed = parse_log(line)

                if parsed:
                    logs.append(parsed)

                    if len(logs) > MAX_LOGS:
                        logs.pop(0)

                    process_log(parsed)

            seen += len(new_lines)

            check_alerts()
            detect_anomaly()

            time.sleep(0.8)  # 🔥 slightly faster

        except Exception as e:
            print("Log reader error:", e)
            time.sleep(1)