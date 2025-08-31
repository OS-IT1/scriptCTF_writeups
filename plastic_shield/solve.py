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
