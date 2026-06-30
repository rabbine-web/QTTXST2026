from itertools import product
from typing import Optional

DirectMaps = dict[str, list[tuple[str, str, int]]]
Isomorphisms = dict[str, list[str]]
IsoTypes = dict[tuple[str, str], int]
IndirectMaps = dict[str, list[tuple[str, str, int, list[str]]]]

#Input: n is the number of strands and k is the number of repetitions
#Logic: creates a list of all kauffmamn states by iterating through 0 to 2^((n-1) * k) and formatting them to have 
#       the correct length and format
#Output: Returns the list of kaufmann states as strings.
def generate_Kauffman_States(n,k):
    kauffmanStates = []
    for x in range((pow(2,(n-1)*k))):
        kauffmanStates.append(bin(x)[2:].zfill((n-1) * k ))
    return kauffmanStates

#Input: n is the number of strands, k is the number of repetitions, s is the kauffman state:
#Logic: Creates a list of a list for a state by taking a window of 2 or 3 depending on a 3 or 4 braid and 
#       stacks them on top of each other where each column is a generator and each row is a repetition
#Output: returns the matrix for the state
def generateMatrix(n: int, k: int, s: str) -> list[list[str]]:
    state = [list(s[i:i + n - 1]) for i in range(0, len(s), n-1)]
    return state

#The four following checks work similarly
#Input: State is a matrix of a kauffman state
#Logic: Iterates through the matrix searching for a 1, if a 1 is found we check the row below it and observe what that 
#       cell is. We then check the right neighbor of the first 1 and the left neighbor of the cell. Based on this format 
#       we just need to check what the neighbors are to find each type. Checks for types in the form of 10...w...01 for example
#Output: Returns true if the check for a certain type is passed, false otherwise
def checkType1Source(state: list[list[str]]) -> bool:
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

def checkType1Target(state: list[list[str]]) -> bool:
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

def checkType2Source(state: list[list[str]]) -> bool:
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

def checkType2Target(state: list[list[str]]) -> bool:
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


#Input: state is a kauffman state
#Logic: Iterates through the kauffman state by character and records the position of each 1
#Output: Returns a list of integers 
def findIndexes(state: str) -> list[int]:
    indexes = []
    for i in range(len(state)):
        if(state[i] == "1"):
            indexes.append(i)
    return indexes

#Input: state is a kauffman state
#Logic: iterates through the kauffman state by character and when a 1 is found we append e + i%2 + 1 to give us the generator corresponding
#       to the position the 1 was found in
#Output: returns a list of strings corresponding to a temperlyleib word
def generateTemperlyLeib(state: str) -> list[str]:
    word = []
    for i in range(len(state)):
        if state[i] == '1':
            word.append("e" + str(i%3 + 1))
    return word

#Input: states is a list of all the kauffman states, homDegrees, indexes and temperlyLeibWords are all lists of lists
#Logic: iterate through the list of all states, we count the appearances of 1, finds the positions of 1's and create the temperly leib word
#       based on the count of ones we append each of those to the corresponding list of list sorting them all by homological degree
#Output: homDegrees is the states sorted by homological degree, indexes is parallel to the state and records the positions of ones and same for
#        temperly leib words
def generateHomdegrees(states: list[str], homDegrees: list[list[str]], indexes: list[list[list[int]]], temperlyLeibWords: list[list[list[str]]]) -> None:
    for state in states:
        
        binaryState = undecorateState(state)

        count = binaryState.count('1')
        index = findIndexes(binaryState)
        word =  generateTemperlyLeib(binaryState)

        homDegrees[count].append(state)
        indexes[count].append(index)
        temperlyLeibWords[count].append(word)

#Input: Source is a temperly leib word corresponding to a source in a map, target is a temperly leib word corresponding to a target in a map
#Logic: iterates through both words one character at a time until a difference is found
#Output: returns the index that the different character was found and what that character was such as e1 or e2
def describeMap(source: list[str], target: list[str]) -> tuple[str, int]:
    i = 0
    while i < len(source):
        if(source[i] == target[i]):
            i += 1
        else:
            return (target[i],i)
    return (target[-1],len(target)-1)

#Input: homDegrees is the sorted states, indexes is the corresponding positions of ones, temperlyLeibWords is the corresponding temperlyleib words, all parallel
#Logic: Starts with a state in homdegree i, then iterates through all states in homedegree i + 1, then checks if the first state is a subset
#       of the second state. If so we describe the map and adds it to our directMap dictionary, otherwise there is no direct map. 
#Output: returns a dictionary where the key is a state and the value is a tuple with the target state, generator added and the postion that 
#        generator is added 
def findDirectMaps(homDegrees: list[list[str]], indexes: list[list[list[int]]], temperlyLeibWords: list[list[list[str]]]) -> DirectMaps:
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


#Input: state is a decorated kauffman state
#Logic: since states are decorated with signs such as - + for the closed componenets, we want to separate them into two parts
#       so we iterate through the string in characters and add them to two separate strings, one is just the binary state, the other is a string of the signs
#Output: binary is a string of the binary part of a kauffman state, signs is a string of the signs for the closed components of a kauffman state
def splitState(state: str) -> tuple[str, str]:
    binary = ""
    signs = ""

    for ch in state:
        if ch == "+" or ch == "-":
            signs += ch
        else: 
            binary += ch
    return (binary,signs)

#Input: state is a decorated kauffman state
#Logic: we want to extract only the binary part of a decorated kauffman state 
#Output: returns the binary string for a decorated kauffman state to do computations on only binary string
def undecorateState(state: str) -> str:
    binary, strings = splitState(state)
    return binary

#Input: state is a decorated kauffman state
#Logic: finds closed components in a 3 braid by checking for 101, or 10..01 with any number of consecutive zeros
#       when the ones are in the same sigma i givins us a loop 
#Output: returns a list of ranges which are the locations of closed loops in the state
def findClosedComponents(state: str) -> list[tuple[int, int]]:
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
            if i % 3 + 1 == j % 3 + 1:
                closedComponents.append((i,j))

    return closedComponents

#Input: state is a decorated or undecorated Kauffman state
#Logic: finds the closed components, then creates all possible sign decorations using + and - for each component
#Output: returns a list of decorated versions of the state
def decorateState(state: str) -> list[str]:
    state = undecorateState(state)

    closedComponents = findClosedComponents(state)
    numClosedComponents = len(closedComponents)
    
    if numClosedComponents == 0:
        return [state]
    
    decoratedStates = []

    for signs in product(["+","-"], repeat = numClosedComponents):
        decoratedStates.append(state + "".join(signs))
    return decoratedStates

#Input: states is a list of Kauffman states
#Logic: decorates each state based on its closed components and combines all decorated states into one list
#Output: returns the full list of decorated states
def decorateStates(states: list[str]) -> list[str]:
    decorated = []
    for state in states:
        decorated.extend(decorateState(state))
    return decorated

#Input: state is a decorated Kauffman state, importantIndex is a binary index inside the state
#Logic: finds which closed component contains importantIndex and returns the corresponding sign from the decoration string
#Output: returns "+", "-", or None if no closed component contains the index
def getSignForClosedComponent(state: str, importantIndex: int) -> Optional[str]:
    binaryState, signs = splitState(state)
    closedComponents = findClosedComponents(binaryState)

    for i in range(len(closedComponents)):
        start, end = closedComponents[i]

        if start <= importantIndex <= end:
            if i < len(signs):
                return signs[i]

    return None

#Input: directMaps is the dictionary of direct maps, n is the number of strands, k is the number of repetitions
#Logic: scans each source for the leftmost Type 3, Type 1, or Type 2 source pattern, checks the expected target,
#       checks the required signs, preserves signs, and prevents a state from being paired twice
#Output: returns the isomorphism dictionary and a parallel dictionary recording the isomorphism type for each pair
def findIsomorphisms(directMaps: DirectMaps, n: int, k: int) -> tuple[Isomorphisms, IsoTypes]:

    isomorphisms = {}
    isoTypes = {}
    matchedStates = set()

    sources = list(directMaps.keys())

    sources.sort(key=lambda state: (undecorateState(state).count("1"),undecorateState(state), splitState(state)[1]))

    for source in sources:

        if source in matchedStates:
            continue

        binarySource = undecorateState(source)

        sourceType = 0
        startIndex = -1
        importantIndex = -1
        windowLength = 0

        for i in range(len(binarySource)):
            if i <= len(binarySource)-4:
                subWord4 = binarySource[i:i+4]
                startSigma = i % (n - 1) + 1

                if subWord4 == "1000" or subWord4 == "1010":
                    sourceType = 1
                    startIndex = i
                    importantIndex = i + 2
                    windowLength = len(subWord4)
                    break

                if (subWord4 == "1001" or subWord4 == "1101") and startSigma <= n - 2:
                    sourceType = 2
                    startIndex = i
                    importantIndex = i + 1
                    windowLength = len(subWord4)
                    break

            elif i <= len(binarySource)-7:
                subWord7 = binarySource[i:i+7]
                if subWord7 == "0100100" or subWord7 == "0100110":
                    importantIndexCanidate = i + 4
                    sign = getSignForClosedComponent(source,importantIndexCanidate)

                    if sign == "+":
                        sourceType = 3
                        startIndex = i
                        importantIndex = importantIndexCanidate
                        windowLength = len(subWord7)
                        break
            
            elif i == len(binarySource) - 6:
                subWord6 = binarySource[i:i+6]
                if(subWord6 == "001001" or subWord6 == "101001"):
                    importantIndexCanidate = i + 5
                    sign = getSignForClosedComponent(source, importantIndexCanidate)

                    if sign == "+":
                        sourceType = 3
                        startIndex = i
                        importantIndex = importantIndexCanidate
                        windowLength = len(subWord6)
                        break
            
        if sourceType == 0:
            continue

        sourceMatrix = generateMatrix(n, k, binarySource)

        if sourceType == 1 and not checkType1Source(sourceMatrix):
            continue

        if sourceType == 2 and not checkType2Source(sourceMatrix):
            continue

        for target, generator, position in directMaps[source]:

            if target in matchedStates:
                continue

            binaryTarget = undecorateState(target)

            expectedTarget = ( binarySource[:importantIndex]+ "1" + binarySource[importantIndex + 1:])

            if binaryTarget != expectedTarget:
                continue

            targetMatrix = generateMatrix(n, k, binaryTarget)

            if sourceType == 1:
                targetSubWord = binaryTarget[startIndex:startIndex+4] 
                if targetSubWord != "1001" or (startIndex % 3 == 2 and targetSubWord != "1101"):
                    continue  

                if not checkType1Target(targetMatrix):
                    continue 
            
            if sourceType == 2:
                targetSubWord = binaryTarget[startIndex:startIndex+4] 
                if targetSubWord != "111":
                    continue  

                if not checkType2Target(targetMatrix):
                    continue 
            
            if sourceType == 3:
                if windowLength == 5:
                    targetSubWord = binaryTarget[startIndex:startIndex+5]
                    if targetSubWord != "01110":
                        continue

                if windowLength == 4:
                    targetSubWord = binaryTarget[startIndex:startIndex+4]
                    if targetSubWord != "0111":
                        continue
             

            sourceBinary, sourceSigns = splitState(source)
            targetBinary, targetSigns = splitState(target)

            sourceClosed = findClosedComponents(sourceBinary)
            targetClosed = findClosedComponents(targetBinary)

            signsAgree = True

            for a in range(len(sourceClosed)):
                component = sourceClosed[a]
                start, end = component

                if start <= importantIndex <= end:
                    continue

                if component not in targetClosed:
                    signsAgree = False
                    break

                b = targetClosed.index(component)

                if a < len(sourceSigns) and b < len(targetSigns):
                    if sourceSigns[a] != targetSigns[b]:
                        signsAgree = False
                        break

            if not signsAgree:
                continue

            for b in range(len(targetClosed)):
                component = targetClosed[b]
                start, end = component

                if start <= importantIndex <= end:
                    continue

                if component not in sourceClosed:
                    signsAgree = False
                    break

            if not signsAgree:
                continue

            if sourceType == 1:
                sign = getSignForClosedComponent(target, importantIndex)

                if sign != "-":
                    continue

            if sourceType == 2:
                sign = getSignForClosedComponent(source, importantIndex)

                if sign != "+":
                    continue
            
            if sourceType == 3:
                sign = getSignForClosedComponent(source, importantIndex)

                if sign != "+":
                    continue

            if source not in isomorphisms:
                isomorphisms[source] = []

            isomorphisms[source].append(target)
            isoTypes[(source, target)] = sourceType

            matchedStates.add(source)
            matchedStates.add(target)

            break

    return isomorphisms, isoTypes

#Input: isomorphisms is the dictionary of source states paired with target states
#Logic: builds a two-way lookup so either state in an isomorphism pair can find its partner
#Output: returns a dictionary where each state in a pair points to its paired state
def buildIsoPairs(isomorphisms: Isomorphisms) -> dict[str, str]:
    isoPairs = {}
    for source in isomorphisms:
        for target in isomorphisms[source]:
            isoPairs[source] = target
            isoPairs[target] = source
    return isoPairs

#Input: directMaps is the dictionary of all direct maps and isomorphisms is the dictionary of paired states
#Logic: collects every state appearing in the direct maps, then removes every state that belongs to an isomorphism pair
#Output: returns the set of states that survive after whittling
def whittleStates(directMaps: DirectMaps, isomorphisms: Isomorphisms) -> set[str]:
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

#Input: small and big are strings of signs
#Logic: checks whether the characters of small appear in big in the same order, not necessarily consecutively
#Output: returns True if small is a subsequence of big, false otherwise
def isSubsequence(small: str, big: str) -> bool:
    i = 0

    for ch in big: 
        if i < len(small) and small[i] == ch:
            i += 1
    return i == len(small)

#Input: source and target are decorated Kauffman states
#Logic: checks that any closed component appearing in both states keeps the same sign and that surviving signs appear in order
#Output: returns True if the decorations are compatible with a valid direct step, false otherwise
def signsPreserved(source: str, target: str) -> bool:
    sourceBinary, sourceSigns = splitState(source)
    targetBinary, targetSigns = splitState(target)

    sourceClosed = findClosedComponents(sourceBinary)
    targetClosed = findClosedComponents(targetBinary)

    for i in range(len(sourceClosed)):
        component = sourceClosed[i]

        if component in targetClosed:
            j = targetClosed.index(component)
            
            if i < len(sourceSigns) and j < len(targetSigns):
                if sourceSigns[i] != targetSigns[j]:
                    return False

    if len(sourceSigns) == len(targetSigns):
        return sourceSigns == targetSigns
    
    if len(sourceSigns) < len(targetSigns):
        return isSubsequence(sourceSigns,targetSigns)
    
    if len(sourceSigns) > len(targetSigns):
        return isSubsequence(targetSigns,sourceSigns)
    
    return True


#Input: directMaps is the dictionary of all direct maps, isomorphisms is the dictionary of isomorphic pairs,
#       and whittled is the set of states that survive after whittling
#Logic: Builds an oriented dictionary called isoBackward so that if source is isomorphic to target, then target points
#       back to source. Then for each whittled state, we follow its direct maps. If a direct map lands in another whittled
#       state, we ignore it because that is already a surviving direct map. If a direct map lands in an isomorphism target,
#       we jump backward to the isomorphism source and continue following direct maps. This allows paths to zigzag through
#       multiple isomorphism pairs. At each direct step, we check that signs are preserved, the path stays in the correct
#       homological degrees, and no state repeats in the same path. Once we reach a whittled target after at least one
#       isomorphism jump, we record it as an indirect map unless the original source already maps directly to that target
#       or we already found that target from the same source.
#Output: returns a dictionary where each key is a whittled source state and each value is a list of tuples containing
#        the whittled target state, the inserted generator, the insertion position, and the full zigzag path
def findIndirectMaps(directMaps: DirectMaps, isomorphisms: Isomorphisms, whittled: set[str]) -> IndirectMaps:
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

        stack = [(start, [start], 0)]

        while stack:
            current, path, zigZagCount = stack.pop()

            currentDegree = undecorateState(current).count("1")

            if currentDegree != startDegree:
                continue

            for nextTarget, nextGenerator, nextPosition in directMaps.get(current, []):
                
                if not signsPreserved(current,nextTarget):
                    continue

                nextDegree = undecorateState(nextTarget).count("1")

                if nextDegree != finalDegree:
                    continue

                if nextTarget in path:
                    continue

                newPath = path + [nextTarget]

                if nextTarget in whittled:
                    if zigZagCount == 0:
                        continue

                    if nextTarget in startDirectMaps:
                        continue

                    pathKey = (start, nextTarget, tuple(newPath))

                    if nextTarget in foundTargets:
                        continue

                    sourceWord = generateTemperlyLeib(undecorateState(start))
                    targetWord = generateTemperlyLeib(undecorateState(nextTarget))

                    insertedGenerator, insertedPosition = describeMap(sourceWord, targetWord)

                    if start not in indirectMaps:
                        indirectMaps[start] = []

                    indirectMaps[start].append((nextTarget, insertedGenerator, insertedPosition, newPath))

                    foundTargets.add(nextTarget)

                elif nextTarget in isoBackward:

                    partner = isoBackward[nextTarget]
                    partnerDegree = undecorateState(partner).count("1")

                    if partnerDegree != startDegree:
                        continue

                    if partner in newPath:
                        continue

                    stack.append((partner, newPath + [partner], zigZagCount + 1))

    return indirectMaps

#Input: state is a decorated or undecorated Kauffman state
#Logic: generates the Temperley-Lieb word for the binary part and joins it into one string
#Output: returns the Temperley-Lieb word as a string
def wordString(state: str) -> str:
    word = generateTemperlyLeib(undecorateState(state))
    return "".join(word)

def printWhittledStates(whittled: set[str]) -> None:
    print("\nWhittled States:")
    for state in sorted(whittled):
        print(state,wordString(state))

def printIsomorphisms(isomorphisms: Isomorphisms, isoTypes: IsoTypes) -> None:
    print("\nIsomorphic pairs:")
    for source in isomorphisms: 
        for target in isomorphisms[source]:
            sourceWord = wordString(source)
            targetWord = wordString(target)
            isoType = isoTypes[(source,target)]
            print(source, sourceWord, "is a type", isoType, "isomorphism with", target, targetWord)            

def printWhittledDirectMaps(directMaps: DirectMaps, whittled: set[str]) -> None:
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

def printIndirectMaps(indirectMaps: IndirectMaps) -> None:
    print("\nIndirect maps:")

    for source in sorted(indirectMaps):
        for target, generator, position, path in indirectMaps[source]:

            sourceWord = wordString(source)
            targetWord = wordString(target)

            print(source , sourceWord , "maps indirectly to" ,target, targetWord , "by inserting" , generator , "at position"
                  , position)

            print("path:", " -> ".join(path))
            print()

def printData(whittled: set[str], directMaps: DirectMaps, isomorphisms: Isomorphisms, indirectMaps: IndirectMaps, isoTypes: IsoTypes) -> None:
    printWhittledStates(whittled)

    #printIsomorphisms(isomorphisms,isoTypes)

    printWhittledDirectMaps(directMaps, isomorphisms)

    printIndirectMaps(indirectMaps)

#n = int(input("Enter the number of Strands "))
print("number of strands will be 4")
n = 4
k = int(input("Enter the number of Repitions "))


tempStates = generate_Kauffman_States(n,k)
states = decorateStates(tempStates)

print(states)

homDegrees = [[] for i in range((k*n-1) + 1)]
indexes = [[] for i in range((k*n-1) + 1)]
temperlyLeibWords = [[] for i in range((k*n-1) + 1)]

generateHomdegrees(states,homDegrees,indexes,temperlyLeibWords)

directMaps = findDirectMaps(homDegrees,indexes,temperlyLeibWords)
isomorphisms, isoTypes = findIsomorphisms(directMaps,n,k)

buildIsoPairs(isomorphisms)

whittledStates = whittleStates(directMaps,isomorphisms)
indirectMaps = findIndirectMaps(directMaps,isomorphisms,whittledStates)

printData(whittledStates,directMaps,isomorphisms,indirectMaps,isoTypes)
