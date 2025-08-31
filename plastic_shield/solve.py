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
