"""Small local GUI for drawing one receipt/label box per image."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

from PIL import Image, ImageOps, ImageTk

try:
    import pillow_heif

    pillow_heif.register_heif_opener()
except ImportError:
    pass


class Labeler:
    def __init__(self, data_root: Path) -> None:
        self.data_root = data_root
        manifest = data_root / "reports" / "manifest.csv"
        with manifest.open("r", encoding="utf-8-sig", newline="") as stream:
            self.rows = list(csv.DictReader(stream))
        if not self.rows:
            raise ValueError("No photos in manifest. Run intake.py after copying images to incoming.")
        self.index = 0
        self.root = tk.Tk()
        self.root.title("Receipt box labels (saved locally)")
        self.title = tk.Label(self.root, font=("Arial", 12))
        self.title.pack(pady=4)
        self.canvas = tk.Canvas(self.root, width=1000, height=700, bg="#333333")
        self.canvas.pack()
        self.canvas.bind("<ButtonPress-1>", self.start_box)
        self.canvas.bind("<B1-Motion>", self.drag_box)
        self.canvas.bind("<ButtonRelease-1>", self.end_box)
        controls = tk.Frame(self.root)
        controls.pack(pady=5)
        tk.Button(controls, text="Previous", command=lambda: self.change(-1)).pack(side="left", padx=5)
        tk.Button(controls, text="Next", command=lambda: self.change(1)).pack(side="left", padx=5)
        self.class_id = tk.IntVar(value=0)
        tk.Radiobutton(controls, text="Receipt", variable=self.class_id, value=0).pack(side="left")
        tk.Radiobutton(controls, text="Label", variable=self.class_id, value=1).pack(side="left")
        tk.Label(controls, text="Drag a box; releasing saves it. Drag again to replace it.").pack(side="left", padx=10)
        self.start = None
        self.photo = None
        self.box = None
        self.image_bounds = (0, 0, 1, 1)
        self.show()

    def current(self) -> dict[str, str]:
        return self.rows[self.index]

    def label_path(self) -> Path:
        return self.data_root / "labels" / f"{self.current()['doc_id']}.txt"

    def show(self) -> None:
        row = self.current()
        path = self.data_root / "incoming" / row["filename"]
        with Image.open(path) as source:
            image = ImageOps.exif_transpose(source).convert("RGB")
        width, height = image.size
        scale = min(980 / width, 680 / height, 1.0)
        shown = image.resize((round(width * scale), round(height * scale)))
        x0 = (1000 - shown.width) // 2
        y0 = (700 - shown.height) // 2
        self.image_bounds = (x0, y0, shown.width, shown.height)
        self.photo = ImageTk.PhotoImage(shown)
        self.canvas.delete("all")
        self.canvas.create_image(x0, y0, image=self.photo, anchor="nw")
        self.title.config(text=f"{self.index + 1}/{len(self.rows)}  {row['filename']}  ID: {row['doc_id']}")
        if row.get("doc_type", "").strip().lower() == "label":
            self.class_id.set(1)
        else:
            self.class_id.set(0)
        self.draw_existing()

    def draw_existing(self) -> None:
        path = self.label_path()
        if not path.exists():
            return
        try:
            class_id, cx, cy, w, h = map(float, path.read_text(encoding="ascii").split())
        except (ValueError, OSError):
            messagebox.showwarning("Invalid label", f"Could not read {path}")
            return
        self.class_id.set(int(class_id))
        x0, y0, iw, ih = self.image_bounds
        left, top = x0 + (cx - w / 2) * iw, y0 + (cy - h / 2) * ih
        right, bottom = x0 + (cx + w / 2) * iw, y0 + (cy + h / 2) * ih
        self.box = self.canvas.create_rectangle(left, top, right, bottom, outline="#00ff66", width=3)

    def clamp(self, x: int, y: int) -> tuple[int, int]:
        x0, y0, iw, ih = self.image_bounds
        return max(x0, min(x0 + iw, x)), max(y0, min(y0 + ih, y))

    def start_box(self, event: tk.Event) -> None:
        self.start = self.clamp(event.x, event.y)
        if self.box is not None:
            self.canvas.delete(self.box)
        self.box = self.canvas.create_rectangle(*self.start, *self.start, outline="#00ff66", width=3)

    def drag_box(self, event: tk.Event) -> None:
        if self.start is not None and self.box is not None:
            self.canvas.coords(self.box, *self.start, *self.clamp(event.x, event.y))

    def end_box(self, event: tk.Event) -> None:
        if self.start is None or self.box is None:
            return
        x1, y1 = self.start
        x2, y2 = self.clamp(event.x, event.y)
        self.start = None
        if abs(x2 - x1) < 5 or abs(y2 - y1) < 5:
            self.canvas.delete(self.box)
            self.box = None
            return
        x0, y0, iw, ih = self.image_bounds
        left, right = sorted((x1, x2))
        top, bottom = sorted((y1, y2))
        cx = ((left + right) / 2 - x0) / iw
        cy = ((top + bottom) / 2 - y0) / ih
        w = (right - left) / iw
        h = (bottom - top) / ih
        path = self.label_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"{self.class_id.get()} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}\n", encoding="ascii")

    def change(self, direction: int) -> None:
        self.index = (self.index + direction) % len(self.rows)
        self.box = None
        self.show()

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, default=Path.home() / "SeminarLab")
    Labeler(parser.parse_args().data_root).run()
