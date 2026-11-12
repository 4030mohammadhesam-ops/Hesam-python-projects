
import cv2
import time
import os
import customtkinter as ctk

from pathlib import Path
from datetime import datetime
from PIL import Image


# ==========================================
# CONFIGURATION
# ==========================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

APP_NAME = "CAMERA VISION"

BG = "#0B1020"
PANEL = "#131B2E"
CARD = "#1A2540"
ACCENT = "#5B8CFF"
GREEN = "#22C58B"
RED = "#E05260"
TEXT = "#F0F4FF"
MUTED = "#8996B3"

BASE_DIR = Path(__file__).resolve().parent
SAVE_DIR = BASE_DIR / "Camera_Records"
PHOTO_DIR = SAVE_DIR / "Photos"
VIDEO_DIR = SAVE_DIR / "Videos"

for folder in (PHOTO_DIR, VIDEO_DIR):
    folder.mkdir(parents=True, exist_ok=True)


# ==========================================
# MAIN APPLICATION
# ==========================================

class CameraVision(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title(APP_NAME)
        self.geometry("1150x750")
        self.minsize(950, 650)
        self.configure(fg_color=BG)

        self.cap = None
        self.running = False
        self.after_id = None

        self.video_writer = None
        self.recording = False

        self.current_frame = None
        self.preview_image = None

        self.previous_gray = None
        self.motion_count = 0
        self.motion_active = False

        self.last_motion_time = 0
        self.last_frame_time = time.perf_counter()
        self.fps = 0

        self.brightness = 0
        self.motion_enabled = True

        self.create_interface()

        self.protocol(
            "WM_DELETE_WINDOW",
            self.close_application
        )

    # ======================================
    # INTERFACE
    # ======================================

    def create_interface(self):

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.create_header()
        self.create_sidebar()
        self.create_workspace()

    def create_header(self):

        header = ctk.CTkFrame(
            self,
            height=75,
            corner_radius=0,
            fg_color=PANEL
        )

        header.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="ew"
        )

        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header,
            text="◉ CAMERA VISION",
            font=("Segoe UI", 22, "bold"),
            text_color=ACCENT
        ).grid(
            row=0,
            column=0,
            padx=25,
            pady=20
        )

        self.system_status = ctk.CTkLabel(
            header,
            text="CAMERA OFFLINE",
            font=("Segoe UI", 11, "bold"),
            text_color=RED
        )

        self.system_status.grid(
            row=0,
            column=2,
            padx=25
        )

    def create_sidebar(self):

        sidebar = ctk.CTkFrame(
            self,
            width=260,
            corner_radius=0,
            fg_color=PANEL
        )

        sidebar.grid(
            row=1,
            column=0,
            sticky="nsew"
        )

        sidebar.grid_propagate(False)

        ctk.CTkLabel(
            sidebar,
            text="CAMERA CONTROL",
            font=("Segoe UI", 14, "bold"),
            text_color=TEXT
        ).pack(pady=(25, 15))

        self.add_button(
            sidebar,
            "Start Camera",
            self.start_camera,
            GREEN
        )

        self.add_button(
            sidebar,
            "Stop Camera",
            self.stop_camera,
            RED
        )

        ctk.CTkLabel(
            sidebar,
            text="CAMERA TOOLS",
            font=("Segoe UI", 12, "bold"),
            text_color=MUTED
        ).pack(anchor="w", padx=18, pady=(25, 10))

        self.add_button(
            sidebar,
            "Take Screenshot",
            self.take_screenshot
        )

        self.add_button(
            sidebar,
            "Start / Stop Recording",
            self.toggle_recording
        )

        self.add_button(
            sidebar,
            "Motion Detection",
            self.toggle_motion
        )

        ctk.CTkLabel(
            sidebar,
            text="BRIGHTNESS",
            font=("Segoe UI", 12, "bold"),
            text_color=MUTED
        ).pack(anchor="w", padx=18, pady=(25, 8))

        self.brightness_slider = ctk.CTkSlider(
            sidebar,
            from_=-50,
            to=50,
            number_of_steps=100,
            command=self.change_brightness
        )

        self.brightness_slider.set(0)

        self.brightness_slider.pack(
            fill="x",
            padx=20,
            pady=5
        )

        self.brightness_value = ctk.CTkLabel(
            sidebar,
            text="0",
            text_color=TEXT
        )

        self.brightness_value.pack(pady=5)

        ctk.CTkLabel(
            sidebar,
            text="STORAGE",
            font=("Segoe UI", 12, "bold"),
            text_color=MUTED
        ).pack(anchor="w", padx=18, pady=(25, 10))

        self.add_button(
            sidebar,
            "Open Records Folder",
            self.open_records
        )

    def add_button(
        self,
        parent,
        text,
        command,
        color=CARD
    ):

        button = ctk.CTkButton(
            parent,
            text=text,
            command=command,
            height=38,
            corner_radius=9,
            fg_color=color,
            hover_color="#34466F",
            font=("Segoe UI", 12, "bold"),
            anchor="w"
        )

        button.pack(
            fill="x",
            padx=15,
            pady=5
        )

        return button

    def create_workspace(self):

        workspace = ctk.CTkFrame(
            self,
            fg_color=BG,
            corner_radius=0
        )

        workspace.grid(
            row=1,
            column=1,
            sticky="nsew",
            padx=20,
            pady=20
        )

        workspace.grid_columnconfigure(0, weight=1)
        workspace.grid_rowconfigure(0, weight=4)
        workspace.grid_rowconfigure(1, weight=1)

        # CAMERA PREVIEW

        preview_card = ctk.CTkFrame(
            workspace,
            fg_color=PANEL,
            corner_radius=15
        )

        preview_card.grid(
            row=0,
            column=0,
            sticky="nsew",
            pady=(0, 15)
        )

        ctk.CTkLabel(
            preview_card,
            text="LIVE CAMERA FEED",
            font=("Segoe UI", 14, "bold"),
            text_color=TEXT
        ).pack(
            anchor="w",
            padx=20,
            pady=15
        )

        self.camera_label = ctk.CTkLabel(
            preview_card,
            text="CAMERA IS OFFLINE\n\nPress Start Camera",
            font=("Segoe UI", 18, "bold"),
            text_color=MUTED,
            fg_color=CARD,
            corner_radius=12
        )

        self.camera_label.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 20)
        )

        # STATISTICS

        stats = ctk.CTkFrame(
            workspace,
            fg_color=PANEL,
            corner_radius=15
        )

        stats.grid(
            row=1,
            column=0,
            sticky="nsew"
        )

        stats.grid_columnconfigure(
            (0, 1, 2),
            weight=1
        )

        self.fps_label = self.create_stat(
            stats,
            "CAMERA FPS",
            "0"
        )

        self.motion_label = self.create_stat(
            stats,
            "MOTION EVENTS",
            "0"
        )

        self.record_label = self.create_stat(
            stats,
            "RECORDING",
            "OFF"
        )

    def create_stat(self, parent, title, value):

        card = ctk.CTkFrame(
            parent,
            fg_color=CARD,
            corner_radius=10
        )

        card.grid(
            row=0,
            column=0 if title == "CAMERA FPS" else (
                1 if title == "MOTION EVENTS" else 2
            ),
            padx=8,
            pady=10,
            sticky="nsew"
        )

        ctk.CTkLabel(
            card,
            text=title,
            font=("Segoe UI", 10, "bold"),
            text_color=MUTED
        ).pack(pady=(10, 3))

        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=("Segoe UI", 22, "bold"),
            text_color=ACCENT
        )

        value_label.pack(pady=(0, 10))

        return value_label

    # ======================================
    # CAMERA CONTROL
    # ======================================

    def start_camera(self):

        if self.running:
            return

        self.cap = cv2.VideoCapture(0)

        if not self.cap.isOpened():

            self.cap.release()
            self.cap = None

            self.set_status("CAMERA NOT FOUND", RED)

            return

        self.cap.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            640
        )

        self.cap.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            480
        )

        self.running = True
        self.previous_gray = None

        self.set_status("CAMERA ONLINE", GREEN)

        self.update_camera()

    def stop_camera(self):

        self.running = False

        if self.after_id is not None:
            self.after_cancel(self.after_id)
            self.after_id = None

        if self.cap is not None:

            self.cap.release()
            self.cap = None

        self.stop_recording()

        self.current_frame = None
        self.previous_gray = None

        self.camera_label.configure(
            image=None,
            text="CAMERA IS OFFLINE\n\nPress Start Camera"
        )

        self.fps_label.configure(text="0")

        self.set_status("CAMERA OFFLINE", RED)

    # ======================================
    # CAMERA LOOP
    # ======================================

    def update_camera(self):

        if not self.running or self.cap is None:
            return

        success, frame = self.cap.read()

        if not success:

            self.set_status("CAMERA FRAME ERROR", RED)

            self.after_id = self.after(
                100,
                self.update_camera
            )

            return

        now = time.perf_counter()

        elapsed = now - self.last_frame_time

        if elapsed > 0:
            instant_fps = 1 / elapsed
            self.fps = (
                self.fps * 0.8 +
                instant_fps * 0.2
            )

        self.last_frame_time = now

        # Brightness

        frame = cv2.convertScaleAbs(
            frame,
            alpha=1.0,
            beta=self.brightness
        )

        # Motion Detection

        if self.motion_enabled:

            frame = self.detect_motion(frame)

        # Recording

        if self.recording and self.video_writer is not None:

            self.video_writer.write(frame)

        self.current_frame = frame.copy()

        # Display

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        image = Image.fromarray(rgb)

        image.thumbnail((760, 450))

        self.preview_image = ctk.CTkImage(
            light_image=image,
            dark_image=image,
            size=image.size
        )

        self.camera_label.configure(
            image=self.preview_image,
            text=""
        )

        self.fps_label.configure(
            text=str(int(self.fps))
        )

        self.after_id = self.after(
            30,
            self.update_camera
        )

    # ======================================
    # MOTION DETECTION
    # ======================================

    def detect_motion(self, frame):

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        gray = cv2.GaussianBlur(
            gray,
            (21, 21),
            0
        )

        if self.previous_gray is None:

            self.previous_gray = gray

            return frame

        difference = cv2.absdiff(
            self.previous_gray,
            gray
        )

        self.previous_gray = gray

        _, threshold = cv2.threshold(
            difference,
            25,
            255,
            cv2.THRESH_BINARY
        )

        threshold = cv2.dilate(
            threshold,
            None,
            iterations=2
        )

        contours, _ = cv2.findContours(
            threshold,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        motion_found = False

        for contour in contours:

            if cv2.contourArea(contour) < 1200:
                continue

            x, y, w, h = cv2.boundingRect(contour)

            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (40, 220, 130),
                2
            )

            motion_found = True

        # Count separate motion events

        now = time.time()

        if (
            motion_found
            and not self.motion_active
            and now - self.last_motion_time > 1.5
        ):

            self.motion_count += 1

            self.motion_label.configure(
                text=str(self.motion_count)
            )

            self.last_motion_time = now

        self.motion_active = motion_found

        return frame

    # ======================================
    # SCREENSHOT
    # ======================================

    def take_screenshot(self):

        if self.current_frame is None:

            self.show_message(
                "Camera is not running."
            )

            return

        filename = datetime.now().strftime(
            "Photo_%Y%m%d_%H%M%S.png"
        )

        path = PHOTO_DIR / filename

        cv2.imwrite(
            str(path),
            self.current_frame
        )

        self.show_message(
            f"Screenshot saved:\n{filename}"
        )

    # ======================================
    # VIDEO RECORDING
    # ======================================

    def toggle_recording(self):

        if not self.running:

            self.show_message(
                "Start the camera first."
            )

            return

        if self.recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):

        if self.current_frame is None:
            return

        height, width = self.current_frame.shape[:2]

        filename = datetime.now().strftime(
            "Video_%Y%m%d_%H%M%S.mp4"
        )

        path = VIDEO_DIR / filename

        codec = cv2.VideoWriter_fourcc(
            *"mp4v"
        )

        writer = cv2.VideoWriter(
            str(path),
            codec,
            20.0,
            (width, height)
        )

        if not writer.isOpened():

            writer.release()

            self.show_message(
                "Could not create video file."
            )

            return

        self.video_writer = writer
        self.recording = True

        self.record_label.configure(
            text="ON",
            text_color=RED
        )

        self.set_status("RECORDING VIDEO", RED)

    def stop_recording(self):

        if self.video_writer is not None:

            self.video_writer.release()
            self.video_writer = None

        self.recording = False

        self.record_label.configure(
            text="OFF",
            text_color=ACCENT
        )

        if self.running:
            self.set_status("CAMERA ONLINE", GREEN)

    # ======================================
    # SETTINGS
    # ======================================

    def toggle_motion(self):

        self.motion_enabled = not self.motion_enabled

        if not self.motion_enabled:

            self.previous_gray = None
            self.motion_active = False

            self.set_status(
                "MOTION DETECTION OFF",
                MUTED
            )

        else:

            self.previous_gray = None

            self.set_status(
                "MOTION DETECTION ON",
                GREEN
            )

    def change_brightness(self, value):

        self.brightness = int(value)

        self.brightness_value.configure(
            text=str(self.brightness)
        )

    # ======================================
    # FILE MANAGEMENT
    # ======================================

    def open_records(self):

        os.startfile(str(SAVE_DIR))

    # ======================================
    # HELPERS
    # ======================================

    def set_status(self, text, color):

        self.system_status.configure(
            text=text,
            text_color=color
        )

    def show_message(self, message):

        from tkinter import messagebox

        messagebox.showinfo(
            "Camera Vision",
            message
        )

    def close_application(self):

        self.stop_camera()
        self.destroy()


# ==========================================
# RUN
# ==========================================

if __name__ == "__main__":

    app = CameraVision()
    app.mainloop()
