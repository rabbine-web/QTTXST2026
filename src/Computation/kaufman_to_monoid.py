def kaufman_to_monoid(
    kauf_state : str,
    numStrands : int
)-> list[int]:

    num_repitions = kauf_state
    temp_lieb = [] 

    index = len(kauf_state) - 1
    element = numStrands - 1 - 1

    while index >= 0:
        if(kauf_state[index] == '1'): #if 1
            temp_lieb.append(element + 1)
        index -= 1
        element = (element - 1) % (numStrands - 1)
        
    return temp_lieb 


print(kaufman_to_monoid("1010000", 3))

