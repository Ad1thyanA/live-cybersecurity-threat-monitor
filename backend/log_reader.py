import requests
import time

from parser import parse_log
from analytics import process_log
from ml_model import detect_anomaly
from data_store import logs, MAX_LOGS
import config 

last_size = 0

def start_reader():
    global last_size

    while True:
        try:
            r = requests.get(config.LOG_SOURCE, timeout=3)
            lines = r.text.strip().split("\n")

            # 🔥 read only new lines based on length
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

                if r.status_code != 200:
                    print("⚠️ Unable to fetch logs")
                    time.sleep(2)
                    continue

            # 🔥 update pointer
            last_size = len(lines)

            detect_anomaly()

            time.sleep(1)

        except Exception as e:
            print("Log reader error:", e)
            time.sleep(1)