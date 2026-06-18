"""
kauf_state will be an int list of 0 and 1s

Work in progress
"""
def detect_closed_loop(kauf_state, n, k):
    protected = [False] * n
    for repitition in range(k):
        for resolution in range(n - 1):

            index = repitition * (n - 1) + resolution
            print(index)
            if(kauf_state[resolution] == 1):
                if(protected[resolution] and protected[resolution + 1]): # both strands are true
                    print("T T")

                elif(resolution < n - 1 and not protected[resolution] and protected[resolution + 1]): # if lower stand is compromised
                    print("F T")
                    protected[resolution] = True
                    temp = resolution
                    while(temp < n - 1 and protected[temp + 1]):
                        temp += 1
                    protected[temp] = False
                    
                elif(resolution < n - 1 and protected[resolution] and not protected[resolution + 1]): # if top stand is compromised
                    print("T F")
                    protected[resolution + 1] = True
                    temp = resolution
                    while(temp > 0 and protected[temp -1]):
                        temp -= 1
                    protected[temp] = False

                elif( not (protected[resolution] or protected[resolution + 1])): # two compromised stands create 2 protected strands
                    print("F F")
                    protected[resolution] = True
                    protected[resolution + 1] = True
                else:
                    print("what?")
                    print(str(protected[resolution - 1]) + " " + str(protected[resolution]) + " " + str(protected[resolution + 1]))
                
            #else:
                #print("was 0")
            print(protected)
            #else: # doesn't change, connections stay the same

if __name__ == "__main__":
    kauf_state  = [1,0,1,0, 1, 0, 0 , 1, 1, 1, 0, 0]
    detect_closed_loop(kauf_state=kauf_state, n=4, k=4)