def detect_closed_loops(kauf_state, n, k):
    forward_strands = []
    num_closed_loops = 0
    for reptition in reversed(range(k)):
        for element_index in range(n - 1):
            # affects strands, element_index and element_index + 1
            has_element = kauf_state >> (reptition * (n - 1) + (n - 2 - element_index) ) & 0b1

            if has_element:
                forward_strands.append([element_index, element_index + 1])
                print("initially " + str(forward_strands))
                # only grows the range
                changed_range = check_connection(forward_strands)
                merged = 0


                for i in reversed(range(len(forward_strands) - 1)):
                    if(forward_strands[-1][0] > forward_strands[i][0] and forward_strands[-1][1] < forward_strands[i][1]):
                        # if contained within another range, then cant
                        break

                    if forward_strands[-1] == forward_strands[i]:
                        print("closed loop detected")
                        num_closed_loops += 1
                        forward_strands.pop()
                
                # if the element could connect to an exisiting range, check if it creates a closed loop or can connect to another range to merge
                while changed_range:
                    # if the range is identical to the previous range, then it's a closed loop

                    for i in reversed(range(len(forward_strands) - 1)):
                        if(forward_strands[-1][0] > forward_strands[i][0] and forward_strands[-1][1] < forward_strands[i][1]):
                            # if contained within another range, then cant
                            break

                        if forward_strands[-1] == forward_strands[i]:
                            print("closed loop detected")
                            num_closed_loops += 1
                            forward_strands.pop()
                
                    # get potentially merged range index, if -1 then no merge
                    changed_range = check_connection(forward_strands)
                    merged += 1
                
                print("merged to " + str(forward_strands))

                # if there's not 2 forward facing ends, then it's impossible to loop since we need 2 forward facing ends to connect to each other
                if(forward_strands[-1][0] == forward_strands[-1][1]):
                    print("closed loop detected")
                    num_closed_loops += 1
                    forward_strands.pop()
                    forward_strands.append([element_index, element_index + 1])

                elif merged == 1:
                    print("merged backwards, impossible to loop")
                    forward_strands.pop()
                    
                # only merges twice if merging top and bottom
                if merged == 2:
                    # TODO: need to properly split the range depending on order, like [0,3] when canceled [0,3] by a merge of [1,2] splits into [0,1] and [2,3]
                    # or when canceled [0,3] by a merge of [0, 1] splits into [1,3]
 
                    forward_strands.append([element_index, element_index + 1])
                print("ends up " + str(forward_strands))
                print()


    
    print("leftover forward_strands: " + str(forward_strands))

    return num_closed_loops

"""
After updating the range of a loop, check if it can connect to another loop. 
If so, merge the two loops into one and return the index of the loop to keep. If not, return -1.
"""
def check_connection(forward_strands):
    # if the bottom of one range is the same as the top of another, then they are connected
    changed_range = len(forward_strands) - 1
    for other_range in reversed(range(len(forward_strands) - 1)):
        if(forward_strands[changed_range][0] > forward_strands[other_range][0] and forward_strands[changed_range][1] < forward_strands[other_range][1]):
            # if contained within another range, then cant
            return False


        #print("checking connection, > 0")
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
        forward_strands.remove(forward_strands[other_range])
        return True
        
    return False



if __name__ == "__main__":
    """
    kauf_state = 0b101010011100
    n = 4
    k = 5
    """
    """
    kauf_state = 0b101001100
    n = 4
    k = 3
    """
    """
    kauf_state = 0b1111
    n = 3
    k = 2
    """
    
    kauf_state = 0b1010
    n = 3
    k = 2
    
    print(detect_closed_loops(kauf_state, n, k))