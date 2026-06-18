import bisect

"""
Args:
    n is the number of strands
    k is the number of repitions
        integers will be represent states through binary, 
"""
def generate_maps(n, k):
    # create a list of valid states for every hom degree
    states_of_hom_deg = [[0]]
    maps_of_hom_deg = {}

    repition_size = n - 1
    max_val = 1 << (k * repition_size)

    one_repition_mask = (1 << (repition_size)) - 1

    # continue to generate while still elements left in last layer
    while states_of_hom_deg[-1]:
        valid_states = states_of_hom_deg[-1]
        states_of_hom_deg.append([])
        if(len(states_of_hom_deg) >= ((n - 1) * k + 1)):
            break
        # try every valid state
        for prev_state in valid_states:
            # try adding 1 temperlieb element, [e1,e2...en-1], into the last repition
            

            for added_elm in range(repition_size):
                new_states = []

                # we can try adding that element to every non zero repition
                insert_at_rep = 0
                index = (repition_size - added_elm) - 1 # starting from the end of the binary
                
                cur_repition = (prev_state >> (repition_size * insert_at_rep)) & one_repition_mask
                while(cur_repition != 0):
                    if((cur_repition >> index) & 0b1 == 0):
                        new_states.append(prev_state | 1 << (index + (insert_at_rep * repition_size)))
                    insert_at_rep += 1
                    cur_repition = (prev_state >> (repition_size * insert_at_rep)) & one_repition_mask
                
                if(insert_at_rep == 0 or added_elm == repition_size - 1):
                    if((cur_repition >> index) & 0b1 == 0):
                        new_states.append(prev_state | 1 << (index + (insert_at_rep * repition_size)))


                for temp_state in new_states:
                    if(max_val < temp_state):
                        continue
                    
                    if(not is_valid(value= temp_state, n=n)):
                        print("not valid " + bin(temp_state))
                        continue

                    
                    existing_maps = maps_of_hom_deg.get((prev_state, temp_state), [])
                    if(not temp_state in states_of_hom_deg[-1]):
                        states_of_hom_deg[-1].append(temp_state)

                    #if(not exists_in_map(existing_maps, (prev_state, temp_state), added_elm)):
                    if(not added_elm in existing_maps):
                        existing_maps.append(added_elm)
                        maps_of_hom_deg[(prev_state, temp_state)] = existing_maps
                
            
            # TODO: observe how much element n-1 has lee way?
            #TODO: then try the indirect mappings of prev state
            type_one_indirect = generate_indirect_type_one(prev_state)
            type_two_indirect = generate_indirect_type_two(prev_state)
            for potential_state in (type_one_indirect + type_two_indirect):
                if(not is_valid(potential_state, n=n)):
                    print("not valid " + bin(potential_state))
                    continue

                
                existing_maps = maps_of_hom_deg.get((prev_state, potential_state), [])
                if(not potential_state in states_of_hom_deg[-1]):
                    states_of_hom_deg[-1].append(potential_state)

                if(not -1 in existing_maps):
                    existing_maps.append(-1)
                    maps_of_hom_deg[(prev_state, potential_state)] = existing_maps



            



        if(len(states_of_hom_deg) >= 5):
            break

    #print(states_of_hom_deg)
    for hom_deg in states_of_hom_deg:
        for state in hom_deg:
            print(bin(state))
        print()


    for key, value in maps_of_hom_deg.items():
        print(f"From {bin(key[0])} takes element {[v + 1 for v in value]} to {bin(key[1])}")
    


def is_valid(value, n):
    #print("chceking valid  " + bin(value))
    # since in most cases we only add if no 1 in this position before
    mask = 0b11 << (n - 2) | 0b11

    one_source = 0b1 << (n - 1) | 0b0
    one_target = 0b1 << (n - 1) | 0b1
    two_source = 0b1 << (n - 1) | 0b1
    two_target = 0b1 << (n - 1) | 0b11

    index = 0


    while(value >= 0b1 << index):
        two_reps = (value >> index) & mask
        
        if(two_reps == one_source or (index % n != 0 and two_reps == two_target)):
            return False
        index += 1

    return True

"""
def exists_in_map(existing_maps, key, new_elm):
    # Binary search to find insertion point
    idx = bisect.bisect_left(existing_maps, new_elm)
    # Verify index boundaries and match
    return idx < len(existing_maps) and existing_maps[idx] == new_elm
"""


def generate_indirect_type_one(prev_state):
    indirect_states = []
    index = 0
    mask = 0b11 << (n - 2) | 0b11

    type1_potential = 0b00 << (n - 2) | 0b01
    type1_end_one = 0b11 << (n - 2) | 0b00
    type1_end_two = 0b10 << (n - 2) | 0b10
    while(prev_state >= (0b1 << index)):
        if((prev_state >> index) & mask == type1_potential):
            # need to set up the site where replacing, sets those 4 digits to 0
            cleared_state = prev_state & (~(mask << index))
            indirect_states.append(cleared_state | (type1_end_one << index))
            indirect_states.append(cleared_state | (type1_end_two << index))
        index += 1
    return indirect_states
    


def generate_indirect_type_two(prev_state):
    indirect_states = []
    index = 0
    mask = 0b11 << (n - 2) | 0b11

    type2_potential_one = 0b00 << (n - 2) | 0b01
    type2_potential_two = 0b11 << (n - 2) | 0b00
    #TODO: check if 10_01 is possible for indirect
    type2_end = 0b10 << (n - 2) | 0b11
    while(prev_state > (0b1 << index)):
        masked_state = (prev_state >> index) & mask
        if(masked_state == type2_potential_one or masked_state == type2_potential_two):
            # need to set up the site where replacing
            cleared_state = prev_state | (~(mask << index))
            indirect_states.append(cleared_state & (type2_end << index))
        index += 1
    return indirect_states


    



if __name__ == "__main__":
    n = 3
    k = 2
    generate_maps(n, k)
    mask = 0b11 << (n - 2) | 0b11
    print(bin(mask))
    print(bin((~(mask))))