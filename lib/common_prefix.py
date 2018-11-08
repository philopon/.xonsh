def _common_prefix2(a, b):
    a, b = (a, b) if len(a) > len(b) else (b, a)
    for i in range(min(len(a), len(b))):
        if a[i] != b[i]:
            return a[:i]

    return b


def common_prefix(cands):
    cands = iter(cands)
    try:
        p = next(cands)
    except StopIteration:
        return ""
    for cand in cands:
        p = _common_prefix2(p, cand)
        if len(p) == 0:
            return ""

    return p
