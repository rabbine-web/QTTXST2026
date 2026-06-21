import igraph

from .BraidResolution import ResolutionCube
from .Display import Display, VerticalSplit



# Generate all binary strings of length k*(n-1) with i ones
def binary_strings(n, k, i):
    m = k * (n - 1)

    if i == 0:
        return [""]
    if i < 0 or i > m:
        return []
    
    result = []

    def backtrack(pos, ones_left, s):
        if pos == m:
            if ones_left == 0:
                result.append(s)
            return

        remaining = m - pos

        if ones_left > remaining:
            return

        # place 0
        backtrack(pos + 1, ones_left, s + "0")

        # place 1
        if ones_left > 0:
            backtrack(pos + 1, ones_left - 1, s + "1")

    backtrack(0, i, "")
    return result

def to_tl(state, n, k):
    word = []

    for i, bit in enumerate(state):
        if bit == "1":
            word.append(i % (n - 1) + 1)

    return word

def is_valid_word(word, n, k):

    pass

def identify_valid_states(states):
    # Placeholder for the actual implementation
    pass

if __name__ == "__main__":

    window = Display()

    window.content = VerticalSplit()
    window.content.right = ResolutionCube(2,3)
    window.content.left = ResolutionCube(1,3)

    window.display()