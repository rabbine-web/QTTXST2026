"""
survivors_diagram.py

igraph visualization of the TL chain complex (survivors only).

  - Only survivor nodes and their maps are shown
  - Click node → detail window: torus braid diagram + node info
  - Click edge → info panel: map type and both endpoint words
  - Edge colours:
      blue   – direct differential map only
      purple – indirect map only
      green  – both direct and indirect
"""

import sys
import tkinter as tk
from collections import defaultdict

import igraph as ig
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from src.Computation.TemperleyLieb import temperleylieb
from src.Computation.mapping import (
    build_direct_maps,
    build_iso_pairs,
    build_indirect_maps,
    popcount,
    node_id
)
from src.Visuals.TorusBraidVisual import visualize_kauffman_state


# ── Palette ────────────────────────────────────────────────────────────────

PALETTE = {
    "bg":             "#0f1117",
    "node_fill":      "#1e2230",
    "node_frame":     "#4a90d9",
    "node_label":     "#e8eaf0",
    "edge_direct":    "#4a90d9",
    "edge_indirect":  "#a259e0",
    "edge_both":      "#50c8a0",
    "panel_bg":       "#161922",
    "panel_border":   "#2a2f3f",
    "text_primary":   "#e8eaf0",
    "text_secondary": "#8892a4",
    "accent":         "#4a90d9",
    "close_btn":      "#2a2f3f",
    "close_hover":    "#3a3f4f",
}

FONT_MONO  = ("JetBrains Mono", 10)     if sys.platform != "win32" else ("Consolas", 10)
FONT_TITLE = ("JetBrains Mono", 12, "bold") if sys.platform != "win32" else ("Consolas", 12, "bold")
FONT_LABEL = ("JetBrains Mono", 9)     if sys.platform != "win32" else ("Consolas", 9)


# ── Helpers ────────────────────────────────────────────────────────────────

def tl_word(state: int, sign: int, n: int, k: int) -> str:
    gens   = temperleylieb(state, n, k)
    word   = "".join(f"e{g}" for g in gens)
    suffix = {1: " (+)", -1: " (−)", 0: ""}
    return (word or "1") + suffix.get(sign, "")


def bin_str(state: int, n: int, k: int) -> str:
    crossings = k * (n - 1)
    return "".join(str((state >> i) & 1) for i in range(crossings))


def sign_label(sign: int) -> str:
    return {1: "+", -1: "−", 0: "0"}.get(sign, "?")


# ── Graph data ─────────────────────────────────────────────────────────────

def build_graph_data(n: int, k: int):
    direct, incoming                        = build_direct_maps(n, k)
    generators, removed, survivors, iso_pairs = build_iso_pairs(n, k)
    indirect                                = build_indirect_maps(
        iso_pairs, direct, incoming, generators
    )

    survivor_set = set(survivors)

    # signs_for is intentionally restricted to survivors only.
    # Using all generators here would add direct edges that include
    # cancelled (state, sign) pairs, preventing "both" edges from
    # being detected when an indirect map shares the same endpoint pair.
    survivor_signs_for: dict[int, list[int]] = {}
    for state, sign in survivor_set:
        survivor_signs_for.setdefault(state, []).append(sign)

    # ── nodes ──
    nodes = []
    for state, sign in sorted(
        survivor_set,
        key=lambda x: (popcount(x[0]), x[0], x[1]),
    ):
        nodes.append({
            "id":    node_id(state, sign),
            "bin":   bin_str(state, n, k),
            "word":  tl_word(state, sign, n, k),
            "row":   popcount(state),
            "sign":  sign,
            "state": state,
        })

    node_id_set = {nd["id"] for nd in nodes}

    # ── edges ──
    edge_map: dict[tuple, set] = {}

    def add_edge(src_id: str, tgt_id: str, etype: str) -> None:
        if src_id not in node_id_set or tgt_id not in node_id_set:
            return
        edge_map.setdefault((src_id, tgt_id), set()).add(etype)

    # Direct edges — only between survivor sign-variants
    for src_state, tgt_states in direct.items():
        for src_sign in survivor_signs_for.get(src_state, []):
            sid = node_id(src_state, src_sign)
            for tgt_state in tgt_states:
                for tgt_sign in survivor_signs_for.get(tgt_state, []):
                    add_edge(sid, node_id(tgt_state, tgt_sign), "direct")

    # Indirect edges
    for X, signX, Y, signY, A, sA, B, sB in indirect:
        add_edge(node_id(X, signX), node_id(Y, signY), "indirect")

    edges = []
    for (src_id, tgt_id), types in edge_map.items():
        etype = "both" if len(types) > 1 else next(iter(types))
        edges.append({"src": src_id, "tgt": tgt_id, "type": etype})

    # ── iso lookup for info panels ──
    iso_lookup = {}
    for A, sA, B, sB in iso_pairs:
        iso_lookup[node_id(A, sA)] = ("source", B, sB)
        iso_lookup[node_id(B, sB)] = ("target", A, sA)

    return nodes, edges, iso_lookup


# ── igraph object ──────────────────────────────────────────────────────────

def build_igraph(nodes: list, edges: list):
    g = ig.Graph(directed=True)
    g.add_vertices(len(nodes))

    for i, nd in enumerate(nodes):
        g.vs[i]["name"]  = nd["id"]
        g.vs[i]["bin"]   = nd["bin"]
        g.vs[i]["word"]  = nd["word"]
        g.vs[i]["row"]   = nd["row"]
        g.vs[i]["sign"]  = nd["sign"]
        g.vs[i]["state"] = nd["state"]
        g.vs[i]["label"] = nd["bin"]

    id_to_idx  = {nd["id"]: i for i, nd in enumerate(nodes)}
    edge_list  = []
    edge_types = []

    for e in edges:
        si = id_to_idx.get(e["src"])
        ti = id_to_idx.get(e["tgt"])
        if si is None or ti is None:
            continue
        edge_list.append((si, ti))
        edge_types.append(e["type"])

    g.add_edges(edge_list)
    g.es["type"] = edge_types
    return g, id_to_idx


# ── Layout ─────────────────────────────────────────────────────────────────

def make_layout(g, nodes: list, n: int, k: int) -> ig.Layout:
    rows: dict[int, list[int]] = defaultdict(list)
    for i, nd in enumerate(nodes):
        rows[nd["row"]].append(i)

    max_row  = max(rows.keys()) if rows else 1
    max_cols = max(len(v) for v in rows.values()) if rows else 1

    x_spacing = max(3.5, max_cols * 0.9)
    y_spacing = max(5.0, max_row  * 1.3)

    coords = [None] * len(nodes)
    for row, idxs in rows.items():
        n_in_row = len(idxs)
        for j, idx in enumerate(sorted(idxs)):
            x = (j - (n_in_row - 1) / 2.0) * x_spacing
            y = -(row / max_row) * y_spacing * max_row
            coords[idx] = (x, y)

    return ig.Layout(coords)


# ── Info panel ─────────────────────────────────────────────────────────────

class InfoPanel:
    """Singleton dark-themed info panel that refreshes in place."""

    def __init__(self):
        self._win   = None
        self._frame = None

    def show(self, title: str, rows: list[tuple[str, str]]) -> None:
        if self._win is not None:
            try:
                self._win.winfo_exists()
                for w in self._frame.winfo_children():
                    w.destroy()
            except Exception:
                self._win = None

        if self._win is None:
            self._win = tk.Toplevel()
            self._win.configure(bg=PALETTE["panel_bg"])
            self._win.geometry("500x380")
            self._win.resizable(False, False)
            self._win.protocol("WM_DELETE_WINDOW", self._close)

            tk.Frame(self._win, bg=PALETTE["accent"], height=3).pack(fill=tk.X, side=tk.TOP)

            tk.Button(
                self._win, text="✕", command=self._close,
                font=FONT_LABEL, bg=PALETTE["close_btn"],
                fg=PALETTE["text_secondary"], relief="flat",
                padx=10, pady=4, cursor="hand2",
                activebackground=PALETTE["close_hover"],
                activeforeground=PALETTE["text_primary"],
            ).pack(side=tk.BOTTOM, pady=12)

            self._frame = tk.Frame(
                self._win, bg=PALETTE["panel_bg"], padx=24, pady=20
            )
            self._frame.pack(fill=tk.BOTH, expand=True)

        self._win.title(title)
        self._win.lift()
        self._win.focus_force()

        tk.Label(
            self._frame, text=title,
            font=FONT_TITLE,
            bg=PALETTE["panel_bg"], fg=PALETTE["accent"],
            anchor="w",
        ).pack(fill=tk.X, pady=(0, 16))

        for label, value in rows:
            if label == "" and value == "":
                tk.Frame(
                    self._frame, bg=PALETTE["panel_border"], height=1
                ).pack(fill=tk.X, pady=8)
                continue
            row_frame = tk.Frame(self._frame, bg=PALETTE["panel_bg"])
            row_frame.pack(fill=tk.X, pady=2)
            tk.Label(
                row_frame, text=label,
                font=FONT_LABEL, width=18, anchor="w",
                bg=PALETTE["panel_bg"], fg=PALETTE["text_secondary"],
            ).pack(side=tk.LEFT)
            tk.Label(
                row_frame, text=value,
                font=FONT_MONO, anchor="w",
                bg=PALETTE["panel_bg"], fg=PALETTE["text_primary"],
            ).pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _close(self) -> None:
        if self._win:
            self._win.destroy()
            self._win = None


# ── Detail window ──────────────────────────────────────────────────────────

_detail_win = None


def open_detail_window(nd: dict, n: int, k: int, iso_lookup: dict) -> None:
    global _detail_win

    state_str = nd["bin"]

    try:
        alive = _detail_win is not None and _detail_win.winfo_exists()
    except Exception:
        alive = False

    if not alive:
        _detail_win = tk.Toplevel()
        _detail_win.configure(bg=PALETTE["bg"])
        try:
            sw = _detail_win.winfo_screenwidth()
            sh = _detail_win.winfo_screenheight() - 40
            _detail_win.geometry(f"{sw // 2}x{sh}+{sw // 2}+0")
        except Exception:
            pass
    else:
        for w in _detail_win.winfo_children():
            w.destroy()

    _detail_win.title(f"State: {state_str}")
    _detail_win.lift()
    plt.close("detail")

    # torus braid figure (top 68%)
    top = tk.Frame(_detail_win, bg=PALETTE["bg"])
    top.place(relx=0, rely=0, relwidth=1.0, relheight=0.68)

    fig = visualize_kauffman_state(state_str, p=k, q=n)
    fig.set_label("detail")

    canvas = FigureCanvasTkAgg(fig, master=top)
    widget = canvas.get_tk_widget()
    widget.pack(fill=tk.BOTH, expand=True)
    canvas.draw()

    def on_resize(event):
        dpi  = fig.get_dpi()
        w_in = max(event.width  / dpi, 1)
        h_in = max(event.height / dpi, 1)
        fig.set_size_inches(w_in, h_in, forward=False)
        canvas.draw_idle()

    widget.bind("<Configure>", on_resize)

    # info panel (bottom 32%)
    bottom = tk.Frame(_detail_win, bg=PALETTE["panel_bg"])
    bottom.place(relx=0, rely=0.68, relwidth=1.0, relheight=0.32)

    tk.Frame(bottom, bg=PALETTE["accent"], height=3).pack(fill=tk.X)
    tk.Label(
        bottom, text=f"  {state_str}",
        font=FONT_TITLE, bg=PALETTE["panel_bg"], fg=PALETTE["accent"],
        anchor="w", pady=12,
    ).pack(fill=tk.X)
    tk.Frame(bottom, bg=PALETTE["panel_border"], height=1).pack(fill=tk.X, padx=16)

    info_rows = [
        ("Binary state", nd["bin"]),
        ("TL word",      nd["word"]),
        ("Row (degree)", str(nd["row"])),
        ("Sign",         sign_label(nd["sign"])),
    ]
    nid = nd["id"]
    if nid in iso_lookup:
        role, p_state, p_sign = iso_lookup[nid]
        info_rows.append(("Iso role",    "Source" if role == "source" else "Target"))
        info_rows.append(("Iso partner", bin_str(p_state, n, k)))

    for label, value in info_rows:
        rf = tk.Frame(bottom, bg=PALETTE["panel_bg"])
        rf.pack(fill=tk.X, padx=18, pady=2)
        tk.Label(rf, text=label, font=FONT_LABEL, width=14, anchor="w",
                 bg=PALETTE["panel_bg"], fg=PALETTE["text_secondary"]).pack(side=tk.LEFT)
        tk.Label(rf, text=value, font=FONT_MONO, anchor="w",
                 bg=PALETTE["panel_bg"], fg=PALETTE["text_primary"]).pack(side=tk.LEFT)


# ── Main run ───────────────────────────────────────────────────────────────

def run(n: int, k: int) -> None:
    nodes, edges, iso_lookup = build_graph_data(n, k)

    if not nodes:
        print(f"No survivors for n={n}, k={k}.")
        return

    g, id_to_idx = build_igraph(nodes, edges)
    layout       = make_layout(g, nodes, n, k)

    edge_color_map = {
        "direct":   PALETTE["edge_direct"],
        "indirect": PALETTE["edge_indirect"],
        "both":     PALETTE["edge_both"],
    }
    e_colors = [edge_color_map.get(g.es[i]["type"], PALETTE["edge_direct"])
                for i in range(g.ecount())]

    crossings = k * (n - 1)
    fig, ax = plt.subplots(figsize=(max(12, crossings * 2.0), max(9, crossings * 1.5)))
    fig.patch.set_facecolor(PALETTE["bg"])
    ax.set_facecolor(PALETTE["bg"])
    ax.set_title(
        f"TL Diagram — Survivors   n={n}  k={k}",
        fontsize=13, color=PALETTE["text_primary"], pad=14, fontfamily="monospace",
    )
    ax.tick_params(colors=PALETTE["text_secondary"])
    for spine in ax.spines.values():
        spine.set_edgecolor(PALETTE["panel_border"])

    ig.plot(
        g, target=ax, layout=layout,
        vertex_size=42,
        vertex_color=PALETTE["node_fill"],
        vertex_label=g.vs["label"],
        vertex_label_size=8,
        vertex_label_color=PALETTE["node_label"],
        vertex_frame_color=PALETTE["node_frame"],
        vertex_frame_width=2.0,
        edge_color=e_colors,
        edge_width=1.8,
        edge_arrow_size=12,
        edge_arrow_width=7,
        edge_curved=0.18,
    )

    ax.legend(
        handles=[
            mpatches.Patch(color=PALETTE["edge_direct"],   label="Direct"),
            mpatches.Patch(color=PALETTE["edge_indirect"], label="Indirect"),
            mpatches.Patch(color=PALETTE["edge_both"],     label="Direct + Indirect"),
        ],
        loc="upper right", fontsize=9, framealpha=0.85,
        facecolor=PALETTE["panel_bg"],
        edgecolor=PALETTE["panel_border"],
        labelcolor=PALETTE["text_primary"],
    )

    root = tk.Tk()
    root.title(f"TL Survivors  n={n}  k={k}")
    root.configure(bg=PALETTE["bg"])

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    canvas.draw()

    info       = InfoPanel()
    _pixel_pos = [None]

    def get_pixel_pos():
        return [ax.transData.transform(layout[i]) for i in range(len(nodes))]

    fig.canvas.mpl_connect("resize_event", lambda e: _pixel_pos.__setitem__(0, None))

    def on_click(event):
        if event.x is None or event.y is None:
            return
        if _pixel_pos[0] is None:
            _pixel_pos[0] = get_pixel_pos()

        xc, yc = event.x, event.y

        # Node hit-test
        best_ni, best_nd = None, float("inf")
        for i, (px, py) in enumerate(_pixel_pos[0]):
            d = ((xc - px) ** 2 + (yc - py) ** 2) ** 0.5
            if d < best_nd:
                best_nd, best_ni = d, i

        if best_nd <= 28 and best_ni is not None:
            open_detail_window(nodes[best_ni], n, k, iso_lookup)
            return

        # Edge hit-test — sample along the actual rendered curve (matches
        # igraph's edge_curved=0.18 quadratic Bezier) and measure distance
        # to the nearest line *segment* between samples (not just to the
        # sample points themselves), so the whole visible line/arrow is
        # clickable rather than only small dots along it.
        def curve_points(sx, sy, tx, ty, curvature=0.18, n_samples=24):
            mx, my = (sx + tx) / 2.0, (sy + ty) / 2.0
            dx, dy = tx - sx, ty - sy
            # perpendicular offset for the curve's control point
            cx = mx - dy * curvature
            cy = my + dx * curvature
            pts = []
            for s in range(n_samples + 1):
                t = s / n_samples
                # quadratic Bezier: (1-t)^2 * P0 + 2(1-t)t * Pc + t^2 * P1
                bx = (1 - t) ** 2 * sx + 2 * (1 - t) * t * cx + t ** 2 * tx
                by = (1 - t) ** 2 * sy + 2 * (1 - t) * t * cy + t ** 2 * ty
                pts.append((bx, by))
            return pts

        def point_segment_dist(px, py, ax0, ay0, bx0, by0):
            vx, vy = bx0 - ax0, by0 - ay0
            seg_len_sq = vx * vx + vy * vy
            if seg_len_sq == 0:
                return ((px - ax0) ** 2 + (py - ay0) ** 2) ** 0.5
            t = ((px - ax0) * vx + (py - ay0) * vy) / seg_len_sq
            t = max(0.0, min(1.0, t))
            cx0, cy0 = ax0 + t * vx, ay0 + t * vy
            return ((px - cx0) ** 2 + (py - cy0) ** 2) ** 0.5

        best_ei, best_ed = None, float("inf")
        for i in range(g.ecount()):
            e      = g.es[i]
            sx, sy = ax.transData.transform(layout[e.source])
            tx, ty = ax.transData.transform(layout[e.target])
            pts    = curve_points(sx, sy, tx, ty)
            for (ax0, ay0), (bx0, by0) in zip(pts[:-1], pts[1:]):
                d = point_segment_dist(xc, yc, ax0, ay0, bx0, by0)
                if d < best_ed:
                    best_ed, best_ei = d, i

        if best_ed <= 18 and best_ei is not None:
            e    = g.es[best_ei]
            src  = nodes[e.source]
            tgt  = nodes[e.target]
            type_label = {
                "direct":   "Direct differential map",
                "indirect": "Indirect map",
                "both":     "Direct + Indirect map",
            }[e["type"]]

            info.show(
                f"Edge  {src['bin']} → {tgt['bin']}",
                [
                    ("Map type",      type_label),
                    ("", ""),
                    ("Source (bin)",  src["bin"]),
                    ("Source (word)", src["word"]),
                    ("", ""),
                    ("Target (bin)",  tgt["bin"]),
                    ("Target (word)", tgt["word"]),
                    ("", ""),
                    ("Row shift",     f"{src['row']}  →  {tgt['row']}"),
                ],
            )

    fig.canvas.mpl_connect("button_press_event", on_click)
    root.mainloop()


# ── Entry point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    n = int(input("Enter n: "))
    k = int(input("Enter k: "))
    run(n, k)