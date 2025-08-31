#!/usr/bin/env python3

# ---- Embedded constants extracted from the native library ----
LL  = [ 32, 92,  4,104,106, 76, 96,113, 42, 65, 22, 43,203, 84,220,
         98,210, 71, 29,123, 20,125,199 ]  # 23 ints

LLL = [ 76,230,117,243, 84, 54,103,197,104,251, 83,253,128,159 ]  # 14 ints

N = 37

def perm_index(i: int) -> int:
    return (5*i + 3) % N

def forward_T(c: int, i: int) -> int:
    # Native transform Java_xyz_scriptctf_Main_sc
    base = c + 2*(i % 7)
    base ^= (44 if (i % 2 == 0) else 19)
    return base + (i & 1)

def invert_T(t: int, i: int) -> int:
    x = t - (i & 1)
    x ^= (44 if (i % 2 == 0) else 19)
    c = x - 2*(i % 7)
    return c & 0xFF

def solve():
    out = ['?'] * N
    # live indices into LL/LLL as we "consume" matches
    li, lj = 0, 0

    # Helper: return next target candidate(s) and which table(s) they come from
    def next_targets():
        targets = []
        if li < len(LL):
            targets.append(("LL", LL[li]))
        if lj < len(LLL):
            targets.append(("LLL", LLL[lj]))
        return targets

    for i in range(N):
        idx = perm_index(i)
        # we’ll pick a character that’s consistent with:
        #   - flag format constraints (known prefix/suffix)
        #   - matching exactly one of the next LL/LLL values via forward_T
        candidates = []

        # Narrow ASCII search based on expected characters if possible
        ascii_range = range(32, 127)

        # Place any format constraints we already know
        if idx < len("scriptCTF{"):
            ascii_range = [ord("scriptCTF{"[idx])]
        elif idx == N-1:
            ascii_range = [ord('}')]

        # try all printable characters (or constrained set) and see which table they match
        for ch in ascii_range:
            t = forward_T(ch, i)
            matched = []
            if li < len(LL)  and t == LL[li]:   matched.append("LL")
            if lj < len(LLL) and t == LLL[lj]:  matched.append("LLL")
            if len(matched) == 1:
                candidates.append( (ch, matched[0]) )

        # If the constraint set is empty (shouldn't happen for this challenge),
        # fall back to full printable set.
        if not candidates:
            for ch in range(32, 127):
                t = forward_T(ch, i)
                matched = []
                if li < len(LL)  and t == LL[li]:   matched.append("LL")
                if lj < len(LLL) and t == LLL[lj]:  matched.append("LLL")
                if len(matched) == 1:
                    candidates.append( (ch, matched[0]) )
            if not candidates:
                raise RuntimeError(f"No unique match at i={i} (li={li}, lj={lj})")

        # choose the (unique) candidate
        ch, which = candidates[0]
        out[idx] = chr(ch)
        if which == "LL":
            li += 1
        else:
            lj += 1

    return ''.join(out)

if __name__ == "__main__":
    flag = solve()
    print(flag)

