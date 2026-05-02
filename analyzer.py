from collections import Counter

SEVERITY_WEIGHTS = {
    "INFO":    1,
    "WARNING": 2,
    "ERROR":   3
}

def analyze_logs(logs):
    """
    Main analysis function.
    Takes a list of log dicts and returns a summary dict with:
    - total count
    - level counts
    - error list
    - IP counts
    - suspicious IPs (appear > 2 times)
    - high traffic IPs (appear > 10 times)
    - repeated error source IPs (> 5 errors)
    - anomaly flag (ERROR ratio > 40%)
    - overall severity score
    - time series per hour and per minute
    """

    levels     = [log["level"] for log in logs]
    level_count = Counter(levels)

    errors     = [log for log in logs if log["level"] == "ERROR"]

    ips        = [log["ip"] for log in logs if log["ip"]]
    ip_count   = Counter(ips)

    # High-traffic: appeared more than 10 times
    high_traffic_ips = [ip for ip, cnt in ip_count.items() if cnt > 5]
    # Suspicious: appeared more than 2 times but NOT already in high-traffic
    high_traffic_set = set(high_traffic_ips)
    suspicious_ips   = [ip for ip, cnt in ip_count.items()
                        if cnt > 2 and ip not in high_traffic_set]

    error_ip_count = Counter(
        log["ip"] for log in logs
        if log["level"] == "ERROR" and log["ip"]
    )
    repeated_error_ips = [ip for ip, cnt in error_ip_count.items() if cnt > 5]

    total = len(logs)
    error_count = level_count.get("ERROR", 0)

    anomaly_detected = (error_count / total > 0.40) if total > 0 else False

    severity_score = sum(
        SEVERITY_WEIGHTS.get(log["level"], 1) for log in logs
    )

    time_series_hour = Counter()
    time_series_min  = Counter()
    for log in logs:
        ts = log["timestamp"]
        time_series_hour[ts[:13] if len(ts) >= 13 else ts] += 1  # "YYYY-MM-DD HH"
        time_series_min [ts[:16] if len(ts) >= 16 else ts] += 1  # "YYYY-MM-DD HH:MM"

    return {
        "total":               total,
        "level_count":         level_count,
        "errors":              errors,
        "ip_count":            ip_count,
        "suspicious_ips":      suspicious_ips,
        "high_traffic_ips":    high_traffic_ips,
        "repeated_error_ips":  repeated_error_ips,
        "anomaly_detected":    anomaly_detected,
        "severity_score":      severity_score,
        "time_series_hour":    time_series_hour,
        "time_series_min":     time_series_min,
    }