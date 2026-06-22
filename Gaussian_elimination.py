# Identifying surviving kauffman states after gaussian elimination for type 1&2 sources and targets.
from src.Computation.TemperleyLieb import kauffmanstates


def bit(state, pos):
    return (state >> pos) & 1

#
# Circle detection
#
# sigma_1      : 10w1
# middle rows  : 10w01
# sigma_(n-1)  : 1w01
#
def has_circle(state, n, k):
    crossings = k * (n - 1)

    for j in range(crossings - (n - 1)):
        sigma_i = (j % (n - 1)) + 1
        first = bit(state, j)
        last = bit(state, j + n - 1)
        valid_w = True

        for pos in range(j + 2, j + n - 2):
            generator = (pos % (n - 1)) + 1
            if generator == sigma_i:
                valid_w = False
                break

        if not valid_w:
            continue

        if sigma_i == 1:
            second = bit(state, j + 1)
            if (
                first == 1 and
                second == 0 and
                last == 1
            ):
                return True

        elif sigma_i == n - 1:
            second_last = bit(state, j + n - 2)
            if (
                first == 1 and
                second_last == 0 and
                last == 1
            ):
                return True

        else:
            second = bit(state, j + 1)
            second_last = bit(state, j + n - 2)
            if (
                first == 1 and
                second == 0 and
                second_last == 0 and
                last == 1
            ):
                return True
    return False


#
# Build generators
#
def build_generators(n, k):
    generators = []

    for state in kauffmanstates(n, k):
        if has_circle(state, n, k):
            generators.append((state, 1))
            generators.append((state, -1))

        else:

            generators.append((state, 0))
    return generators


#
# Detect S1 and S2 sources
#
def source_matches(state, n, k):
    crossings = k * (n - 1)
    matches = []

    for j in range(crossings - (n - 1)):
        sigma_i = (j % (n - 1)) + 1
        first = bit(state, j)
        second = bit(state, j + 1)
        second_last = bit(state, j + n - 2)
        last = bit(state, j + n - 1)
        valid_w = True

        for pos in range(j + 2, j + n - 2):
            generator = (pos % (n - 1)) + 1
            if generator == sigma_i:
                valid_w = False
                break

        if not valid_w:
            continue

        if (
            first == 1 and
            second == 0 and
            second_last == 0 and
            last == 0
        ):
            matches.append(("S1", sigma_i, j))

        if (
            first == 1 and
            second == 0 and
            second_last == 0 and
            last == 1 and
            sigma_i <= n - 2
        ):
            matches.append(("S2", sigma_i, j))

    return matches


def run_cancellation(n, k):
    generators = build_generators(n, k)
    gen_set = set(generators)
    signs_by_state = {}
    for state, sign in generators:
        signs_by_state.setdefault(state, []).append(sign)

    removed = set()

    for state, sign in generators:
        matches = source_matches(state, n, k)
        for source_type, sigma_i, j in matches:

            if source_type == "S1":
                target_state = state | (1 << (j + n - 1))
                removed.add((state, sign))
                if (target_state, -1) in gen_set:
                    removed.add((target_state, -1))

            elif source_type == "S2" and sign == 1:
                target_state = state | (1 << (j + 1))
                removed.add((state, 1))
                for g_sign in signs_by_state.get(target_state, []):
                    removed.add((target_state, g_sign))

    survivors = [(s, sg) for s, sg in generators if (s, sg) not in removed]
    return survivors, generators, removed


if __name__ == "__main__":
    n = int(input("Enter n: "))
    k = int(input("Enter k: "))

    crossings = k * (n - 1)
    survivors, generators, removed = run_cancellation(n, k)

    print("\nSurviving generators:\n")

    for state, sign in generators:
        if (state, sign) in removed:
            continue

        binary = ''.join(
            str((state >> i) & 1)
            for i in range(crossings)
        )

        if sign == 1:
            print(binary, "(+)")

        elif sign == -1:
            print(binary, "(-)")

        else:
            print(binary)

    print("\nSurviving generators =", len(survivors))
    print("Removed generators =", len(removed))
