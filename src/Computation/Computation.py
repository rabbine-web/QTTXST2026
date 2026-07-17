from kaufman_to_monoid import kaufman_to_monoid
from math import ceil

"""
STANDARD:

TEMPERLEY-LIEB WORDS:
    - lists of integers from 1 to n-1
    - must manually keep track of numStrands for each word

KAUFFMAN STATES:
    - strings of ones and zeroes
    - padding can be truncated or included

    SIGN INFORMATION OF KAUFFMAN STATES:
        - for each closed loop, there should be an ordered pair (s,e) of indices
        - the indicies are where the clsoed loop begins and ends in the kauffman state
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
Input a kauffman state, 
Output a list of ordered pairs for each closed loop, with pairs sorted based on first occurance.
        Indices are ordered from the rightmost bit

e.g.    find_closed_loops("101010010010101", 4) returns [(0, 14), (4, 7), (7, 10)]
        find_closed_loops("101", 3) returns [(0, 2)]
        find_closed_loops("1010", 3) returns [(1, 3)]

Should be O(n) where n is the required length of the state, since each strand is only checked once.
sorting at the end should be O(n) since closed loops is almost sorted except for nested/enclosed loops
"""
def find_closed_loops(
    state: str,
    numStrands: int
) -> list[tuple[int, int], list[int], list[int]]:
    
    kauf_state = int(state, 2)
    required_repitions = ceil(kauf_state.bit_length() / (numStrands - 1))

    # tracks where each forward facing strand is connected to, if any
    # we can use earliest in the kauffman state as ID's for each stand
    # [other end of strand, earliest in the kauffman state, lowest strand, highest strand]
    forward_strands = [[-1, -1 * index, -1, -1] for index in range(2, numStrands + 2)]
    waiting_for = [[None, None] for _ in range(numStrands - 1)]


    incomplete_top = [] # almost became loop, but has a single 1 resolution at the top
    incomplete_bottom = [] # almost became loop, but has a single 1 resolution at the bottom

    closed_loops = []
    complete_top = [] # almost became loop, but has a single 1 resolution at the top
    complete_bottom = [] # almost became loop, but has a single 1 resolution at the bottom

    # reads the kaufman state right to left
    for reptition in range(required_repitions):
        for element_index in range(numStrands - 1):
            position_from_right = (reptition * (numStrands - 1)) + element_index
            has_element = kauf_state >> (position_from_right) & 0b1

            if has_element:
                print(f"element found at position from right: {position_from_right} ")
                print(f"before: {forward_strands} ")
                # which forward facing strands the backfacing strand is connected to, if any
                backfacing_connection = [element_index, element_index + 1]
                rightmost_position = forward_strands[element_index][1] # at most will be at first position_from_right, len(state) - 1 from the rightmost
                #strand_id = forward_strands[element_index][1]
                lowest = numStrands
                highest = -1
                
                top_merged = False
                bottom_merged = False

                # if the connected end has a pre-existing assigned strand
                if forward_strands[backfacing_connection[0]][0] >= 0:
                    print(f"merged top")
                    bottom_merged = True
                    backfacing_connection[0] = forward_strands[backfacing_connection[0]][0]
                    rightmost_position = min(rightmost_position, forward_strands[backfacing_connection[0]][1]) # get the rightmost starting position_from_right
                    lowest = min(lowest,  forward_strands[backfacing_connection[0]][2])
                    highest = max(highest,  forward_strands[backfacing_connection[0]][3])

                    # remove the old strand since merged into new strand
                    remove_forwardfacing_strand(forward_strands, backfacing_connection[0])

                if forward_strands[backfacing_connection[1]][0] >= 0:
                    print(f"merged bottom")
                    top_merged = True
                    backfacing_connection[1] = forward_strands[backfacing_connection[1]][0] # the new strand is connected to the old strand's other end
                    rightmost_position = min(rightmost_position, forward_strands[backfacing_connection[1]][1]) # get the rightmost starting position_from_right
                    lowest = min(lowest,  forward_strands[backfacing_connection[1]][2])
                    highest = max(highest,  forward_strands[backfacing_connection[1]][3])

                    # remove the old strand since merged into new strand
                    remove_forwardfacing_strand(forward_strands, backfacing_connection[1]) 





                # something had to merge so rightmost_position has been properly set
                if backfacing_connection[0] == backfacing_connection[1]:
                    print("closed loop found")
                    closed_loops.append((rightmost_position, position_from_right, lowest, highest))

                # if connected to two ends, re add since can still be closed
                # 1 and 0 connections don't have anything to re add
                elif bottom_merged and top_merged:
                    add_forwardfacing_strand(forward_strands, backfacing_connection, rightmost_position, lowest, highest)

                # only need to check multiple if merged to them
                if bottom_merged or top_merged:
                    # in the one case, we need to track which side got merged since
                    print(f"searching gaps [{lowest}, {highest}]")
                    for affected_index in range(lowest, highest):
                        print(f"affected index {affected_index}")
                        if(affected_index % 2 == element_index % 2):
                            print(f"not affecting the other end")
                            continue
                        if(waiting_for[affected_index][0] == rightmost_position):
                            print(f"pinch found at {waiting_for[affected_index][1]}")
                            complete_bottom.append(waiting_for[affected_index][1])
                            waiting_for[affected_index][0] = None
                            waiting_for[affected_index][1] = None
                    
                # what strand we're expecting and where it's recorded to start from
                waiting_for[element_index][0] = forward_strands[backfacing_connection[0]][1]
                waiting_for[element_index][1] = position_from_right

                print(f"backstrands {backfacing_connection}")
                print(f"merged: {forward_strands} ")
                print(f"waiting strands {waiting_for}")

                # regardless of what happens, the forward facing strand of the inital backfacing strand will be added
                add_forwardfacing_strand(forward_strands, (element_index, element_index + 1), position_from_right, element_index, element_index + 1)
                print(f"added: {forward_strands} ")
                print()

    return [sorted(closed_loops), complete_bottom, complete_top]



def add_forwardfacing_strand(
    forward_strands: list[list[int, int]],
    ends: tuple[int, int],
    position_from_right: int,
    lowest: int,
    highest: int
    ) -> None:
    forward_strands[ends[0]][0] = ends[1]
    forward_strands[ends[0]][1] = position_from_right
    forward_strands[ends[0]][2] = lowest
    forward_strands[ends[0]][3] = highest

    forward_strands[ends[1]][0] = ends[0]
    forward_strands[ends[1]][1] = position_from_right
    forward_strands[ends[1]][2] = lowest
    forward_strands[ends[1]][3] = highest




def remove_forwardfacing_strand(
    forward_strands: list[list[int, int]],
    this_end: int, # one end points to the other end so only one is needed
    ) -> None:
    other_end = forward_strands[this_end][0]
    forward_strands[other_end][0] = -1
    #forward_strands[other_end][1] = -1
    forward_strands[other_end][2] = -1
    forward_strands[other_end][3] = -1
    
    forward_strands[this_end][0] = -1
    #forward_strands[this_end][1] = -1
    forward_strands[this_end][2] = -1
    forward_strands[this_end][3] = -1


"""
For a given state, find all targets which can be reached by a direct map
# Returns a tuple (target, isomorphism_type, index) where index is the position_from_right of the
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
def detect_distinguished_target(
    state: str, 
    numStrands: int, 
    loopRanges: list[tuple[int, int, int, int]],
    loopSigns: list[str]
) -> tuple[int, int]:
    # going to assume that all isomorphisms require the smallest possible loop?
    # check type 1 and type 2 isomorphisms
    type_and_index = check_type_1_or_2()
    if type_and_index is not None:
        return type_and_index
    
    detect_type_3_target(state, numStrands, loopRanges, loopSigns)
"""
Given a state, check if it is a type 1 or type 2 isomorphism target.
If it is a target, return the index of the bit to be flipped to reach the source state
If it isn't a target, return -1
"""
def check_type_1_or_2(
    state: str,
    numStrands: int,
    loopRanges: list[tuple[int, int, int]],
    loopSigns: list[str]
) -> tuple[int, int]:
    
    return None


"""
Given a state, check if it is a type 3 isomorphism target. To check this, we need to check if the state
with e_i e_i+1 e_i, this is first possible occurance

If it is a target, return the index of the bit to be flipped to reach the source state
If it isn't a target, return -1
"""
def check_type_1_or_2(
    state: str,
    numStrands: int,
    loopRanges: list[tuple[int, int, int, int]],
    loopSigns: list[str]
) -> tuple[int, int]:
    # so type 1 target is any closed loop which is negative?
    # TODO: check if range matters, probably not since isomorphism seem to only flip 1?
    for i in range(len(loopSigns)):
        if loopSigns[i] == '-':
            return (1, loopRanges[i][1]) # assume you get rid of the second occurance that closes range
        
    # assume that the remaining signs are now all +
    return None


def bit(state: int, index: int) -> int:
    return (state >> index) & 1




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
    print(find_closed_loops("001111011100", 4))
    print(("001111011100", 4))
    
    #print(find_closed_loops("111", 3))
    

if __name__ == "__main__":
    main()