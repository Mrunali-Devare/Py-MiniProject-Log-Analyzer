import tkinter as tk
from tkinter import filedialog, messagebox
import random
from datetime import datetime, timedelta


MESSAGES = {
    "INFO": [
        "User login successful",
        "Page loaded",
        "Session started",
        "Config loaded",
        "Backup completed",
        "Service started",
        "Cache refreshed",
    ],
    "WARNING": [
        "Disk usage above 80%",
        "Slow response time detected",
        "Memory usage high",
        "Retry attempt {n}",
        "Missing optional config key",
        "Deprecated API called",
    ],
    "ERROR": [
        "Failed login attempt from {ip}",
        "Database connection failed",
        "Null pointer exception",
        "Timeout while connecting to {ip}",
        "Unhandled exception in module",
        "Permission denied for {ip}",
    ],
}

RANDOM_IPS = [f"192.168.1.{i}" for i in range(1, 30)]
RANDOM_IPS += [f"10.0.0.{i}" for i in range(1, 10)]
RANDOM_IPS += [f"172.16.0.{i}" for i in range(1, 10)]
RANDOM_IPS += [f"172.17.{i}.{i}" for i in range(1, 10)]


def _random_timestamp(base: datetime, spread_minutes: int, interval_sec: int, index: int) -> str:
    """
    Returns a timestamp string for log entry #index.
    Adds a small random jitter around a base + index*interval position.
    """
    offset = timedelta(seconds=index * interval_sec + random.randint(0, 5))
    ts = base + offset
    return ts.strftime("%Y-%m-%d %H:%M:%S")


def generate_logs(
    num_entries: int,
    level_dist: dict,
    use_random_ips: bool,
    predefined_ips: list,
    custom_messages: dict,
    interval_sec: int,
    include_anomalies: bool,
) -> list[str]:
    """
    Core generator function.  Returns a list of formatted log line strings.
    """

    levels = []
    for level, weight in level_dist.items():
        levels.extend([level] * weight)
    if not levels:
        levels = ["INFO"] * 100

    ip_pool = RANDOM_IPS if use_random_ips else (predefined_ips or RANDOM_IPS)

    base_time = datetime.now() - timedelta(minutes=num_entries * interval_sec // 60)

    lines = []

    high_traffic_ip = random.choice(ip_pool) if include_anomalies else None

    hot_ips = random.sample(ip_pool, min(3, len(ip_pool)))

    for i in range(num_entries):
        ts    = _random_timestamp(base_time, num_entries, interval_sec, i)
        level = random.choice(levels)

        if include_anomalies and random.random() < 0.30:
            level = "ERROR"
            ip    = high_traffic_ip
        elif random.random() < 0.25:
            ip = random.choice(hot_ips)
        else:
            ip = random.choice(ip_pool)

        msg_pool = (custom_messages.get(level) or []) + MESSAGES[level]
        msg_tmpl = random.choice(msg_pool)
        msg = msg_tmpl.replace("{ip}", ip).replace("{n}", str(random.randint(1, 5)))

        if ip and ip not in msg:
            msg += f" from {ip}"

        lines.append(f"{ts} {level} {msg}")

    return lines


class GeneratorWindow(tk.Toplevel):
    """
    A Toplevel window (child of main app) for configuring log generation.
    After "Generate", writes the file and optionally triggers a callback
    so main.py can auto-load the new file.
    """

    def __init__(self, parent, on_generated_callback=None):
        super().__init__(parent)
        self.title("Test Log Generator")
        self.geometry("460x560")
        self.resizable(False, False)
        self.on_generated_callback = on_generated_callback

        self._build_ui()

    def _build_ui(self):
        pad = {"padx": 10, "pady": 5}

        tk.Label(self, text="🛠  Test Log Generator", font=("Arial", 14, "bold")).pack(pady=10)

        frame1 = tk.LabelFrame(self, text="Log Volume", padx=8, pady=5)
        frame1.pack(fill="x", **pad)

        tk.Label(frame1, text="Number of log entries:").grid(row=0, column=0, sticky="w")
        self.num_entries_var = tk.IntVar(value=100)
        tk.Spinbox(frame1, from_=10, to=5000, textvariable=self.num_entries_var, width=8).grid(row=0, column=1, sticky="w", padx=5)

        tk.Label(frame1, text="Time interval between logs (seconds):").grid(row=1, column=0, sticky="w")
        self.interval_var = tk.IntVar(value=5)
        tk.Spinbox(frame1, from_=1, to=300, textvariable=self.interval_var, width=8).grid(row=1, column=1, sticky="w", padx=5)

        frame2 = tk.LabelFrame(self, text="Log Level Distribution (%)", padx=8, pady=5)
        frame2.pack(fill="x", **pad)

        self.info_var    = tk.IntVar(value=60)
        self.warning_var = tk.IntVar(value=25)
        self.error_var   = tk.IntVar(value=15)

        for row, (label, var) in enumerate([
            ("INFO %",    self.info_var),
            ("WARNING %", self.warning_var),
            ("ERROR %",   self.error_var),
        ]):
            tk.Label(frame2, text=label, width=12, anchor="w").grid(row=row, column=0, sticky="w")
            tk.Spinbox(frame2, from_=0, to=100, textvariable=var, width=8).grid(row=row, column=1, sticky="w", padx=5)

        frame3 = tk.LabelFrame(self, text="IP Address Options", padx=8, pady=5)
        frame3.pack(fill="x", **pad)

        self.use_random_ip_var = tk.BooleanVar(value=True)
        tk.Checkbutton(frame3, text="Use random IPs", variable=self.use_random_ip_var,
                       command=self._toggle_ip_field).grid(row=0, column=0, sticky="w")

        tk.Label(frame3, text="Predefined IPs (comma-separated):").grid(row=1, column=0, sticky="w")
        self.ip_entry = tk.Entry(frame3, width=35, state="disabled")
        self.ip_entry.insert(0, "10.0.0.1, 10.0.0.2, 192.168.1.5")
        self.ip_entry.grid(row=2, column=0, sticky="w", pady=3)

        frame4 = tk.LabelFrame(self, text="Custom ERROR Messages (one per line, optional)", padx=8, pady=5)
        frame4.pack(fill="x", **pad)

        self.custom_msg_text = tk.Text(frame4, height=3, width=48)
        self.custom_msg_text.pack()

        frame5 = tk.LabelFrame(self, text="Anomaly Injection", padx=8, pady=5)
        frame5.pack(fill="x", **pad)

        self.anomaly_var = tk.BooleanVar(value=False)
        tk.Checkbutton(frame5,
                       text="Inject anomalies (high-traffic IP + repeated errors)",
                       variable=self.anomaly_var).pack(anchor="w")

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Generate & Save", width=18, command=self._generate).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Cancel", width=10, command=self.destroy).pack(side="left", padx=5)


    def _toggle_ip_field(self):
        """Enable/disable manual IP entry based on checkbox."""
        if self.use_random_ip_var.get():
            self.ip_entry.config(state="disabled")
        else:
            self.ip_entry.config(state="normal")


    def _generate(self):
        """Reads form values, generates logs, saves to user-chosen file."""
        num      = self.num_entries_var.get()
        interval = self.interval_var.get()

        level_dist = {
            "INFO":    self.info_var.get(),
            "WARNING": self.warning_var.get(),
            "ERROR":   self.error_var.get(),
        }

        use_random = self.use_random_ip_var.get()
        raw_ips    = self.ip_entry.get()
        predefined = [ip.strip() for ip in raw_ips.split(",") if ip.strip()]

        raw_msgs = self.custom_msg_text.get("1.0", "end").strip()
        custom_messages = {}
        if raw_msgs:
            custom_messages["ERROR"] = [m for m in raw_msgs.splitlines() if m.strip()]

        anomalies = self.anomaly_var.get()

        save_path = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")],
            initialfile="generated_test.log",
        )
        if not save_path:
            return  

        lines = generate_logs(num, level_dist, use_random, predefined, custom_messages, interval, anomalies)

        with open(save_path, "w") as f:
            f.write("\n".join(lines))

        messagebox.showinfo("Done", f"{num} log entries saved to:\n{save_path}")

        if self.on_generated_callback:
            self.on_generated_callback(save_path)

        self.destroy()