# -*- coding: utf-8 -*-
"""
批量照片加 Logo 工具
功能：
1. 选择照片文件夹、Logo 图片、输出文件夹
2. 在界面中调整 Logo 大小、透明度、X/Y 位置
3. 可直接在预览图上拖动 Logo
4. 批量处理 jpg/png/webp/bmp/tiff 等常见图片
5. Windows/macOS/Linux 通用；macOS 可用 Python 直接运行，也可在 Mac 上用 PyInstaller 打包为 .app

依赖：
    pip install pillow
运行：
    python logo_batch_gui.py
"""

import os
import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

from PIL import Image, ImageTk, ImageOps


SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}


class BatchLogoApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("照片批量加 Logo 工具")
        self.geometry("1120x760")
        self.minsize(980, 680)

        self.input_dir = tk.StringVar()
        self.logo_path = tk.StringVar()
        self.output_dir = tk.StringVar()

        self.logo_width_pct = tk.DoubleVar(value=18.0)
        self.opacity_pct = tk.DoubleVar(value=100.0)
        self.x_pct = tk.DoubleVar(value=72.0)
        self.y_pct = tk.DoubleVar(value=72.0)

        self.output_mode = tk.StringVar(value="保持原格式")
        self.jpeg_quality = tk.IntVar(value=95)
        self.add_suffix = tk.BooleanVar(value=True)

        self.image_files = []
        self.preview_index = 0
        self.logo_image = None

        self.preview_photo = None
        self.preview_box = None
        self.dragging = False
        self.canvas_img_rect = (0, 0, 1, 1)  # left, top, width, height
        self.base_preview_size = (1, 1)
        self.logo_display_size = (1, 1)

        self._build_ui()

        # 参数变化时刷新预览
        for var in [self.logo_width_pct, self.opacity_pct, self.x_pct, self.y_pct]:
            var.trace_add("write", lambda *args: self.update_preview())

    def _build_ui(self):
        root = ttk.Frame(self, padding=10)
        root.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(root)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        right = ttk.Frame(root)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 文件选择区
        select_box = ttk.LabelFrame(left, text="1. 选择文件")
        select_box.pack(fill=tk.X, pady=(0, 10))

        self._path_row(select_box, "照片文件夹：", self.input_dir, self.choose_input_dir, row=0)
        self._path_row(select_box, "Logo 图片：", self.logo_path, self.choose_logo, row=1)
        self._path_row(select_box, "输出文件夹：", self.output_dir, self.choose_output_dir, row=2)

        ttk.Button(select_box, text="刷新照片列表", command=self.scan_images).grid(
            row=3, column=0, columnspan=3, sticky="ew", padx=6, pady=6
        )

        # 调整区
        control_box = ttk.LabelFrame(left, text="2. 调整 Logo")
        control_box.pack(fill=tk.X, pady=(0, 10))

        self._slider(control_box, "Logo 宽度（占照片宽度 %）", self.logo_width_pct, 1, 80, row=0)
        self._slider(control_box, "透明度（%）", self.opacity_pct, 0, 100, row=1)
        self._slider(control_box, "水平位置 X（%）", self.x_pct, 0, 100, row=2)
        self._slider(control_box, "垂直位置 Y（%）", self.y_pct, 0, 100, row=3)

        hint = ttk.Label(
            control_box,
            text="提示：也可以直接在右侧预览图里拖动 Logo。",
            foreground="#555555",
        )
        hint.grid(row=4, column=0, columnspan=3, sticky="w", padx=6, pady=(6, 8))

        # 输出设置
        out_box = ttk.LabelFrame(left, text="3. 输出设置")
        out_box.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(out_box, text="输出格式：").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        ttk.OptionMenu(out_box, self.output_mode, self.output_mode.get(), "保持原格式", "JPG", "PNG").grid(
            row=0, column=1, sticky="ew", padx=6, pady=6
        )
        out_box.columnconfigure(1, weight=1)

        ttk.Label(out_box, text="JPG质量：").grid(row=1, column=0, sticky="w", padx=6, pady=6)
        ttk.Scale(out_box, from_=70, to=100, variable=self.jpeg_quality, orient=tk.HORIZONTAL).grid(
            row=1, column=1, sticky="ew", padx=6, pady=6
        )
        self.quality_label = ttk.Label(out_box, textvariable=self.jpeg_quality, width=4)
        self.quality_label.grid(row=1, column=2, sticky="e", padx=6, pady=6)

        ttk.Checkbutton(out_box, text="输出文件名添加 _logo 后缀", variable=self.add_suffix).grid(
            row=2, column=0, columnspan=3, sticky="w", padx=6, pady=6
        )

        # 批处理按钮
        action_box = ttk.LabelFrame(left, text="4. 批量处理")
        action_box.pack(fill=tk.X)

        self.file_count_label = ttk.Label(action_box, text="未读取照片")
        self.file_count_label.pack(anchor="w", padx=6, pady=(6, 2))

        self.progress = ttk.Progressbar(action_box, orient=tk.HORIZONTAL, mode="determinate")
        self.progress.pack(fill=tk.X, padx=6, pady=6)

        self.status_label = ttk.Label(action_box, text="准备就绪", foreground="#444444")
        self.status_label.pack(anchor="w", padx=6, pady=(0, 6))

        self.start_btn = ttk.Button(action_box, text="开始批量加 Logo", command=self.start_batch)
        self.start_btn.pack(fill=tk.X, padx=6, pady=(0, 8))

        # 预览区
        preview_box = ttk.LabelFrame(right, text="预览")
        preview_box.pack(fill=tk.BOTH, expand=True)

        toolbar = ttk.Frame(preview_box)
        toolbar.pack(fill=tk.X, padx=6, pady=6)

        ttk.Button(toolbar, text="上一张", command=self.prev_preview).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="下一张", command=self.next_preview).pack(side=tk.LEFT, padx=(6, 0))

        self.preview_name_label = ttk.Label(toolbar, text="请选择照片文件夹和 Logo")
        self.preview_name_label.pack(side=tk.LEFT, padx=12)

        self.canvas = tk.Canvas(preview_box, bg="#eeeeee", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 6))

        self.canvas.bind("<Configure>", lambda event: self.update_preview())
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

    def _path_row(self, parent, label, var, command, row):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", padx=6, pady=6)
        ttk.Entry(parent, textvariable=var, width=34).grid(row=row, column=1, sticky="ew", padx=6, pady=6)
        ttk.Button(parent, text="选择", command=command).grid(row=row, column=2, sticky="e", padx=6, pady=6)
        parent.columnconfigure(1, weight=1)

    def _slider(self, parent, label, var, start, end, row):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", padx=6, pady=6)
        ttk.Scale(parent, from_=start, to=end, variable=var, orient=tk.HORIZONTAL).grid(
            row=row, column=1, sticky="ew", padx=6, pady=6
        )
        value_label = ttk.Label(parent, text="", width=6)
        value_label.grid(row=row, column=2, sticky="e", padx=6, pady=6)

        def refresh_label(*_):
            value_label.config(text=f"{var.get():.1f}")

        var.trace_add("write", refresh_label)
        refresh_label()
        parent.columnconfigure(1, weight=1)

    def choose_input_dir(self):
        path = filedialog.askdirectory(title="选择照片文件夹")
        if path:
            self.input_dir.set(path)
            if not self.output_dir.get():
                self.output_dir.set(str(Path(path) / "output_logo"))
            self.scan_images()

    def choose_logo(self):
        path = filedialog.askopenfilename(
            title="选择 Logo 图片",
            filetypes=[
                ("图片文件", "*.png *.jpg *.jpeg *.webp *.bmp *.tif *.tiff"),
                ("所有文件", "*.*"),
            ],
        )
        if path:
            self.logo_path.set(path)
            self.load_logo()
            self.update_preview()

    def choose_output_dir(self):
        path = filedialog.askdirectory(title="选择输出文件夹")
        if path:
            self.output_dir.set(path)

    def load_logo(self):
        try:
            self.logo_image = ImageOps.exif_transpose(Image.open(self.logo_path.get())).convert("RGBA")
        except Exception as exc:
            self.logo_image = None
            messagebox.showerror("Logo 读取失败", f"无法读取 Logo 图片：\n{exc}")

    def scan_images(self):
        folder = Path(self.input_dir.get())
        if not folder.exists():
            self.image_files = []
            self.file_count_label.config(text="照片文件夹不存在")
            self.update_preview()
            return

        self.image_files = sorted(
            [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS]
        )
        self.preview_index = 0
        self.file_count_label.config(text=f"已读取 {len(self.image_files)} 张照片")
        self.update_preview()

    def read_current_image(self):
        if not self.image_files:
            return None
        path = self.image_files[self.preview_index]
        try:
            return ImageOps.exif_transpose(Image.open(path)).convert("RGBA")
        except Exception:
            return None

    def get_logo_for_image(self, base_size):
        if self.logo_image is None:
            self.load_logo()
        if self.logo_image is None:
            return None

        base_w, base_h = base_size
        logo_w = max(1, int(base_w * self.logo_width_pct.get() / 100.0))
        ratio = logo_w / self.logo_image.width
        logo_h = max(1, int(self.logo_image.height * ratio))

        # 防止 logo 超过图片高度
        if logo_h > base_h:
            logo_h = base_h
            logo_w = max(1, int(self.logo_image.width * (logo_h / self.logo_image.height)))

        logo = self.logo_image.resize((logo_w, logo_h), Image.Resampling.LANCZOS)

        opacity = max(0, min(100, self.opacity_pct.get())) / 100.0
        if opacity < 1:
            r, g, b, a = logo.split()
            a = a.point(lambda px: int(px * opacity))
            logo = Image.merge("RGBA", (r, g, b, a))

        return logo

    def composite_logo(self, img):
        logo = self.get_logo_for_image(img.size)
        if logo is None:
            return img, (0, 0, 0, 0)

        max_x = max(0, img.width - logo.width)
        max_y = max(0, img.height - logo.height)

        x = int(img.width * self.x_pct.get() / 100.0)
        y = int(img.height * self.y_pct.get() / 100.0)
        x = max(0, min(x, max_x))
        y = max(0, min(y, max_y))

        layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        layer.paste(logo, (x, y), logo)
        result = Image.alpha_composite(img, layer)
        return result, (x, y, logo.width, logo.height)

    def update_preview(self):
        self.canvas.delete("all")
        canvas_w = max(100, self.canvas.winfo_width())
        canvas_h = max(100, self.canvas.winfo_height())

        if not self.image_files:
            self.preview_name_label.config(text="请选择照片文件夹")
            self.canvas.create_text(
                canvas_w / 2,
                canvas_h / 2,
                text="暂无照片。请选择照片文件夹。",
                fill="#666666",
                font=("Arial", 15),
            )
            return

        if self.logo_image is None and self.logo_path.get():
            self.load_logo()

        img = self.read_current_image()
        if img is None:
            self.canvas.create_text(
                canvas_w / 2,
                canvas_h / 2,
                text="当前照片读取失败",
                fill="#aa0000",
                font=("Arial", 15),
            )
            return

        composite, logo_box_original = self.composite_logo(img)

        scale = min(canvas_w / composite.width, canvas_h / composite.height, 1.0)
        display_w = max(1, int(composite.width * scale))
        display_h = max(1, int(composite.height * scale))
        left = int((canvas_w - display_w) / 2)
        top = int((canvas_h - display_h) / 2)

        display = composite.resize((display_w, display_h), Image.Resampling.LANCZOS)
        self.preview_photo = ImageTk.PhotoImage(display.convert("RGB"))
        self.canvas.create_image(left, top, anchor="nw", image=self.preview_photo)

        self.canvas_img_rect = (left, top, display_w, display_h)
        self.base_preview_size = (img.width, img.height)

        x, y, lw, lh = logo_box_original
        bx1 = left + x * scale
        by1 = top + y * scale
        bx2 = left + (x + lw) * scale
        by2 = top + (y + lh) * scale
        self.logo_display_size = (max(1, bx2 - bx1), max(1, by2 - by1))
        self.preview_box = (bx1, by1, bx2, by2)

        # 画一个虚线框，方便用户知道 logo 可拖动
        self.canvas.create_rectangle(
            bx1,
            by1,
            bx2,
            by2,
            outline="#ffffff",
            width=2,
            dash=(4, 3),
        )
        self.canvas.create_rectangle(
            bx1 + 1,
            by1 + 1,
            bx2 - 1,
            by2 - 1,
            outline="#333333",
            width=1,
            dash=(4, 3),
        )

        name = self.image_files[self.preview_index].name
        self.preview_name_label.config(text=f"{self.preview_index + 1}/{len(self.image_files)}  {name}")

    def on_mouse_down(self, event):
        if not self.preview_box:
            return
        x1, y1, x2, y2 = self.preview_box
        if x1 <= event.x <= x2 and y1 <= event.y <= y2:
            self.dragging = True

    def on_mouse_drag(self, event):
        if not self.dragging:
            return

        left, top, display_w, display_h = self.canvas_img_rect
        logo_dw, logo_dh = self.logo_display_size

        new_x = event.x - logo_dw / 2
        new_y = event.y - logo_dh / 2

        new_x = max(left, min(new_x, left + display_w - logo_dw))
        new_y = max(top, min(new_y, top + display_h - logo_dh))

        x_pct = (new_x - left) / display_w * 100.0
        y_pct = (new_y - top) / display_h * 100.0

        # set 会触发刷新
        self.x_pct.set(round(x_pct, 2))
        self.y_pct.set(round(y_pct, 2))

    def on_mouse_up(self, event):
        self.dragging = False

    def prev_preview(self):
        if self.image_files:
            self.preview_index = (self.preview_index - 1) % len(self.image_files)
            self.update_preview()

    def next_preview(self):
        if self.image_files:
            self.preview_index = (self.preview_index + 1) % len(self.image_files)
            self.update_preview()

    def get_output_path(self, src_path):
        out_dir = Path(self.output_dir.get())
        mode = self.output_mode.get()

        if mode == "JPG":
            suffix = ".jpg"
        elif mode == "PNG":
            suffix = ".png"
        else:
            suffix = src_path.suffix.lower()

        stem = src_path.stem + ("_logo" if self.add_suffix.get() else "")
        out_path = out_dir / f"{stem}{suffix}"

        # 防止覆盖原图
        if out_path.resolve() == src_path.resolve():
            out_path = out_dir / f"{src_path.stem}_logo{suffix}"

        # 防止同名覆盖
        if out_path.exists():
            i = 1
            while True:
                candidate = out_dir / f"{stem}_{i}{suffix}"
                if not candidate.exists():
                    out_path = candidate
                    break
                i += 1

        return out_path

    def save_image(self, img_rgba, out_path):
        suffix = out_path.suffix.lower()
        quality = int(self.jpeg_quality.get())

        if suffix in {".jpg", ".jpeg"}:
            # JPG 不支持透明通道，使用白色背景合成
            background = Image.new("RGB", img_rgba.size, (255, 255, 255))
            background.paste(img_rgba, mask=img_rgba.split()[-1])
            background.save(out_path, quality=quality, optimize=True)
        elif suffix == ".png":
            img_rgba.save(out_path, optimize=True)
        elif suffix == ".webp":
            img_rgba.save(out_path, quality=quality, method=6)
        else:
            # bmp/tif 等格式通常保存 RGB 更稳妥
            img_rgba.convert("RGB").save(out_path)

    def validate_before_batch(self):
        if not self.input_dir.get() or not Path(self.input_dir.get()).exists():
            messagebox.showwarning("缺少照片文件夹", "请先选择照片文件夹。")
            return False
        if not self.logo_path.get() or not Path(self.logo_path.get()).exists():
            messagebox.showwarning("缺少 Logo 图片", "请先选择 Logo 图片。")
            return False
        if not self.output_dir.get():
            messagebox.showwarning("缺少输出文件夹", "请先选择输出文件夹。")
            return False

        if not self.image_files:
            self.scan_images()
        if not self.image_files:
            messagebox.showwarning("没有照片", "照片文件夹中没有可处理的图片。")
            return False

        return True

    def start_batch(self):
        if not self.validate_before_batch():
            return

        self.start_btn.config(state=tk.DISABLED)
        self.progress["value"] = 0
        self.progress["maximum"] = len(self.image_files)
        self.status_label.config(text="正在处理，请不要关闭程序……")

        worker = threading.Thread(target=self.batch_worker, daemon=True)
        worker.start()

    def batch_worker(self):
        out_dir = Path(self.output_dir.get())
        out_dir.mkdir(parents=True, exist_ok=True)

        success = 0
        failed = []

        for idx, src in enumerate(self.image_files, start=1):
            try:
                img = ImageOps.exif_transpose(Image.open(src)).convert("RGBA")
                result, _ = self.composite_logo(img)
                out_path = self.get_output_path(src)
                self.save_image(result, out_path)
                success += 1
            except Exception as exc:
                failed.append((src.name, str(exc)))

            self.after(0, self._update_progress, idx, src.name)

        self.after(0, self._finish_batch, success, failed)

    def _update_progress(self, idx, filename):
        self.progress["value"] = idx
        self.status_label.config(text=f"正在处理：{filename}")

    def _finish_batch(self, success, failed):
        self.start_btn.config(state=tk.NORMAL)
        if failed:
            msg = f"处理完成：成功 {success} 张，失败 {len(failed)} 张。\n\n失败文件示例：\n"
            msg += "\n".join([f"{name}: {err}" for name, err in failed[:5]])
            self.status_label.config(text=f"完成：成功 {success} 张，失败 {len(failed)} 张")
            messagebox.showwarning("处理完成但有失败", msg)
        else:
            self.status_label.config(text=f"处理完成：成功 {success} 张")
            messagebox.showinfo("处理完成", f"全部处理完成，共输出 {success} 张图片。")


if __name__ == "__main__":
    app = BatchLogoApp()
    app.mainloop()
