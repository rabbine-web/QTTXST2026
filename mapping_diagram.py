"""
mapping_diagram.py

Diagram showing all states and mapping between them.

Node label:  binary string (display, LSB-first) on top line
             TL word below  e.g.  e1e2(+)
Edge labels:
  direct   – sorted TL gens of target, with the newly-added one written εi
  iso      – no label
  indirect – read Y's generators; bits new relative to X are ε, bits already in X are e
  both     – single dark pink edge, direct label only

This file will generate html code needed for diagram mapping, after running mapping_diagram.py run tl_diagram_n{n}_k{k}.html to get the live result.
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
    diff     = tgt_state ^ src_state
    bit_pos  = diff.bit_length() - 1
    crossings = k * (n - 1)
    tgt_gens      = temperleylieb(tgt_state, n, k)
    tgt_crossings = [i for i in range(crossings) if (tgt_state >> i) & 1]
    parts = []
    for crossing, g in zip(tgt_crossings, tgt_gens):
        if crossing == bit_pos:
            parts.append(f"\u03b5{g}")   # ε  – newly added bit
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
# Build all node/edge data
# ---------------------------------------------------------------------------
def build_tl_diagram(n, k):
    """
    Compute nodes and edges for the TL diagram.

    Returns
    -------
    nodes_data : list[dict]
    edges_data : list[dict]
    indirect   : list  (raw indirect-map tuples)
    iso_pairs  : list  (raw iso-pair tuples)
    """
    direct, incoming = build_direct_maps(n, k)
    generators, removed, survivors, iso_pairs = build_iso_pairs(n, k)
    indirect = build_indirect_maps(iso_pairs, direct, incoming, generators)

    iso_pair_nodes = set()
    for (A, sA, B, sB) in iso_pairs:
        iso_pair_nodes.add((A, sA))
        iso_pair_nodes.add((B, sB))

    survivor_set = set(survivors)
    signs_for = {}
    for state, sign in generators:
        signs_for.setdefault(state, []).append(sign)

    node_set = set(survivors)
    for (A, sA, B, sB) in iso_pairs:
        node_set.add((A, sA))
        node_set.add((B, sB))

    nodes_data = []
    for (state, sign) in sorted(node_set, key=lambda x: (popcount(x[0]), x[0], x[1])):
        nodes_data.append({
            "id":       node_id(state, sign),
            "bin":      state_to_bin(state, k * (n - 1)),
            "word":     tl_word(state, sign, n, k),
            "row":      popcount(state),
            "survived": (state, sign) in survivor_set,
            "iso_node": (state, sign) in iso_pair_nodes,
            "sign":     sign,
            "state":    state,
        })

    # Accumulate raw edges, then merge direct+indirect on the same (src, tgt) -> "both"
    raw_edges = {}   # (src_id, tgt_id) -> {"direct": lbl, "indirect": lbl, "iso": True}

    def add_raw(src_id, tgt_id, etype, label=""):
        key = (src_id, tgt_id)
        raw_edges.setdefault(key, {})
        raw_edges[key][etype] = label

    # Iso edges
    for (A, sA, B, sB) in iso_pairs:
        add_raw(node_id(A, sA), node_id(B, sB), "iso", "")

    # Direct edges (skip pairs where both endpoints are iso-pair nodes)
    for src_state, tgt_states in direct.items():
        for src_sign in signs_for.get(src_state, []):
            if (src_state, src_sign) not in node_set:
                continue
            for tgt_state in tgt_states:
                for tgt_sign in signs_for.get(tgt_state, []):
                    if (tgt_state, tgt_sign) not in node_set:
                        continue
                    if (src_state, src_sign) in iso_pair_nodes and \
                       (tgt_state, tgt_sign) in iso_pair_nodes:
                        continue
                    lbl = edge_label_direct(src_state, tgt_state, n, k)
                    add_raw(node_id(src_state, src_sign),
                            node_id(tgt_state, tgt_sign), "direct", lbl)

    # Indirect edges
    for (X, signX, Y, signY, A, sA, B, sB) in indirect:
        lbl = compose_indirect_word(X, signX, Y, signY, A, sA, B, sB, n, k)
        add_raw(node_id(X, signX), node_id(Y, signY), "indirect", lbl)

    # Merge into final edge list
    edges_data = []
    for (src_id, tgt_id), types in raw_edges.items():
        if "iso" in types:
            edges_data.append({"src": src_id, "tgt": tgt_id, "type": "iso",      "label": ""})
        elif "direct" in types and "indirect" in types:
            edges_data.append({"src": src_id, "tgt": tgt_id, "type": "both",     "label": types["direct"]})
        elif "direct" in types:
            edges_data.append({"src": src_id, "tgt": tgt_id, "type": "direct",   "label": types["direct"]})
        else:
            edges_data.append({"src": src_id, "tgt": tgt_id, "type": "indirect", "label": types["indirect"]})

    return nodes_data, edges_data, indirect, iso_pairs


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
h1  {{ font-size: 1rem; font-weight: normal; letter-spacing: .05em; margin-bottom: 3px; color: #444; }}
.sub {{ font-size: .78rem; color: #888; font-family: monospace; margin-bottom: 16px; }}
.legend {{ display: flex; flex-wrap: wrap; gap: 20px; margin-bottom: 20px;
           font-size: .76rem; align-items: center; }}
.leg    {{ display: flex; align-items: center; gap: 6px; }}
#wrap   {{ overflow-x: auto; }}
svg     {{ display: block; background: #fff; border: 1px solid #e8e8e8; border-radius: 4px; }}
</style>
</head>
<body>
<h1>Kauffman / Temperley–Lieb Complex</h1>
<div class="sub">n = {n}, k = {k} &nbsp;|&nbsp; crossings = {crossings}</div>
<div class="legend">
  <div class="leg"><svg width="30" height="4"><line x1="0" y1="2" x2="30" y2="2" stroke="#c06000" stroke-width="2"/></svg>direct</div>
  <div class="leg"><svg width="30" height="4"><line x1="0" y1="2" x2="30" y2="2" stroke="#1a55c4" stroke-width="2" stroke-dasharray="6,3"/></svg>indirect</div>
  <div class="leg"><svg width="30" height="4"><line x1="0" y1="2" x2="30" y2="2" stroke="#c0006a" stroke-width="2"/></svg>direct + indirect</div>
  <div class="leg"><svg width="30" height="4"><line x1="0" y1="2" x2="30" y2="2" stroke="#990000" stroke-width="2" stroke-dasharray="8,3"/></svg>isomorphism pair</div>
  <div class="leg"><svg width="14" height="14"><circle cx="7" cy="7" r="6" fill="#f0f8f0" stroke="#1a6b1a" stroke-width="2"/></svg>surviving</div>
  <div class="leg"><svg width="14" height="14"><circle cx="7" cy="7" r="6" fill="#fff8f0" stroke="#884400" stroke-width="1.8"/></svg>iso pair node</div>
</div>
<div id="wrap"><svg id="g"></svg></div>

<script>
const nodes = {nodes_json};
const edges = {edges_json};

// Layout constants
const PAD_X      = 110;   // horizontal padding
const PAD_TOP    = 80;    // top padding
const PAD_BOTTOM = 80;    // bottom padding
const ROW_H      = 220;   // vertical distance between rows
const COL_W      = 200;   // horizontal distance between columns
const NODE_R     = 36;    // node circle radius (px)
const LABEL_T    = 0.3;   // Bézier parameter for edge-label placement (0=src, 1=tgt)

const byRow   = {{}};
nodes.forEach(n => {{ (byRow[n.row] = byRow[n.row] || []).push(n); }});
const maxRow  = Math.max(...nodes.map(n => n.row));
const maxCols = Math.max(...Object.values(byRow).map(a => a.length));
const W = Math.max(800, PAD_X * 2 + maxCols * COL_W);
const H = PAD_TOP + maxRow * ROW_H + PAD_BOTTOM;

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
function mkArrow(id, col, reverse) {{
  const m = document.createElementNS("http://www.w3.org/2000/svg", "marker");
  m.setAttribute("id", id);
  m.setAttribute("markerWidth", "8"); m.setAttribute("markerHeight", "8");
  m.setAttribute("refX", reverse ? "2" : "6");
  m.setAttribute("refY", "3");
  m.setAttribute("orient", "auto");
  const p = document.createElementNS("http://www.w3.org/2000/svg", "path");
  p.setAttribute("d", reverse ? "M8,0 L8,6 L0,3 z" : "M0,0 L0,6 L8,3 z");
  p.setAttribute("fill", col);
  m.appendChild(p);
  return m;
}}
defs.appendChild(mkArrow("arr-dir",   "#c06000", false));
defs.appendChild(mkArrow("arr-ind",   "#1a55c4", false));
defs.appendChild(mkArrow("arr-both",  "#c0006a", false));
defs.appendChild(mkArrow("arr-iso-f", "#990000", false));
defs.appendChild(mkArrow("arr-iso-b", "#990000", true));
svg.appendChild(defs);

// Count parallel edges between each unordered node pair (for fan-out offset)
const edgeCount = {{}};
edges.forEach(e => {{
  const key = [e.src, e.tgt].sort().join("|");
  edgeCount[key] = (edgeCount[key] || 0) + 1;
}});
const edgeSeen = {{}};

function drawEdge(e) {{
  const p1 = pos[e.src], p2 = pos[e.tgt];
  if (!p1 || !p2) return;

  const isIso  = e.type === "iso";
  const isInd  = e.type === "indirect";
  const isBoth = e.type === "both";
  const col  = isInd ? "#1a55c4" : isBoth ? "#c0006a" : isIso ? "#990000" : "#c06000";
  const dash = isInd ? "7,4" : isIso ? "9,3" : "";

  // Fan parallel edges apart
  const pairKey = [e.src, e.tgt].sort().join("|");
  const idx     = edgeSeen[pairKey] = (edgeSeen[pairKey] || 0);
  edgeSeen[pairKey]++;
  const total   = edgeCount[pairKey] || 1;
  const baseOff = isIso ? 55 : isInd ? 42 : 18;
  const fanOff  = baseOff + (idx - (total - 1) / 2) * 28;

  // Shorten endpoints so arrows don't overlap the node circle
  const dx = p2.x - p1.x, dy = p2.y - p1.y;
  const len = Math.sqrt(dx * dx + dy * dy);
  if (len < 1) return;
  const ux = dx / len, uy = dy / len;
  const gap = isIso ? NODE_R + 10 : NODE_R;
  const x1 = p1.x + ux * gap,      y1 = p1.y + uy * gap;
  const x2 = p2.x - ux * (gap + 7), y2 = p2.y - uy * (gap + 7);

  // Quadratic Bézier control point (perpendicular offset = fanOff)
  const cx = (x1 + x2) / 2 - uy * fanOff;
  const cy = (y1 + y2) / 2 + ux * fanOff;
  const d  = `M${{x1}},${{y1}} Q${{cx}},${{cy}} ${{x2}},${{y2}}`;

  // Label position along the Bézier at parameter LABEL_T
  const t = LABEL_T;
  const lx = (1-t)*(1-t)*x1 + 2*(1-t)*t*cx + t*t*x2;
  const ly = (1-t)*(1-t)*y1 + 2*(1-t)*t*cy + t*t*y2;

  const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
  path.setAttribute("d", d);
  path.setAttribute("fill", "none");
  path.setAttribute("stroke", col);
  path.setAttribute("stroke-width", "1.7");
  path.setAttribute("opacity", "0.82");
  if (dash) path.setAttribute("stroke-dasharray", dash);
  if (isIso) {{
    path.setAttribute("marker-start", "url(#arr-iso-b)");
    path.setAttribute("marker-end",   "url(#arr-iso-f)");
  }} else {{
    path.setAttribute("marker-end", `url(#${{isBoth ? "arr-both" : isInd ? "arr-ind" : "arr-dir"}})`);
  }}
  svg.appendChild(path);

  if (e.label) {{
    const fs  = 10;
    const pad = 5;
    const tw  = e.label.length * 6.0 + pad * 2;
    const th  = fs + pad * 2;

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
    txt.setAttribute("x",                  lx);
    txt.setAttribute("y",                  ly);
    txt.setAttribute("text-anchor",        "middle");
    txt.setAttribute("dominant-baseline",  "middle");
    txt.setAttribute("font-family",        "Georgia,serif");
    txt.setAttribute("font-size",          fs);
    txt.setAttribute("font-style",         "italic");
    txt.setAttribute("fill",               col);
    txt.textContent = e.label;
    svg.appendChild(txt);
  }}
}}

// Draw order: direct → indirect → both → iso (iso on top)
["direct", "indirect", "both", "iso"].forEach(type =>
  edges.filter(e => e.type === type).forEach(drawEdge)
);

// Draw nodes
nodes.forEach(nd => {{
  const {{x, y}} = pos[nd.id];
  const g = document.createElementNS("http://www.w3.org/2000/svg", "g");

  // Circle fill/stroke by node class
  let fill = "#fff", stroke = "#aaa", sw = "1.4";
  if (nd.survived && !nd.iso_node) {{ fill = "#f0f8f0"; stroke = "#1a6b1a"; sw = "2.2"; }}
  else if (nd.iso_node)            {{ fill = "#fff8f0"; stroke = "#884400"; sw = "1.9"; }}
  if (nd.sign ===  1) fill = nd.iso_node ? "#fff4e8" : "#edf8ed";
  if (nd.sign === -1) fill = nd.iso_node ? "#fff0f0" : "#f8f0f0";

  const c = document.createElementNS("http://www.w3.org/2000/svg", "circle");
  c.setAttribute("cx", x); c.setAttribute("cy", y); c.setAttribute("r", NODE_R);
  c.setAttribute("fill", fill); c.setAttribute("stroke", stroke); c.setAttribute("stroke-width", sw);
  g.appendChild(c);

  // Binary string label (top)
  const t0 = document.createElementNS("http://www.w3.org/2000/svg", "text");
  t0.setAttribute("x", x); t0.setAttribute("y", y - 10);
  t0.setAttribute("text-anchor", "middle"); t0.setAttribute("dominant-baseline", "auto");
  t0.setAttribute("font-family", "Courier New,monospace"); t0.setAttribute("font-size", "9");
  t0.setAttribute("fill", "#333");
  t0.textContent = nd.bin;
  g.appendChild(t0);

  // TL word label (bottom, split off sign suffix if present)
  const hasPl  = nd.word.endsWith("(+)");
  const hasMi  = nd.word.endsWith("(-)");
  const mainW  = (hasPl || hasMi) ? nd.word.slice(0, -3) : nd.word;
  const signW  = hasPl ? "(+)" : hasMi ? "(-)" : "";

  const t1 = document.createElementNS("http://www.w3.org/2000/svg", "text");
  t1.setAttribute("x", x); t1.setAttribute("y", signW ? y + 5 : y + 7);
  t1.setAttribute("text-anchor", "middle"); t1.setAttribute("dominant-baseline", "auto");
  t1.setAttribute("font-family", "Georgia,serif"); t1.setAttribute("font-size", "10");
  t1.setAttribute("font-style", "italic"); t1.setAttribute("fill", "#111");
  t1.textContent = mainW;
  g.appendChild(t1);

  if (signW) {{
    const t2 = document.createElementNS("http://www.w3.org/2000/svg", "text");
    t2.setAttribute("x", x); t2.setAttribute("y", y + 18);
    t2.setAttribute("text-anchor", "middle"); t2.setAttribute("dominant-baseline", "auto");
    t2.setAttribute("font-family", "Georgia,serif"); t2.setAttribute("font-size", "9");
    t2.setAttribute("font-style", "italic");
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

    nodes_data, edges_data, indirect, iso_pairs = build_tl_diagram(n, k)

    base     = os.path.dirname(os.path.abspath(__file__))
    out_html = os.path.join(base, f"tl_diagram_n{n}_k{k}.html")

    html = build_html(n, k, nodes_data, edges_data)
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\nHTML saved : {out_html}")

if __name__ == "__main__":
    main()
