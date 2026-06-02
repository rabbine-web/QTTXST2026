# This function generates the kauffman states iteratively instead of recursively.
# A list of the form 0,1,2,...,2^(k* n-1) - 1 is input as well as the desired length.
# Then each index from that list is access and converted into binary with formatting and appended to a list
# Once all values have been processed the list is returned.
# This reasoning for this function is now we have two forms of kauffmam states, one with binary representations such as 
# 0100 and a second list with all of those same binary strings but represented as integer for compuational purposes to 
# avoid having to convert strings to integers.

def generate_Kauffman_States(n,k, kauffmanStatesInts):
    kauffmanStates = []
    for x in range(len(kauffmanStatesInts)):
        kauffmanStates.append(bin (kauffmanStatesInts[x])[2:].zfill((n-1) * k ))
    return kauffmanStates

n = int(input("Enter the number of Strands "))
k = int(input("Enter the number of Repitions "))

print("The list will have length ", (n-1) * k )

#generatorList = list(range(listLength))
#for i in range(len(generatorList)):
#    generatorList[i] = generatorList[i]%2
#print("The generator list is", generatorList)

totalKauffmanStates = (pow(2,(n-1) * k))
print("\nThere will be ", totalKauffmanStates, " Kauffman states")
temp = input("Do you wish to proceed ")
if (temp == "Yes" or temp == "yes"):
    kauffmanStatesInts = list(range(totalKauffmanStates))
    kauffmanStates = generate_Kauffman_States(n,k, kauffmanStatesInts)
    #print (kauffmanStatesInts)
    print(kauffmanStates)