import igraph as ig
import matplotlib.pyplot as plt
"""
state                       a binary string representing a kaufman state
numStrands                  the numebr of strands

list[tuple[str, int, int]]  a list of the states, the type of isomorphism, what bit flips back
"""

def find_direct_targets(
    state: str, 
    numStrands: int
) -> list[tuple[str, int, int]]:
        
    if(numStrands != 3):
        raise ValueError("numStands not 3")


    # convert starting kaufman state
    kaufman_state = int(state, 2)
    direct_targets = []

    repition_size = numStrands - 1
    repition_mask = (0b1 << repition_size) - 1

    # try adding all possible elements
    for added_temp_lieb in range(numStrands):
        # hold onto potential new states to add to next layer
        possible_states = []

        # we can try adding that element to every non zero repition
        insert_at_rep = 0
        index = (repition_size - added_temp_lieb) - 1 # starting from the end of the binary
        
        # get the repition we're trying to add to
        cur_repition = kaufman_state & repition_mask
        # some repitions can be added to repitions 
        while(cur_repition != 0):
            if((cur_repition >> index) & 0b1 == 0):
                possible_states.append(kaufman_state | 1 << (index + (insert_at_rep * repition_size)))

            insert_at_rep += 1
            cur_repition = (kaufman_state >> (repition_size * insert_at_rep)) & repition_mask
        
        # add an element to the farthest reptition
        possible_states.append(kaufman_state | 1 << (index + (insert_at_rep * repition_size)))

        # detect if the possible states are targets or not
        for temp_state in possible_states:
            string_state = f"{temp_state:b}"
            detected = detect_dist_target(string_state, numStrands)
            direct_targets.append((string_state, detected[0], detected[1]))
            
    return direct_targets