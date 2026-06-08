import time

def generate_Kauffman_States(n,k):
    kauffmanStates = []
    for x in range((pow(2,(n-1)*k))):
        kauffmanStates.append(bin(x)[2:].zfill((n-1) * k ))
    return kauffmanStates

def kauffmanstates(n, k):
    return range(1 << (k*(n-1)))

def temperleylieb(s, n, k):
    return [i % (n-1) + 1 for i in range(k*(n-1)) if s & (1 << i)]


def generateMatrix(n,k,s):
    state = [list(s[i:i + n - 1]) for i in range(0, len(s), n-1)]
    return state
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
                    left = state[r][c-1]
                    #print("row",r,"col",c,"left",left)
                if right == '0' and left == '0':
                    return True
    return False

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

                if right == '1' and left == '0':
                    return True
    return False
        

n = int(input("Enter the number of Strands "))
k = int(input("Enter the number of Repitions "))


''' This is just prints out all binary strings, left out as a comment to decide to show it or not. 
print("\nThere will be ", pow(2,(n-1) * k), " Kauffman states of length",((n-1) * k) )
for state in range((pow(2,(n-1)*k))):
    print((bin(state)[2:].zfill((n-1) * k )))
'''

temp = input("Do you wish to proceed ")
if (temp == "Yes" or temp == "yes"):
    type1Targets = []
    type1Sources = []
    type2Sources = []
    type2Targets = []

    binaryTime = 0
    matrixTime = 0
    checkTime = 0

    for state in range((pow(2,(n-1)*k))):
        start = time.perf_counter()
        kauffman = bin(state)[2:].zfill((n-1) * k )
        binaryTime += time.perf_counter() - start

        start = time.perf_counter()
        matrix = generateMatrix(n,k,kauffman)
        matrixTime += time.perf_counter() - start

        start = time.perf_counter()
        if checkType1Source(matrix):
            type1Sources.append(state)
        if checkType1Target(matrix):
            type1Targets.append(state)
        if checkType2Source(matrix):
            type2Sources.append(state)
        if checkType2Target(matrix):
            type2Targets.append(state)
        
        checkTime += time.perf_counter() - start

print("\nTiming data")
print("\nIt took", binaryTime, "seconds to convert the states into binary")
print("\nIt took", matrixTime, "seconds to convert the states into a matrix")
print("\nIt took", checkTime, "seconds to check the types of states")
print("\nIt took", binaryTime + matrixTime + checkTime, "seconds in total.")
