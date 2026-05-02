import matplotlib.pyplot as plt
import numpy as np


def plot_bar(level_count):
    """Bar chart – count of each log level (INFO / WARNING / ERROR)."""
    plt.figure(figsize=(6, 4))
    colors = []
    for key in level_count.keys():
        if key == "ERROR":
            colors.append("#e74c3c")
        elif key == "WARNING":
            colors.append("#f39c12")
        else:
            colors.append("#2ecc71")

    plt.bar(level_count.keys(), level_count.values(), color=colors)
    plt.title("Log Level Distribution")
    plt.xlabel("Level")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.show()


def plot_pie(level_count):
    """Pie chart – proportion of each log level with annotated labels."""
    labels = list(level_count.keys())
    sizes  = list(level_count.values())

    fig, ax = plt.subplots(figsize=(6, 5))
    wedges, texts = ax.pie(sizes, startangle=90)

    for i, wedge in enumerate(wedges):
        angle = (wedge.theta2 - wedge.theta1) / 2 + wedge.theta1
        x = wedge.r * 1.2 * np.cos(np.deg2rad(angle))
        y = wedge.r * 1.2 * np.sin(np.deg2rad(angle))

        ax.annotate(
            f"{labels[i]} ({sizes[i]} – {sizes[i] / sum(sizes) * 100:.1f}%)",
            xy=(np.cos(np.deg2rad(angle)), np.sin(np.deg2rad(angle))),
            xytext=(x, y),
            arrowprops=dict(arrowstyle="->"),
        )

    ax.set_title("Log Distribution (Pie View)")
    plt.tight_layout()
    plt.show()


def plot_time_series(time_series, mode="hour"):
    """
    Line chart – log entries over time.
    mode: 'hour'   -> keys are 'YYYY-MM-DD HH', labels show only HH
          'minute' -> keys are 'YYYY-MM-DD HH:MM', labels show HH:MM
    """
    if not time_series:
        return

    sorted_items = sorted(time_series.items())
    times  = [item[0] for item in sorted_items]
    counts = [item[1] for item in sorted_items]

    if mode == "hour":
        tick_labels = [t[-2:]    for t in times]   # "HH"
        title  = "Log Activity Over Time (per Hour)"
        xlabel = "Hour"
        rotation, fontsize = 0, 9
    else:
        tick_labels = [t[-5:]    for t in times]   # "HH:MM"
        title  = "Log Activity Over Time (per Minute)"
        xlabel = "Time (HH:MM)"
        rotation, fontsize = 45, 7

    plt.figure(figsize=(10, 4))
    plt.plot(range(len(times)), counts, marker="o", color="#3498db", linewidth=2)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel("Log Count")
    plt.xticks(ticks=range(len(times)), labels=tick_labels,
               rotation=rotation, ha="right" if rotation else "center", fontsize=fontsize)
    plt.tight_layout()
    plt.show()