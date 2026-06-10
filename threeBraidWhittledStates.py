import time


# Input: n = number of strands, k = number of repetitions 
# Output: Returns a list of all the kauffman states in the form of '1001' for example
def generate_Kauffman_States(n,k):
    kauffmanStates = []
    for x in range((pow(2,(n-1)*k))):
        kauffmanStates.append(bin(x)[2:].zfill((n-1) * k ))
    return kauffmanStates

# Input: n = number of strands, k = number of repetitions, s = kauffman state
# Ooutput: returns the kauffman state in matrix form where there are n - 1 columns where the first column represents
# the first generator and the second column the second generator and so on. The first row corresponds to the first repetition,
# second row is the second repetition and so on.
# Imagine the string '100111, where we have 3 segments of sigma1,sigma2 10 01 11, we can "stacK" the segments on top of each other to get a matrix 
# of the form 
# 1 0 
# 0 1
# 1 1 
def generateMatrix(n,k,s):
    state = [list(s[i:i + n - 1]) for i in range(0, len(s), n-1)]
    return state


# The four check functions all have the same structure. They begin by scanning through every single value in the matrix,
# searching for a 1.

# Input: state = a given kauffman state
# Output: returns true or false if the state is a type 1 source.
# Given a 1 is found, we check the value of the cell in the same column one row below. If it's a 0 we then check what is the
# value on the right of the 1 and what is the value on the left of the 0. Left and right can be the same value, there is logic
# to check if the left or right are edge cases for example if the 0 is in the first column then it's left neighbor is the very last 
# cell in the row above the 0. In the case of a type 1 source we need the left and right neighbors to both be 0

def checkType1Source(state):
    #print("Test",len(state[0])-1)
    for r in range(len(state) - 1):
        for c in range(len(state[r])):
            if state[r][c] == '1' and state[r+1][c] == '0': 
                if c < (len(state[r])-1): 
                  right = state[r][c+1]
                  #print("row",r,"col",c,"right",right)
                else:
                    right = state[r+1][0]
                    #print("row",r,"col",c,"Right",right)
                if c > 0:
                    left = state[r+1][c-1]
                    #print("row",r,"col",c,"left",left)
                else:
                    left = state[r][len(state[r])-1]
                    #print("row",r,"col",c,"lefter",left)
                if right == '0' and left == '0':
                    return True
    return False

# Input: state = a given kauffman state
# Output: returns true or false if the state is a type 1 target.
# This behaves the same as checking for a type 1 source, but we need a 1 with a 1 below it in the matrix, and left and right
# neighbors must both be 0
def checkType1Target(state):
    for r in range(len(state) - 1):
        for c in range(len(state[r])):
            if state[r][c] == '1' and state[r+1][c] == '1': 
                if c < (len(state[r])) - 1: 
                  right = state[r][c+1]
                else:
                    right = state[r+1][0]
                if c > 0:
                    left = state[r+1][c-1]
                else:
                    left = state[r][c-1]

                if right == '0' and left == '0':
                    return True
    return False

# Input: state = a given kauffman state
# Output: returns true or false if the state is a type 1 target.
# This behaves the same as checking for type 1 source, but includes the condition i <= n - 2, in matrix form this means 
# we ignore the last column. In this case of type 2 source we need a 1 and a 1 below it in the matrix and the left and right 
# neighbors must both be 0.
def checkType2Source(state):
    for r in range(len(state) - 1):
        for c in range(len(state[r])-1):
            if state[r][c] == '1' and state[r+1][c] == '1': 
                if c < (len(state[r])) - 1: 
                  right = state[r][c+1]
                else:
                    right = state[r+1][0]
                if c > 0:
                    left = state[r+1][c-1]
                else:
                    left = state[r][c-1]

                if right == '0' and left == '0':
                    return True
    return False

# Input: state = a given kauffman state
# Output: returns true or false if the state is a type 1 target.
# This behaves the same as checking for type 2 source, in matrix form this means we ignore the last column. 
# Since this is a 3 braid, a type 2 target can be of the form 111 so we need a 1 and a 1 below it in the matrix, and the 
# left and right neighbors must both be 1 
def checkType2Target(state):
    for r in range(len(state) - 1):
        for c in range(len(state[r])-1):
            if state[r][c] == '1' and state[r+1][c] == '1': 
                if c < (len(state[r])) - 1: 
                  right = state[r][c+1]
                else:
                    right = state[r+1][0]
                if c > 0:
                    left = state[r+1][c-1]
                else:
                    left = state[r][c-1]

                if right == '1' and left == '1':
                    return True
    return False
        

#User input for n and k,
n = int(input("Enter the number of Strands "))
k = int(input("Enter the number of Repitions "))
totalStates = pow(2,(n-1)*k)

# Provides control to continue with the whittling or not, with large values of n and k the computational time,
# exponentially increases. This prevents your computer from crashing, freezing, or any other issues with millions of
# operations. 
print("There are", totalStates, "total states. ")
temp = input("Do you wish to proceed (yes or Yes to continue) ")
if (temp == "Yes" or temp == "yes"):

    # surviving states is an emtpy list that we fill with all remaining states.
    # states stores all possibel kauffman states before the whittling
    # start takes the start time of the whittling
    survivingStates = []
    states = generate_Kauffman_States(n,k)
    start = time.perf_counter()

    # This is the main calculation, the algorithm iterates through every single state. In each iteration 
    # we generate the matrix for that state, then check if its a type 1 source, if its a type 1 target AND 
    # a type 2 source, and if its a type 2 target. Any states that are not any of those will be added to the 
    # surviving states list
    for state in states:
        
        matrix = generateMatrix(n,k,state)
        if(checkType1Source(matrix)):
            pass
        elif checkType1Target(matrix) and checkType2Source(matrix):
            pass
        elif checkType2Target(matrix):
            pass
        else:
            survivingStates.append(state)

    # Takes the time after the whittling
    # Outputs all the states in the survivng states and also checks if the state has '101' which means we have a 
    # close component and we know only positive components survive so a + is added to the end of the state visually.
    # Does not affect the data in the survivngStates list
    end1 = time.perf_counter()
    for state in survivingStates:
        if "101" in state:
            print(state,'+')
        else:
            print(state)
    end2 = time.perf_counter()
    print("It took a total of", end1-start, "Seconds to whittle and", end2-start, " seconds in total with whittling and printing the surviving states.")
