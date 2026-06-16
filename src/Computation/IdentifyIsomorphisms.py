import timeit
import random

from ..Visuals.TorusBraidVisual import *

def pPrint(SET):
    """
    Pretty-prints a set of states in binary format (reversed bit order).
    
    Converts each integer state to a binary string with k*(n-1) bits and
    reverses the bit order for display.
    
    Args:
        SET: A set of integer states to print
    """
    for s in SET:
        print(format(s, f'0{k*(n-1)}b')[::-1])

def identifyState(state, k, n):
    """
    Identifies Type I and Type II isomorphism targets. This is will not choose
    distinguished isomorphisms but instead identifies the potential sources and targets
    for these isomorphisms.
    
    Args:
        state: Integer representing a binary state
    """
    for i in range((k-1)*(n-1)):
        if not (state >> i) & 1:
            continue
 
        bit_i_plus_nm1     = (state >> (i + (n-1)))   & 1
        bit_i_plus_1       = (state >> (i + 1))        & 1
        bit_i_plus_nm1_m1  = (state >> (i + (n-1) - 1)) & 1
 
        # Case 1
        if bit_i_plus_nm1 == 0 and bit_i_plus_1 == 0 and bit_i_plus_nm1_m1 == 0:
            type1Source.add(state)
            type1Target.add(state | (1 << (i + (n-1))))
 
        # Case 2
        if bit_i_plus_nm1 == 1 and bit_i_plus_1 == 0 and bit_i_plus_nm1_m1 == 0 and i % (n-1) < n-2:
            type2Source.add(state)
            type2Target.add(state | (1 << (i + 1)))

def randomTrials():
    """
    Performs a series of random trial runs to estimate computation time.
    
    Generates random states and calls identifyState on each, accumulating
    data in the global type sets. This is used for Monte Carlo estimation
    of total computation time for exhaustively processing all possible states.
    
    Executes numTests iterations of random state generation and identification.
    """

    for i in range(numTests):

        randomState = random.randrange(1 << k*(n-1))
        identifyState(randomState, k, n)


if __name__ == "__main__":

    # Parameters for the state space
    n=7
    k=10
    numTests = 100000
    numRepeats = 5

    kauffmanStates = range(1 << k*(n-1))

    # Global sets to accumulate state categorization results
    type1Source = set()
    type1Target = set()
    type2Source = set()
    type2Target = set()

    ## Monte Carlo style estimate of total compute time
    # Run random trials multiple times and average to get an estimate
    # Then extrapolate to the full state space
    trialTime = timeit.timeit(randomTrials, number=numRepeats)/numRepeats
    estimatedSeconds = trialTime * ((1 << k*(n-1))/numTests)
    print(f"Estimated time for n={n}, k={k}:")
    print(f"SEC: {format(estimatedSeconds,',')}")
    print(f"MIN: {estimatedSeconds/60}")
    print(f"HRS: {estimatedSeconds/(60*60)}")
    print(f"DAY: {estimatedSeconds/(60*60*24)}")
    print(f"YRS: {estimatedSeconds/(60*60*24*365):,}")



##for state in kauffmanStates:
##
##    """
##        given a state iterate through all the ones in the binary representation
##        which occur before the (k-1)(n-1)-th bit. For a given 1 that occurs in the
##        i-th bit we are trying to identify two possibilities:
##
##        Case 1 (Type 1 Source):
##            iff the (i+(n-1)) bit is a zero and the (i+1) bit is zero and the
##            (i+(n-1)-1) bit is zero:
##            Add this number to the type1Source set, flip the (i+(n-1)) bit to a 1 and
##            add the resulting number to the type1Target set
##
##        Case 2 (Type 2 Source):
##            iff the (i+(n-1)) bit is a one and the (i+1) bit is a zero and the
##            (i+(n-1)-1) bit is zero AND the i%(n-1)<n-2:
##            Add this number to the type2Source set, flip the (i+1) to a 1 and add
##            the resulting number to the type2Target set
##    """
##
##    identifyState(state, k, n)
##
##
##survivingStates = set(kauffmanStates)
##survivingStates -= type1Source
##survivingStates -= type2Target
##survivingStates -= type2Source
##
##
##print("ALL")
##pPrint(survivingStates)
##print(len(survivingStates))
##print()

##print("TYPE 1 SOURCE")
##pPrint(type1Source)
##print()
##
##print("TYPE 1 TARGET")
##pPrint(type1Target)
##print()
##
##print("TYPE 2 SOURCE")
##pPrint(type2Source)
##print()
##
##print("TYPE 2 TARGET")
##pPrint(type2Target)


##display_state_set(type1Target, k, n, title="TYPE 1 TARGET")
##display_state_set(type2Source, k, n, title="TYPE 2 SOURCE")









