def generate_Kauffman_States(n,k):
    kauffmanStates = []
    for x in range((pow(2,(n-1)*k))):
        kauffmanStates.append(bin(x)[2:].zfill((n-1) * k ))
    return kauffmanStates

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
                 # print("row",r,"col",c,"right",right)
                else:
                    right = state[r+1][0]
                   # print("row",r,"col",c,"Right",right)
                if c > 0:
                    left = state[r+1][c-1]
                    #print("row",r,"col",c,"left",left)
                else:
                    left = state[r][len(state[r])-1]
                  # print("row",r,"col",c,"lefter",left)
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

def findIndexes(state):
    indexes = []
    for i in range(len(state)):
        if(state[i] == "1"):
            indexes.append(i)
    return indexes

def generateHomdegrees(states,homDegrees,indexes,temperlyLeibWords):
    for state in states:
        count = state.count('1')
        index = findIndexes(state)
        word =  generateTemperlyLeib(state)
        homDegrees[count].append(state)
        indexes[count].append(index)
        temperlyLeibWords[count].append(word)

def generateTemperlyLeib(state):
    word = []
    for i in range(len(state)):
        if state[i] == '1':
            word.append("e" + str(i%2 + 1))
    return word

def printStates(homDegrees,indexes,temperlyLeibWords):
    for i in range(len(homDegrees)):
        for j in range(len(homDegrees[i])):
            print(homDegrees[i][j], indexes[i][j], temperlyLeibWords[i][j])

def describeMap(source,target):
    i = 0
    while i < len(source):
        if(source[i] == target[i]):
            i += 1
        else:
            return (target[i],i)
    return (target[-1],len(target)-1)
        
def findDirectMaps(homDegrees,indexes,temperlyLeibWords):
    maps = {}
    for i in range(len(homDegrees) - 1):
            
            for k in range(len(homDegrees[i])):

                state1 = (homDegrees[i][k], indexes[i][k], temperlyLeibWords[i][k])

                for l in range(len(homDegrees[i + 1])):

                    state2 = (homDegrees[i + 1][l], indexes[i + 1][l],temperlyLeibWords[i+1][l])

                    if set(state1[1]).issubset(state2[1]):
                        generator,position = describeMap(state1[2],state2[2])

                        if(state1[0] not in maps):
                            maps[state1[0]] = []

                        maps[state1[0]].append((state2[0],generator,position))
    return maps

def findImportantIndex(state,n):
    for i in range(len(state)-2):

        subWord = state[i:i+3]

        if(subWord == "100"):
            return (i + 2)
        
        if(subWord == "101" and (i % 2 + 1) <= n - 2):
            return i + 1
    return (-1)

def findIsomorphisms(maps,n,k):
    isomorphisms = {}
    for source in maps:
        
        sourceMatrix = generateMatrix(n,k,source)
        sourceIsType1 = checkType1Source(sourceMatrix)
        sourceIsType2 = checkType2Source(sourceMatrix)
        
        importantIndex = findImportantIndex(source,n)
        
        if importantIndex == -1:
            continue
        
        for target, generator, position in maps[source]:

            targetMatrix = generateMatrix(n,k,target)

            if sourceIsType1 and checkType1Target(targetMatrix):
                if target[importantIndex] == '1':
                    if source not in isomorphisms:
                        isomorphisms[source] = []
                    isomorphisms[source].append(target)
            elif sourceIsType2 and checkType2Target(targetMatrix):
                if target[importantIndex] == '1':
                    if source not in isomorphisms:
                        isomorphisms[source] = []
                    isomorphisms[source].append(target)

    return isomorphisms
            
def printMaps(homeDegrees,indexes,temperlyLebiWords):
    for source in maps:
        for target, generator, position in maps[source]:
            word1 = generateTemperlyLeib(source)
            word2 = generateTemperlyLeib(target)
            print(source, word1, "maps to target", target, word2, "by inserting", generator, "at position", position)

n = int(input("Enter the number of Strands "))
k = int(input("Enter the number of Repitions "))

temp = input("Do you wish to proceed ")
states = generate_Kauffman_States(n,k)

homDegrees = [[] for i in range((k*n-1))]
indexes = [[] for i in range((k*n-1))]
temperlyLeibWords = [[] for i in range((k*n-1))]

generateHomdegrees(states,homDegrees,indexes,temperlyLeibWords)
maps = findDirectMaps(homDegrees,indexes,temperlyLeibWords)
isomorphisms = findIsomorphisms(maps,n,k)

printMaps(homDegrees,indexes,temperlyLeibWords)

for source in isomorphisms:
    for target in isomorphisms[source]:
        print (source, "is isomorphic to", target)
