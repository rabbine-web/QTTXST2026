import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk

from itertools import product
from pathlib import Path

from .TorusBraidVisual import draw_torus_braid
from .Display import SingleContainer, Display


def generate_all_states(p, q):
    # Total number of crossings in the grid
    n_crossings = p * (q - 1)
    
    # 1. Identify and order the crossing coordinates
    crossings = []
    for col in range(n_crossings):
        for row in range(q - 1):
            if (row % (q - 1)) == (col % (q - 1)):
                crossings.append((col, row))
                
    # 2. Generate all binary string states for the crossings
    states = list(product([0, 1], repeat=n_crossings))
    
    # 3. Group states by the number of 1s they contain (these are our columns)
    layers = {}
    for state in states:
        n_ones = sum(state)
        if n_ones not in layers:
            layers[n_ones] = []
        layers[n_ones].append(state)
        
    n_layers = n_crossings + 1
    max_height = max(len(layer) for layer in layers.values())
    
    # Dimensions for calculating figure size
    cell_w = p * 0.9
    cell_h = q * 0.6
    
    # 4. Create a blank figure
    fig = plt.figure(figsize=(n_layers * cell_w, max_height * cell_h), facecolor="#f7f7f5")
    
    # Set up coordinate grid logic (0.0 to 1.0)
    margin_x = 0.05
    margin_y = 0.05
    usable_w = 1.0 - 2 * margin_x
    usable_h = 1.0 - 2 * margin_y
    
    col_w = usable_w / n_layers
    row_h = usable_h / max_height
    
    # Padding inside each cell to prevent crowding
    ax_w = col_w * 0.8
    ax_h = row_h * 0.8
    
    # 5. Populate the canvas using exact mathematical placement
    for n_ones in range(n_layers):
        layer_states = layers.get(n_ones, [])
        col_count = len(layer_states)
        
        # X center for the entire column
        cx = margin_x + (n_ones * col_w) + (col_w / 2)
        
        for i, state in enumerate(layer_states):
            # Y center for this specific state. 
            # 0.5 is the absolute center of the figure. We stack up/down from there.
            cy = 0.5 + ((col_count - 1) * row_h / 2) - (i * row_h)
            
            # Bounding box for the axes: [left, bottom, width, height]
            left = cx - (ax_w / 2)
            bottom = cy - (ax_h / 2)
            
            # Add axes directly to the figure at the computed coordinates
            ax = fig.add_axes([left, bottom, ax_w, ax_h])
            ax.axis("off")
            
            # Map binary state (0/1) to visual modes (1/2)
            initial_modes = {}
            for bit, coord in zip(state, crossings):
                initial_modes[coord] = 1 if bit == 0 else 2
                
            # Draw the state
            draw_torus_braid(p, q, ax=ax, initial_modes=initial_modes)
            
            # Label
            binary_str = "".join(map(str, state))
            ax.set_title(binary_str, fontsize=8, pad=2)
            
        # Draw the vertical black separator line to the right of this column 
        # (Skipping the final column)
        if n_ones < n_layers - 1:
            line_x = margin_x + ((n_ones + 1) * col_w)
            line = mlines.Line2D(
                [line_x, line_x], 
                [margin_y, 1.0 - margin_y], 
                color="black", 
                linewidth=1.5, 
                zorder=0
            )
            fig.add_artist(line)
            
    return fig


class ResolutionCube(SingleContainer):
    """Display a resolution cube (all states of a braid) in a tkinter frame."""

    def __init__(self, p: int, q: int):
        super().__init__()

        self.p = p
        self.q = q

    def draw(self, frame: tk.Frame) -> None:
        """Generate and display the resolution cube in the provided frame."""
        fig = generate_all_states(self.p, self.q)
        
        # Embed the matplotlib figure in the tkinter frame
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    window = Display(title="Braid Resolution")
    cube = ResolutionCube(p=2, q=4)
    window.content = cube
    window.display()
