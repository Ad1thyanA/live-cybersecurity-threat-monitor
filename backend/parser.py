printed_once = False   

def parse_log(line):
    global printed_once

    parts = line.split()

    if len(parts) < 9:
        return None

    ip = parts[0]
    endpoint = parts[6]
    status = parts[8]

    
    if not printed_once:
        print("Project made by Adithyan, Devaduth, Yedhu Krishnan\n")
        printed_once = True

    print(f"IP: {ip}, Endpoint: {endpoint}, Status: {status}")

    return {
        "ip": ip,
        "endpoint": endpoint,
        "status": status
    }