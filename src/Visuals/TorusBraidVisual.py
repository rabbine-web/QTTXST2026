"""
display/TorusBraidVisual.py

Torus braid visualizer.

Click a crossing cell to cycle through three rendering modes:
  Mode 0 – X crossing (over/under strands)
  Mode 1 – Two horizontal lines (top and bottom edges of cell)
  Mode 2 – Two arcs on left/right edges curving inward

Public API:
  draw_torus_braid          – draw onto an existing Axes (interactive)
  state_to_crossing_modes   – integer state  → crossing-modes dict
  output_str_to_crossing_modes – binary string → crossing-modes dict
  visualize_kauffman_state  – binary string  → Figure (for embedding)
  visualize_tlword          – TL-word string → Figure (for embedding)
  state_set_display         – set of states  → grid Figure
"""

import numpy as np
import matplotlib.pyplot as plt

from src.Computation.TemperleyLieb import kauffmanstates

# ── TL-word → Kauffman state transform ────────────────────────────────────

def transform(in_str: str, p: int = None) -> str:
    """Convert a TL-word binary string to its Kauffman state binary string."""
    out = []
    for i in range(len(in_str) - 1, -1, -1):
        if in_str[i] == "1":
            out = ["0", "1"] + out
        else:
            if out and out[0] == "0":
                out[0] = "1"
            else:
                out = ["1", "0"] + out
    result = "".join(out)
    pad = 2 * (p if p is not None else len(in_str))
    return result.zfill(pad)


# ── Core drawing ───────────────────────────────────────────────────────────

def draw_torus_braid(
    p: int,
    q: int,
    ax,
    title: str = None,
    initial_modes: dict = None,
) -> None:
    """
    Draw an interactive torus braid on ax.

    Parameters
    ----------
    p              : number of full twists (k)
    q              : number of strands    (n)
    ax             : matplotlib Axes to draw on
    initial_modes  : dict mapping (col, row) → mode {0, 1, 2};
                     crossings absent from dict default to mode 0
    """
    if q < 2:
        raise ValueError("q must be >= 2.")
    if p < 1:
        raise ValueError("p must be >= 1.")

    rows = q - 1
    cols = p * (q - 1)
    lw   = 2.5
    gap  = 0.18
    color = "#1a6fc4"

    def is_crossing(col: int, row: int) -> bool:
        if col < 0 or col >= cols or row < 0 or row >= rows:
            return False
        return (row % (q - 1)) == (col % (q - 1))

    def strand_y(col: int, row: int) -> tuple[float, float]:
        below = any(is_crossing(col, r) for r in range(0, row))
        above = any(is_crossing(col, r) for r in range(row + 1, rows))
        if below and above:
            return row, row + 1
        elif below:
            return row + 1, row + 1
        elif above:
            return row, row
        return row + 0.5, row + 0.5

    crossing_modes:   dict = {}
    crossing_artists: dict = {}

    def draw_crossing(col: int, row: int, mode: int) -> list:
        xl, xr = col, col + 1
        yb, yt = row, row + 1
        cx, cy = col + 0.5, row + 0.5
        artists = []

        if mode == 0:
            ln, = ax.plot([xl, xr], [yb, yt], color=color, lw=lw,
                          solid_capstyle="butt", zorder=4)
            artists.append(ln)
            ln, = ax.plot([xl, cx - gap], [yt, cy + gap], color=color, lw=lw,
                          solid_capstyle="butt", zorder=3)
            artists.append(ln)
            ln, = ax.plot([cx + gap, xr], [cy - gap, yb], color=color, lw=lw,
                          solid_capstyle="butt", zorder=3)
            artists.append(ln)

        elif mode == 1:
            ln, = ax.plot([xl, xr], [yt, yt], color=color, lw=lw,
                          solid_capstyle="butt", zorder=4)
            artists.append(ln)
            ln, = ax.plot([xl, xr], [yb, yb], color=color, lw=lw,
                          solid_capstyle="butt", zorder=4)
            artists.append(ln)

        elif mode == 2:
            t  = np.linspace(0, 1, 60)
            bx = (1-t)**2 * xl + 2*(1-t)*t * cx + t**2 * xl
            by = (1-t)**2 * yb + 2*(1-t)*t * cy + t**2 * yt
            ln, = ax.plot(bx, by, color=color, lw=lw, solid_capstyle="butt", zorder=4)
            artists.append(ln)
            bx = (1-t)**2 * xr + 2*(1-t)*t * cx + t**2 * xr
            ln, = ax.plot(bx, by, color=color, lw=lw, solid_capstyle="butt", zorder=4)
            artists.append(ln)

        return artists

    # Initial draw
    for col in range(cols):
        for row in range(rows):
            if is_crossing(col, row):
                mode = (initial_modes or {}).get((col, row), 0)
                crossing_modes[(col, row)]   = mode
                crossing_artists[(col, row)] = draw_crossing(col, row, mode)
            else:
                yl, yr = strand_y(col, row)
                ax.plot([col, col + 1], [yl, yr], color=color, lw=lw,
                        solid_capstyle="butt", zorder=2)

    ax.set_xlim(-0.05, cols + 0.05)
    ax.set_ylim(-0.1,  rows + 0.1)
    ax.axis("off")

    def on_click(event):
        if event.inaxes is not ax:
            return
        col = int(np.floor(event.xdata))
        row = int(np.floor(event.ydata))
        if (col, row) not in crossing_modes:
            return
        for artist in crossing_artists[(col, row)]:
            artist.remove()
        new_mode = (crossing_modes[(col, row)] + 1) % 3
        crossing_modes[(col, row)]   = new_mode
        crossing_artists[(col, row)] = draw_crossing(col, row, new_mode)
        ax.figure.canvas.draw_idle()

    ax.figure.canvas.mpl_connect("button_press_event", on_click)


# ── State / mode conversion helpers ───────────────────────────────────────

def state_to_crossing_modes(state: int, p: int, q: int) -> dict:
    """Integer state → crossing-modes dict.  Bit 1 → mode 2,  bit 0 → mode 1."""
    rows = q - 1
    cols = p * (q - 1)

    crossings = [
        (col, row)
        for col in range(cols)
        for row in range(rows)
        if (row % (q - 1)) == (col % (q - 1))
    ]
    return {
        (col, row): (2 if (state >> i) & 1 else 1)
        for i, (col, row) in enumerate(crossings)
    }


def output_str_to_crossing_modes(out_str: str, p: int, q: int) -> dict:
    """Binary string → crossing-modes dict.  '1' → mode 2,  '0' → mode 1."""
    rows = q - 1
    cols = p * (q - 1)

    crossings = [
        (col, row)
        for col in range(cols)
        for row in range(rows)
        if (row % (q - 1)) == (col % (q - 1))
    ]
    return {
        (col, row): (2 if i < len(out_str) and out_str[i] == "1" else 1)
        for i, (col, row) in enumerate(crossings)
    }


# ── Public visualization factories ─────────────────────────────────────────

def visualize_kauffman_state(state_str: str, p: int, q: int):
    """
    Return a matplotlib Figure for state_str on T(q, p).
    Sized to fill whatever Tk canvas it is embedded in.
    """
    modes  = output_str_to_crossing_modes(state_str, p, q)
    cols   = p * (q - 1)
    rows   = q - 1
    aspect = cols / max(rows, 1)

    fig, ax = plt.subplots(figsize=(8 * aspect, 8), facecolor="#f7f7f5")
    ax.set_facecolor("#f7f7f5")
    draw_torus_braid(p, q, ax=ax, initial_modes=modes)
    ax.set_title(f"Kauffman: {state_str}", fontsize=10, family="monospace", pad=6)
    return fig


def visualize_tlword(in_str: str, p: int = None):
    """Return a Figure for a TL-word string (transforms to Kauffman state first)."""
    q = 3
    if p is None:
        p = len(in_str)
    out_str = transform(in_str, p=p)

    print(f"Input  ({len(in_str):2d} bits): {in_str}")
    print(f"Output ({len(out_str):2d} bits): {out_str}")

    modes = output_str_to_crossing_modes(out_str, p, q)
    fig, ax = plt.subplots(
        figsize=(p * (q - 1), (q - 1) * 0.9),
        facecolor="#f7f7f5",
    )
    ax.set_facecolor("#f7f7f5")
    draw_torus_braid(p, q, ax=ax, initial_modes=modes)
    ax.set_title(
        f"TL-Word: {in_str}  →  Kauffman: {out_str}",
        fontsize=10, family="monospace", pad=6,
    )
    plt.tight_layout()
    return fig


def state_set_display(
    state_set,
    p: int,
    q: int,
    title: str = "Kauffman States",
):
    """Return a grid Figure of all states in state_set as torus braid diagrams."""
    states = sorted(state_set)
    if not states:
        print("Empty set — nothing to display.")
        return None

    ncols = int(np.ceil(np.sqrt(len(states))))
    nrows = int(np.ceil(len(states) / ncols))

    fig_w = max(ncols * p * (q - 1) * 0.8, 4)
    fig_h = max(nrows * (q - 1) * 0.5 + nrows * 0.4, 3)

    fig, axes = plt.subplots(
        nrows, ncols,
        figsize=(fig_w, fig_h),
        facecolor="#f7f7f5",
    )
    fig.suptitle(title, fontsize=13, y=1.01)

    if nrows == 1 and ncols == 1:
        axes = np.array([[axes]])
    elif nrows == 1:
        axes = axes[np.newaxis, :]
    elif ncols == 1:
        axes = axes[:, np.newaxis]

    total_bits = p * (q - 1)
    for idx, state in enumerate(states):
        r, c = divmod(idx, ncols)
        ax   = axes[r][c]
        ax.set_facecolor("#f7f7f5")
        draw_torus_braid(p, q, ax=ax, initial_modes=state_to_crossing_modes(state, p, q))
        ax.set_title(
            format(state, f"0{total_bits}b")[::-1],
            fontsize=9, pad=3, family="monospace",
        )

    for idx in range(len(states), nrows * ncols):
        r, c = divmod(idx, ncols)
        axes[r][c].axis("off")

    plt.tight_layout()
    return fig