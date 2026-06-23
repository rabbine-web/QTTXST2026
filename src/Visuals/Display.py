"""
display/containers.py

Tkinter layout primitives used across all visualization windows.

Classes:
  Container       – abstract base
  SingleContainer – holds one optional child
  VerticalSplit   – side-by-side layout  (.left / .right)
  HorizontalSplit – stacked layout       (.top  / .bottom)
  FigureContainer – embeds a matplotlib Figure
  Display         – top-level Tk window
"""

import tkinter as tk
from abc import ABC, abstractmethod
from typing import Optional

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# ── Container hierarchy ────────────────────────────────────────────────────

class Container(ABC):
    """Abstract base for all drawable containers."""

    @abstractmethod
    def draw(self, frame: tk.Frame) -> None:
        pass


class SingleContainer(Container):
    """Holds and renders one optional child container."""

    def __init__(self):
        self.content: Optional[Container] = None

    def draw(self, frame: tk.Frame) -> None:
        if self.content is not None:
            self.content.draw(frame)


class VerticalSplit(Container):
    """Side-by-side split. Children accessible via .left / .right."""

    def __init__(self, ratio: float = 0.5):
        self.ratio = max(0.0, min(1.0, ratio))
        self.left  = SingleContainer()
        self.right = SingleContainer()

    def draw(self, frame: tk.Frame) -> None:
        left_frame = tk.Frame(frame)
        left_frame.place(relx=0, rely=0, relwidth=self.ratio, relheight=1.0)

        right_frame = tk.Frame(frame)
        right_frame.place(
            relx=self.ratio, rely=0,
            relwidth=1.0 - self.ratio, relheight=1.0,
        )

        self.left.draw(left_frame)
        self.right.draw(right_frame)


class HorizontalSplit(Container):
    """Stacked split. Children accessible via .top / .bottom."""

    def __init__(self, ratio: float = 0.5):
        self.ratio = max(0.0, min(1.0, ratio))
        self.top    = SingleContainer()
        self.bottom = SingleContainer()

    def draw(self, frame: tk.Frame) -> None:
        top_frame = tk.Frame(frame)
        top_frame.place(relx=0, rely=0, relwidth=1.0, relheight=self.ratio)

        bottom_frame = tk.Frame(frame)
        bottom_frame.place(
            relx=0, rely=self.ratio,
            relwidth=1.0, relheight=1.0 - self.ratio,
        )

        self.top.draw(top_frame)
        self.bottom.draw(bottom_frame)


class FigureContainer(Container):
    """Embeds a matplotlib Figure into a Tk Frame."""

    def __init__(self, fig):
        self.fig = fig

    def draw(self, frame: tk.Frame) -> None:
        canvas = FigureCanvasTkAgg(self.fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


# ── Top-level window ───────────────────────────────────────────────────────

class Display:
    """
    Top-level Tk window.

    Usage::

        window = Display(title="My App")
        split  = VerticalSplit(ratio=0.6)
        split.left.content = FigureContainer(my_fig)
        window.content = split
        window.display()
        window.root.mainloop()
    """

    def __init__(
        self,
        title:      str       = "TITLE",
        fullscreen: bool      = True,
        content:    Container = None,
    ):
        self.root = tk.Tk()
        self.root.title(title)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self.fullscreen    = fullscreen
        self.content_frame = tk.Frame(self.root)
        self.content_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.content: Container = content or SingleContainer()

    def _on_close(self) -> None:
        self.root.destroy()
        self.root.quit()

    def display(self) -> None:
        self.content.draw(self.content_frame)
        try:
            if self.fullscreen:
                self.root.state("zoomed")
            else:
                sw = self.root.winfo_screenwidth()
                sh = self.root.winfo_screenheight() - 40
                ww = sw // 2
                self.root.geometry(f"{ww}x{sh}+{sw - ww - 7}+0")
        except Exception:
            pass

    def refresh(self) -> None:
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.content.draw(self.content_frame)