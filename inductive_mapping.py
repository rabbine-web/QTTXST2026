from collections import deque
"""
n is the number of strands
k is the number of repitions
    integers will be represent states through binary, 
"""
def generate_maps(n, k):
    # create a list of valid states for every hom degree
    states_of_hom_deg = [[] for _ in range((n - 1) * k)]
    maps_of_hom_deg = [[] for _ in range((n - 1) * k)]
    hom_deg = 0

    repition_mask = (1 << (n - 1)) - 1

    # continue to generate while still elements left in last layer
    while states_of_hom_deg[hom_deg]:
        # try every valid state
        for prev_state in states_of_hom_deg[hom_deg]:
            # try adding 1 temperlieb element into the last repition
            for i in range(n - 1):
                index = (n - 2 - i)
                # we can try adding that element to every non zero repition

        hom_deg += 1


if __name__ == "__main__":
    n = 3
    k = 2
