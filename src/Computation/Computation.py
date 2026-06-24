
"""
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
"""
def tl_to_kauffman(
    tl_state: list[int], 
    numStrands: int,
    padding: int = None
) -> str:

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
"""
def exists_direct_map(
    state: str, 
    other_state: str
) -> bool:

    binary_diff = int(other_state, 2) - int(state, 2)
    return binary_diff & (binary_diff-1) == 0

"""
DONE
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
    """

    return []

"""
For a given state, find all targets which can be reached by a direct map
# Returns a tuple (target, isomorphism_type, index) where index is the position of the
# bit to by flipped in the state to reach the target through an isomorphism_type
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
def detect_distinguished_target(
    state: str,
    numStrands: int
) -> tuple[int, int]:

    pass

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
