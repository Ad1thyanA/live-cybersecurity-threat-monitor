import requests
import time

from parser import parse_log
from analytics import process_log
from ml_model import detect_anomaly
from data_store import logs, MAX_LOGS

URL = "http://127.0.0.1:9000/live.log"

last_size = 0

def start_reader():
    global last_size

    while True:
        try:
            r = requests.get(URL)
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

            # 🔥 update pointer
            last_size = len(lines)

            detect_anomaly()

            time.sleep(1)

        except Exception as e:
            print("Log reader error:", e)
            time.sleep(1)