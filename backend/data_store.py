from collections import defaultdict

# Count requests per IP
ip_counter = defaultdict(int)

# Store parsed logs
logs = []

# Store alerts
alerts = []

# Limit logs to avoid memory overflow
MAX_LOGS = 100