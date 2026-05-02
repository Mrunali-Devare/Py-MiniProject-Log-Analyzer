import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import csv

# my modules
from parser import parse_logs
from analyzer import analyze_logs
from visualizer import plot_bar, plot_pie, plot_time_series
from log_generator import GeneratorWindow


BG       = "#1e1e2e"
FG       = "#cdd6f4"
ACCENT   = "#89b4fa"
BTN_BG   = "#313244"
ERR_CLR  = "#f38ba8"
WARN_CLR = "#fab387"
OK_CLR   = "#a6e3a1"

# Main Window or GUI
class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Log Analyzer Pro")
        self.root.geometry("1100x700")
        self.root.configure(bg=BG)

        self.logs   = []       # all parsed logs
        self.result = {}       # analysis output

        self._build_toolbar()
        self._build_filter_bar()
        self._build_table()
        self._build_summary()
        self._build_chart_buttons()


    def _build_toolbar(self):
        """Top row: Upload, Generate, Export buttons."""

        bar = tk.Frame(self.root, bg=BG)
        bar.pack(fill="x", padx=10, pady=8)

        self._btn(bar, "Upload Log File",    self.load_file).pack(side="left", padx=4)
        self._btn(bar, "Generate Test Logs", self.open_generator).pack(side="right", padx=4)
        self._btn(bar, "Export TXT",         self.export_txt).pack(side="right", padx=4)
        self._btn(bar, "Export CSV",         self.export_csv).pack(side="right", padx=4)


    def _build_filter_bar(self):
        """Row of search/filter controls."""
        bar = tk.Frame(self.root, bg=BG)
        bar.pack(fill="x", padx=10, pady=2)

        tk.Label(bar, text="Filter by Level:", bg=BG, fg=FG).pack(side="left")
        self.level_var = tk.StringVar(value="ALL")
        level_menu = ttk.Combobox(bar, textvariable=self.level_var,
                                  values=["ALL", "INFO", "WARNING", "ERROR"],
                                  width=10, state="readonly")
        level_menu.pack(side="left", padx=4)
        level_menu.bind("<<ComboboxSelected>>", lambda _: self._apply_filter())

        tk.Label(bar, text="  Filter by IP:", bg=BG, fg=FG).pack(side="left")
        self.ip_var = tk.StringVar()
        ip_entry = tk.Entry(bar, textvariable=self.ip_var, width=18, bg=BTN_BG, fg=FG,
                            insertbackground=FG)
        ip_entry.pack(side="left", padx=4)
        ip_entry.bind("<KeyRelease>", lambda _: self._apply_filter())

        self._btn(bar, "Reset Filters", self._reset_filter).pack(side="left", padx=8)


    def _build_table(self):
        """Treeview table for log entries."""
        cols = ("Time", "Level", "Message", "IP")

        frame = tk.Frame(self.root, bg=BG)
        frame.pack(expand=True, fill="both", padx=10)

        style = ttk.Style()
        style.configure("Treeview",
                         background=BTN_BG, foreground=FG,
                         fieldbackground=BTN_BG, rowheight=22)
        style.configure("Treeview.Heading", background=BG, foreground=BG)

        self.tree = ttk.Treeview(frame, columns=cols, show="headings")
        col_widths = {"Time": 155, "Level": 75, "Message": 580, "IP": 130}
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=col_widths[col])

        self.tree.tag_configure("ERROR",   foreground=ERR_CLR)
        self.tree.tag_configure("WARNING", foreground=WARN_CLR)
        self.tree.tag_configure("INFO",    foreground=OK_CLR)

        scroll = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.tree.pack(expand=True, fill="both")


    def _build_summary(self):
        """Label area showing analysis results."""
        self.summary_var = tk.StringVar(value="Load a log file to see analysis.")
        lbl = tk.Label(self.root, textvariable=self.summary_var,
                       bg=BG, fg=FG, font=("Consolas", 9),
                       justify="left", anchor="w", wraplength=1080)
        lbl.pack(fill="x", padx=12, pady=4)


    def _build_chart_buttons(self):
        """Bottom row of chart buttons + time-axis toggle."""
        bar = tk.Frame(self.root, bg=BG)
        bar.pack(pady=6)

        self._btn(bar, "Level Bar Chart",
                  lambda: plot_bar(self.result.get("level_count", {}))).pack(side="left", padx=5)
        self._btn(bar, "Level Pie Chart",
                  lambda: plot_pie(self.result.get("level_count", {}))).pack(side="left", padx=5)

        # ── Time-series section ──────────────────────────────────────────────
        self._btn(bar, "Activity Over Time",
                  self._plot_time_series).pack(side="left", padx=5)

        # Radio toggle: Hours / Minutes
        self.time_axis_var = tk.StringVar(value="hour")
        toggle_frame = tk.Frame(bar, bg=BG)
        toggle_frame.pack(side="left", padx=4)
        for label, val in (("Hours", "hour"), ("Mins", "minute")):
            tk.Radiobutton(
                toggle_frame, text=label, variable=self.time_axis_var, value=val,
                bg=BG, fg=FG, selectcolor=BTN_BG, activebackground=BG,
                activeforeground=ACCENT, font=("Consolas", 8),
            ).pack(side="left")


    def _plot_time_series(self):
        """Plot time series using the currently selected axis granularity."""
        mode = self.time_axis_var.get()          # "hour" or "minute"
        key  = "time_series_hour" if mode == "hour" else "time_series_min"
        plot_time_series(self.result.get(key, {}), mode=mode)


    def _btn(self, parent, text, cmd):
        return tk.Button(parent, text=text, command=cmd,
                         bg=BTN_BG, fg=FG, activebackground=ACCENT,
                         relief="flat", padx=10, pady=4, cursor="hand2")


    def load_file(self, path: str = None):
        """Parse a log file, analyze it, and refresh the UI."""
        if not path:
            path = filedialog.askopenfilename(
                filetypes=[("Log / Text files", "*.log *.txt"), ("All files", "*.*")]
            )
        if not path:
            return

        self.logs   = parse_logs(path)
        self.result = analyze_logs(self.logs)
        self._refresh_table(self.logs)
        self._refresh_summary()


    def _refresh_table(self, logs_to_show: list):
        """Clear and repopulate the Treeview from a list of log dicts."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        for log in logs_to_show:
            tag = log["level"] if log["level"] in ("INFO", "WARNING", "ERROR") else ""
            self.tree.insert("", "end",
                             values=(log["timestamp"], log["level"], log["message"], log["ip"] or "–"),
                             tags=(tag,))


    def _refresh_summary(self):
        """Build the summary text from self.result and update the label."""
        r = self.result
        if not r:
            return

        lc  = r["level_count"]
        lvl = "  |  ".join(f"{k}: {v}" for k, v in lc.items())

        anomaly_txt  = "ANOMALY DETECTED (ERROR > 40%)" if r["anomaly_detected"] else "No anomaly"
        ht_txt       = ", ".join(r["high_traffic_ips"]) or "None"
        re_txt       = ", ".join(r["repeated_error_ips"]) or "None"
        susp_txt     = ", ".join(r["suspicious_ips"]) or "None"

        text = (
            f"Total: {r['total']}   |   {lvl}   |   Severity Score: {r['severity_score']}   |   {anomaly_txt}\n"
            f"Suspicious IPs: {susp_txt}\nHigh-Traffic IPs: {ht_txt}\nRepeated-Error IPs: {re_txt}"
        )
        self.summary_var.set(text)


    def _apply_filter(self):
        """Filter self.logs by selected level and IP substring, refresh table."""
        level_filter = self.level_var.get()
        ip_filter    = self.ip_var.get().strip()

        filtered = self.logs

        if level_filter != "ALL":
            filtered = [l for l in filtered if l["level"] == level_filter]

        if ip_filter:
            filtered = [l for l in filtered if l["ip"] and ip_filter in l["ip"]]

        self._refresh_table(filtered)


    def _reset_filter(self):
        self.level_var.set("ALL")
        self.ip_var.set("")
        self._refresh_table(self.logs)


    def _report_lines(self) -> list[str]:
        """Build a plain-text report as a list of strings."""
        r = self.result
        if not r:
            return ["No data loaded."]

        lines = [
            "=" * 50,
            "         LOG ANALYZER REPORT",
            "=" * 50,
            f"Total Logs    : {r['total']}",
            "",
            "Level Counts:",
        ]
        for level, count in r["level_count"].items():
            lines.append(f"  {level:<10}: {count}")

        lines += [
            "",
            f"Severity Score       : {r['severity_score']}",
            f"Anomaly Detected     : {'YES ' if r['anomaly_detected'] else 'No'}",
            "",
            f"Suspicious IPs       : {', '.join(r['suspicious_ips']) or 'None'}",
            f"High-Traffic IPs     : {', '.join(r['high_traffic_ips']) or 'None'}",
            f"Repeated-Error IPs   : {', '.join(r['repeated_error_ips']) or 'None'}",
            "=" * 50,
        ]
        return lines


    def export_txt(self):
        """Save analysis report as a plain text file."""
        if not self.result:
            messagebox.showwarning("No Data", "Please load a log file first.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            initialfile="log_report.txt",
        )
        if not path:
            return

        with open(path, "w") as f:
            f.write("\n".join(self._report_lines()))

        messagebox.showinfo("Exported", f"Report saved to:\n{path}")


    def export_csv(self):
        """Save all parsed log entries as a CSV file."""
        if not self.logs:
            messagebox.showwarning("No Data", "Please load a log file first.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="logs_export.csv",
        )
        if not path:
            return

        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["timestamp", "level", "message", "ip"])
            writer.writeheader()
            writer.writerows(self.logs)

        messagebox.showinfo("Exported", f"CSV saved to:\n{path}")


    def open_generator(self):
        """Open the log generator window; auto-load the file when done."""
        GeneratorWindow(self.root, on_generated_callback=self.load_file)


if __name__ == "__main__":
    root = tk.Tk()
    app  = App(root)
    root.mainloop()