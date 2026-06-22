"""
survivors_diagram.py

Diagram showing only surviving states after Gaussian elimination —
iso-pair nodes and iso edges are hidden.

Node label:  binary string (LSB-first) on top line
             TL word below  e.g.  e1e2(+)
Edge labels:
  direct   – sorted TL gens of target; newly-added bit written εi
  indirect – Y's generators; bits new relative to X are ε, existing are e
  both     – single dark-pink edge, direct label only

Usage:
    python survivors_diagram.py
    > Enter n: 3
    > Enter k: 2
    Outputs survivors_n3_k2.html
"""

import os, json, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from elimination.week1 import kauffmanstates, temperleylieb
from elimination.gaussian_SourceTarget_indicator import build_generators, source_matches, has_circle, bit

from mapping.all_maps import (
    build_direct_maps, build_iso_pairs, build_indirect_maps,
    popcount, state_to_bin, node_id,
)


# ---------------------------------------------------------------------------
# TL word string
# ---------------------------------------------------------------------------
def tl_word(state, sign, n, k):
    """Return the TL word string for a signed Kauffman state."""
    gens = temperleylieb(state, n, k)
    word = "".join(f"e{g}" for g in gens)
    if sign == 1:    word += "(+)"
    elif sign == -1: word += "(-)"
    return word if word else "1"


# ---------------------------------------------------------------------------
# Edge label for a direct map src_state -> tgt_state
# ---------------------------------------------------------------------------
def edge_label_direct(src_state, tgt_state, n, k):
    """
    Build the edge label for a direct map.
    The newly-added generator bit is written εi; existing ones are ei.
    """
    diff          = tgt_state ^ src_state
    bit_pos       = diff.bit_length() - 1
    crossings     = k * (n - 1)
    tgt_gens      = temperleylieb(tgt_state, n, k)
    tgt_crossings = [i for i in range(crossings) if (tgt_state >> i) & 1]
    parts = []
    for crossing, g in zip(tgt_crossings, tgt_gens):
        if crossing == bit_pos:
            parts.append(f"\u03b5{g}")   # ε – newly added bit
        else:
            parts.append(f"e{g}")
    return "".join(parts)


# ---------------------------------------------------------------------------
# Indirect map label
# ---------------------------------------------------------------------------
def compose_indirect_word(X, signX, Y, signY, A, sA, B, sB, n, k):
    """
    Build the edge label for an indirect (iso-composed) map X -> Y.
    Bits of Y already present in X are written ei; new bits are εi.
    """
    crossings     = k * (n - 1)
    tgt_gens      = temperleylieb(Y, n, k)
    tgt_crossings = [i for i in range(crossings) if (Y >> i) & 1]
    parts = []
    for crossing, g in zip(tgt_crossings, tgt_gens):
        if (X >> crossing) & 1:
            parts.append(f"e{g}")
        else:
            parts.append(f"\u03b5{g}")   # ε – bit new relative to X
    return "".join(parts)


# ---------------------------------------------------------------------------
# Build node/edge data — survivors only
# ---------------------------------------------------------------------------
def build_tl_diagram(n, k):
    """
    Compute nodes and edges for the survivors-only TL diagram.

    Returns
    -------
    nodes_data : list[dict]
    edges_data : list[dict]
    """
    crossings = k * (n - 1)
    direct, incoming = build_direct_maps(n, k)
    generators, removed, survivors, iso_pairs = build_iso_pairs(n, k)
    indirect = build_indirect_maps(iso_pairs, direct, incoming, generators)

    survivor_set = set(survivors)
    signs_for = {}
    for state, sign in generators:
        signs_for.setdefault(state, []).append(sign)

    nodes_data = []
    for (state, sign) in sorted(survivor_set, key=lambda x: (popcount(x[0]), x[0], x[1])):
        nodes_data.append({
            "id":    node_id(state, sign),
            "bin":   state_to_bin(state, crossings),
            "word":  tl_word(state, sign, n, k),
            "row":   popcount(state),
            "sign":  sign,
            "state": state,
        })

    node_id_set = {nd["id"] for nd in nodes_data}

    edges_data = []
    seen_edges = set()

    def add_edge(src_id, tgt_id, etype, label=""):
        key = (src_id, tgt_id, etype)
        if key not in seen_edges:
            seen_edges.add(key)
            edges_data.append({"src": src_id, "tgt": tgt_id, "type": etype, "label": label})

    # Direct edges 
    for src_state, tgt_states in direct.items():
        for src_sign in signs_for.get(src_state, []):
            src_id = node_id(src_state, src_sign)
            if src_id not in node_id_set:
                continue
            for tgt_state in tgt_states:
                for tgt_sign in signs_for.get(tgt_state, []):
                    tgt_id = node_id(tgt_state, tgt_sign)
                    if tgt_id not in node_id_set:
                        continue
                    lbl = edge_label_direct(src_state, tgt_state, n, k)
                    add_edge(src_id, tgt_id, "direct", lbl)

    # Indirect edges
    for (X, signX, Y, signY, A, sA, B, sB) in indirect:
        src_id = node_id(X, signX)
        tgt_id = node_id(Y, signY)
        if src_id not in node_id_set:
            continue
        if tgt_id not in node_id_set:
            continue
        composed = compose_indirect_word(X, signX, Y, signY, A, sA, B, sB, n, k)
        add_edge(src_id, tgt_id, "indirect", composed)

    return nodes_data, edges_data

# ---------------------------------------------------------------------------
# HTML diagram  (template kept inline)
# ---------------------------------------------------------------------------
_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>TL Diagram n={n} k={k}</title>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  background: #fff;
  font-family: 'Georgia', 'Times New Roman', serif;
  color: #111;
  padding: 28px 32px;
}}
h1  {{ font-size: 1.1rem; font-weight: normal; letter-spacing: .05em; margin-bottom: 3px; color: #444; }}
.sub    {{ font-size: .82rem; color: #888; font-family: monospace; margin-bottom: 18px; }}
.legend {{ display: flex; flex-wrap: wrap; gap: 24px; margin-bottom: 22px;
           font-size: .80rem; align-items: center; }}
.leg    {{ display: flex; align-items: center; gap: 8px; }}
#wrap   {{ overflow: auto; }}
svg     {{ display: block; background: #fff; border: 1px solid #e0e0e0; border-radius: 6px; }}
</style>
</head>
<body>
<h1>Kauffman / Temperley–Lieb Complex (Survivors Only)</h1>
<div class="sub">n = {n}, k = {k} &nbsp;|&nbsp; crossings = {crossings}</div>
<div class="legend">
  <div class="leg"><svg width="36" height="4"><line x1="0" y1="2" x2="36" y2="2" stroke="#c06000" stroke-width="2.2"/></svg>direct differential</div>
  <div class="leg"><svg width="36" height="4"><line x1="0" y1="2" x2="36" y2="2" stroke="#1a55c4" stroke-width="2.2" stroke-dasharray="7,3"/></svg>indirect (post-cancellation)</div>
  <div class="leg"><svg width="36" height="4"><line x1="0" y1="2" x2="36" y2="2" stroke="#c0006a" stroke-width="2.2"/></svg>direct + indirect</div>
  <div class="leg"><svg width="16" height="16"><circle cx="8" cy="8" r="7" fill="#eaf5ea" stroke="#1a6b1a" stroke-width="2"/></svg>surviving node</div>
</div>
<div id="wrap"><svg id="g"></svg></div>

<script>
const nodes = {nodes_json};
const edges = {edges_json};

// Layout constants
const PAD_X    = 120;   // horizontal padding
const PAD_TOP  = 90;    // top padding
const PAD_BOT  = 90;    // bottom padding
const ROW_H    = 260;   // vertical distance between rows (px)
const COL_W    = 220;   // horizontal distance between columns (px)
const NODE_R   = 44;    // node circle radius (px)
const LABEL_T  = 0.3;   // Bézier parameter for edge-label placement (0=src, 1=tgt)

const byRow = {{}};
nodes.forEach(n => {{ (byRow[n.row] = byRow[n.row] || []).push(n); }});
const maxRow  = Math.max(...nodes.map(n => n.row));
const maxCols = Math.max(...Object.values(byRow).map(a => a.length));
const W = Math.max(900, PAD_X * 2 + maxCols * COL_W);
const H = PAD_TOP + maxRow * ROW_H + PAD_BOT;

const svg = document.getElementById("g");
svg.setAttribute("viewBox", `0 0 ${{W}} ${{H}}`);
svg.setAttribute("width",  W);
svg.setAttribute("height", H);

// Assign (x, y) positions to every node
const pos = {{}};
Object.entries(byRow).forEach(([row, arr]) => {{
  const r    = parseInt(row);
  const span = (arr.length - 1) * COL_W;
  const x0   = (W - span) / 2;
  arr.forEach((nd, i) => {{ pos[nd.id] = {{ x: x0 + i * COL_W, y: PAD_TOP + r * ROW_H }}; }});
}});

// Arrow-head markers
const defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
function mkArrow(id, col) {{
  const m = document.createElementNS("http://www.w3.org/2000/svg", "marker");
  m.setAttribute("id", id);
  m.setAttribute("markerWidth", "9"); m.setAttribute("markerHeight", "9");
  m.setAttribute("refX", "7");        m.setAttribute("refY", "3.5");
  m.setAttribute("orient", "auto");
  const p = document.createElementNS("http://www.w3.org/2000/svg", "path");
  p.setAttribute("d", "M0,0 L0,7 L9,3.5 z");
  p.setAttribute("fill", col);
  m.appendChild(p);
  return m;
}}
defs.appendChild(mkArrow("arr-dir",  "#c06000"));
defs.appendChild(mkArrow("arr-ind",  "#1a55c4"));
defs.appendChild(mkArrow("arr-both", "#c0006a"));
svg.appendChild(defs);

// Count parallel edges per unordered node pair (for fan-out offset)
const pairCount = {{}};
edges.forEach(e => {{
  const key = [e.src, e.tgt].sort().join("|");
  pairCount[key] = (pairCount[key] || 0) + 1;
}});
const pairSeen = {{}};

// Merge direct+indirect on same (src, tgt) into "both" before drawing
const edgeMap = {{}};
edges.forEach(e => {{
  const key = e.src + "|" + e.tgt;
  edgeMap[key] = edgeMap[key] || {{}};
  edgeMap[key][e.type] = e;
}});
const mergedEdges = [];
Object.values(edgeMap).forEach(types => {{
  if (types.direct && types.indirect) {{
    mergedEdges.push({{ src: types.direct.src, tgt: types.direct.tgt,
                        type: "both", label: types.direct.label }});
  }} else if (types.direct) {{
    mergedEdges.push(types.direct);
  }} else {{
    mergedEdges.push(types.indirect);
  }}
}});

function drawEdge(e) {{
  const p1 = pos[e.src], p2 = pos[e.tgt];
  if (!p1 || !p2) return;

  const isBoth = e.type === "both";
  const isDir  = e.type === "direct";
  const col    = isBoth ? "#c0006a" : isDir ? "#c06000" : "#1a55c4";
  const dash   = (!isDir && !isBoth) ? "8,4" : "";

  // Shorten endpoints so arrows don't overlap the node circle
  const dx = p2.x - p1.x, dy = p2.y - p1.y;
  const len = Math.sqrt(dx * dx + dy * dy);
  if (len < 1) return;
  const ux = dx / len, uy = dy / len;
  const x1 = p1.x + ux * NODE_R,       y1 = p1.y + uy * NODE_R;
  const x2 = p2.x - ux * (NODE_R + 9), y2 = p2.y - uy * (NODE_R + 9);

  // Fan parallel edges apart
  const key  = [e.src, e.tgt].sort().join("|");
  pairSeen[key] = (pairSeen[key] || 0) + 1;
  const idx   = pairSeen[key];
  const total = pairCount[key] || 1;
  const slot  = idx - (total + 1) / 2;
  const off   = (isDir ? 0 : 45) + slot * 55;

  let d, lx, ly;
  if (Math.abs(off) > 2) {{
    // Quadratic Bézier with perpendicular offset
    const cx = (x1 + x2) / 2 - uy * off;
    const cy = (y1 + y2) / 2 + ux * off;
    d  = `M${{x1}},${{y1}} Q${{cx}},${{cy}} ${{x2}},${{y2}}`;
    const t = LABEL_T;
    lx = (1-t)*(1-t)*x1 + 2*(1-t)*t*cx + t*t*x2;
    ly = (1-t)*(1-t)*y1 + 2*(1-t)*t*cy + t*t*y2;
  }} else {{
    // Straight line for direct edges with no parallel neighbours
    d  = `M${{x1}},${{y1}} L${{x2}},${{y2}}`;
    lx = (x1 + x2) / 2 - uy * 16;
    ly = (y1 + y2) / 2 + ux * 16 - 5;
  }}

  const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
  path.setAttribute("d", d);
  path.setAttribute("fill", "none");
  path.setAttribute("stroke", col);
  path.setAttribute("stroke-width", "2");
  if (dash) path.setAttribute("stroke-dasharray", dash);
  path.setAttribute("opacity", "0.85");
  path.setAttribute("marker-end",
    isBoth ? "url(#arr-both)" : isDir ? "url(#arr-dir)" : "url(#arr-ind)");
  svg.appendChild(path);

  if (e.label) {{
    const fs = 11.5;
    const tw = e.label.length * 6.8 + 14;
    const th = fs + 10;

    const pill = document.createElementNS("http://www.w3.org/2000/svg", "rect");
    pill.setAttribute("x",            lx - tw / 2);
    pill.setAttribute("y",            ly - th / 2);
    pill.setAttribute("width",        tw);
    pill.setAttribute("height",       th);
    pill.setAttribute("rx",           th / 2);
    pill.setAttribute("fill",         "white");
    pill.setAttribute("stroke",       col);
    pill.setAttribute("stroke-width", "1");
    pill.setAttribute("opacity",      "0.97");
    svg.appendChild(pill);

    const txt = document.createElementNS("http://www.w3.org/2000/svg", "text");
    txt.setAttribute("x",                 lx);
    txt.setAttribute("y",                 ly);
    txt.setAttribute("text-anchor",       "middle");
    txt.setAttribute("dominant-baseline", "middle");
    txt.setAttribute("font-family",       "Georgia,serif");
    txt.setAttribute("font-size",         fs);
    txt.setAttribute("font-style",        "italic");
    txt.setAttribute("fill",              col);
    txt.textContent = e.label;
    svg.appendChild(txt);
  }}
}}

// Draw order: direct → indirect → both
["direct", "indirect", "both"].forEach(type =>
  mergedEdges.filter(e => e.type === type).forEach(drawEdge)
);

// Draw nodes
nodes.forEach(nd => {{
  const {{x, y}} = pos[nd.id];
  const g = document.createElementNS("http://www.w3.org/2000/svg", "g");

  const fill = nd.sign === 1 ? "#e8f5e8" : nd.sign === -1 ? "#f6eeee" : "#eaf5ea";
  const c = document.createElementNS("http://www.w3.org/2000/svg", "circle");
  c.setAttribute("cx", x); c.setAttribute("cy", y); c.setAttribute("r", NODE_R);
  c.setAttribute("fill", fill);
  c.setAttribute("stroke", "#1a6b1a");
  c.setAttribute("stroke-width", "2.5");
  g.appendChild(c);

  // Binary string label (top)
  const t0 = document.createElementNS("http://www.w3.org/2000/svg", "text");
  t0.setAttribute("x", x); t0.setAttribute("y", y - 14);
  t0.setAttribute("text-anchor", "middle");
  t0.setAttribute("font-family", "Courier New,monospace");
  t0.setAttribute("font-size",   "10");
  t0.setAttribute("fill",        "#444");
  t0.textContent = nd.bin;
  g.appendChild(t0);

  // TL word label (bottom, split off sign suffix if present)
  const hasPl = nd.word.endsWith("(+)");
  const hasMi = nd.word.endsWith("(-)");
  const mainW = (hasPl || hasMi) ? nd.word.slice(0, -3) : nd.word;
  const signW = hasPl ? "(+)" : hasMi ? "(-)" : "";

  const t1 = document.createElementNS("http://www.w3.org/2000/svg", "text");
  t1.setAttribute("x", x); t1.setAttribute("y", signW ? y + 4 : y + 7);
  t1.setAttribute("text-anchor", "middle");
  t1.setAttribute("font-family", "Georgia,serif");
  t1.setAttribute("font-size",   "12");
  t1.setAttribute("font-style",  "italic");
  t1.setAttribute("fill",        "#111");
  t1.textContent = mainW;
  g.appendChild(t1);

  if (signW) {{
    const t2 = document.createElementNS("http://www.w3.org/2000/svg", "text");
    t2.setAttribute("x", x); t2.setAttribute("y", y + 20);
    t2.setAttribute("text-anchor", "middle");
    t2.setAttribute("font-family", "Georgia,serif");
    t2.setAttribute("font-size",   "11");
    t2.setAttribute("font-style",  "italic");
    t2.setAttribute("fill", nd.sign === 1 ? "#1a6b1a" : "#aa1111");
    t2.textContent = signW;
    g.appendChild(t2);
  }}

  svg.appendChild(g);
}});
</script>
</body>
</html>
"""


def build_html(n, k, nodes_data, edges_data):
    """Render the HTML diagram by filling in the template."""
    return _HTML_TEMPLATE.format(
        n=n, k=k,
        crossings=k * (n - 1),
        nodes_json=json.dumps(nodes_data, ensure_ascii=False),
        edges_json=json.dumps(edges_data, ensure_ascii=False),
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    """Prompt for n and k, then write the HTML"""
    try:
        n = int(input("Enter n: "))
        k = int(input("Enter k: "))
    except ValueError:
        print("Error: n and k must be integers.", file=sys.stderr)
        sys.exit(1)

    if n < 1 or k < 1:
        print("Error: n and k must be positive integers.", file=sys.stderr)
        sys.exit(1)

    nodes_data, edges_data = build_tl_diagram(n, k)

    base     = os.path.dirname(os.path.abspath(__file__))
    out_html = os.path.join(base, f"survivors_n{n}_k{k}.html")

    html = build_html(n, k, nodes_data, edges_data)
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\nHTML saved : {out_html}")

if __name__ == "__main__":
    main()
