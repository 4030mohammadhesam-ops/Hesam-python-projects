
import customtkinter as ctk
import psutil
import platform
import time
import shutil
import subprocess
import socket
from datetime import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ================= CONFIGURATION =================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BG = "#090F1E"
SIDEBAR = "#10192B"
CARD = "#151F33"
ACCENT = "#38BDF8"
GREEN = "#22C55E"
ORANGE = "#F59E0B"
PURPLE = "#A78BFA"
RED = "#EF4444"
TEXT = "#F1F5F9"
MUTED = "#94A3B8"

REFRESH_MS = 1500


# ================= MAIN APPLICATION =================

class PCMonitorPro(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("PC Monitor Pro 2.0")
        self.geometry("1200x780")
        self.minsize(950, 650)
        self.configure(fg_color=BG)

        self.running = True
        self.current_page = "Dashboard"

        self.last_net = psutil.net_io_counters()
        self.last_net_time = time.time()

        self.cpu_history = [0] * 30
        self.ram_history = [0] * 30

        self.process_widgets = []

        # Initialize CPU measurement
        psutil.cpu_percent(interval=None)

        self.create_sidebar()

        self.content = ctk.CTkFrame(
            self,
            fg_color=BG,
            corner_radius=0
        )
        self.content.pack(
            side="right",
            fill="both",
            expand=True
        )

        self.show_dashboard()
        self.update_data()

        self.protocol("WM_DELETE_WINDOW", self.close_app)

    # ================= SIDEBAR =================

    def create_sidebar(self):

        self.sidebar = ctk.CTkFrame(
            self,
            width=215,
            fg_color=SIDEBAR,
            corner_radius=0
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        ctk.CTkLabel(
            self.sidebar,
            text="PC MONITOR",
            font=("Segoe UI", 21, "bold"),
            text_color=ACCENT
        ).pack(pady=(30, 5))

        ctk.CTkLabel(
            self.sidebar,
            text="SYSTEM CONTROL CENTER",
            font=("Segoe UI", 9),
            text_color=MUTED
        ).pack(pady=(0, 35))

        self.nav_buttons = {}

        items = [
            ("Dashboard", "▦"),
            ("Processes", "◈"),
            ("System Info", "⚙")
        ]

        for name, symbol in items:

            btn = ctk.CTkButton(
                self.sidebar,
                text=f"   {symbol}   {name}",
                anchor="w",
                height=45,
                corner_radius=10,
                fg_color="transparent",
                hover_color="#253650",
                text_color=TEXT,
                font=("Segoe UI", 14),
                command=lambda n=name: self.navigate(n)
            )

            btn.pack(fill="x", padx=15, pady=5)
            self.nav_buttons[name] = btn

        ctk.CTkLabel(
            self.sidebar,
            text="PC MONITOR PRO 2.0\nLightweight Edition",
            font=("Segoe UI", 10),
            text_color=MUTED
        ).pack(side="bottom", pady=25)

    # ================= NAVIGATION =================

    def navigate(self, page):

        self.current_page = page

        for name, btn in self.nav_buttons.items():
            btn.configure(
                fg_color="#1E3A5F" if name == page else "transparent"
            )

        for widget in self.content.winfo_children():
            widget.destroy()

        if page == "Dashboard":
            self.show_dashboard()

        elif page == "Processes":
            self.show_processes()

        elif page == "System Info":
            self.show_system_info()

    # ================= HEADER =================

    def create_header(self, title, subtitle):

        header = ctk.CTkFrame(
            self.content,
            fg_color="transparent"
        )
        header.pack(fill="x", padx=25, pady=(25, 15))

        ctk.CTkLabel(
            header,
            text=title,
            font=("Segoe UI", 27, "bold"),
            text_color=TEXT
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text=subtitle,
            font=("Segoe UI", 12),
            text_color=MUTED
        ).pack(anchor="w", pady=(3, 0))

        self.clock = ctk.CTkLabel(
            header,
            text="",
            font=("Segoe UI", 12),
            text_color=ACCENT
        )
        self.clock.pack(anchor="e")

    # ================= DASHBOARD =================

    def show_dashboard(self):

        self.create_header(
            "Dashboard",
            "Real-time system performance monitoring"
        )

        self.dashboard = ctk.CTkScrollableFrame(
            self.content,
            fg_color="transparent"
        )
        self.dashboard.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=5
        )

        self.dashboard.grid_columnconfigure(
            (0, 1), weight=1
        )

        self.cpu_card = self.create_metric_card(
            "CPU USAGE", ACCENT, 0, 0
        )

        self.ram_card = self.create_metric_card(
            "RAM USAGE", GREEN, 0, 1
        )

        self.gpu_card = self.create_metric_card(
            "GPU STATUS", PURPLE, 1, 0
        )

        self.disk_card = self.create_metric_card(
            "DISK USAGE", ORANGE, 1, 1
        )

        self.network_card = self.create_card(
            self.dashboard,
            "NETWORK ACTIVITY",
            2,
            0,
            2
        )

        self.network_label = ctk.CTkLabel(
            self.network_card,
            text="Download: 0 KB/s     Upload: 0 KB/s",
            font=("Segoe UI", 14),
            text_color=TEXT
        )
        self.network_label.pack(anchor="w", padx=18, pady=15)

        self.graph_card = self.create_card(
            self.dashboard,
            "LIVE PERFORMANCE GRAPH",
            3,
            0,
            2
        )

        self.create_graph()

        self.refresh_button = ctk.CTkButton(
            self.dashboard,
            text="Refresh Data",
            command=self.refresh_now,
            fg_color="#1D4ED8",
            hover_color="#2563EB",
            height=38
        )
        self.refresh_button.grid(
            row=4, column=0, columnspan=2,
            sticky="ew", padx=10, pady=15
        )

    # ================= METRIC CARDS =================

    def create_card(self, parent, title, row, column, span=1):

        card = ctk.CTkFrame(
            parent,
            fg_color=CARD,
            corner_radius=15
        )

        card.grid(
            row=row,
            column=column,
            columnspan=span,
            padx=8,
            pady=8,
            sticky="nsew"
        )

        ctk.CTkLabel(
            card,
            text=title,
            font=("Segoe UI", 13, "bold"),
            text_color=MUTED
        ).pack(anchor="w", padx=18, pady=(15, 5))

        return card

    def create_metric_card(self, title, color, row, column):

        card = self.create_card(
            self.dashboard, title, row, column
        )

        value = ctk.CTkLabel(
            card,
            text="--",
            font=("Segoe UI", 30, "bold"),
            text_color=color
        )
        value.pack(anchor="w", padx=18)

        progress = ctk.CTkProgressBar(
            card,
            height=10,
            progress_color=color,
            fg_color="#26334D"
        )
        progress.pack(fill="x", padx=18, pady=12)
        progress.set(0)

        detail = ctk.CTkLabel(
            card,
            text="Collecting data...",
            font=("Segoe UI", 11),
            text_color=MUTED
        )
        detail.pack(anchor="w", padx=18, pady=(0, 15))

        return {
            "value": value,
            "progress": progress,
            "detail": detail
        }

    # ================= GRAPH =================

    def create_graph(self):

        self.figure = Figure(
            figsize=(7, 2.2),
            dpi=85,
            facecolor=CARD
        )

        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor(CARD)

        self.ax.set_ylim(0, 100)
        self.ax.set_xlim(0, 29)

        self.ax.set_ylabel(
            "Usage %",
            color=MUTED
        )

        self.ax.tick_params(
            colors=MUTED,
            labelsize=8
        )

        self.ax.grid(
            True,
            alpha=0.15
        )

        self.cpu_line, = self.ax.plot(
            self.cpu_history,
            color=ACCENT,
            linewidth=2,
            label="CPU"
        )

        self.ram_line, = self.ax.plot(
            self.ram_history,
            color=GREEN,
            linewidth=2,
            label="RAM"
        )

        self.ax.legend(
            facecolor=CARD,
            labelcolor=TEXT,
            fontsize=8
        )

        self.figure.tight_layout()

        self.canvas = FigureCanvasTkAgg(
            self.figure,
            master=self.graph_card
        )

        self.canvas.get_tk_widget().pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

    def update_graph(self, cpu, ram):

        if not hasattr(self, "cpu_line"):
            return

        self.cpu_history.append(cpu)
        self.ram_history.append(ram)

        self.cpu_history = self.cpu_history[-30:]
        self.ram_history = self.ram_history[-30:]

        self.cpu_line.set_ydata(self.cpu_history)
        self.ram_line.set_ydata(self.ram_history)

        self.canvas.draw_idle()

    # ================= PROCESSES =================

    def show_processes(self):

        self.create_header(
            "Processes",
            "Applications currently running on your computer"
        )

        self.process_page = ctk.CTkScrollableFrame(
            self.content,
            fg_color="transparent"
        )
        self.process_page.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        top = ctk.CTkFrame(
            self.process_page,
            fg_color=CARD,
            corner_radius=12
        )
        top.pack(fill="x", pady=8)

        self.process_count = ctk.CTkLabel(
            top,
            text="Running processes",
            text_color=ACCENT,
            font=("Segoe UI", 14, "bold")
        )
        self.process_count.pack(
            anchor="w",
            padx=15,
            pady=12
        )

        self.process_container = ctk.CTkFrame(
            self.process_page,
            fg_color="transparent"
        )
        self.process_container.pack(
            fill="both",
            expand=True
        )

        self.update_process_list()

    def update_process_list(self):

        if self.current_page != "Processes":
            return

        for widget in self.process_container.winfo_children():
            widget.destroy()

        processes = []

        for proc in psutil.process_iter(
            ["pid", "name", "memory_info", "cpu_percent"]
        ):
            try:
                info = proc.info

                memory = info["memory_info"]
                memory_mb = (
                    memory.rss / (1024 * 1024)
                    if memory else 0
                )

                processes.append({
                    "pid": info["pid"],
                    "name": info["name"] or "Unknown",
                    "memory": memory_mb,
                    "cpu": info["cpu_percent"] or 0
                })

            except (psutil.NoSuchProcess,
                    psutil.AccessDenied,
                    psutil.ZombieProcess):
                continue

        processes.sort(
            key=lambda x: x["memory"],
            reverse=True
        )

        self.process_count.configure(
            text=f"Running processes: {len(processes)}"
        )

        header = ctk.CTkFrame(
            self.process_container,
            fg_color="#1E293B",
            corner_radius=8
        )
        header.pack(fill="x", pady=5)

        for text in ["PID", "PROCESS", "CPU %", "RAM MB"]:
            ctk.CTkLabel(
                header,
                text=text,
                font=("Segoe UI", 11, "bold"),
                text_color=ACCENT,
                width=110
            ).pack(side="left", padx=5, pady=12)

        for proc in processes[:25]:

            row = ctk.CTkFrame(
                self.process_container,
                fg_color=CARD,
                corner_radius=7
            )
            row.pack(fill="x", pady=3)

            values = [
                str(proc["pid"]),
                proc["name"][:22],
                f'{proc["cpu"]:.1f}%',
                f'{proc["memory"]:.1f}'
            ]

            for value in values:

                ctk.CTkLabel(
                    row,
                    text=value,
                    font=("Segoe UI", 11),
                    text_color=TEXT,
                    width=110,
                    anchor="w"
                ).pack(side="left", padx=5, pady=10)

        self.after(5000, self.update_process_list)

    # ================= SYSTEM INFO =================

    def show_system_info(self):

        self.create_header(
            "System Information",
            "Hardware and operating system details"
        )

        info_page = ctk.CTkScrollableFrame(
            self.content,
            fg_color="transparent"
        )
        info_page.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=10
        )

        details = [
            ("Operating System",
             f"{platform.system()} {platform.release()}"),

            ("Processor",
             platform.processor() or "Unknown"),

            ("Architecture",
             platform.machine()),

            ("Logical CPU Cores",
             str(psutil.cpu_count(logical=True))),

            ("Physical CPU Cores",
             str(psutil.cpu_count(logical=False))),

            ("CPU Frequency",
             self.get_cpu_frequency()),

            ("Total RAM",
             f"{psutil.virtual_memory().total / (1024**3):.2f} GB"),

            ("Hostname",
             socket.gethostname()),

            ("Boot Time",
             datetime.fromtimestamp(
                 psutil.boot_time()
             ).strftime("%Y-%m-%d %H:%M:%S")),

            ("Python Version",
             platform.python_version()),

            ("GPU",
             self.get_gpu_info()),

            ("Temperature",
             self.get_temperature())
        ]

        for title, value in details:

            card = ctk.CTkFrame(
                info_page,
                fg_color=CARD,
                corner_radius=10
            )
            card.pack(fill="x", pady=5)

            ctk.CTkLabel(
                card,
                text=title,
                font=("Segoe UI", 12, "bold"),
                text_color=ACCENT
            ).pack(anchor="w", padx=15, pady=(10, 2))

            ctk.CTkLabel(
                card,
                text=value,
                font=("Segoe UI", 12),
                text_color=TEXT,
                wraplength=850,
                justify="left"
            ).pack(anchor="w", padx=15, pady=(2, 10))

    # ================= HARDWARE HELPERS =================

    def get_cpu_frequency(self):

        try:
            freq = psutil.cpu_freq()

            if freq:
                return f"{freq.current:.0f} MHz"

        except Exception:
            pass

        return "Unavailable"

    def get_gpu_info(self):

        if not shutil.which("nvidia-smi"):
            return "GPU details unavailable (NVIDIA driver tool not found)"

        try:
            result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=name",
                    "--format=csv,noheader"
                ],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode == 0:
                return result.stdout.strip() or "Unknown GPU"

        except Exception:
            pass

        return "GPU information unavailable"

    def get_temperature(self):

        try:
            temperatures = psutil.sensors_temperatures()

            if temperatures:
                for name, entries in temperatures.items():
                    if entries:
                        entry = entries[0]
                        return f"{name}: {entry.current} °C"

        except Exception:
            pass

        return "Not supported by this system"

    # ================= LIVE DATA =================

    def update_data(self):

        if not self.running:
            return

        try:
            cpu = psutil.cpu_percent(interval=None)

            memory = psutil.virtual_memory()
            ram = memory.percent

            if self.current_page == "Dashboard":

                # CPU
                self.cpu_card["value"].configure(
                    text=f"{cpu:.1f}%"
                )

                self.cpu_card["progress"].set(
                    cpu / 100
                )

                self.cpu_card["detail"].configure(
                    text=f"{psutil.cpu_count()} logical processors | "
                         f"{self.get_cpu_frequency()}"
                )

                # RAM
                self.ram_card["value"].configure(
                    text=f"{ram:.1f}%"
                )

                self.ram_card["progress"].set(
                    ram / 100
                )

                self.ram_card["detail"].configure(
                    text=f"{memory.used / (1024**3):.2f} GB used / "
                         f"{memory.total / (1024**3):.2f} GB total"
                )

                # GPU
                gpu_text = self.get_gpu_info()

                self.gpu_card["value"].configure(
                    text="Available" if gpu_text !=
                    "GPU details unavailable (NVIDIA driver tool not found)"
                    else "N/A",
                    font=("Segoe UI", 22, "bold")
                )

                self.gpu_card["detail"].configure(
                    text=gpu_text[:55]
                )

                self.gpu_card["progress"].set(0)

                # DISK
                try:
                    disk = psutil.disk_usage("C:\\")
                    disk_percent = disk.percent

                    self.disk_card["value"].configure(
                        text=f"{disk_percent:.1f}%"
                    )

                    self.disk_card["progress"].set(
                        disk_percent / 100
                    )

                    self.disk_card["detail"].configure(
                        text=f"{disk.free / (1024**3):.1f} GB free on C:"
                    )

                except Exception:
                    self.disk_card["detail"].configure(
                        text="Disk information unavailable"
                    )

                # NETWORK
                now = time.time()
                net = psutil.net_io_counters()
                elapsed = max(now - self.last_net_time, 0.001)

                download = (
                    net.bytes_recv - self.last_net.bytes_recv
                ) / elapsed / 1024

                upload = (
                    net.bytes_sent - self.last_net.bytes_sent
                ) / elapsed / 1024

                self.last_net = net
                self.last_net_time = now

                self.network_label.configure(
                    text=f"Download: {download:.1f} KB/s     "
                         f"Upload: {upload:.1f} KB/s"
                )

                self.update_graph(cpu, ram)

            self.clock.configure(
                text=datetime.now().strftime(
                    "%Y-%m-%d  |  %H:%M:%S"
                )
            )

        except Exception as error:
            print("Monitoring error:", error)

        self.after(REFRESH_MS, self.update_data)

    # ================= REFRESH =================

    def refresh_now(self):

        self.last_net = psutil.net_io_counters()
        self.last_net_time = time.time()

        self.update_data()

    # ================= CLOSE =================

    def close_app(self):

        self.running = False
        self.destroy()


# ================= START =================

if __name__ == "__main__":

    app = PCMonitorPro()
    app.mainloop()
