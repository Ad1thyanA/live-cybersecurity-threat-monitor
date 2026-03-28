# attack_classifier.py  

from collections import defaultdict
import time

class AttackClassifier:
    def __init__(self):
        self.ip_activity = defaultdict(list)
        self.failed_attempts = defaultdict(int)

    def update_activity(self, ip):
        now = time.time()
        self.ip_activity[ip].append(now)

        # Keep last 10 seconds activity
        self.ip_activity[ip] = [
            t for t in self.ip_activity[ip] if now - t <= 10
        ]

    def classify(self, logs, ip_counts, status_distribution, endpoints):
        attack_results = []

        total_requests = sum(ip_counts.values())

        # Detect DDoS (global spike)
        if total_requests > 200:
            attack_results.append({
                "type": "DDoS Attack",
                "severity": "HIGH",
                "description": "Unusual spike in total traffic"
            })

        for ip, count in ip_counts.items():

            # Track activity window
            self.update_activity(ip)
            recent_count = len(self.ip_activity[ip])

            # 1. Brute Force Detection
            if "/login" in endpoints and count > 20:
                attack_results.append({
                    "ip": ip,
                    "type": "Brute Force Attack",
                    "severity": "HIGH",
                    "description": "Repeated login attempts"
                })

            # 2. High Frequency (Possible Bot / Flood)
            elif recent_count > 50:
                attack_results.append({
                    "ip": ip,
                    "type": "High Frequency Attack",
                    "severity": "MEDIUM",
                    "description": "Too many requests in short time"
                })

            # 3. Endpoint Scanning (many endpoints)
            elif len(endpoints) > 10:
                attack_results.append({
                    "ip": ip,
                    "type": "Endpoint Scanning",
                    "severity": "MEDIUM",
                    "description": "Accessing multiple endpoints rapidly"
                })

            # 4. Failed Login Attempts
            if "401" in status_distribution or "403" in status_distribution:
                self.failed_attempts[ip] += 1

                if self.failed_attempts[ip] > 10:
                    attack_results.append({
                        "ip": ip,
                        "type": "Authentication Attack",
                        "severity": "HIGH",
                        "description": "Multiple failed authentication attempts"
                    })

        # If nothing detected
        if not attack_results:
            attack_results.append({
                "type": "Normal Traffic",
                "severity": "LOW",
                "description": "No suspicious activity detected"
            })


        for attack in attack_results:
            print(f"{attack['type']} detected: {attack.get('ip', 'N/A')}")

        return attack_results