from itertools import product
#Generate kauffman States
def generate_Kauffman_States(n,k):
    kauffmanStates = []
    for x in range((pow(2,(n-1)*k))):
        kauffmanStates.append(bin(x)[2:].zfill((n-1) * k ))
    return kauffmanStates

#generate kaufmann state matrix 

def generateMatrix(n,k,s):
    state = [list(s[i:i + n - 1]) for i in range(0, len(s), n-1)]
    return state

#check for each type in a 3 braid 

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

                if right == '1' and left == '1':
                    return True
    return False        


#finds the position of 1 in each state and returns a list of those positions 
def findIndexes(state):
    indexes = []
    for i in range(len(state)):
        if(state[i] == "1"):
            indexes.append(i)
    return indexes

#generates a list which is the TL word for a state 
def generateTemperlyLeib(state):
    word = []
    for i in range(len(state)):
        if state[i] == '1':
            word.append("e" + str(i%2 + 1))
    return word

# a 2d list where its sorted by homological degree in the form state, indexes of ones, TL word
def generateHomdegrees(states,homDegrees,indexes,temperlyLeibWords):
    for state in states:
        
        binaryState = undecorateState(state)

        count = binaryState.count('1')
        index = findIndexes(binaryState)
        word =  generateTemperlyLeib(binaryState)

        homDegrees[count].append(state)
        indexes[count].append(index)
        temperlyLeibWords[count].append(word)

#takes a source and a target and describes how to map between the two with TL words
def describeMap(source,target):
    i = 0
    while i < len(source):
        if(source[i] == target[i]):
            i += 1
        else:
            return (target[i],i)
    return (target[-1],len(target)-1)

#finds all possible direct maps by flipping ones    
def findDirectMaps(homDegrees,indexes,temperlyLeibWords):
    directMaps = {}
    for i in range(len(homDegrees) - 1):
            
            for k in range(len(homDegrees[i])):

                state1 = (homDegrees[i][k], indexes[i][k], temperlyLeibWords[i][k])

                for l in range(len(homDegrees[i + 1])):

                    state2 = (homDegrees[i + 1][l], indexes[i + 1][l],temperlyLeibWords[i+1][l])

                    if set(state1[1]).issubset(state2[1]):
                        generator,position = describeMap(state1[2],state2[2])

                        if(state1[0] not in directMaps):
                            directMaps[state1[0]] = []

                        directMaps[state1[0]].append((state2[0],generator,position))
    return directMaps


#splits a decorated state into two parts, binary part and sign part and returns boths
def splitState(state):
    binary = ""
    signs = ""

    for ch in state:
        if ch == "+" or ch == "-":
            signs += ch
        else: 
            binary += ch
    return (binary,signs)

#takes a decorated state and returns the binary for the state
def undecorateState(state):
    binary, strings = splitState(state)
    return binary

#finds closed components in a 3 braid by checking for 101, or 10..01 with any number of consecutive zeros
# when the ones are in the same sigma i 
def findClosedComponents(state):
    state = undecorateState(state)

    closedComponents = []

    for i in range(len(state)):
        if state[i] != "1":
            continue

        j = i + 1
        zeroCounter = 0

        while j < len(state) and state[j] == "0":
            j += 1
            zeroCounter += 1
        
        if j < len(state) and state[j] == "1" and zeroCounter != 0:
            if i % 2 + 1 == j % 2 + 1:
                closedComponents.append((i,j))

    return closedComponents

#based on the number of closed loops add + and - to the state
def decorateState(state):
    state = undecorateState(state)

    closedComponents = findClosedComponents(state)
    numClosedComponents = len(closedComponents)
    
    if numClosedComponents == 0:
        return [state]
    
    decoratedStates = []

    for signs in product(["+","-"], repeat = numClosedComponents):
        decoratedStates.append(state + "".join(signs))
    return decoratedStates

#decorates all states 
def decorateStates(states):
    decorated = []
    for state in states:
        decorated.extend(decorateState(state))
    return decorated

                    
#takes a state, performs a sliding 3 window to find 100 or 101 for type 1 and type 2 source, 
# returns the index that is flipped that will correspond to the isomorphism
def findImportantIndex(state,n):
    state = undecorateState(state)
    for i in range(len(state)-2):

        subWord = state[i:i+3]

        if(subWord == "100"):
            return (i + 2)
        
        if(subWord == "101" and (i % 2 + 1) <= n - 2):
            return i + 1
    return (-1)

#finds which closed component corresponds to the important index and returns the sign
def getSignForClosedComponent(state, importantIndex):
    binaryState, signs = splitState(state)
    closedComponents = findClosedComponents(binaryState)

    for i in range(len(closedComponents)):
        start, end = closedComponents[i]

        if start <= importantIndex <= end:
            if i < len(signs):
                return signs[i]

    return None

#finds all isomorphisms by checking signs and types to correctly match states
def findIsomorphisms(directMaps,n,k):
    isomorphisms = {}
    for source in directMaps:
        binarySource = undecorateState(source)

        sourceMatrix = generateMatrix(n,k,binarySource)
        sourceIsType1 = checkType1Source(sourceMatrix)
        sourceIsType2 = checkType2Source(sourceMatrix)
        
        importantIndex = findImportantIndex(binarySource,n)
        
        if importantIndex == -1:
            continue
        
        for target, generator, position in directMaps[source]:

            binaryTarget = undecorateState(target)
            targetMatrix = generateMatrix(n,k,binaryTarget)

            if sourceIsType1 and checkType1Target(targetMatrix):
                if binaryTarget[importantIndex] == '1':
                    sign = getSignForClosedComponent(target,importantIndex)
                    if sign == "-": 
                        if source not in isomorphisms:
                            isomorphisms[source] = []
                        isomorphisms[source].append(target)

            elif sourceIsType2 and checkType2Target(targetMatrix):
                if binaryTarget[importantIndex] == '1':
                    sign = getSignForClosedComponent(source, importantIndex)
                    if sign == "+": 

                        if source not in isomorphisms:
                            isomorphisms[source] = []
                        isomorphisms[source].append(target)
    return isomorphisms
            
#builds a dictionary that has all isomorphic pairs
def buildIsoPairs(isomorphisms):
    isoPairs = {}
    for source in isomorphisms:
        for target in isomorphisms[source]:
            isoPairs[source] = target
            isoPairs[target] = source
    return isoPairs

#takes all states and whittles them based on if they are apart of an isomorphic pair
def whittleStates(directMaps, isomorphisms):
    isoPairs = buildIsoPairs(isomorphisms)

    allStates = set()

    for source in directMaps:
        allStates.add(source)
        for target, generator, position in directMaps[source]:
            allStates.add(target)

    whittled = set()

    for state in allStates:
        if state not in isoPairs:
            whittled.add(state)

    return whittled

#finds all indirect maps by starting with a whittled state, searching though the direct maps chaining through isomorphism,
# to find a valid map to a next whittled state
# currently works for a single zigzag
def findIndirectMaps(directMaps, isomorphisms, whittled):
    isoBackward = {}

    for source in isomorphisms:
        for target in isomorphisms[source]:
            isoBackward[target] = source

    indirectMaps = {}


    for start in whittled:

        startDegree = undecorateState(start).count("1")
        finalDegree = startDegree + 1

        startDirectMaps = set()

        for target, generator, position in directMaps.get(start, []):
            startDirectMaps.add(target)

        foundTargets = set()

        for firstTarget, generator, position in directMaps.get(start, []):

            if firstTarget in whittled:
                continue

            if firstTarget not in isoBackward:
                continue

            partner = isoBackward[firstTarget]

            for finalTarget, finalGenerator, finalPosition in directMaps.get(partner, []):

                finalTargetDegree = undecorateState(finalTarget).count("1")

                if finalTargetDegree != finalDegree:
                    continue

                if finalTarget not in whittled:
                    continue

                if finalTarget in startDirectMaps:
                    continue

                if finalTarget in foundTargets:
                    continue

                startWord = generateTemperlyLeib(undecorateState(start))
                targetWord = generateTemperlyLeib(undecorateState(finalTarget))

                insertedGenerator, insertedPosition = describeMap(startWord, targetWord)

                if start not in indirectMaps:
                    indirectMaps[start] = []

                indirectMaps[start].append((finalTarget, insertedGenerator, insertedPosition, [start, firstTarget, partner, finalTarget]))

                foundTargets.add(finalTarget)

    return indirectMaps


#ALl of these are for printing data
def wordString(state):
    word = generateTemperlyLeib(undecorateState(state))
    return "".join(word)

def printWhittledStates(whittled):
    print("\nWhittled States:")
    for state in sorted(whittled):
        print(state,wordString(state))

def printIsomorphisms(isomorphisms):
    print("\nIsomorphic pairs:")
    for source in isomorphisms: 
        for target in isomorphisms[source]:
            sourceWord = wordString(source)
            targetWord = wordString(target)
            print(source, sourceWord, "is isomorphic to", target, targetWord)            

def printWhittledDirectMaps(directMaps, whittled):
    whittled = whittleStates(directMaps, isomorphisms)

    print("\nWhittled direct maps:")

    for source in sorted(directMaps):
        if source not in whittled:
            continue

        for target, generator, position in directMaps[source]:
            if target not in whittled:
                continue

            sourceWord = wordString(source)
            targetWord = wordString(target)

            print(source , sourceWord , "maps directly to" , target , targetWord , "by inserting"
                , generator , "at position" , position)

def printIndirectMaps(indirectMaps):
    print("\nIndirect maps:")

    for source in sorted(indirectMaps):
        for target, generator, position, path in indirectMaps[source]:

            sourceWord = wordString(source)
            targetWord = wordString(target)

            print(source , sourceWord , "maps indirectly to" , targetWord , "by inserting" , generator , "at position"
                  , position)

            print("path:", " -> ".join(path))
            print()

def printData(whittled,directMaps, isomorphisms, indirectMaps):
    printWhittledStates(whittled)

    printIsomorphisms(isomorphisms)

    printWhittledDirectMaps(directMaps, isomorphisms)

    printIndirectMaps(indirectMaps)


if name = __main__
    n = int(input("Enter the number of Strands "))
    k = int(input("Enter the number of Repitions "))

    temp = input("Do you wish to proceed ")
    tempStates = generate_Kauffman_States(n,k)

    states = decorateStates(tempStates)

    homDegrees = [[] for i in range((k*n-1))]
    indexes = [[] for i in range((k*n-1))]
    temperlyLeibWords = [[] for i in range((k*n-1))]

    generateHomdegrees(states,homDegrees,indexes,temperlyLeibWords)

    directMaps = findDirectMaps(homDegrees,indexes,temperlyLeibWords)
    isomorphisms = findIsomorphisms(directMaps,n,k)

    buildIsoPairs(isomorphisms)
        
    whittledStates = whittleStates(directMaps,isomorphisms)
    indirectMaps = findIndirectMaps(directMaps,isomorphisms,whittledStates)

    printData(whittledStates,directMaps,isomorphisms,indirectMaps)
