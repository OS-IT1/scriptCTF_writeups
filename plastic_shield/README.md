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
import sys
import string

# --- Put the ciphertext here (hex string as found in the binary) ---
CIPHERTEXT_HEX = "713d7f2c0f502f485a8af0c284bd3f1e7b03d27204a616a8340beaae23f130edf65401c1f99fe99f63486a385ccea217"

def try_decrypt(ciphertext: bytes, key: bytes, iv: bytes):
    """Return a tuple (plain_bytes, used_unpad:bool) or (None, False) if both fail."""
    cipher = AES.new(key, AES.MODE_CBC, iv)
    # try without unpad first
    try:
        plain_raw = cipher.decrypt(ciphertext)
        return plain_raw, False
    except Exception:
        # unlikely to fail here; AES decrypt normally returns bytes
        pass

    # try with unpad (PKCS#7)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    try:
        plain_unpadded = unpad(cipher.decrypt(ciphertext), AES.block_size)
        return plain_unpadded, True
    except ValueError:
        return None, False

def is_likely_flag(b: bytes):
    
    try:
        s = b.decode('utf-8', errors='ignore')
    except Exception:
        return False
    if "scriptCTF{" in s and "}" in s:
        # also ensure majority printable
        printable_ratio = sum(1 for ch in s if ch in string.printable) / max(1, len(s))
        return printable_ratio > 0.6
    return False

def printable_char_repr(byte_val: int):
    if 32 <= byte_val <= 126:
        return chr(byte_val)
    # show escape for common control characters
    escapes = {9: r"\t", 10: r"\n", 13: r"\r"}
    return escapes.get(byte_val, f"\\x{byte_val:02x}")

def main():
    try:
        ciphertext = binascii.unhexlify(CIPHERTEXT_HEX)
    except binascii.Error:
        sys.exit(1)

    tried = 0
    for digest_size in (48, 64):
        for candidate in range(256):
            tried += 1
            pwd_byte = bytes([candidate])
            h = blake2b(digest_size=digest_size)
            h.update(pwd_byte)
            key_iv = h.digest()

            key = key_iv[:32]            # AES-256 key
            iv  = key_iv[32:48]         # 16-byte IV (even if digest is 64, IV is still first 16 bytes after key)

            # decrypt (both raw and unpadded possibilities are checked)
            plain, used_unpad = try_decrypt(ciphertext, key, iv)
            if plain is None:
                # nothing usable
                continue

            if is_likely_flag(plain):
                try:
                    print(plain.decode())
                except Exception:
                    print("    plaintext (repr):", repr(plain))
                return


if __name__ == "__main__":
    main()
```
The output is :
```bash
scriptCTF{20_cau541i71e5_d3f3n5es_d0wn}
```

## Final Flag: scriptCTF{20_cau541i71e5_d3f3n5es_d0wn}
