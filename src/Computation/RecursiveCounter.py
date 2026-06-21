"""
POSSIBLE IMPROVEMENTS:

- preallocate hashset so resizing does not have to occur
    - investigate if set.clear() preserves hash table size
        - set.clear() will almost never cause the hashtable to shrink

- Main Goal: reduce redundancy
    - many different insertions of a bit into an (i-1)-string can produce the same i-string
    - so, the same i-string is created many times and inserted in the set many times
        - run diagnostics to get estimate of how often these collisions occur
"""


import os

SRC_DIR    = os.path.dirname(os.path.abspath(__file__))
OUT_DIR    = os.path.join(SRC_DIR, '..', '..', 'out')
GLOBAL_PATH = os.path.join(OUT_DIR, 'global.txt')
KI_DIR     = os.path.join(OUT_DIR, 'k_i')



def count_braid_repititions(string):
    return string.count('1') + 1*string.endswith('0')


"""loads all binary strings from text file k_i.txt"""
def load_all_strings(k, i):
    filepath = os.path.join(KI_DIR, f"{k}_{i}.txt")
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"No string file found for k={k}, i={i}: {filepath}")
    with open(filepath, 'r') as f:
        return [line.strip() for line in f if line.strip()]



## Since sliding window is length 4 we would like to avoid wonky starting conditions
k=26
interrupted = False


while not interrupted:

    ## Starting at strings of length k since at least everything for i<k is
    ## exactly the recurrance relation (has not entered end behavior)
    i = k
    
    num_strings_found = -1


    while num_strings_found != 0:
        
        valid_strings = set()

        ## if this is the first non-trivial calculation, load from previous k-value
        if i == k:
            previous_strings = load_all_strings(k-1, i-1)
        else:
            previous_strings = load_all_strings(k, i-1)
            
        
        for prev in previous_strings:

            num_braid_reps = count_braid_repititions(prev)
            offset = 0
            
            ## find i-strings from inserting 1
            if num_braid_reps < k:
                for index in range(0, i ,1):

                    valid_strings.add(
                        prev[:index] + "1" + prev[index:]
                        )

                    
            ## if num_braid_reps==k we cannot add a zero at the end
            else:
                offset = 1

            ## find i-strings from inserting 0
            
            ## add ghost ones
            prev = '11' + prev + '11'
            
            ## sliding window looking for 4 consecutive ones
            for window in range(0, i-offset, 1):
                if prev[window:window+4] == "1111":
                    valid_strings.add(
                        prev[2:window+2] + "0" + prev[window+2:-2]
                        )


        ## write valid strings to new file
        filepath = os.path.join(KI_DIR, f"{k}_{i}.txt")
        with open(filepath, 'w') as file:
            for string in valid_strings:
                file.write(string + "\n")
        
        num_strings_found = len(valid_strings)
        print(f"Finished k={k}, i={i} with {num_strings_found} strings\n")
        
        ## write (k, i, num_strings) to global counter
        with open(GLOBAL_PATH, 'a') as global_counter:
            global_counter.write(f"{k},{i},{num_strings_found}\n")
            global_counter.flush()
                           
        i += 1


    k += 1
