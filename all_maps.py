"""
all_maps.py
  - States with circles are split into separate (+) and (−) nodes in the diagram
  - Indirect maps follow strictly: X -> B (iso target) <-> A (iso source) -> Y
  - Only kept if both (X, signX) and (Y, signY) are survivors (not in any iso pair)
  - Sign variants of circle states are checked independently
  - If a (src, tgt) pair has both direct and indirect edges, shown as single black edge
"""

import os
import json
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.Computation.TemperleyLieb import kauffmanstates
from Gaussian_elimination import (
    build_generators,
    source_matches,
    has_circle,
)


# ---------------------------------------------------------------------------
# Step 1 – Direct maps 
# ---------------------------------------------------------------------------
def build_direct_maps(n, k):
    crossings = k * (n - 1)
    valid = set(kauffmanstates(n, k))
    direct = {}
    incoming = {}

    for state in valid:
        targets = []
        for bit_pos in range(crossings):
            if not ((state >> bit_pos) & 1):
                target = state | (1 << bit_pos)
                if target in valid:
                    targets.append(target)
        direct[state] = targets
        for t in targets:
            incoming.setdefault(t, []).append(state)

    return direct, incoming


# ---------------------------------------------------------------------------
# Step 2 – Isomorphism pairs from Gaussian cancellation
# ---------------------------------------------------------------------------
def build_iso_pairs(n, k):
    generators = build_generators(n, k)
    gen_set = set(generators)
    signs_by_state = {}
    for state, sign in generators:
        signs_by_state.setdefault(state, []).append(sign)

    removed = set()
    iso_pairs = []

    for state, sign in generators:
        matches = source_matches(state, n, k)
        for source_type, sigma_i, j in matches:

            if source_type == "S1":
                target_state = state | (1 << (j + n - 1))
                if (target_state, -1) in gen_set:
                    if (state, sign) not in removed and (target_state, -1) not in removed:
                        iso_pairs.append((state, sign, target_state, -1))
                        removed.add((state, sign))
                        removed.add((target_state, -1))

            elif source_type == "S2" and sign == 1:
                target_state = state | (1 << (j + 1))
                if (state, 1) not in removed:
                    for g_sign in signs_by_state.get(target_state, []):
                        if (target_state, g_sign) not in removed:
                            iso_pairs.append((state, 1, target_state, g_sign))
                            removed.add((state, 1))
                            removed.add((target_state, g_sign))
                            break

    survivors = [(s, sg) for s, sg in generators if (s, sg) not in removed]
    return generators, removed, survivors, iso_pairs


# ---------------------------------------------------------------------------
# Step 3 – Indirect maps
#
#   Strict pattern: X -> B (iso target) <-> A (iso source) -> Y
#
#   For each iso pair (A, sA, B, sB):
#     - Find all X with a direct edge into state B
#     - Find all Y that state A has a direct edge to
#     - For each sign variant (X, signX) and (Y, signY):
#         - Skip if (X, signX) is cancelled (in any iso pair)
#         - Skip if (Y, signY) is cancelled (in any iso pair)
#         - X and Y must be exactly one row apart (popcount differs by 1)
#         - If all checks pass, record indirect map (X, signX) -> (Y, signY)
# ---------------------------------------------------------------------------
def build_indirect_maps(iso_pairs, direct, incoming, generators):
    indirect = []
    seen = set()

    # Build set of (state, sign) pairs that are cancelled
    iso_pair_nodes = set()
    for (A, sA, B, sB) in iso_pairs:
        iso_pair_nodes.add((A, sA))
        iso_pair_nodes.add((B, sB))

    # Build map of state -> list of signs from generators
    signs_for = {}
    for (state, sign) in generators:
        signs_for.setdefault(state, []).append(sign)

    for (A, sA, B, sB) in iso_pairs:
        # Strict pattern: X -> B (target) <-> A (source) -> Y
        incomingB = set(incoming.get(B, []))
        outgoingA = set(direct.get(A, []))

        if incomingB and outgoingA:
            for X in incomingB:
                for signX in signs_for.get(X, []):
                    # Skip if this specific (X, signX) is cancelled
                    if (X, signX) in iso_pair_nodes:
                        continue
                    for Y in outgoingA:
                        for signY in signs_for.get(Y, []):
                            # Skip if this specific (Y, signY) is cancelled
                            if (Y, signY) in iso_pair_nodes:
                                continue
                            # X and Y must be exactly one row apart
                            if abs(popcount(X) - popcount(Y)) != 1:
                                continue
                            key = (X, signX, Y, signY, B, A)
                            if key not in seen:
                                seen.add(key)
                                indirect.append((X, signX, Y, signY, A, sA, B, sB))

    return indirect


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def state_to_bin(state, crossings):
    return ''.join(str((state >> i) & 1) for i in range(crossings))


def popcount(state):
    return bin(state).count('1')


def node_id(state, sign):
    return f"{state}_{sign}"


def node_label(state, sign, crossings):
    b = state_to_bin(state, crossings)
    if sign == 1:
        return b + " (+)"
    elif sign == -1:
        return b + " (−)"
    else:
        return b
