
ENCODED = [
    32, 92, 4, 104, 106, 76, 96, 113, 42, 65, 22, 43,
    203, 84, 220, 98, 210, 71, 29, 123, 20, 125, 199,
    76, 230, 117, 243, 84, 54, 103, 197, 104, 251, 83,
    253, 128, 159
]

N = len(ENCODED)

def unscramble1(encoded: int, i: int) -> int:
    """Direct inversion (s1, even indices)"""
    return ((encoded ^ 0x5A) - (i * 3)) ^ (i + 19)

def unscramble2(encoded: int, i: int) -> int:
    """Brute-force ASCII candidates (s2, odd indices)"""
    for c in range(32, 127):  # printable ASCII
        base = c + 2 * (i % 7)
        if i % 2 == 0:
            base ^= 0x2C
        else:
            base ^= 0x13
        base += (i & 1)
        if base == encoded:
            return c
    return ord('?')  # should not happen

def solve() -> str:
    flag = ['?'] * N
    for i, val in enumerate(ENCODED):
        decoded = unscramble1(val, i) if i % 2 == 0 else unscramble2(val, i)
        idx = (i * 5 + 3) % N
        flag[idx] = chr(decoded)
    return ''.join(flag)

if __name__ == "__main__":
    print("Recovered flag:", solve())
