import requests
import time
from collections import defaultdict

URL = "http://10.128.236.234:9000/live.log"

seen_lines = 0

ip_count = defaultdict(int)
endpoint_count = defaultdict(int)

total_requests = 0
SUSPICIOUS_THRESHOLD = 5

print("REAL-TIME CYBER THREAT MONITOR STARTED")

while True:
    try:
        r = requests.get(URL)
        lines = r.text.split("\n")

        new_lines = lines[seen_lines:]

        for line in new_lines:
            if line.strip():

                parts = line.split()

                if len(parts) >= 9:
                    ip = parts[0]
                    endpoint = parts[6]
                    status = parts[8]

                    ip_count[ip] += 1
                    endpoint_count[endpoint] += 1
                    total_requests += 1

                    print("\n===== LIVE LOG EVENT =====")
                    print(f"IP Address : {ip}")
                    print(f"Endpoint   : {endpoint}")
                    print(f"Status     : {status}")

                    print("\n--- TRAFFIC ANALYTICS ---")
                    print(f"Total Requests      : {total_requests}")
                    print(f"Requests from {ip} : {ip_count[ip]}")
                    print(f"Requests for {endpoint}: {endpoint_count[endpoint]}")

                    if ip_count[ip] > SUSPICIOUS_THRESHOLD:
                        print("\n⚠ ALERT: Possible Suspicious Traffic Detected")

        seen_lines = len(lines)

        time.sleep(0.5)

    except Exception as e:
        print("Waiting for logs...")
        time.sleep(1)