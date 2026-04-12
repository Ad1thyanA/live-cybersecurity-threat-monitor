#project done by adithyan, yedhu , devaduth

from backend.data_store import ip_counter
def process_log(log):
    ip = log["ip"]
    ip_counter[ip] += 1
    for ip, count in ip_counter.items():
        print(f"{ip} → {count}")
    THRESHOLD = 20  # you can adjust

    for ip, count in ip_counter.items():
        if count > THRESHOLD:
            print(f"High traffic detected from {ip}")