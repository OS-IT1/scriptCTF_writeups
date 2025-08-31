# Plastic Shield
Category: REV
## Lets see what we were provided:
Lets check the file type:
```bash
$ file plastic-shield
plastic-shield: ELF 64-bit LSB executable, x86-64, dynamically linked
```
We are given an ELF file.
Also a discription was given on the website: "OPSec is useless unless you do it correctly"

## Running the file:
 Firstly see the permission for the executable so that we are able to run it:
```bash
chmod u+x plastic-shield
```
Now it just asks a password from us.
If we type any wrong password it gives us a decrypted text like this: ��[��2rw�*J�*��3�da.
With this we can infer that some AES decryption is happening.

## Opening File in Ghidra:
Now over here if we check lets see what is inside the main function.
There is a prompt asking for  the password and also a call to __isoc99_scanf("%s").
Then another functioni is called with input .

## Inspecting the function:
We find the following:
<ul>
  <li>BLAKE2b being used to hash the input</li>
  <li>First 32 bytes of the hash AES-256 key</li>
  <li>Next 16 bytes of the hash CBC IV</li>
</ul>
Yes I had to google some of them :) .

We also find something that is very important:

```c++
unsigned char keydata[1];
keydata[0] = input[0];
blake2b(key_iv, 48, keydata, 1, NULL, 0);
```
We find that only the first byte of the password is used in hashing (Very Very Important Observation).
## Understanding the Hashing:
1) Firstly from the input it takes the first byte. 
2) Then it does the hashing:
   ```python
   key_iv = BLAKE2b( input_byte )
   ```
3) Decryption:
   ```python
   plaintext = AES-256-CBC(ciphertext, key=key_iv[0:32], iv=key_iv[32:])
   ```
Note that key_iv[0:32] is AES-256 key, And key_iv[32:48] is CBV IV.
After it just prints print the plaintext.

## Plan:
Since we found that only 256 possible keys (inside inspecting the function) , we can brute force them.

## Finding ciphertext:
```shell
strings -tx plastic-shield | grep 713d7f
```
This outputs the ciphertext.
Now with this we can write our solver code without using the binary.

## Solver:
Finally we have our solver :) .
Below is the boring part.
```python
from hashlib import blake2b
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import binascii

# Ciphertext from binary
ciphertext_hex = "713d7f2c0f502f485a8af0c284bd3f1e7b03d27204a616a8340beaae23f130edf65401c1f99fe99f63486a385ccea217"
ciphertext = binascii.unhexlify(ciphertext_hex)

for candidate in range(256):
    # Create BLAKE2b hash from single byte
    password_byte = bytes([candidate])
    hasher = blake2b(digest_size=48)
    hasher.update(password_byte)
    key_iv = hasher.digest()

    key = key_iv[:32]
    iv = key_iv[32:]

    try:
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(ciphertext), AES.block_size)

        # Check if result is ASCII
        if decrypted.startswith(b"scriptCTF{"):
            print(f"Password byte: {candidate} ({chr(candidate)})")
            print(f"Flag: {decrypted.decode()}")
            break
    except:
        continue
```
The output is :
```bash
Password byte: 96 (`) 
Flag: scriptCTF{20_cau541i71e5_d3f3n5es_d0wn}
```

## Final Flag: scriptCTF{20_cau541i71e5_d3f3n5es_d0wn}
