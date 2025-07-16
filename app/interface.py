import os
import cv2
import numpy as np
from PIL import Image, ImageTk, ImageDraw
import tkinter as tk
import sv_ttk
from tkinter import filedialog, messagebox, ttk
from ultralytics import YOLO


PRIMARY_COLOR = "#0078D7"
ACCENT_COLOR = "#107C10"
BACKGROUND_COLOR = "#ffffff"
PANEL_BG_COLOR = "#ffffff"
TEXT_COLOR = "#202020"
BORDER_COLOR = "#E0E0E0"

model = YOLO("model/aug/best.pt")


def split_image(image_path, tile_size=None, tile_ratio=None):
    img = Image.open(image_path).convert("RGB")
    width, height = img.size
    tiles = []
    positions = []

    tile_w, tile_h = 0, 0
    if tile_ratio:
        cols, rows = tile_ratio
        if cols > 0 and rows > 0:
            tile_w = width // cols
            tile_h = height // rows
    elif tile_size:
        tile_w, tile_h = tile_size

    if tile_w <= 0 or tile_h <= 0:
        raise ValueError("Kích thước hoặc tỉ lệ ô không hợp lệ (phải là số dương).")

    if width <= tile_w and height <= tile_h:
        tiles.append(img)
        positions.append((0, 0, width, height))
        return img, tiles, positions

    for top in range(0, height, tile_h):
        for left in range(0, width, tile_w):
            right = min(left + tile_w, width)
            bottom = min(top + tile_h, height)
            tile = img.crop((left, top, right, bottom))
            tiles.append(tile)
            positions.append((left, top, right, bottom))
    return img, tiles, positions


def detect_people(img_pil):
    img_cv = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    results = model.predict(img_cv, conf=0.4)[0]
    count = 0
    img_draw_on = img_cv.copy()
    for box in results.boxes:
        cls = int(box.cls)
        if model.names[cls] == "person":
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(img_draw_on, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green for person
            count += 1
    return Image.fromarray(cv2.cvtColor(img_draw_on, cv2.COLOR_BGR2RGB)), count


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Công cụ Nhận diện Người thông minh")

        sv_ttk.set_theme("light")
        self.style = ttk.Style()
        # self.style.theme_use('clam')  # Thử các theme khác: 'clam', 'alt', 'default', 'classic'

        # try:
        #     from ctypes import windll
        #     windll.shcore.SetProcessDpiAwareness(1)
        # except Exception as e:
        #     print(f"Lỗi khi cài DPI awareness: {e}")  # Bỏ qua nếu lỗi
        #
        # smooth_canvas = tk.Canvas(self.root, width=1, height=1, bd=0, highlightthickness=0)
        # smooth_canvas.place(x=-10, y=-10)  # Đặt ra ngoài màn hình
        # smooth_canvas.create_line(0, 0, 1, 1, smooth=True)

        # self.style.configure('.', font=('Segoe UI', 10))  # Default font for all widgets
        self.style.configure('.',
                             background=BACKGROUND_COLOR,
                             foreground=TEXT_COLOR,
                             font=('Segoe UI', 10),  # Font hiện đại, có sẵn trên Windows
                             borderwidth=0,
                             relief='flat')

        self.style.configure('TFrame', background=BACKGROUND_COLOR)
        self.style.configure('TLabel', background=PANEL_BG_COLOR, foreground=TEXT_COLOR)
        self.style.configure('TLabelframe', background=PANEL_BG_COLOR)
        self.style.configure('TLabelframe.Label', font=('Segoe UI', 11, 'regular'), foreground=ACCENT_COLOR,
                             background=PANEL_BG_COLOR)

        self.style.configure('TButton',
                             font=('Segoe UI', 10, 'bold'),
                             padding=(10, 8),  # Tăng padding (ngang, dọc)
                             borderwidth=0,
                             focusthickness=0)
        self.style.map('TButton',
                       background=[('active', '#b30000'), ('!disabled', PRIMARY_COLOR)],
                       foreground=[('active', 'white'), ('!disabled', 'white')])

        self.style.configure('Accent.TButton', background=ACCENT_COLOR, foreground='white')
        self.style.map('Accent.TButton',
                       background=[('active', '#0056b3'), ('!disabled', ACCENT_COLOR)])

        self.style.configure('Secondary.TButton',
                             font=('Segoe UI', 9),  # Font nhỏ hơn một chút
                             padding=(8, 6),
                             background="#6c757d",  # Màu xám trung tính
                             foreground="white")
        self.style.map('Secondary.TButton',
                       background=[('active', '#5a6268'), ('!disabled', '#6c757d')])

        self.style.configure('TEntry', fieldbackground='white', foreground=TEXT_COLOR, borderwidth=1, relief='solid')
        self.style.configure('TCheckbutton', background=PANEL_BG_COLOR, foreground=TEXT_COLOR)
        self.style.configure('Custom.TLabel', background=PANEL_BG_COLOR, foreground=TEXT_COLOR, font=('Segoe UI', 10))
        self.style.configure('Tile.TLabel', background='#f7f7f7', borderwidth=1, relief="solid", padding=5,
                             bordercolor=BORDER_COLOR)  # For individual image tiles

        # Main window
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        self.root.geometry(f"{int(screen_width * 0.85)}x{int(screen_height * 0.85)}")  # Kích thước lớn hơn
        self.root.minsize(1000, 700)  # Kích thước tối thiểu
        self.root.configure(bg=BACKGROUND_COLOR)

        self.img_large = None
        self.img_tiles = []
        self.tile_positions = []
        self.tile_counts = []
        self.detected_tiles = []
        self.page = 0
        self.tiles_per_page = 8
        self.use_ratio = tk.BooleanVar()
        self.img_path = None

        # Main frame
        self.main_frame = ttk.Frame(root, padding="15")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Left control
        self.left_panel = ttk.Frame(self.main_frame, style='TFrame')  # Use default TFrame style
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))

        ttk.Label(self.left_panel, text="Ảnh nhận diện", font=('Segoe UI', 13, 'bold'),
                  background=BACKGROUND_COLOR, foreground=TEXT_COLOR).pack(pady=(0, 10), anchor='w')
        self.canvas_large = tk.Canvas(self.left_panel,
                                      bg=PANEL_BG_COLOR,
                                      borderwidth=0,  # Bỏ viền 3D
                                      highlightthickness=1,  # Tạo một đường viền phẳng 1-pixel
                                      highlightbackground=BORDER_COLOR)
        self.canvas_large.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.canvas_large.bind('<Configure>', self._on_large_canvas_resize)  # Bind resize event

        self.total_label = ttk.Label(self.left_panel, text="Tổng số người phát hiện: 0",
                                     font=("Segoe UI", 14, "bold"), foreground=PRIMARY_COLOR, background=BACKGROUND_COLOR)
        self.total_label.pack(pady=10, anchor='w', padx=10)

        # Right Control
        self.right_panel = ttk.Frame(self.main_frame, width=420,
                                     style='TFrame')
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)
        self.right_panel.pack_propagate(False)

        self.control_frame = ttk.LabelFrame(self.right_panel, text="Cài đặt & Thao tác", padding="15")
        self.control_frame.pack(fill=tk.X, pady=(0, 15))

        action_button_frame = ttk.Frame(self.control_frame)
        action_button_frame.pack(fill=tk.X, pady=5)

        action_button_frame.columnconfigure(0, weight=1)
        action_button_frame.columnconfigure(1, weight=1)

        ttk.Button(action_button_frame, text="\U0001F4C1 Chọn ảnh", command=self.choose_image,
                   style='Accent.TButton').grid(row=0, column=0, padx=(0, 5), sticky='ew')

        ttk.Button(action_button_frame, text="\U0001F50E Nhận diện ảnh lớn", command=self.detect_large_image,
                   style='Accent.TButton').grid(row=0, column=1, padx=(5, 0), sticky='ew')

        ttk.Separator(self.control_frame, orient='horizontal').pack(fill='x', pady=10)

        ttk.Checkbutton(self.control_frame, text="Chia ảnh theo tỉ lệ (WxH)", variable=self.use_ratio,
                        command=self.toggle_mode).pack(pady=(5, 5), anchor='w')

        self.size_input_frame = ttk.Frame(self.control_frame)
        self.size_input_frame.columnconfigure(1, weight=1)  # Allow entry to expand
        ttk.Label(self.size_input_frame, text="Rộng (px):", style='Custom.TLabel').grid(row=0, column=0, padx=5, pady=2,
                                                                                        sticky='w')
        self.width_entry = ttk.Entry(self.size_input_frame)
        self.width_entry.insert(0, "500")
        self.width_entry.grid(row=0, column=1, padx=5, pady=2, sticky='ew')
        ttk.Label(self.size_input_frame, text="Cao (px):", style='Custom.TLabel').grid(row=1, column=0, padx=5, pady=2,
                                                                                       sticky='w')
        self.height_entry = ttk.Entry(self.size_input_frame)
        self.height_entry.insert(0, "500")
        self.height_entry.grid(row=1, column=1, padx=5, pady=2, sticky='ew')

        self.ratio_input_frame = ttk.Frame(self.control_frame)
        self.ratio_input_frame.columnconfigure(1, weight=1)
        ttk.Label(self.ratio_input_frame, text="Tỉ lệ (VD: 5x2):", style='Custom.TLabel').grid(row=0, column=0, padx=5,
                                                                                               pady=2, sticky='w')
        self.ratio_entry = ttk.Entry(self.ratio_input_frame)
        self.ratio_entry.insert(0, "5x2")
        self.ratio_entry.grid(row=0, column=1, padx=5, pady=2, sticky='ew')

        ttk.Button(self.control_frame, text="\U00002702 Tách & Nhận diện ảnh con", command=self.split_and_detect,
                   style='Accent.TButton').pack(fill=tk.X, pady=(10, 5))

        self.toggle_mode()

        # Tile view
        self.view_option_frame = ttk.LabelFrame(self.right_panel, text="Cài đặt hiển thị ảnh con", padding="15")
        self.view_option_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(self.view_option_frame, text="Số ảnh con/trang:", style='Custom.TLabel').pack(side=tk.LEFT, padx=5,
                                                                                                pady=5)
        self.num_entry = ttk.Entry(self.view_option_frame, width=5)
        self.num_entry.insert(0, str(self.tiles_per_page))
        self.num_entry.pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(self.view_option_frame, text="Cập nhật", command=self.update_tile_count,
                   style='Accent.TButton').pack(side=tk.LEFT, padx=5, pady=5
        )

        # Tiles Display
        ttk.Label(self.right_panel, text="Ảnh con đã nhận diện:",
                  font=('Segoe UI', 13, 'bold'), background=BACKGROUND_COLOR, foreground=TEXT_COLOR).pack(pady=(0, 10),
                                                                                                       anchor='w')

        self.tile_canvas_frame = ttk.Frame(self.right_panel)
        self.tile_canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.scroll_canvas = tk.Canvas(self.tile_canvas_frame,
                                       bg=PANEL_BG_COLOR,  # Nền trắng để chứa ảnh
                                       borderwidth=0,  # Bỏ viền của Canvas
                                       highlightthickness=1,  # Tạo một đường viền mỏng, phẳng
                                       highlightbackground=BORDER_COLOR)

        self.scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.v_scrollbar = ttk.Scrollbar(self.tile_canvas_frame, orient="vertical", command=self.scroll_canvas.yview)
        self.v_scrollbar.pack(side=tk.RIGHT, fill="y")
        self.scroll_canvas.configure(yscrollcommand=self.v_scrollbar.set)

        self.h_scrollbar = ttk.Scrollbar(self.right_panel, orient="horizontal", command=self.scroll_canvas.xview)
        self.h_scrollbar.pack(fill="x")
        self.scroll_canvas.configure(xscrollcommand=self.h_scrollbar.set)

        self.scroll_frame = ttk.Frame(self.scroll_canvas, style='TFrame')

        # Scroll window
        self.canvas_frame_id = self.scroll_canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw",
                                                                tags="self.scroll_frame")
        self.scroll_frame.bind("<Configure>", self._on_scroll_frame_configure)
        self.scroll_canvas.bind('<Configure>', self._on_tile_canvas_resize)

        # Mouse dragging
        self.scroll_canvas.bind("<ButtonPress-1>", self._start_scroll)
        self.scroll_canvas.bind("<B1-Motion>", self._do_scroll)
        self.scroll_canvas.bind("<MouseWheel>", self._on_mouse_wheel)  # Windows & macOS
        self.scroll_canvas.bind("<Button-4>", self._on_mouse_wheel)  # Linux (scroll up)
        self.scroll_canvas.bind("<Button-5>", self._on_mouse_wheel)

        # Pagination
        self.nav_frame = ttk.Frame(self.right_panel, padding="5")
        self.nav_frame.pack(fill=tk.X, pady=10)

        self.page_info = ttk.Label(self.nav_frame, text="Trang 0/0", font=('Segoe UI', 10, 'italic'),
                                   background=BACKGROUND_COLOR)
        self.page_info.pack(side=tk.LEFT, expand=True, padx=5)

        ttk.Button(
            self.nav_frame, text="< Trước", command=self.prev_page, style='Accent.TButton').pack(side=tk.LEFT, padx=3
                                                                                                 )
        ttk.Button(
            self.nav_frame, text="Tiếp >", command=self.next_page, style='Accent.TButton').pack(side=tk.LEFT, padx=3
                                                                                                )
        ttk.Button(self.nav_frame, text="\U0001F4BE Lưu kết quả", command=self.save_results,
                   style='Accent.TButton').pack(side=tk.RIGHT, padx=5)

        self.zoom_tkimg = None

    def _on_large_canvas_resize(self, event):
        if self.img_large:
            self._display_large_image(self.img_large)

    def _on_tile_canvas_resize(self, event):
        """
        When the canvas itself resizes, update the internal frame's width and re-show tiles to adjust
        column layout. Ensure the canvas window (scroll_frame) inside the canvas matches the canvas width
        """
        self.scroll_canvas.itemconfig(self.canvas_frame_id, width=event.width)
        if self.detected_tiles:
            self.show_tiles()

    def _on_scroll_frame_configure(self, event):
        self.scroll_canvas.config(scrollregion=self.scroll_canvas.bbox("all"))

    def _start_scroll(self, event):
        self.scroll_canvas.scan_mark(event.x, event.y)

    def _do_scroll(self, event):
        self.scroll_canvas.scan_dragto(event.x, event.y, gain=1)

    def _on_mouse_wheel(self, event):
        widget_under_cursor = self.root.winfo_containing(event.x_root, event.y_root)

        current_widget = widget_under_cursor
        while current_widget is not None:
            if current_widget == self.scroll_frame:
                if event.num == 5 or event.delta < 0:
                    self.scroll_canvas.yview_scroll(1, "units")
                elif event.num == 4 or event.delta > 0:
                    self.scroll_canvas.yview_scroll(-1, "units")
                return "break"

            current_widget = current_widget.master

        return

    # --- UI Logic Functions ---
    def toggle_mode(self):
        if self.use_ratio.get():
            self.size_input_frame.pack_forget()
            self.ratio_input_frame.pack(fill=tk.X)
        else:
            self.ratio_input_frame.pack_forget()
            self.size_input_frame.pack(fill=tk.X)
        self.control_frame.update_idletasks()

    def choose_image(self):
        self.img_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.jpeg *.bmp")])
        if self.img_path:
            self.img_large = Image.open(self.img_path).convert("RGB")
            self._display_large_image(self.img_large)
            self.clear_tiles_display()
            self.total_label.config(text=f"\U0001F464 Tổng số người phát hiện: 0")  # Reset count

    def _display_large_image(self, image_to_display):
        canvas_width = self.canvas_large.winfo_width()
        canvas_height = self.canvas_large.winfo_height()

        # Fallback for initial render where winfo_width/height might be 1
        if canvas_width <= 1 or canvas_height <= 1:
            # Estimate based on parent panel size, minus padding/borders
            canvas_width = self.left_panel.winfo_width() - 30 if self.left_panel.winfo_width() > 50 else 600
            canvas_height = self.left_panel.winfo_height() - 100 if self.left_panel.winfo_height() > 100 else 400

        img_w, img_h = image_to_display.size

        # Calculate ratio to fit while maintaining aspect ratio
        if img_w > canvas_width or img_h > canvas_height:
            ratio = min(canvas_width / img_w, canvas_height / img_h)
            new_w = int(img_w * ratio)
            new_h = int(img_h * ratio)
        else:  # Image is smaller than canvas, display at original size
            new_w, new_h = img_w, img_h

        resized_img = image_to_display.resize((new_w, new_h), Image.Resampling.LANCZOS)
        self.tk_large = ImageTk.PhotoImage(resized_img)

        self.canvas_large.delete("all")
        # Center the image on the canvas
        self.canvas_large.create_image(canvas_width / 2, canvas_height / 2, anchor=tk.CENTER, image=self.tk_large)
        self.canvas_large.image = self.tk_large  # Keep a reference!

    def clear_tiles_display(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self.detected_tiles = []
        self.tile_counts = []
        self.tile_positions = []
        self.page = 0
        self.page_info.config(text="Trang 0/0")
        self.scroll_canvas.xview_moveto(0)  # Reset scroll position
        self.scroll_canvas.yview_moveto(0)  # Reset scroll position

    def update_tile_count(self):
        try:
            val = int(self.num_entry.get())
            if val > 0:
                self.tiles_per_page = val
                if self.detected_tiles:  # Only update if tiles already exist
                    self.show_tiles()
            else:
                messagebox.showwarning("Cảnh báo", "Số ảnh con/trang phải lớn hơn 0.")
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập một số nguyên hợp lệ cho số ảnh con/trang.")

    def split_and_detect(self):
        if not self.img_path:
            messagebox.showwarning("Chưa có ảnh", "Vui lòng chọn ảnh trước khi tách và nhận diện.")
            return

        try:
            if self.use_ratio.get():
                ratio_str = self.ratio_entry.get().lower()
                if 'x' not in ratio_str:
                    raise ValueError("Tỉ lệ phải có định dạng 'sốxsố' (ví dụ: 5x2).")
                cols_str, rows_str = ratio_str.split("x")
                cols, rows = int(cols_str), int(rows_str)
                if cols <= 0 or rows <= 0:
                    raise ValueError("Tỉ lệ phải là số dương.")
                self.img_large, self.img_tiles, self.tile_positions = split_image(self.img_path,
                                                                                  tile_ratio=(cols, rows))
            else:
                width = int(self.width_entry.get())
                height = int(self.height_entry.get())
                if width <= 0 or height <= 0:
                    raise ValueError("Kích thước phải là số dương.")
                self.img_large, self.img_tiles, self.tile_positions = split_image(self.img_path,
                                                                                  tile_size=(width, height))
        except ValueError as e:
            messagebox.showerror("Lỗi nhập liệu", f"Vui lòng kiểm tra lại thông số: {e}")
            return
        except Exception as e:
            messagebox.showerror("Lỗi xử lý", f"Có lỗi xảy ra khi tách ảnh: {e}")
            return

        if not self.img_tiles:
            messagebox.showwarning("Không có ảnh con",
                                   "Không thể tạo ảnh con với các thông số đã cho. Vui lòng thử lại với các thông số khác.")
            return

        self.detected_tiles = []
        self.tile_counts = []
        # Có thể thêm một thanh tiến trình ở đây nếu có nhiều ảnh con
        for i, tile in enumerate(self.img_tiles):
            det_img, count = detect_people(tile)
            self.detected_tiles.append(det_img)
            self.tile_counts.append(count)

        self.page = 0
        self.show_large_with_overlay()
        self.show_tiles()
        messagebox.showinfo("Thành công", f"Đã tách và nhận diện {len(self.detected_tiles)} ảnh con.")

    def detect_large_image(self):
        if not self.img_path:
            messagebox.showwarning("Chưa có ảnh", "Vui lòng chọn ảnh trước khi nhận diện.")
            return

        self.img_large_original = Image.open(self.img_path).convert("RGB")  # Keep original for overlay
        self.detected_large, count = detect_people(self.img_large_original)
        self._display_large_image(self.detected_large)
        self.total_label.config(text=f"\U0001F464 Số người phát hiện: {count}")
        self.clear_tiles_display()  # Clear tiles when showing full detection

    def show_large_with_overlay(self):
        if not self.img_large or not self.tile_positions:
            if self.img_path:  # If an image was chosen but no tiles were generated
                self._display_large_image(Image.open(self.img_path).convert("RGB"))
            self.total_label.config(text=f"\U0001F464 Tổng số người phát hiện: 0")
            return

        # Use the original full image for overlay if it exists, otherwise use current self.img_large
        draw_img = Image.open(self.img_path).convert("RGB") if hasattr(self,
                                                                       'img_path') and self.img_path else self.img_large.copy()
        draw_overlay = ImageDraw.Draw(draw_img)

        start = self.page * self.tiles_per_page
        end = min(start + self.tiles_per_page, len(self.tile_positions))

        for i in range(start, end):
            x1, y1, x2, y2 = self.tile_positions[i]
            draw_overlay.rectangle([x1, y1, x2, y2], outline="#007bff", width=4)  # Blue border for current page tiles

        self._display_large_image(draw_img)
        total_people = sum(self.tile_counts)
        self.total_label.config(text=f"\U0001F464 Tổng số người phát hiện: {total_people}")

    def show_tiles(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        # Calculate columns based on available width and desired tile size
        tile_display_size = 150  # Fixed size for displayed tile image
        padding = 10  # Padding around each tile

        # Get actual canvas width (after packing and resizing by Tkinter)
        canvas_width = self.scroll_canvas.winfo_width()
        if canvas_width <= 1:  # Fallback if canvas width is not yet determined
            canvas_width = self.right_panel.winfo_width() - self.v_scrollbar.winfo_width() - 30
            if canvas_width < tile_display_size + padding: canvas_width = tile_display_size + padding * 2

        num_cols = max(1, (canvas_width - padding) // (tile_display_size + padding))

        start = self.page * self.tiles_per_page
        end = min(start + self.tiles_per_page, len(self.detected_tiles))

        self.tk_tile_images = []  # Store PhotoImage objects to prevent garbage collection

        for i in range(start, end):
            original_tile_img = self.detected_tiles[i].copy()

            # Create a fixed-size square image and paste the resized tile onto it
            square_img = Image.new("RGB", (tile_display_size, tile_display_size), (255, 255, 255))  # Light background

            img_w, img_h = original_tile_img.size
            ratio = min(tile_display_size / img_w, tile_display_size / img_h)
            new_w = int(img_w * ratio)
            new_h = int(img_h * ratio)

            resized_img = original_tile_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            square_img.paste(resized_img, ((tile_display_size - new_w) // 2, (tile_display_size - new_h) // 2))

            tkimg = ImageTk.PhotoImage(square_img)
            self.tk_tile_images.append(tkimg)  # Store reference

            lbl = ttk.Label(self.scroll_frame, image=tkimg, text=f"Người: {self.tile_counts[i]}", compound="top",
                            font=("Segoe UI", 10, "bold"), foreground="#333", style='Tile.TLabel')

            # Grid layout for tiles
            row_idx = (i - start) // num_cols
            col_idx = (i - start) % num_cols
            lbl.grid(row=row_idx, column=col_idx, padx=padding, pady=padding, sticky="nsew")

            # Bind click event for zoom
            lbl.bind("<Button-1>", lambda e, im=self.detected_tiles[i]: self.zoom_image(
                im))  # lbl.bind("<Button-1>", lambda e, im=original_tile_img: self.zoom_image(im))

        # Configure columns to distribute space evenly for an organized grid
        for col in range(num_cols):
            self.scroll_frame.grid_columnconfigure(col, weight=1)

        # Force update layout to ensure scrollregion calculation is accurate
        self.scroll_frame.update_idletasks()
        self.scroll_canvas.config(scrollregion=self.scroll_canvas.bbox("all"))

    def zoom_image(self, image):
        top = tk.Toplevel(self.root)
        top.title("Xem ảnh chi tiết")
        top.transient(self.root)  # Make it a transient window relative to root
        top.grab_set()  # Grab focus until window is closed
        top.resizable(False, False)  # Disable resizing for zoom window
        top.configure(bg=PANEL_BG_COLOR)

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        max_zoom_width = int(screen_width * 0.7)
        max_zoom_height = int(screen_height * 0.7)

        img_w, img_h = image.size

        # Calculate resize ratio to fit within max_zoom_size without upscaling
        ratio = min(max_zoom_width / img_w, max_zoom_height / img_h)
        if ratio > 1:  # Prevent upscaling if image is smaller than max_zoom_size
            ratio = 1.0

        new_w = int(img_w * ratio)
        new_h = int(img_h * ratio)

        resized_img = image.resize((new_w, new_h), Image.Resampling.LANCZOS)

        # Keep a reference to the PhotoImage in the instance to prevent garbage collection
        # This is the most crucial part for the zoom window to work
        self.zoom_tkimg = ImageTk.PhotoImage(resized_img)

        lbl = ttk.Label(top, image=self.zoom_tkimg, background=PANEL_BG_COLOR)
        lbl.pack(padx=20, pady=20)

        # Center the toplevel window
        top.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (top.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (top.winfo_height() // 2)
        top.geometry(f"+{x}+{y}")

        # When the toplevel window is closed, release the reference
        top.protocol("WM_DELETE_WINDOW", lambda: self._on_zoom_window_close(top))

    def _on_zoom_window_close(self, window):
        self.zoom_tkimg = None
        window.destroy()

    def next_page(self):
        if self.detected_tiles and (self.page + 1) * self.tiles_per_page < len(self.detected_tiles):
            self.page += 1
            self.show_large_with_overlay()
            self.show_tiles()
            self.scroll_canvas.xview_moveto(0)
            self.scroll_canvas.yview_moveto(0)

    def prev_page(self):
        if self.page > 0:
            self.page -= 1
            self.show_large_with_overlay()
            self.show_tiles()
            self.scroll_canvas.xview_moveto(0)  # Reset horizontal scroll on new page
            self.scroll_canvas.yview_moveto(0)  # Reset vertical scroll on new page

    def save_results(self):
        if not self.detected_tiles:
            messagebox.showwarning("Chưa có ảnh", "Bạn chưa nhận diện ảnh nào để lưu!")
            return

        save_dir = filedialog.askdirectory(title="Chọn thư mục lưu ảnh")
        if not save_dir:
            return

        try:
            for idx, img in enumerate(self.detected_tiles):
                file_name = f"tile_result_{idx + 1}_persons_{self.tile_counts[idx]}.jpg"
                img.save(os.path.join(save_dir, file_name))
            messagebox.showinfo("Thành công",
                                f"Đã lưu tất cả {len(self.detected_tiles)} ảnh nhận diện vào:\n{save_dir}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi khi lưu ảnh: {e}")
