printed_once = False

def parse_log(line):
    global printed_once

    parts = line.split()

    if len(parts) < 5:
        return None

    ip = parts[0]

    # 🔥 find endpoint safely
    endpoint = None
    for part in parts:
        if part.startswith("/"):
            endpoint = part.strip('"')
            break

    # 🔥 find status safely
    status = None
    for part in parts:
        if part.isdigit() and len(part) == 3:
            status = part
            break

    if not endpoint or not status:
        return None

    if not printed_once:
        print("Project made by Adithyan, Devaduth, Yedhu Krishnan\n")
        printed_once = True

    print(f"IP: {ip}, Endpoint: {endpoint}, Status: {status}")

    return {
        "ip": ip,
        "endpoint": endpoint,
        "status": status
    }