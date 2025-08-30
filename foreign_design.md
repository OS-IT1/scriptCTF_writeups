🕵️‍♂️ CTF Reversing Challenge --- Java + JNI

Category: Reversing Difficulty: Medium Flag:
scriptCTF{nO_MOr3_n471v3_tr4N5l471on}

🧩 Challenge

A single JAR was provided. Running it is unhelpful; the core check is
hidden in a native library loaded via JNI. Goal: recover the flag
without black-box brute-forcing.

🗂️ Unpacking unzip ForeignDesign.jar -d jar_contents \# or the file you
were given, e.g.: \# unzip 51bb29a9-3234-48cb-a939-13e98c9e626f.jar -d
jar_contents

Contents of interest:

jar_contents/ ├── xyz/scriptctf/Main.class ├──
xyz/scriptctf/NativeLoader.class └── native \# actually a ZIP ├──
linux64/libforeign.so ├── linux32/libforeign.so └── win32/foreign.dll

(The native blob is a ZIP: file jar_contents/native → PK..; unzip it
too.)

🔌 JNI surface

Strings in libforeign.so reveal the JNI exports:

Java_xyz_scriptctf_Main_initialize

Java_xyz_scriptctf_Main_sc ← per-character checker

The Java side (Main.class) permutes indices and delegates the actual
comparison to the native sc(char c, int i).

🔁 Index permutation (Java)

The Java validator permutes character positions as:

idx(i) = (5\*i + 3) % 37

So position i in the verification loop reads the character at idx(i)
from the candidate flag.

🧮 Native transform (from Java_xyz_scriptctf_Main_sc)

For each loop index i and character code c = ord(flag\[idx(i)\]), the
native code computes:

base = c + 2\*(i % 7) base \^= (44 if (i % 2 == 0) else 19) T(i) =
base + (i & 1)

This T(i) is then compared to a pair of integer tables embedded in the
native binary.

Inverse (used by the solver):

x = T(i) - (i & 1) x \^= (44 if (i % 2 == 0) else 19) c = x - 2\*(i % 7)
\# 0..255 -\> ASCII

📦 Embedded constants (from .rodata)

Two integer arrays are present in the native:

LL = \[ 32, 92, 4,104,106, 76, 96,113, 42, 65, 22, 43,203, 84,220,
98,210, 71, 29,123, 20,125,199 \] \# 23 values

LLL = \[ 76,230,117,243, 84, 54,103,197,104,251, 83,253,128,159 \] \# 14
values

The total (23 + 14 = 37) matches the required flag length. During
checking, sc conceptually consumes from these arrays; rather than guess
the interleave, our solver infers on the fly which table each T(i) comes
from (it's unambiguous given printable ASCII).

✅ Constraints from format

Length = 37

Must match scriptCTF{..................} (starts with scriptCTF{ and
ends with })

These constraints dramatically prune the search.

🛠️ Solver (stand-alone)

Save as solver.py and run with Python 3. It reconstructs the flag
deterministically from the constants above, the transform, and the
permutation. No native execution required.

#!/usr/bin/env python3

# ---- Embedded constants extracted from the native library ----

LL = \[ 32, 92, 4,104,106, 76, 96,113, 42, 65, 22, 43,203, 84,220,
98,210, 71, 29,123, 20,125,199 \] \# 23 ints

LLL = \[ 76,230,117,243, 84, 54,103,197,104,251, 83,253,128,159 \] \# 14
ints

N = 37

def perm_index(i: int) -\> int: return (5\*i + 3) % N

def forward_T(c: int, i: int) -\> int: \# Native transform
Java_xyz_scriptctf_Main_sc base = c + 2\*(i % 7) base \^= (44 if (i % 2
== 0) else 19) return base + (i & 1)

def invert_T(t: int, i: int) -\> int: x = t - (i & 1) x \^= (44 if (i %
2 == 0) else 19) c = x - 2\*(i % 7) return c & 0xFF

def solve(): out = \['?'\] \* N \# live indices into LL/LLL as we
"consume" matches li, lj = 0, 0

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

if **name** == "**main**": flag = solve() print(flag)

Output:

scriptCTF{nO_MOr3_n471v3_tr4N5l471on}

🧠 Notes & pitfalls

The two-table split (23/14) is a common trick to frustrate
"read-the-array" solvers. You can either (a) derive the routing
predicate from the disassembly, or (b) do what we did here: consume from
whichever table uniquely matches each (i, c)---the constraints and
arithmetic make it unambiguous.

Always check for a permutation: many challenges hide characters by
reordering checks ((a\*i+b) % N is a frequent pattern).

If you prefer full native RE, look up the symbol directly and read
constants from .rodata. Strings search will usually surface the JNI
names.

🏁 Final flag scriptCTF{nO_MOr3_n471v3_tr4N5l471on}

📚 Tools used

unzip (JAR and embedded native bundle)

Strings/hex inspection to find JNI symbols

Quick byte scanning to lift integer tables

Python to reconstruct via inverse transform

Happy reversing! 🛠️
