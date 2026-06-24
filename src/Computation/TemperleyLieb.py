import timeit

from src.Visuals.Display import Display, FigureContainer, HorizontalSplit
from src.Visuals.TorusBraidVisual import visualize_kauffman_state

# Define torus braid strands and size
# See Algorithm Notes Section -1: Standard Notations
n=3
k=12

# Create Reusable Bitmasks for each k(n-1) bit
# See Algorithm Notes Section 0, Universal Optimizations
#
# This includes a bitmask which masks nothing. Deal with it. 
# bitmasks[i] = 2^i, a bit in the (i+1)-th position (1-indexed)
# Also includes one extra bitmask for iteration purposes
bitmasks = tuple(1 << i for i in range(k*(n-1)+1))

# Partition the 2^k(n-1) states into buckets based on leading zeros
# See Algorithm Notes Section 1, Detecting... ...from Kauffman States
#
# This partition excludes the all zeros case as this can never be a source or target
PPartition = [range(bitmasks[i*(n-1)],bitmasks[(i+1)*(n-1)]) for i in range(k)]
print(sum(len(i) for i in PPartition))
print(bitmasks[-1])


"""
Returns a list of integers ranging from 0 (inclusive) to 2^(k*(n-1)) (exclusive).
The binary representation of each integer represents a different kauffman state on
the torus braid with n strands and k twists.
"""
def kauffmanstates(n, k):
    return range(1 << (k*(n-1)))

def surviving_tl_states(numStrands: int, homDegree: int) -> list[list[int]]:

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

def tl_to_kauffman(tl_state: list[int], p=None) -> str:

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
    if p is None:
        result = result.zfill(2 * len(in_str))
    else:
        result = result.zfill(2 * p)

    return result

"""
Given a kauffman state s (an integer as a binary number) on a braid, and integers n,k
number of strands and number of twists repspectively, temperleylieb(s, n, k) outputs a
list of integers corresponding [a,b,c,...] encoding the Temperley-Lieb word ...e_c e_b e_a.
"""
def temperleylieb(s, n, k):
    m = n-1
    return [i % m + 1 for i in range(k*m) if s & (1 << i)]

def temperley2(s, n, k):
    m = n - 1
    out = []
    while s:
        lsb = s & -s
        pos = lsb.bit_length() - 1
        out.append(pos % m)
        s ^= lsb
    return out

def kauffman():
    global states
    states = kauffmanstates(n,k)

def timeTrial():

    def naive():
        return [temperleylieb(state,n,k) for state in states]

    def other():
        return [temperley2(state,n,k) for state in states]

    """
    Given the 2^k(n-1)
    """

    print(timeit.timeit(naive, number=1))
    print(timeit.timeit(other, number=1))



if __name__ == "__main__":
    for i in range(0, 10):

        states = surviving_tl_states(3, i)
        kauff = [tl_to_kauffman(state) for state in states]

        print(f"{i}-States: {states}")
        print(f"{i}-Kauffman: {kauff}")

        if len(states) != 2:
            print(f"    ERROR: too few states: {len(states)}")

        for state in states:

            k = max(3, i)
            display = Display(
                title=f"Torus Braid Visual: {state}",
                content=HorizontalSplit(ratio=0.33)
            )
            display.content.top=FigureContainer(
                visualize_kauffman_state(
                    tl_to_kauffman(state, p=k),  
                    p=k, q=3
                )
            )
            display.display()
            display.root.mainloop()

            if len(state) != i:
                print(f"    ERROR: State {state} has length {len(state)}, expected {i}")

        print()