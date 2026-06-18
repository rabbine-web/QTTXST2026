import numpy as np
import timeit
import random

"""
kauf_num is an int which represents a kaufman state with binary representation
        - this binary string will
n is the number of strands
k is the number of repitions
"""
def gauss_elim_iso(kauf_num, n, k):
    # treat     '+' means +, '-' means -, '_' means +-
    closed_signs = []

    # Mask used to grab needed bits
    mask_normal = 0b11 | 0b11 << (n - 2)

    # Mask for plus minus
    mask_pm_first = 0b11 | 0b1 << (n - 2) # to grab 1...01
    #mask_pm_mid = 0b11 | 0b11 << (n - 2) # to grab 10...01 # just normal
    mask_pm_last = 0b1 | 0b11 << (n - 2 + 1) # to grab 10...1

    mask_repition = (0b1 << n) - 1

    one_source_val = 0b00 | 0b10 << (n - 2) # 10...00
    one_target_val = 0b01 | 0b10 << (n - 2) # 10...01
    two_source_val = 0b01 | 0b10 << (n - 2) # 10...01
    two_target_val = 0b01 | 0b11 << (n - 2) # 11...01


    # reversed would be 10w1
    pm_first = 0b1 | 0b10 << (n - 2 + 1) # 10...1
    # reversed would be 1w01
    pm_last = 0b01 | 0b1 << (n - 2) # 1...01

    for repition in range(k - 1): # each repition, stop 1 early since no next rep to check at repition = k - 1
        # for stand 1
        #check basic stuff first
        masked_val = (kauf_num >> ((repition * (n - 1)))) & mask_normal
        masked_rep = (kauf_num >> ((repition * (n - 1)))) & mask_repition

        if(masked_val == one_source_val):
            return 1
        elif(masked_val == two_source_val):
            return 3
        elif(masked_val == two_target_val):
            return 4
        
        # Plus Minus if there's a 1 inbetween, else Type 1 source
        masked_val = (kauf_num >> ((repition * (n - 1)))) & mask_pm_first
        if(masked_val == mask_pm_first):
            if(masked_rep > pm_first): # check if there's a 1 between
                closed_signs.append('_')
            else: # no one guarentees type 1 target since 10...1 -> 10...01
                closed_signs.append('+')

        # for stands [2, n-1]
        for i in range(1, n - 2): # each sigma within the repition

            # Shift to desired index and get bit values
            masked_val = (kauf_num >> ((repition * (n - 1)) + i)) & mask_normal
            masked_rep = (kauf_num >> ((repition * (n - 1)) + i)) & mask_repition

            if(masked_val == one_source_val):
                return 1
            elif(masked_val == one_target_val and mask_repition > one_target_val):
                #print(mask_repition > one_source_val)
                closed_signs.append('_')
            elif(masked_val == two_source_val):
                return 3
            elif(masked_val == two_target_val):
                return 4

        # type 1 only since type 2, i <= n - 2
        
        masked_val = (kauf_num >> ((repition * (n - 1)) + n - 2)) & mask_pm_last
        masked_rep = (kauf_num >> ((repition * (n - 1)) + n - 2)) & mask_repition


        if(masked_val == one_source_val):
            return 1
        if(masked_val == mask_pm_last and masked_rep > pm_last): # check if there's a 1 between 1...10
            closed_signs.append('_')
        elif(masked_val == one_target_val): # no 1 guarentees type 1 target
            closed_signs.append('+')

    return closed_signs

if __name__ == "__main__":
    # just plug in your wanted value
    n = 5
    k = 3

    # TODO improve program efficiency?
    survive = []
    S1 = []
    T1 = []
    
    S2 = []
    T2 = []

    labels = ["", "Type 1 Source", "Type 1 Target", "Type 2 Source", "Type 2 Target"]


    homologous_degree = [[] for _ in range(k * (n - 1) + 1)]

    # want binary from 0b0...0 to 0b1...1
    for kauf_state in range( 1 << ((n-1) * k) ):
        result_val = gauss_elim_iso(kauf_num=kauf_state, n=n, k=k)

        if isinstance(result_val, list):
            #print(kauf_state.bit_count())
            homologous_degree[kauf_state.bit_count()].append(bin(kauf_state)[2:].zfill((n-1) * k) + " : [" + ', '.join(result_val) + "]")
            print(bin(kauf_state)[2:].zfill((n-1) * k ) + " : [" + ', '.join(result_val) + "]")
        else:
            print(bin(kauf_state)[2:].zfill((n-1) * k ) + " : " + labels[result_val])
    
    """
    for kauf_set in homologous_degree:
        for state in kauf_set:
            print(state)
        print()
        """

                



        
    