import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from abc import ABC, abstractmethod
from typing import Optional


class Container(ABC):
    """Abstract base for all drawable containers.

    Containers receive a frame and render themselves into it.
    They know nothing about their parents.
    """

    @abstractmethod
    def draw(self, frame: tk.Frame) -> None:
        """Render this container into the provided frame.

        Subclasses must implement this.
        """
        pass


class SingleContainer(Container):
    """A container that holds and renders a single child container."""

    def __init__(self):
        self.content: Optional[Container] = None

    def draw(self, frame: tk.Frame) -> None:
        """Render the child if present into the provided frame."""
        if self.content is None:
            return
        self.content.draw(frame)


class VerticalSplit(Container):
    """Create vertical split. `self.left` and `self.right` are containers."""

    def __init__(self, ratio: float = 0.5):

        self.ratio = max(0.0, min(1.0, ratio))
        self.left = SingleContainer()
        self.right = SingleContainer()

    def draw(self, frame: tk.Frame) -> None:
        """Place left and right containers into subframes and render them."""
        left_frame = tk.Frame(frame)
        left_frame.place(relx=0, rely=0, relwidth=self.ratio, relheight=1.0)
        
        right_frame = tk.Frame(frame)
        right_frame.place(relx=self.ratio, rely=0, relwidth=1.0 - self.ratio, relheight=1.0)
        
        self.left.draw(left_frame)
        self.right.draw(right_frame)


class HorizontalSplit(Container):
    """Create horizontal split. `self.top` and `self.bottom` are containers."""

    def __init__(self, ratio: float = 0.5):
        self.ratio = max(0.0, min(1.0, ratio))
        self.top = SingleContainer()
        self.bottom = SingleContainer()

    def draw(self, frame: tk.Frame) -> None:
        """Place top and bottom containers into subframes and render them."""
        top_frame = tk.Frame(frame)
        top_frame.place(relx=0, rely=0, relwidth=1.0, relheight=self.ratio)
        
        bottom_frame = tk.Frame(frame)
        bottom_frame.place(relx=0, rely=self.ratio, relwidth=1.0, relheight=1.0 - self.ratio)
        
        self.top.draw(top_frame)
        self.bottom.draw(bottom_frame)


class FigureContainer(Container):
    def __init__(self, fig):
        self.fig = fig

    def draw(self, frame: tk.Frame) -> None:
        canvas = FigureCanvasTkAgg(self.fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


class Display:
    """
    Usage example:

        window = Display(title="My App")

        split = VerticalSplit(ratio=0.6)
        graph1 = SomeCustomContainer()

        split.left = graph1
        window.content = split

        window.display()
    """

    def __init__(self, title: str = "TITLE", 
                 content: Container = SingleContainer()):

        self.root = tk.Tk()
        self.root.title(title)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # Root content frame
        self.content_frame = tk.Frame(self.root)
        self.content_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        # Root container
        self.content = content

    def _on_close(self) -> None:
        """Handle window close event."""
        self.root.destroy()
        self.root.quit()

    def display(self) -> None:
        """Draw content and show the window."""
        # Draw the content into the frame
        self.content.draw(self.content_frame)

        # Window starts maximized
        try:
            self.root.state('zoomed')
        except Exception:
            pass

        self.root.mainloop()
