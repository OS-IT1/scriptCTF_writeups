# Foreign_Design

Category: REV

## Lets see what we were given:

A .jar file was provided. Running it didn't do much.
The main check is hidden in a native library loaded via JNI (Java Native Interface , yes I had to google a lot of it).

## Unpacking :
unzip ForeignDesign.jar -d jar_contents

Contents of interest:
```text
jar_contents
    ├── xyz/scriptctf/Main.class
    ├── xyz/scriptctf/NativeLoader.class
    └── native
        ├── linux64/libforeign.so
        ├── linux32/libforeign.so
        └── win32/foreign.dll
```
Note that the native was actually a zip and I extracted it using binwalk (for no reason).

## Analysing the libraries:

Strings in libforeign.so reveal the following JNI exports (also I didn't knew how to check .so otherwise so strings it was):
```text
Java_xyz_scriptctf_Main_initialize

Java_xyz_scriptctf_Main_sc 
```
The Java side (Main.class) permutes indices and delegates the actual comparison to the native sc(char c, int i).


## Understanding Java:

The Java validator permutes character positions as:
```python
idx(i) = (5*i + 3) % 37
```
This gives us the positions from which the flag is being read.

## Java_xyz_scriptctf_Main_sc:

For each loop index i and character code c = ord(flag\[idx(i)\]), the code finds the following:
```python
base = c + 2*(i % 7) 
base ^= (44 if (i % 2 == 0) else 19) 
T(i) = base + (i & 1)
```

This T(i) is then compared to a pair of integer tables in the native binary.

Following is the inverse used by the solver:
```python
x = T(i) - (i & 1) # In the native code, if i (character index) is odd, 1 was added to the computed value before storing it in the table. So here we subtract it back when reversing.
x ^= (44 if (i % 2 == 0) else 19)  # In the checker, the value was XORed with 44 for even indices and 19 for odd indices.
c = x - 2*(i % 7) #In the binary, after XOR, they added 2 * (i % 7) to the result before storing it . To reverse it, we subtract this term to recover the original ASCII code.
```
## From .rodata:

Two integer arrays are present in the native:
```python
LL = [32,92,4,104,106,76,96,113,42,65,22,43,203,84,220,98,210,71,29,123,20,125,199]# 23 values

LLL = [76,230,117,243,84,54,103,197,104,251,83,253,128,159 ] # 14 values
```
The total (23 + 14 = 37) matches the required flag length. During
checking, sc conceptually consumes from these arrays;our solver infers on the fly which table each T(i) comes
from.

## Constraints
This was know from the format

Length = 37
Obviously scriptCTF{ should be at the starting and ending with a }.
Hence our search becomes limited

## Our solver (finally!):

I have included a solver.py file. It reconstructs the flag from the constants above,the transform,and the
permutation.

Output (lets goooooo!!!!) :

### scriptCTF{nO_MOr3_n471v3_tr4N5l471on} 
