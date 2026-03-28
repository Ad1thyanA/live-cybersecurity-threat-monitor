import json
import time
from collections import defaultdict

LOG_FILE = "logs.json"

print("BCA FINAL PROJECT DONE BY ADITHYAN, DEVADUTH, YEDHUKRISHNAN")
print("SPRINT 2: STRUCTURED LOG PARSING + TRAFFIC ANALYTICS ENGINE")

# Track request counts
ip_count = defaultdict(int)
endpoint_count = defaultdict(int)

# Suspicious traffic threshold
SUSPICIOUS_THRESHOLD = 5

def follow_logs():

    total_requests = 0

    with open(LOG_FILE, "r") as f:
        f.seek(0, 2)  # move to end of file

        while True:
            line = f.readline()

            if not line:
                time.sleep(1)
                continue

            line = line.strip()
            if line == "":
                continue

            try:
                log = json.loads(line)

                # Structured fields
                ip = log["ip"]
                endpoint = log["endpoint"]
                timestamp = log["timestamp"]

                # Update analytics
                ip_count[ip] += 1
                endpoint_count[endpoint] += 1
                total_requests += 1

                print("\n==============================")
                print("NEW LOG EVENT DETECTED")
                print("==============================")

                print(f"Time      : {timestamp}")
                print(f"IP Address: {ip}")
                print(f"Endpoint  : {endpoint}")

                print("\n--- TRAFFIC ANALYTICS ---")
                print(f"Total Requests      : {total_requests}")
                print(f"Requests from {ip} : {ip_count[ip]}")
                print(f"Requests for {endpoint}: {endpoint_count[endpoint]}")

                # Simple suspicious detection
                if ip_count[ip] > SUSPICIOUS_THRESHOLD:
                    print("\n⚠ WARNING: HIGH REQUEST RATE DETECTED")
                    print(f"Suspicious IP: {ip} ({ip_count[ip]} requests)")

                print("------------------------------")

            except json.JSONDecodeError:
                print("Skipped invalid log line")

if __name__ == "__main__":
    follow_logs()