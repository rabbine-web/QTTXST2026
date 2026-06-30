import math
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
Given a kauffman state, returns an ordered pair for each closed loop, with indicies 
bounding where the loop occurs in the state 
"""
def find_closed_loops(
    state: str,
    numStrands: int
) -> list[tuple[int, int]]:
    
    kauf_state = int(state, 2)
    required_repitions = math.ceil(kauf_state.bit_length() / (numStrands - 1))
    total_length = required_repitions * (numStrands - 1)
    excluded_length = total_length - 1

    forward_strands = []
    closed_loops = []

    for reptition in range(required_repitions):
        for element_index in range(numStrands - 1):
            position = (reptition * ( numStrands - 1)) + element_index
            has_element = kauf_state >> (total_length - position - 1) & 0b1
            string_position = excluded_length - position
            
            #print(str(position) + " " + str(has_element))

            if has_element:
                forward_strands.append([element_index, element_index + 1, string_position])
                #print("initially " + str(forward_strands))
                # only grows the range
                range_was_changed = merge_ranges(forward_strands)
                merged = 0

                for i in reversed(range(len(forward_strands) - 1)):
                    if(forward_strands[-1][0] > forward_strands[i][0] and forward_strands[-1][1] < forward_strands[i][1]):
                        # if contained within another range, then cant
                        break

                    if forward_strands[-1][0] == forward_strands[i][0] and forward_strands[-1][1] == forward_strands[i][1] :
                        #print("closed loop detected 1")
                        closed_loops.append([forward_strands.pop(i)[2], string_position])
                
                # if the element could connect to an exisiting range, check if it creates a closed loop or can connect to another range to merge
                while range_was_changed:
                    # if the range is identical to the previous range, then it's a closed loop
                    for i in reversed(range(len(forward_strands) - 1)):
                        if(forward_strands[-1][0] > forward_strands[i][0] and forward_strands[-1][1] < forward_strands[i][1]):
                            # if contained within another range, then cant
                            break

                        if forward_strands[-1][0] == forward_strands[i][0] and forward_strands[-1][1] == forward_strands[i][1] :
                            #print("closed loop detected 2")
                            closed_loops.append([forward_strands.pop(i)[2], string_position])

                    # get potentially merged range index, if -1 then no merge
                    range_was_changed = merge_ranges(forward_strands)
                    merged += 1
                
                #print("merged to " + str(forward_strands))

                # if there's not 2 forward facing ends, then it's impossible to loop since we need 2 forward facing ends to connect to each other
                if(forward_strands[-1][0] == forward_strands[-1][1]):
                    #print("closed loop detected 3")
                    closed_loops.append([forward_strands.pop()[2], string_position])
                    forward_strands.append([element_index, element_index + 1, string_position])

                # if it only merged once, then that means one strand points back
                if merged != 0:
                    if merged == 1:
                        #print("merged backwards, impossible to loop")
                        forward_strands.pop()
                    forward_strands.append([element_index, element_index + 1, string_position])
                #print("ends up " + str(forward_strands) + "\n")
    #print("left over " + str(forward_strands))

    return closed_loops

"""
After updating the range of a loop, check if it can connect to another loop. 
If so, merge the two loops into one and return the index of the loop to keep. If not, return -1.
"""
def merge_ranges(forward_strands):
    # if the bottom of one range is the same as the top of another, then they are connected
    changed_range = len(forward_strands) - 1
    for other_range in reversed(range(len(forward_strands) - 1)):
        if(forward_strands[changed_range][0] > forward_strands[other_range][0] and forward_strands[changed_range][1] < forward_strands[other_range][1]):
            # if contained within another range, then cant
            return False


        ###print("checking connection, > 0")
        if(forward_strands[changed_range][0] == forward_strands[other_range][1]):
            # since connected bottom to top, set new bottom
            forward_strands[changed_range][0] = forward_strands[other_range][0]
        
        elif(forward_strands[changed_range][1] == forward_strands[other_range][0]):
            # since connected top to bottom, set new top
            forward_strands[changed_range][1] = forward_strands[other_range][1]

        # these will reduce the range since bottom connected bottom
        elif(forward_strands[changed_range][0] == forward_strands[other_range][0]):

            forward_strands[changed_range][0] = min(forward_strands[changed_range][1], forward_strands[other_range][1])
            forward_strands[changed_range][1] = max(forward_strands[changed_range][1], forward_strands[other_range][1])

        # these will reduce the range since bottom connected bottom
        elif(forward_strands[changed_range][1] == forward_strands[other_range][1]):
            if(forward_strands[changed_range][0] < forward_strands[other_range][0]):
                forward_strands[changed_range][1] = forward_strands[other_range][0]
            else:
                forward_strands[changed_range][1] = forward_strands[changed_range][0]
                forward_strands[changed_range][0] = forward_strands[other_range][0]
        else:
            return False
        
        forward_strands[-1][2] = forward_strands.pop(other_range)[2]
        return True
        
    return False


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



if __name__ == "__main__":

    state = "10100"
    numStrands = 3
    print(find_closed_loops(state, numStrands))