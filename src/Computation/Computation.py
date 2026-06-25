from src.Computation.kaufman_to_monoid import kaufman_to_monoid

"""
STANDARD:

TEMPERLEY-LIEB WORDS:
    - lists of integers from 1 to n-1
    - must manually keep track of n for each word

KAUFFMAN STATES:
    - strings of ones and zeroes
    - padding can be truncated or included

"""


"""
TODO:

3-BRAID:
    - find_direct_targets
    - detect_distinguished_target
    - test/verify backtrack_isomorphism
    - algorithm for kauffman_indirect_maps
    - implementation of kauffman_indirect_maps

AFTERWARD 3-BRAID LIST COMPLETE, n>3:
    - tl_to_kauffman
        - this should be relatively straightforward
    - detect_distinguished_target
        - known general formula for target/source pattern detections
    - surviving_tl_states
        - no currently known mathematical formula
        - computing naively can give intuition towards a general formula
    - kauffman_indirect_maps
        - proper time has not been committed to considering the complexity of generalizing this algorithm
        - importantly, max length of an indirect path is not known
"""


"""
Returns a list of all surviving states after whittling Type I, II, and III for a given homological degree.
States are given as Temperley-Lieb words in the STANDARD format.
"""
def surviving_tl_states(
    numStrands: int, 
    homDegree: int
) -> list[list[int]]:

    ## Currently only the 3-braid case is implemented
    if numStrands != 3:
        raise ValueError("numStrands must be 3")

    if homDegree < 0:
        raise ValueError("homDegree must be at least 0")
    if homDegree == 0:
        return [[]]
    if homDegree == 1:
        return [[1], [2]]
    if homDegree == 2:
        return [[1,2], [2,1]]

    C = [1,2,2,2]
    match (homDegree-1) % 4:

        case 0:
            return [
                ((homDegree-1)//4)*C + [1],
                [2,2] + ((homDegree-5)//4)*C + [1] + [2,2]
            ]
        
        case 1:
            return [
                ((homDegree-2)//4)*C + [1] + [2],
                [2,2] + ((homDegree)//4 - 1)*C + [1,2,2] + [1]
            ]

        case 2:
            return [
                ((homDegree-3)//4)*C + [1] + [2,2],
                [2,2] + ((homDegree-3)//4)*C + [1]
            ]
        
        case 3:
            return [
                [2,2] + ((homDegree-4)//4)*C + [1] + [2],
                ((homDegree)//4 - 1)*C + [1,2,2] + [1]
            ]

"""
Receives a Temperley-Lieb word and converts it to a Kauffman state.
"""
def tl_to_kauffman(
    tl_state: list[int], 
    numStrands: int,
    padding: int = None
) -> str:
    
    ## Currently only the 3-braid case is implemented
    if numStrands != 3:
        raise ValueError("numStrands must be 3")

    in_str = ''.join(str(i) for i in tl_state)

    out = []  # list of chars, index 0 = leftmost

    for i in range(len(in_str) - 1, -1, -1):  # right to left
        curr = in_str[i]

        if curr == '2':
            out = ['0', '1'] + out
        else:  # curr == '0'
            if len(out) > 0 and out[0] == '0':
                out[0] = '1'
            else:
                out = ['1', '0'] + out

    result = ''.join(out)
    if padding is None:
        result = result.zfill(2 * len(in_str))
    else:
        result = result.zfill(2 * padding)

    return result

"""
Helper function to check if there exists a direct map between two states.
Order of the states is important.
"""
def exists_direct_map(
    state: str, 
    other_state: str
) -> bool:

    binary_diff = int(other_state, 2) - int(state, 2)
    return binary_diff & (binary_diff-1) == 0

"""
For a list of lists of Kauffman states (ordered by hom degree), returns a list of ordered
pairs of states where (A, B) is returned iff there is a direct map from A to B.

Works for an arbitrary number of strands since direct maps can flip any bit.
"""
def kauffman_direct_maps(
    kauff_states_by_degree: list[list[str]]
) -> list[tuple[str, str]]:

    states = kauff_states_by_degree

    edges = []

    for i in range(0, len(states)-1):

        for state in states[i]:
            for other_state in states[i+1]:
                
                if  exists_direct_map(state, other_state):
                    edge = (state, other_state)
                    edges.append(edge)

    return edges

"""
For a list of states (ordered by hom degree) returns a list of ordered pairs of states
where (A, B) is returned iff there is an indirect map from A to B.

There needs to be an extension of this function which returns the path an indirect map takes.
"""
def kauffman_indirect_maps(
    kauff_states_by_degree: list[list[str]],
    numStrands: int
) -> list[tuple[str, str]]:

    """
    for each hom degree:
        for each state:
            find_direct_targets
            for each target:
                backtrack_isomorphism to source
                for each source:
                    check for direct maps to next hom degree
                    check for direct maps to NEW targets
                        for each NEW target:
                            check for direct maps to next hom degree

    Optimization:
        - eliminate isomorphism types which can occur in indirect sequence
        - limit the max possible length of an indirectpath
    """

    return []

"""
For a given state, find all targets which can be reached by a direct map
# Returns a tuple (target, isomorphism_type, index) where index is the position of the
# bit to by flipped in the state to reach the target of given isomorphism_type
"""
def find_direct_targets(
    state: str, 
    numStrands: int
) -> list[tuple[str, int, int]]:
    
    """
    Use the detect_distinguished_target function to identify all possible isomorphisms.

    Key:
        - understand at most how many padded zeroes should be flipped (max k)

    Optimization:
        - create patterns which are candidate bit flips for ismorphisms
        - eliminate patterns which cannot lead to distinguished targets
    """

    pass

"""
Detects if the given state has a distinguished isomorphism.
Returns (A, B) where A is zero iff the state is not a distinguished target 
and A is the isomorphism target type otherwise.
B is the index of the bit to be flipped (from 1 to zero).

This function detects all THREE isomorphism types.
"""
def detect_distinguished_target(state: str, numStrands: int, sign: str = None) -> tuple:
    k = len(state) // (numStrands - 1)
    state = int(state[::-1], 2)

    for iso_type, stype, offset in [(1,"S1",numStrands-1), (2,"S2",1)]:
        matched, j = _check_target(state, numStrands, k, stype, offset, sign)
        if matched:
            return (iso_type, j)

    matched, j = _is_target3(state, numStrands, k)
    if matched:
        return (3, j)

    return (0, None)

def bit(state: int, index: int) -> int:
    return (state >> index) & 1


def has_circle(state: int, n: int, k: int) -> bool:
    for j in range(k * (n - 1) - (n - 1)):
        sigma_i = (j % (n - 1)) + 1
        if not all((pos % (n-1)) + 1 != sigma_i for pos in range(j+2, j+n-2)):
            continue
        if bit(state,j)==1 and bit(state,j+1)==0 and bit(state,j+n-2)==0 and bit(state,j+n-1)==1:
            return True
    return False


def source_matches(state: int, n: int, k: int) -> list:
    matches = []
    for j in range(k * (n - 1) - (n - 1)):
        sigma_i = (j % (n - 1)) + 1
        f, s, sl, l = bit(state,j), bit(state,j+1), bit(state,j+n-2), bit(state,j+n-1)
        if not all((pos % (n-1)) + 1 != sigma_i for pos in range(j+2, j+n-2)):
            continue
        if f==1 and s==0 and sl==0 and l==0:
            matches.append(("S1", sigma_i, j))
        if f==1 and s==0 and sl==0 and l==1 and sigma_i <= n-2:
            matches.append(("S2", sigma_i, j))
    return matches


def _check_target(state: int, n: int, k: int, stype: str, offset: int, sign: str = None) -> tuple:
    if stype == "S1" and sign == "+":
        return (False, None)
    for j in range(k * (n - 1) - (n - 1)):
        idx = j + offset
        if bit(state, idx) != 1:
            continue
        candidate = state & ~(1 << idx)
        if any(t == stype and mj == j for t, _, mj in source_matches(candidate, n, k)):
            return (True, idx)
    return (False, None)


def _is_target3(state: str, n: int) -> tuple[bool, int]:
    cand = kaufman_to_monoid(state, n)

    for i in range(len(cand) - 2):
        if cand[i] == 2 and cand[i + 1] == 1 and cand[i + 2] == 2:
            wl = cand[:i]
            wr = cand[i + 3:]
            if identify_wL(wl, n) and identify_wR(wr, n):
                return (True, i+1)

    return (False, None)




"""
Given an isomorphism type and an index, backtrack the isomorphism to find the source state.
Returns the ismorphism source state, preserving the length of the string.
"""
def backtrack_isomorphism(
        target: str,
        isomorphism_type: int,
        index: int
) -> str:

    return str(int(str(target), 2) - 2**index).zfill(len(target))


def main():
    state_str = input("Enter Kauffman state (e.g. 0110): ").strip()
    n = int(input("Enter number of strands: ").strip())
    k = len(state_str) // (n - 1)
    state = int(state_str[::-1], 2)

    sign = None
    if has_circle(state, n, k):
        print("This state has closed loops.")
        sign = input("Enter sign (+ or -): ").strip()
        while sign not in ("+", "-"):
            sign = input("Invalid. Enter + or -: ").strip()

    print(detect_distinguished_target(state_str, n, sign))

if __name__ == "__main__":
    main()