from data_store import ip_counter, alerts

THRESHOLD = 10

def check_alerts():
    for ip, count in ip_counter.items():
        if count > THRESHOLD:
            alert = f"Suspicious IP: {ip} ({count} requests)"

            if alert not in alerts:
                alerts.append(alert)