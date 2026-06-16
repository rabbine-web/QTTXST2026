"""
Torus Braid Visualizer — Interactive
=====================================
Click a crossing cell to cycle through three modes:
  Mode 0 (default): X crossing (over/under strands)
  Mode 1: Two vertical lines (left edge and right edge of cell)
  Mode 2: Two horizontal lines (top edge and bottom edge of cell)
"""

import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np

from ..Computation.TemperleyToState import *


def draw_torus_braid(p: int, q: int, ax=None, title=None, initial_modes=None):
    """
    initial_modes: dict mapping (col, row) -> mode (0,1,2) for crossing cells.
                   Crossings not in the dict default to mode 0.
    """
    if q < 2:
        raise ValueError("q must be >= 2.")
    if p < 1:
        raise ValueError("p must be >= 1.")

    rows = q - 1
    cols = p * (q - 1)

    if ax is None:
        ax = plt.gca()

    lw    = 2.5
    gap   = 0.18
    color = "#1a6fc4"

    def is_crossing(col, row):
        if col < 0 or col >= cols or row < 0 or row >= rows:
            return False
        return (row % (q - 1)) == (col % (q - 1))

    def strand_y(col, row):
        has_crossing_below = any(is_crossing(col, r) for r in range(0, row))
        has_crossing_above = any(is_crossing(col, r) for r in range(row + 1, rows))
        if has_crossing_below and has_crossing_above:
            return row, row + 1
        elif has_crossing_below:
            return row + 1, row + 1
        elif has_crossing_above:
            return row, row
        else:
            return row + 0.5, row + 0.5

    # Track crossing mode: (col, row) -> 0, 1, or 2
    crossing_modes = {}
    # Store the artists for each crossing cell so we can redraw them
    crossing_artists = {}

    def draw_crossing(col, row, mode):
        """Draw (or redraw) a crossing cell in the given mode. Returns list of artists."""
        xl, xr = col, col + 1
        yb, yt = row, row + 1
        cx, cy = col + 0.5, row + 0.5
        artists = []

        if mode == 0:
            # Over-strand: bottom-left → top-right
            ln, = ax.plot([xl, xr], [yb, yt],
                          color=color, lw=lw, solid_capstyle="butt", zorder=4)
            artists.append(ln)
            # Under-strand: top-left → bottom-right, broken
            ln, = ax.plot([xl,       cx - gap], [yt,       cy + gap],
                          color=color, lw=lw, solid_capstyle="butt", zorder=3)
            artists.append(ln)
            ln, = ax.plot([cx + gap, xr      ], [cy - gap, yb      ],
                          color=color, lw=lw, solid_capstyle="butt", zorder=3)
            artists.append(ln)

        elif mode == 1:
            # Two horizontals: top edge and bottom edge (straight lines)
            ln, = ax.plot([xl, xr], [yt, yt],
                          color=color, lw=lw, solid_capstyle="butt", zorder=4)
            artists.append(ln)
            ln, = ax.plot([xl, xr], [yb, yb],
                          color=color, lw=lw, solid_capstyle="butt", zorder=4)
            artists.append(ln)

        elif mode == 2:
            # Two arcs on left and right edges, curving inward toward cell centre
            t = np.linspace(0, 1, 60)
            # Left arc: (xl,yb) -> (xl,yt), control point pulled right to cx
            bx = (1-t)**2*xl + 2*(1-t)*t*cx + t**2*xl
            by = (1-t)**2*yb + 2*(1-t)*t*cy + t**2*yt
            ln, = ax.plot(bx, by, color=color, lw=lw, solid_capstyle="butt", zorder=4)
            artists.append(ln)
            # Right arc: (xr,yb) -> (xr,yt), control point pulled left to cx
            bx = (1-t)**2*xr + 2*(1-t)*t*cx + t**2*xr
            by = (1-t)**2*yb + 2*(1-t)*t*cy + t**2*yt
            ln, = ax.plot(bx, by, color=color, lw=lw, solid_capstyle="butt", zorder=4)
            artists.append(ln)

        return artists

    # Initial draw
    for col in range(cols):
        for row in range(rows):
            xl, xr = col, col + 1
            yb, yt = row, row + 1

            if is_crossing(col, row):
                mode = (initial_modes or {}).get((col, row), 0)
                crossing_modes[(col, row)] = mode
                crossing_artists[(col, row)] = draw_crossing(col, row, mode)
            else:
                y_left, y_right = strand_y(col, row)
                ax.plot([xl, xr], [y_left, y_right],
                        color=color, lw=lw, solid_capstyle="butt", zorder=2)


    ax.set_xlim(-0.05, cols + 0.05)
    ax.set_ylim(-0.1,  rows + 0.1)
    ax.axis("off")

    def on_click(event):
        if event.inaxes is not ax:
            return
        # Convert click to grid cell
        col = int(np.floor(event.xdata))
        row = int(np.floor(event.ydata))
        if (col, row) not in crossing_modes:
            return
        # Remove old artists
        for artist in crossing_artists[(col, row)]:
            artist.remove()
        # Cycle mode
        new_mode = (crossing_modes[(col, row)] + 1) % 3
        crossing_modes[(col, row)] = new_mode
        crossing_artists[(col, row)] = draw_crossing(col, row, new_mode)
        ax.figure.canvas.draw_idle()

    ax.figure.canvas.mpl_connect("button_press_event", on_click)

def state_to_crossing_modes(state, p, q):
    """
    Convert an integer state to a crossing_modes dict for draw_torus_braid.
    Bit i of the reversed binary string maps to the i-th crossing (enumerated
    col-major, bottom-to-top). Bit value 1 -> mode 1, 0 -> mode 0.
    """
    rows = q - 1
    cols = p * (q - 1)
 
    def is_crossing(col, row):
        return (row % (q - 1)) == (col % (q - 1))
 
    # Enumerate crossings in the same order as the binary string (col-major, row asc)
    crossings = [
        (col, row)
        for col in range(cols)
        for row in range(rows)
        if is_crossing(col, row)
    ]
 
    modes = {}
    for i, (col, row) in enumerate(crossings):
        bit = (state >> i) & 1
        modes[(col, row)] = 2 if bit else 1
    return modes

def display_state_set(state_set, p, q, title="Kauffman States"):
    """
    Display all states in state_set as torus braid diagrams in a single window.
    Each diagram is labelled with its reversed binary string.
    """
    states = sorted(state_set)
    num_states = len(states)
    if num_states == 0:
        print("Empty set — nothing to display.")
        return
 
    # Lay out in a grid, roughly square
    ncols = int(np.ceil(np.sqrt(num_states)))
    nrows = int(np.ceil(num_states / ncols))
 
    cell_w = p * (q - 1)
    cell_h = (q - 1)
    fig_w  = ncols * cell_w * 0.8
    fig_h  = nrows * cell_h * 0.5 + nrows * 0.4   # extra for labels
 
    fig, axes = plt.subplots(nrows, ncols,
                             figsize=(max(fig_w, 4), max(fig_h, 3)),
                             facecolor="#f7f7f5")
    fig.suptitle(title, fontsize=13, y=1.01)
 
    # Flatten axes array for easy indexing
    if nrows == 1 and ncols == 1:
        axes = np.array([[axes]])
    elif nrows == 1:
        axes = axes[np.newaxis, :]
    elif ncols == 1:
        axes = axes[:, np.newaxis]
 
    total_bits = p * (q - 1)
 
    for idx, state in enumerate(states):
        r, c = divmod(idx, ncols)
        ax = axes[r][c]
        ax.set_facecolor("#f7f7f5")
        modes = state_to_crossing_modes(state, p, q)
        draw_torus_braid(p, q, ax=ax, initial_modes=modes)
        label = format(state, f'0{total_bits}b')[::-1]
        ax.set_title(label, fontsize=9, pad=3, family="monospace")
 
    # Hide any unused axes
    for idx in range(num_states, nrows * ncols):
        r, c = divmod(idx, ncols)
        axes[r][c].axis("off")
 
    plt.tight_layout()
    plt.show()


def output_str_to_crossing_modes(out_str, p, q):
    """
    Map the transform() output string directly to crossing modes.
      '0' -> mode 1  (two horizontals)
      '1' -> mode 2  (two arcs)
    Crossings are enumerated col-major, row ascending (matching state_to_crossing_modes).
    """
    rows = q - 1
    cols = p * (q - 1)

    def is_crossing(col, row):
        return (row % (q - 1)) == (col % (q - 1))

    crossings = [
        (col, row)
        for col in range(cols)
        for row in range(rows)
        if is_crossing(col, row)
    ]

    modes = {}
    for i, (col, row) in enumerate(crossings):
        if i < len(out_str):
            modes[(col, row)] = 2 if out_str[i] == '1' else 1
    return modes


def visualize_from_input(in_str):
    q = 3
    p = len(in_str)          # p == k
    out_str = transform(in_str)

    print(f"Input  ({len(in_str):2d} bits): {in_str}")
    print(f"Output ({len(out_str):2d} bits): {out_str}")

    modes = output_str_to_crossing_modes(out_str, p, q)

    fig, ax = plt.subplots(figsize=(p * (q-1), (q-1) * 0.9), facecolor="#f7f7f5")
    ax.set_facecolor("#f7f7f5")
    draw_torus_braid(p, q, ax=ax, initial_modes=modes)
    ax.set_title(f"TL-Word: {in_str}  →  Kauffman: {out_str}", fontsize=10, family="monospace", pad=6)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":

    visualize_from_input("011011")

    
