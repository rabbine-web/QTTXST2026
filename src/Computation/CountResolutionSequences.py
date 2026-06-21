import os
from itertools import combinations

# Paths relative to this script's location (src/ -> ../out/)
SRC_DIR    = os.path.dirname(os.path.abspath(__file__))
OUT_DIR    = os.path.join(SRC_DIR, '..', '..', 'out')
GLOBAL_PATH = os.path.join(OUT_DIR, 'global.txt')
KI_DIR     = os.path.join(OUT_DIR, 'k_i')
SAFETY_CAP = 20  # adjust as needed

os.makedirs(KI_DIR, exist_ok=True)

def has_forbidden_substring(s):
    """Check if string contains '00' or '010' as a substring."""
    return '00' in s or '010' in s

def get_subsequences_of_length(master, length):
    """Return all unique strings formed by choosing `length` indices from master."""
    seen = set()
    for indices in combinations(range(len(master)), length):
        s = ''.join(master[j] for j in indices)
        seen.add(s)
    return seen

def generate_filtered_strings(master, length):
    """Generate all length-i subsequences of master, removing those with forbidden substrings."""
    candidates = get_subsequences_of_length(master, length)
    return sorted(s for s in candidates if not has_forbidden_substring(s))

def read_last_entry(global_path):
    """Return (k, i, count) of the last fully computed entry, or (0, 0, -1) if file is empty/missing."""
    if not os.path.exists(global_path):
        return 0, 0, -1
    last = None
    with open(global_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                last = line
    if last is None:
        return 0, 0, -1
    parts = last.split(',')
    return int(parts[0]), int(parts[1]), int(parts[2])

last_k, last_i, last_count = read_last_entry(GLOBAL_PATH)
print(f"Resuming after k={last_k}, i={last_i}, count={last_count}")

# Determine the (start_k, start_i) for computation
if last_k == 0:
    start_k, start_i = 1, 0
else:
    max_i_for_last_k = 2 * last_k
    k_is_done = last_i >= max_i_for_last_k or last_count == 0
    if last_i == 0:
        start_k, start_i = last_k, 1
    elif k_is_done:
        start_k, start_i = last_k + 1, 0
    else:
        start_k, start_i = last_k, last_i + 1

# Clear the first k_i file to be written (may be incomplete from a prior interrupted run)
if start_i >= 1:
    first_file = os.path.join(KI_DIR, f"{start_k}_{start_i}.txt")
    if os.path.exists(first_file):
        open(first_file, 'w').close()
        print(f"Cleared potentially incomplete file: {first_file}")

with open(GLOBAL_PATH, 'a') as global_file:
    k = start_k
    while k <= SAFETY_CAP:
        master = '01' * k

        i_begin = start_i if k == start_k else 0
        if i_begin == 0:
            global_file.write(f"{k},0,1\n")
            global_file.flush()
            i_begin = 1

        print(f"\n=== k = {k}, master = '{master}' (i from {i_begin} to {2 * k}) ===")

        for i in range(i_begin, 2 * k + 1):
            survivors = generate_filtered_strings(master, i)
            count = len(survivors)

            global_file.write(f"{k},{i},{count}\n")
            global_file.flush()

            if count == 0:
                print(f"  i={i}: 0 strings — stopping early for k={k}")
                break

            filepath = os.path.join(KI_DIR, f"{k}_{i}.txt")
            with open(filepath, 'w') as f:
                for s in survivors:
                    f.write(s + '\n')

            print(f"  i={i}: {count} strings written to {filepath}")

        k += 1

print(f"\nDone. Summary written to {GLOBAL_PATH}")
