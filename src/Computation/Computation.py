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

def add_forwardfacing_strand(
    forward_strands: list[list[int, int]],
    ends: tuple[int, int],
    earliest_index: int,
    lowest: int,
    highest: int
    ) -> None:
    if(ends[0] >= 0): # if the end doesn't connect to an end
        forward_strands[ends[0]][0] = ends[1]
        forward_strands[ends[0]][1] = earliest_index
        forward_strands[ends[0]][2] = lowest
        forward_strands[ends[0]][3] = highest

    if(ends[1] >= 0):
        forward_strands[ends[1]][0] = ends[0]
        forward_strands[ends[1]][1] = earliest_index
        forward_strands[ends[1]][2] = lowest
        forward_strands[ends[1]][3] = highest




def remove_forwardfacing_strand(
    forward_strands: list[list[int, int]],
    this_end: int, # one end points to the other end so only one is needed
    string_index : int # need to record is this strand is connected to a loop or the ends
    ) -> None:
    other_end = forward_strands[this_end][0]
    print(f"deleting strands {this_end} and {other_end}")
    if(other_end >= 0):
        forward_strands[other_end][0] = -1
        forward_strands[other_end][1] = string_index
        forward_strands[other_end][2] = -1
        forward_strands[other_end][3] = -1
    
    if(this_end >= 0):
        forward_strands[this_end][0] = -1
        forward_strands[this_end][1] =  string_index
        forward_strands[this_end][2] = -1
        forward_strands[this_end][3] = -1

"""
"""
def detect_features(
    state: str,
    numStrands: int
) -> list[tuple[int, int], list[int], list[int]]:
    # The logic of this functions works on the left and right portions of the 1 resolution
    # the left portion connects existing strands
    # the right portion prepares a new strand
    # pinches are just left and right portions which are part of the same strand

    kauf_state = int(state, 2)

    # tracks where each forward facing strand is connected to, if any
    # we can use earliest in the kauffman state as ID's for each stand
    # [other strand end, strand id(earliest resolution), lowest strand, highest strand]
    # forward_strands[0] represents the lowest strand
    forward_strands = [[-1, -1 * index, index - 1, index - 1] for index in range(1, numStrands + 1)]
    # tracks the left part of resolution, waits for right part of resolution to be determined, if matchin, have a pinch
    # [expected strand id, index of resolution, has bottom strand, has top strand]
    # waiting_for[0] represents the lowest strand
    # has bottom strand and has top strand will be used to determine what pinch is occuring
    waiting_for = [[None, None, None, None] for _ in range(numStrands - 1)]

    closed_loops = []
    pinch_above = [] # almost became loop, but has a single 1 resolution at the top
    pinch_below = [] # almost became loop, but has a single 1 resolution at the bottom

    print(f"state: {state}")
    print(f"nums_strands: {numStrands}\n")

    leftmost_resolution = kauf_state.bit_length() - 1
    for index_from_right in range(leftmost_resolution, -1, -1): # move from left to right
        string_index = len(state) - 1 - index_from_right # index corresponding to the string representation of the state
        gap_index = string_index % (numStrands - 1) # the gap corresponding to the resolution at this index
        has_element = state[string_index] == '1' # if there is a resolution at this index
        print(f"evaluating index {string_index}, gap {gap_index}, element {state[string_index]}")

        if has_element: # need to add left and right part of resolution
            # adding left part of resolution
            # Connecting existing strands so need to gather information for new combined strand
            bottom_connection = forward_strands[gap_index] # get the connected strand connected
            top_connection = forward_strands[gap_index + 1]
            new_ends = [bottom_connection[0], top_connection[0]] 
            print(f"new_ends: {new_ends}")
            new_earliest = min(bottom_connection[1], top_connection[1]) # acts as a new pseudo strand id
            print(f"new_earliest: {new_earliest}")
            print(f"bottom_connection[1]: {bottom_connection[1]}, top_connection[1]: {top_connection[1]}")
            disposed_id = max(bottom_connection[1], top_connection[1]) # need to update other strand's id
            new_lowest = min(bottom_connection[2], top_connection[2]) # record how far we'll need to check
            new_highest = max(bottom_connection[3], top_connection[3])

            # pinches occur when 2 existing strands connect at a resolution, with one strand on the left partition, the other on the right
            for new_gap_index in range(bottom_connection[2], bottom_connection[3]):
                if  waiting_for[new_gap_index][0] == top_connection[1]:
                    if (new_gap_index - gap_index) % 2 == 1:
                        if new_gap_index < gap_index:
                            pinch_above.append(waiting_for[new_gap_index][1])
                        if new_gap_index > gap_index:
                            pinch_below.append(waiting_for[new_gap_index][1])
                        waiting_for[new_gap_index][0] = None
                    else:
                        waiting_for[new_gap_index][0] = new_earliest

            for new_gap_index in range(top_connection[2], top_connection[3]):
                if  waiting_for[new_gap_index][0] == bottom_connection[1]:
                    if (new_gap_index - gap_index) % 2 == 1:
                        if new_gap_index < gap_index:
                            pinch_above.append(waiting_for[new_gap_index][1])
                        if new_gap_index > gap_index:
                            pinch_below.append(waiting_for[new_gap_index][1])
                        waiting_for[new_gap_index][0] = None
                    else:
                        waiting_for[new_gap_index][0] = new_earliest

# =======================================================================================================================

            # add right part of the resolution
            # set up waiting_for so right, the right portion also starts a new strand

            # wait for corresponding id, record where the pinch is, check if strand goes lower(implying this is a top pinch), check if this strand goes higher(implying this is a bottom pinch) 
            # new_earliest will never match for strands connected to braid ends
            # new_lowest < gap_index checks if this has a part of the strand below, since left right alternate it's impossible to 
            # similar logic for new_highest
            print(f"new_lowest: {new_lowest}, new_highest: {new_highest}")
            # has a top based on if top connection 
            waiting_for[gap_index] = [new_earliest, string_index, new_lowest < gap_index, new_highest > gap_index + 1] 
            
            print(forward_strands)

            if(new_earliest >= 0 and forward_strands[new_ends[0]][0] == new_ends[1]): # found a closed loop, no need to readd ends since it canceled itself out
                # nothing to remove, will be overwritten
                print(f"found loop: {new_earliest}, {string_index}")
                closed_loops.append((new_earliest, string_index)) # add the opening(earliest) and closing(current position) of the loop
            else: # not a closed loop, so update the strand's ends
                # remove the existing strands ends
                remove_forwardfacing_strand(forward_strands, gap_index, string_index)
                remove_forwardfacing_strand(forward_strands, gap_index + 1, string_index)
                # add new ends, negative ends or ends not in a loop will not be added
                add_forwardfacing_strand(forward_strands, new_ends, new_earliest, new_lowest, new_highest)

            add_forwardfacing_strand(forward_strands, [gap_index, gap_index + 1], string_index, gap_index, gap_index + 1) # add the right part of the resolution
            #print(waiting_for)
            print(forward_strands)
            print()

    return [sorted(closed_loops), sorted(pinch_above), sorted(pinch_below)]


def main():
    # print(find_features("001111011100", 4))
    # print(("001111011100", 4))
    
    #print(find_features("1111000000001100", 3))
    #print(detect_features("001111010001", 4))
    print(detect_features("10101010110010001100", 6))
    #print(detect_features("1010101011001000110010000", 6))
    #print(detect_features("1010", 3))
    

if __name__ == "__main__":
    main()



"""
For a given state, find all targets which can be reached by a direct map
# Returns a tuple (target, isomorphism_type, index) where index is the index_from_right of the
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

