def reduce_kauf_man(temp_lieb_elements, n):
    # create an array of extra size [0, n] since we just use [1, n - 1]
    # only need booleans since if commutable any following is can be ignored based on rule 1 or 3
    can_reach = [False] * (n + 2)

    # record where this value was last seen
    most_recent = [-1] * (n + 2)

    # tracking if there was an adjacent behind that can be commuted to
    # [0] means index - 1, [1] means index + 1
    reach_before_blocked = [[-1, -1] for _ in range(n + 2)]

    # Mark what to keep since insertion and deletion is slow
    keep = [False] * len(temp_lieb_elements)

    # Deciding what to keep
    for i in range(len(temp_lieb_elements)):
        # indexes should be within [1, n -1]
        element_type = temp_lieb_elements[i]
        if(element_type == n - 1):
            keep[i] = True

            # record where adjacent elements are located before blocking
            reach_before_blocked[element_type][0] = most_recent[element_type - 1]
            reach_before_blocked[element_type][1] = most_recent[element_type + 1]

            # block values
            most_recent[element_type + 1] = -1
            most_recent[element_type - 1] = -1 


            #need to block adjacent values since can no longer commute past an adjacent element
            can_reach[element_type - 1] = False
            can_reach[element_type] = True # we're literaly at it, should be able to commute
            can_reach[element_type + 1] = False
            most_recent[element_type] = i

        # if this a duplicate of an element that can be commuted to
        elif can_reach[element_type]:
            # then ignore this value and move on
            keep[i] = False

        # if cannot commutable to duplicate, then either relation 3 or nothing
        else:
            # e_i e_i-1 e_i -> e_i,    
            # second e_i need to commute to e_i-1
            # e_i-1 needs to comute to first e_1
            if can_reach[element_type - 1] and reach_before_blocked[element_type - 1][1] != -1: # element_type - 1 + 1 = element_type
                # don't keep second e_i and e_i-1
                keep[i] = False
                keep[most_recent[element_type - 1]] = False # must only be one element_type - 1 otherwise can't commute to first e_i

                # restore commutable as if e_i-1 never added
                most_recent[element_type] = reach_before_blocked[element_type - 1][1] 
                most_recent[element_type - 1] = -1 # must be -1 as then it'd be relation 1 right now
                most_recent[element_type - 2] = reach_before_blocked[element_type - 1][0] 

                # e_i-2 is unrelated so no info on it, |= since if currently commutable no need to overwrite with false
                can_reach[element_type - 2] |= (reach_before_blocked[element_type - 1][0] != -1) #
                # e_i-1 can't have a commutable duplicate or else it would activate this elif first
                can_reach[element_type - 1] = False
                # e_i must be commutable since e_i-1 could commute to it
                can_reach[element_type] = True 

                # no e_i-1 no longer blocks, so update
                reach_before_blocked[element_type - 1][0] = reach_before_blocked[element_type - 1][1] = -1

            # e_i e_i-1 e_i -> e_i,    
            # second e_i need to commute to e_i-1
            # e_i-1 needs to comute to first e_1
            elif can_reach[element_type + 1] and reach_before_blocked[element_type + 1][0] != -1: # element_type + 1 - 1 = element_type
                # don't keep second e_i and e_i+1
                keep[i] = False
                keep[most_recent[element_type + 1]] = False # must only be one element_type + 1 otherwise can't commute to first e_i

                # restore commutable as if e_i+1 never added
                most_recent[element_type] = reach_before_blocked[element_type + 1][0] 
                most_recent[element_type + 1] = -1 # must be -1 as then it'd be relation 1 right now
                most_recent[element_type + 2] = reach_before_blocked[element_type + 1][1] 

                # e_i+2 is unrelated so no info on it, |= since if currently commutable no need to overwrite with false
                can_reach[(element_type + 2) % (n + 1)] |= (reach_before_blocked[element_type + 1][1] != -1) #
                # e_i+1 can't have a commutable duplicate or else it would activate this elif first
                can_reach[element_type + 1] = False
                # e_i must be commutable since e_i-1 could commute to it
                can_reach[element_type] = True 

                # no e_i+1 no longer blocks, so update
                reach_before_blocked[element_type + 1][0] = reach_before_blocked[element_type + 1][1] = -1

            # nothing, add a blockade
            else:
                # this is the element we keep
                keep[i] = True

                # record where adjacent elements are located before blocking
                reach_before_blocked[element_type][0] = most_recent[element_type - 1]
                reach_before_blocked[element_type][1] = most_recent[element_type + 1]

                # block values
                most_recent[element_type + 1] = -1
                most_recent[element_type - 1] = -1 

                #need to block adjacent values since can no longer commute past an adjacent element
                can_reach[element_type - 1] = False
                can_reach[element_type] = True # we're literaly at it, should be able to commute
                can_reach[element_type + 1] = False
                most_recent[element_type] = i

        
    reduced = [0] * sum(keep)
    index = 0
    for i in range(len(temp_lieb_elements)):
        if(keep[i]):
            reduced[index] = temp_lieb_elements[i]
            index += 1
    return reduced
    
    
def temp_lieb_to_whittled(reduced, n):
    kauf_state = [0] * (n - 1)
    cur_rep = 0
    last_index = n

    for elm_index in reversed(reduced):
        if last_index <= elm_index:
            cur_rep += 1
            kauf_state += [0] * (n - 1)
        last_index = elm_index
        kauf_state[cur_rep * (n - 1) + (n - last_index - 1)] = 1
    return "".join(map(str, kauf_state[::-1]))
           


if __name__ == "__main__":
    # INPUTS HERE
    n = 4
    temp_lieb_int = [3,3,1,2,1]
    reduced = reduce_kauf_man(temp_lieb_int, n)
    whittled_kauf = temp_lieb_to_whittled(reduced, n)
    print(whittled_kauf)
