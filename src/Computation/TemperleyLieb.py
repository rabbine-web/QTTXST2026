import timeit

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

##print(temperleylieb(
##    state=0b1010,
##    n=3,
##    k=2 
##   ))

states = []

def kauffman():
    global states
    states = kauffmanstates(n,k)


if __name__ == "__main__":

    ##print(timeit.timeit(kauffman, number=1))
    ##for s in states:
    ##    print(str(bin(s)) + ": ", temperleylieb(s, n, k))

    print


    def naive():
        return [temperleylieb(state,n,k) for state in states]

    def other():
        return [temperley2(state,n,k) for state in states]



    """
    Given the 2^k(n-1)
    """
        

    ##print(naive())


    print(timeit.timeit(naive, number=1))
    print(timeit.timeit(other, number=1))






