from sklearn.cluster import KMeans
from data_store import ip_counter, logs

def extract_features():
    features = []
    ip_list = []

    for ip in ip_counter:
        count = ip_counter[ip]

        # Error rate
        errors = sum(1 for log in logs if log["ip"] == ip and log["status"] != "200")
        total = count if count > 0 else 1
        error_rate = errors / total

        # Unique endpoints
        endpoints = set(log["endpoint"] for log in logs if log["ip"] == ip)
        unique_endpoints = len(endpoints)

        features.append([count, error_rate, unique_endpoints])
        ip_list.append(ip)
        
    return features, ip_list

   

def detect_anomaly():
    features, ip_list = extract_features()

    if len(features) < 2:
        return []

    try:
        kmeans = KMeans(n_clusters=2, random_state=0, n_init=10)
        labels = kmeans.fit_predict(features)

        # Find cluster with highest average request count
        cluster_scores = {}
        for i, label in enumerate(labels):
            cluster_scores.setdefault(label, []).append(features[i][0])

        high_cluster = max(
            cluster_scores,
            key=lambda k: sum(cluster_scores[k]) / len(cluster_scores[k])
        )

        anomalies = []
        for i, label in enumerate(labels):
            if label == high_cluster:
                anomalies.append(f"Anomaly detected: {ip_list[i]}")

        

        return anomalies

    except Exception as e:
        print("ML Error:", e)
        return []