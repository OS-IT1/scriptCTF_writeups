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

Strings in libforeign.so reveal the following JNI exports :
```text
Java_xyz_scriptctf_Main_initialize

Java_xyz_scriptctf_Main_sc 
```
## Identifying the JNI function:
If we run the following: 
```shell
strings -tx foreign_design/native/linux64/libforeign.so | grep Java
```
We will get something like :
```text
00000000000011e0 Java_xyz_scriptctf_Main_sc
```
Then we just disassimble that function:
```shell
objdump -d --start-address=0x11e0 --stop-address=0x1300 \
    libforeign.so > checker.txt
```
This contains XOR operations, Index Based Permutations and comparision against .rodata tables (We will come to the last one later).

The Java side (Main.class) permutes indices and delegates the actual comparison to the native sc(char c, int i).

Similarly we do for Java_xyz_scriptctf_Main_initialize and find that initialize() sets up two integer arrays LL and LLL with inside the Java Side

## Understanding Java:

The Java validator permutes character positions as:
```python
idx(i) = (5*i + 3) % 37
```
This gives us the positions from which the flag is being read.

## Transform:

For each loop index i and character code c = ord(flag\[idx(i)\]), the code finds the following:
```python
# if i is even:
encoded = ((c ^ 0x5A) - (i * 3)) ^ (i + 19)

# if i is odd:
base = c + (i % 7) * 2
base ^= 0x13
base += 1
encoded = base
```

After this encoded value is used against arrays LL and LLL.
## From .rodata:
The .rodata file is obtained by running the following command inside the linux64 directory:
```shell
objdump -s -j .rodata libforeign.so > rodata.txt
```
In this file starting at the offset 0x2090 we have some 32-bit little-endian integers (the ones that have a alphabatic character in them) stored in a sequence 
Integer array is present in the native:
```python
LL = [32,92,4,104,106,76,96,113,42,65,22,43,203,84,220,98,210,71,29,123,20,125,199,76,230,117,243,84,54,103,197,104,251,83,253,128,159] 
```
The total 37 elements matches the required flag length. During
checking, sc conceptually consumes from these arrays;our solver infers on the fly which table each T(i) comes
from.

## Constraints
This was know from the format

Length = 37
Obviously scriptCTF{ should be at the starting and ending with a }.
Hence our search becomes limited

## Our solver (finally!):
For even indices , the transform can be simply reverted by the following: 
```python
((encoded ^ 0x5A) - (i * 3)) ^ (i + 19)
```
This looks similar to the forward transform because XOR and subtraction are reversible operations, applying the same expression recovers the original character.
As for odd indices The forward transform involves c + 2*(i%7), then an XOR with 0x13, then a final +1.
I have included a solver.py file. It reconstructs the flag from the constants above,the transform,and the
permutation.

Output (lets goooooo!!!!) :

### scriptCTF{nO_MOr3_n471v3_tr4N5l471on} 
