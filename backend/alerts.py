from backend.data_store import alerts

def generate_alerts(attack_predictions):
    alerts.clear()

    for attack in attack_predictions:
        severity = attack.get("severity", "LOW")
        attack_type = attack.get("type", "Unknown")
        ip = attack.get("ip", "N/A")

        message = f"[{severity}] {attack_type} from {ip}"

        alerts.append(message)