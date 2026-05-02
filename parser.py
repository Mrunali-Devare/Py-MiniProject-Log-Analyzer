import re

def parse_logs(file_path):
    logs = []

    with open(file_path, 'r') as file:
        for line in file:

            match = re.match(r'(\S+ \S+) (\w+) (.*)', line)

            if match:
                timestamp, level, message = match.groups()
            else:
                timestamp = "Unknown"
                level = "INFO"
                message = line.strip()

            ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', message)
            ip = ip_match.group(1) if ip_match else None

            logs.append({
                "timestamp": timestamp,
                "level": level,
                "message": message,
                "ip": ip
            })

    return logs