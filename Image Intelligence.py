
import os
import customtkinter as ctk

from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageFilter, ImageOps, ImageEnhance


# ==========================================
# CONFIGURATION
# ==========================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

APP_NAME = "IMAGE INTELLIGENCE"
WINDOW_SIZE = "1150x750"

BG_COLOR = "#0B1020"
PANEL_COLOR = "#131B2E"
CARD_COLOR = "#1A2540"
ACCENT_COLOR = "#5B8CFF"
TEXT_COLOR = "#F0F4FF"
MUTED_COLOR = "#8996B3"


# ==========================================
# MAIN APPLICATION
# ==========================================

class ImageIntelligence(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry(WINDOW_SIZE)
        self.minsize(950, 650)
        self.configure(fg_color=BG_COLOR)

        self.original_image = None
        self.current_image = None
        self.current_path = None
        self.preview_image = None

        self.create_interface()

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
            fg_color=PANEL_COLOR
        )

        header.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="ew"
        )

        header.grid_columnconfigure(1, weight=1)

        title = ctk.CTkLabel(
            header,
            text="✦ IMAGE INTELLIGENCE",
            font=("Segoe UI", 22, "bold"),
            text_color=ACCENT_COLOR
        )

        title.grid(row=0, column=0, padx=25, pady=20)

        self.status_label = ctk.CTkLabel(
            header,
            text="SYSTEM READY",
            font=("Segoe UI", 11, "bold"),
            text_color="#51D6A5"
        )

        self.status_label.grid(
            row=0,
            column=2,
            padx=25
        )

    def create_sidebar(self):

        sidebar = ctk.CTkFrame(
            self,
            width=260,
            corner_radius=0,
            fg_color=PANEL_COLOR
        )

        sidebar.grid(
            row=1,
            column=0,
            sticky="nsew"
        )

        sidebar.grid_propagate(False)

        ctk.CTkLabel(
            sidebar,
            text="IMAGE TOOLS",
            font=("Segoe UI", 15, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=(25, 15))

        self.add_button(
            sidebar,
            "＋  Open Image",
            self.open_image,
            ACCENT_COLOR
        )

        ctk.CTkLabel(
            sidebar,
            text="IMAGE EFFECTS",
            font=("Segoe UI", 12, "bold"),
            text_color=MUTED_COLOR
        ).pack(anchor="w", padx=20, pady=(25, 10))

        self.add_button(
            sidebar,
            "Grayscale",
            lambda: self.apply_effect("gray")
        )

        self.add_button(
            sidebar,
            "Blur",
            lambda: self.apply_effect("blur")
        )

        self.add_button(
            sidebar,
            "Edge Detection",
            lambda: self.apply_effect("edges")
        )

        self.add_button(
            sidebar,
            "Sharpen",
            lambda: self.apply_effect("sharpen")
        )

        self.add_button(
            sidebar,
            "Enhance Colors",
            lambda: self.apply_effect("color")
        )

        ctk.CTkLabel(
            sidebar,
            text="IMAGE MANAGEMENT",
            font=("Segoe UI", 12, "bold"),
            text_color=MUTED_COLOR
        ).pack(anchor="w", padx=20, pady=(25, 10))

        self.add_button(
            sidebar,
            "Reset Image",
            self.reset_image
        )

        self.add_button(
            sidebar,
            "Save Image",
            self.save_image,
            "#168B70"
        )

        self.add_button(
            sidebar,
            "Analyze Image",
            self.analyze_image
        )

    def add_button(
        self,
        parent,
        text,
        command,
        color=CARD_COLOR
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
            fg_color=BG_COLOR,
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
        workspace.grid_rowconfigure(0, weight=3)
        workspace.grid_rowconfigure(1, weight=2)

        # IMAGE PREVIEW

        preview_card = ctk.CTkFrame(
            workspace,
            fg_color=PANEL_COLOR,
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
            text="IMAGE PREVIEW",
            font=("Segoe UI", 14, "bold"),
            text_color=TEXT_COLOR
        ).pack(
            anchor="w",
            padx=20,
            pady=15
        )

        self.image_label = ctk.CTkLabel(
            preview_card,
            text="",
            fg_color=CARD_COLOR,
            corner_radius=12
        )

        self.image_label.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 20)
        )

        # INFORMATION PANEL

        info_card = ctk.CTkFrame(
            workspace,
            fg_color=PANEL_COLOR,
            corner_radius=15
        )

        info_card.grid(
            row=1,
            column=0,
            sticky="nsew"
        )

        ctk.CTkLabel(
            info_card,
            text="IMAGE INFORMATION",
            font=("Segoe UI", 14, "bold"),
            text_color=TEXT_COLOR
        ).pack(
            anchor="w",
            padx=20,
            pady=(15, 10)
        )

        self.info_label = ctk.CTkLabel(
            info_card,
            text="No image loaded.",
            font=("Segoe UI", 12),
            text_color=MUTED_COLOR,
            justify="left",
            anchor="w"
        )

        self.info_label.pack(
            anchor="w",
            padx=20,
            pady=5
        )

        self.palette_frame = ctk.CTkFrame(
            info_card,
            fg_color="transparent"
        )

        self.palette_frame.pack(
            anchor="w",
            padx=20,
            pady=10
        )

    # ======================================
    # OPEN IMAGE
    # ======================================

    def open_image(self):

        path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[
                ("Image Files", "*.png *.jpg *.jpeg *.bmp *.webp"),
                ("All Files", "*.*")
            ]
        )

        if not path:
            return

        try:

            image = Image.open(path)
            image.load()

            if image.width * image.height > 25000000:
                messagebox.showwarning(
                    "Large Image",
                    "This image is very large. Processing may take longer."
                )

            image = ImageOps.exif_transpose(image)
            image = image.convert("RGB")

            self.original_image = image.copy()
            self.current_image = image.copy()
            self.current_path = path

            self.show_image()
            self.analyze_image()

            self.set_status("IMAGE LOADED")

        except Exception as error:

            messagebox.showerror(
                "Image Error",
                str(error)
            )

    # ======================================
    # DISPLAY IMAGE
    # ======================================

    def show_image(self):

        if self.current_image is None:
            return

        image = self.current_image.copy()

        image.thumbnail((650, 360))

        self.preview_image = ctk.CTkImage(
            light_image=image,
            dark_image=image,
            size=image.size
        )

        self.image_label.configure(
            image=self.preview_image,
            text=""
        )

    # ======================================
    # IMAGE EFFECTS
    # ======================================

    def apply_effect(self, effect):

        if self.current_image is None:

            messagebox.showinfo(
                "No Image",
                "Please open an image first."
            )

            return

        try:

            image = self.current_image.copy()

            if effect == "gray":

                image = ImageOps.grayscale(image)
                image = image.convert("RGB")

            elif effect == "blur":

                image = image.filter(
                    ImageFilter.GaussianBlur(radius=3)
                )

            elif effect == "edges":

                image = image.filter(
                    ImageFilter.FIND_EDGES
                )

            elif effect == "sharpen":

                image = image.filter(
                    ImageFilter.SHARPEN
                )

            elif effect == "color":

                image = ImageEnhance.Color(image)
                image = image.enhance(1.7)

            self.current_image = image

            self.show_image()
            self.set_status("EFFECT APPLIED")

        except Exception as error:

            messagebox.showerror(
                "Processing Error",
                str(error)
            )

    # ======================================
    # RESET IMAGE
    # ======================================

    def reset_image(self):

        if self.original_image is None:
            return

        self.current_image = self.original_image.copy()

        self.show_image()
        self.analyze_image()

        self.set_status("IMAGE RESET")

    # ======================================
    # ANALYZE IMAGE
    # ======================================

    def analyze_image(self):

        if self.current_image is None:
            return

        image = self.current_image

        width, height = image.size

        image_format = "Unknown"

        if self.current_path:
            try:
                with Image.open(self.current_path) as source:
                    image_format = source.format or "Unknown"
            except Exception:
                pass

        file_size = 0

        if self.current_path:
            file_size = os.path.getsize(self.current_path)

        size_kb = file_size / 1024

        aspect_ratio = width / height if height else 0

        info = (
            f"Width: {width} px\n"
            f"Height: {height} px\n"
            f"Format: {image_format}\n"
            f"File Size: {size_kb:.2f} KB\n"
            f"Aspect Ratio: {aspect_ratio:.2f}\n"
            f"Color Mode: {image.mode}"
        )

        self.info_label.configure(text=info)

        self.show_color_palette()

        self.set_status("ANALYSIS COMPLETE")

    # ======================================
    # COLOR PALETTE
    # ======================================

    def show_color_palette(self):

        for widget in self.palette_frame.winfo_children():
            widget.destroy()

        image = self.current_image.copy()

        image.thumbnail((150, 150))

        image = image.quantize(colors=5)

        palette = image.getpalette()
        colors = image.getcolors()

        if not palette or not colors:
            return

        colors = sorted(
            colors,
            reverse=True
        )

        ctk.CTkLabel(
            self.palette_frame,
            text="MAIN COLORS:",
            font=("Segoe UI", 11, "bold"),
            text_color=MUTED_COLOR
        ).pack(
            anchor="w",
            pady=(0, 8)
        )

        color_container = ctk.CTkFrame(
            self.palette_frame,
            fg_color="transparent"
        )

        color_container.pack(anchor="w")

        for count, color_index in colors:

            index = color_index * 3

            red = palette[index]
            green = palette[index + 1]
            blue = palette[index + 2]

            hex_color = "#{:02X}{:02X}{:02X}".format(
                red,
                green,
                blue
            )

            color_box = ctk.CTkFrame(
                color_container,
                width=38,
                height=38,
                fg_color=hex_color,
                corner_radius=7
            )

            color_box.pack(
                side="left",
                padx=4
            )

            color_box.pack_propagate(False)

    # ======================================
    # SAVE IMAGE
    # ======================================

    def save_image(self):

        if self.current_image is None:

            messagebox.showinfo(
                "No Image",
                "There is no image to save."
            )

            return

        path = filedialog.asksaveasfilename(
            title="Save Image",
            defaultextension=".png",
            filetypes=[
                ("PNG Image", "*.png"),
                ("JPEG Image", "*.jpg"),
                ("WEBP Image", "*.webp")
            ]
        )

        if not path:
            return

        try:

            self.current_image.save(path)

            messagebox.showinfo(
                "Success",
                "Image saved successfully!"
            )

            self.set_status("IMAGE SAVED")

        except Exception as error:

            messagebox.showerror(
                "Save Error",
                str(error)
            )

    # ======================================
    # STATUS
    # ======================================

    def set_status(self, text):

        self.status_label.configure(
            text=text
        )


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    app = ImageIntelligence()
    app.mainloop()
