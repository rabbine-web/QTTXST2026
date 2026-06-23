import igraph as ig
import matplotlib.pyplot as plt
"""
Using n = 3 case to reduce cases
"""


"""
Args:
    n is the number of strands
    k is the number of repitions
        integers will be represent states through binary, 
"""
def generate_maps(k):
    n = 3
    # create a list of valid states for every hom degree
    states_of_hom_deg = [[0]]
    # map end result to the prev_state and the element added to get there
    maps_of_hom_deg = {}

    repition_size = n - 1
    max_val = 1 << (k * repition_size)


    one_repition_mask = (1 << (repition_size)) - 1

    # continue to generate while still elements left in last layer to build off of
    while states_of_hom_deg[-1]:
        valid_states = states_of_hom_deg[-1]
        # set up next layer
        states_of_hom_deg.append([])

        # try building off every valid state
        for prev_state in valid_states:
            print("building off of prev state: " + bin(prev_state))
            
            # try adding 1 temperlieb element, [e1,e2...en-1], into the last repition
            for added_elm in range(repition_size):
                # hold onto potential new states to add to next layer
                new_states = []

                # we can try adding that element to every non zero repition
                insert_at_rep = 0
                index = (repition_size - added_elm) - 1 # starting from the end of the binary
                
                # get the repition we're trying to add to
                cur_repition = (prev_state >> (repition_size * insert_at_rep)) & one_repition_mask
                # some repitions can be added to repitions 
                while(cur_repition != 0):
                    if((cur_repition >> index) & 0b1 == 0):
                        new_states.append(prev_state | 1 << (index + (insert_at_rep * repition_size)))

                    insert_at_rep += 1
                    cur_repition = (prev_state >> (repition_size * insert_at_rep)) & one_repition_mask
                
                # moved to a repition that has an open spot to add element
                new_states.append(prev_state | 1 << (index + (insert_at_rep * repition_size)))

                # last element can be added one reptition ahead since avoids type 1
                if(added_elm == repition_size - 1):
                    insert_at_rep += 1
                    cur_repition = (prev_state >> (repition_size * insert_at_rep)) & one_repition_mask
                    # if next rep down is open
                    if (cur_repition >> index) & 0b1 == 0:
                        new_states.append(prev_state | 1 << (index + (insert_at_rep * repition_size)))







                # check validity of new states and add to next layer and mapping if valid
                for temp_state in new_states:
                    #print("checking " + bin(temp_state) + " from " + bin(prev_state) + " by adding element " + str(added_elm))
                    if(not is_valid(value= temp_state, n=n) or temp_state > max_val):
                        print("not valid " + bin(temp_state))
                        continue

                    #print("valid " + bin(temp_state))
                    existing_maps = maps_of_hom_deg.get(temp_state, [])
                    if(not temp_state in states_of_hom_deg[-1]):
                        states_of_hom_deg[-1].append(temp_state)

                    #if(not exists_in_map(existing_maps, (prev_state, temp_state), added_elm)):
                    if(not (prev_state, added_elm) in existing_maps):
                        existing_maps.append((prev_state, added_elm))
                        maps_of_hom_deg[temp_state] = existing_maps
                
            
            # TODO: observe how much element n-1 has lee way?
            #TODO: then try the indirect mappings of prev state

            type_one_indirect = generate_indirect_type_one(prev_state)
            type_two_indirect = generate_indirect_type_two(prev_state)
            print("potential cases include: " + str([bin(x) for x in type_one_indirect]) + " and " + str([bin(y) for y in type_two_indirect]))
            
            for potential_state in (type_one_indirect):
                if(not is_valid(potential_state, n=n)):
                    print("not valid " + bin(potential_state))
                    continue

                print("indirect found from " + bin(prev_state) + " to " + bin(potential_state))

                existing_maps = maps_of_hom_deg.get(potential_state, [])
                if(not potential_state in states_of_hom_deg[-1]):
                    states_of_hom_deg[-1].append(potential_state)

                if(not -1 in existing_maps):
                    existing_maps.append((prev_state, -1))
                    maps_of_hom_deg[potential_state] = existing_maps
            #print("repeating " + str(len(states_of_hom_deg)) + " " + str(states_of_hom_deg[-1]))
        
            
            for potential_state in (type_two_indirect):
                if(not is_valid(potential_state, n=n)):
                    print("not valid " + bin(potential_state))
                    continue

                print("indirect found from " + bin(prev_state) + " to " + bin(potential_state))

                existing_maps = maps_of_hom_deg.get(potential_state, [])
                if(not potential_state in states_of_hom_deg[-1]):
                    states_of_hom_deg[-1].append(potential_state)

                if(not -2 in existing_maps):
                    existing_maps.append((prev_state, -2))
                    maps_of_hom_deg[potential_state] = existing_maps
            print("repeating " + str(len(states_of_hom_deg)) + " " + str(states_of_hom_deg[-1]))
        

    #print(states_of_hom_deg)
    for hom_deg in states_of_hom_deg:
        for state in hom_deg:
            if(state < 0b1 << (repition_size * k)):
                print(bin(state)[2:].zfill(repition_size * k))
        print()


    for key, value in maps_of_hom_deg.items():
        print(f"From {bin(key)[2:].zfill(k*(n - 1))} takes element from { ([",  ".join("(" + bin(v[0])[2:].zfill(k*(n - 1)) + ", " + str(v[1]) + ")" for v in value)]) } ")
    
    return (states_of_hom_deg, maps_of_hom_deg)
"""
When fed a binary string, will respond whether it corresponds to a type 
TODO need to implement + - closed loops to seperate out two_target/sources
"""
def is_valid(value, n):
    #print("chceking valid  " + bin(value))
    # since in most cases we only add if no 1 in this position before
    mask = 0b111

    one_source = 0b100
    one_target = 0b101
    two_source = 0b101
    two_target = 0b111

    index = 0


    while(value >= (0b1 << index)):
        two_reps = (value >> index) & mask
        
        if(two_reps == one_source):
            return False
        elif(index % n != 0 and (two_reps == two_target or two_reps == two_source)):
            return False
        index += 1

    return True

# technically 2 cases for 4 strand
def generate_indirect_type_one(prev_state):
    indirect_states = []
    index = 0
    mask = 0b111 

    type1_potential = 0b001
    type1_end = 0b110
    while(prev_state >= (0b1 << index)):
        if(((prev_state >> index) & mask) == type1_potential):
            # need to set up the site where replacing, sets those 4 digits to 0
            cleared_state = prev_state & ~(mask << index)
            indirect_states.append(cleared_state | (type1_end << index))
        index += 1
    return indirect_states
    


def generate_indirect_type_two(prev_state):
    indirect_states = []
    index = 0
    mask = 0b111

    type2_potential_one = 0b001
    type2_potential_two = 0b110
    #TODO: check if 10_01 is possible for indirect
    type2_end = 0b111
    while(prev_state > (0b1 << index)):
        masked_state = (prev_state >> index) & mask
        if(index % 3 != 0 and (masked_state == type2_potential_one or masked_state == type2_potential_two)):
            # need to set up the site where replacing
            cleared_state = prev_state & ~(mask << index)
            indirect_states.append(cleared_state | (type2_end << index))
        index += 1
    return indirect_states


    



if __name__ == "__main__":
    k = 3

    states_and_map = generate_maps(k)
    #print(states_and_map)
    
    g = ig.Graph(directed = True)
    edges = []
    edge_properties = []

    vertices = [bin(item)[2:] for sublist in states_and_map[0] for item in sublist]
    print(vertices)
    g.add_vertices(vertices)
    g.vs["label"] = vertices


    for child_id, children in states_and_map[1].items(): 
        for parent_id, prop in children: 
            parent_str = bin(parent_id)[2:]
            child_str = bin(child_id)[2:]
            #print((parent_str, child_str))
            edges.append((parent_str, child_str)) 
            edge_properties.append(prop)

    g.add_edges(edges)
    g.es["property"] = edge_properties

    root_str = bin(states_and_map[0][0][0])[2:] # Adjust indexing depending on your exact nested structure
    root_index = g.vs.find(root_str).index
    
    # 6. Generate the tree layout using the correct root index
    layout = g.layout_reingold_tilford(root=[root_index]) 
    
    fig, ax = plt.subplots(figsize=(6, 6))
    ig.plot(g, layout=layout, target=ax, vertex_size=40)
    plt.show()

