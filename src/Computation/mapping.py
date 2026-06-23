"""
mapping.py

Constructs the three layers of maps for the Khovanov chain complex:

  1. build_direct_maps   : raw differential maps between Kauffman states
  2. build_iso_pairs     : isomorphism pairs identified by Gaussian cancellation
  3. build_indirect_maps : post-cancellation maps via  X → B ↔ A → Y

Helpers:
  popcount, state_to_bin, node_id, node_label
"""

from src.Computation.TemperleyLieb import kauffmanstates
from src.Computation.gaussian import build_generators, source_matches


# ── Helpers ────────────────────────────────────────────────────────────────

def popcount(state: int) -> int:
    return bin(state).count("1")


def state_to_bin(state: int, crossings: int) -> str:
    return "".join(str((state >> i) & 1) for i in range(crossings))


def node_id(state: int, sign: int) -> str:
    return f"{state}_{sign}"


def node_label(state: int, sign: int, crossings: int) -> str:
    b = state_to_bin(state, crossings)
    if sign == 1:
        return b + " (+)"
    elif sign == -1:
        return b + " (−)"
    return b


# ── Step 1 – Direct maps ───────────────────────────────────────────────────

def build_direct_maps(
    n: int, k: int
) -> tuple[dict[int, list[int]], dict[int, list[int]]]:
    """
    Build raw differential maps: for each state, flip one 0-bit to 1
    if the result is also a valid Kauffman state.

    Returns:
      direct   : state  → list of target states
      incoming : target → list of source states
    """
    crossings = k * (n - 1)
    valid     = set(kauffmanstates(n, k))
    direct:   dict[int, list[int]] = {}
    incoming: dict[int, list[int]] = {}

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


# ── Step 2 – Isomorphism pairs ─────────────────────────────────────────────

def build_iso_pairs(
    n: int, k: int
) -> tuple[list, set, list, list]:
    """
    Run Gaussian cancellation to identify isomorphism pairs.

    Returns:
      generators : all (state, sign) pairs
      removed    : set of cancelled (state, sign) pairs
      survivors  : list of non-cancelled (state, sign) pairs
      iso_pairs  : list of (A, sA, B, sB) cancellation pairs
    """
    generators     = build_generators(n, k)
    gen_set        = set(generators)
    signs_by_state: dict[int, list[int]] = {}
    for state, sign in generators:
        signs_by_state.setdefault(state, []).append(sign)

    removed:   set[tuple[int, int]]        = set()
    iso_pairs: list[tuple[int, int, int, int]] = []

    for state, sign in generators:
        for source_type, sigma_i, j in source_matches(state, n, k):

            if source_type == "S1":
                target = state | (1 << (j + n - 1))
                if (target, -1) in gen_set:
                    if (state, sign) not in removed and (target, -1) not in removed:
                        iso_pairs.append((state, sign, target, -1))
                        removed.add((state, sign))
                        removed.add((target, -1))

            elif source_type == "S2" and sign == 1:
                target = state | (1 << (j + 1))
                if (state, 1) not in removed:
                    for g_sign in signs_by_state.get(target, []):
                        if (target, g_sign) not in removed:
                            iso_pairs.append((state, 1, target, g_sign))
                            removed.add((state, 1))
                            removed.add((target, g_sign))
                            break

    survivors = [(s, sg) for s, sg in generators if (s, sg) not in removed]
    return generators, removed, survivors, iso_pairs


# ── Step 3 – Indirect maps ─────────────────────────────────────────────────

def build_indirect_maps(
    iso_pairs: list,
    direct:    dict[int, list[int]],
    incoming:  dict[int, list[int]],
    generators: list,
) -> list[tuple]:
    """
    Build post-cancellation indirect maps following the strict pattern:

        X → B  (iso target)  ↔  A  (iso source)  → Y

    Conditions:
      - (X, signX) must be a survivor (not cancelled)
      - (Y, signY) must be a survivor (not cancelled)
      - popcount(X) and popcount(Y) differ by exactly 1

    Returns a list of 8-tuples: (X, signX, Y, signY, A, sA, B, sB)
    """
    indirect: list[tuple] = []
    seen:     set[tuple]  = set()

    iso_pair_nodes: set[tuple[int, int]] = set()
    for A, sA, B, sB in iso_pairs:
        iso_pair_nodes.add((A, sA))
        iso_pair_nodes.add((B, sB))

    signs_for: dict[int, list[int]] = {}
    for state, sign in generators:
        signs_for.setdefault(state, []).append(sign)

    for A, sA, B, sB in iso_pairs:
        incomingB = set(incoming.get(B, []))
        outgoingA = set(direct.get(A, []))

        for X in incomingB:
            for signX in signs_for.get(X, []):
                if (X, signX) in iso_pair_nodes:
                    continue
                for Y in outgoingA:
                    for signY in signs_for.get(Y, []):
                        if (Y, signY) in iso_pair_nodes:
                            continue
                        if abs(popcount(X) - popcount(Y)) != 1:
                            continue
                        key = (X, signX, Y, signY, B, A)
                        if key not in seen:
                            seen.add(key)
                            indirect.append((X, signX, Y, signY, A, sA, B, sB))

    return indirect