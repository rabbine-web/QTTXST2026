def transform(in_str, p=None):
    out = []  # list of chars, index 0 = leftmost

    for i in range(len(in_str) - 1, -1, -1):  # right to left
        curr = in_str[i]

        if curr == '1':
            out = ['0', '1'] + out
        else:  # curr == '0'
            if len(out) > 0 and out[0] == '0':
                out[0] = '1'
            else:
                out = ['1', '0'] + out

    result = ''.join(out)
    if p is None:
        result = result.zfill(2 * len(in_str))
    else:
        result = result.zfill(2 * p)

    return result


# Test
INPUT = "011101"
print(transform(INPUT))
