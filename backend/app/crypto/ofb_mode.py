# ofb_mode.py
# OFB mode implementation using the Serpent block cipher

# ***********************************************************
# ofb_mode.py
# Output Feedback Mode - OFB
# ***********************************************************
#
# This file implements OFB mode using the block cipher from
# serpent.py.
#
# OFB mode turns a block cipher into a stream-like cipher:
# - The IV is encrypted first
# - The output becomes a keystream
# - The keystream is XORed with plaintext/ciphertext
#
# The same function is used for encryption and decryption.
#
# In this project, OFB is used to encrypt:
# - Exam files
# - Student answer files
# ***********************************************************


from .serpent import encrypt_block, BLOCK_SIZE
from .utils import xor_bytes


def generate_keystream(key, iv, data_length):
    """
    Generate a keystream using OFB mode.

    OFB:
        output_1 = Encrypt(IV)
        output_2 = Encrypt(output_1)
        output_3 = Encrypt(output_2)
        ...

    The keystream is then XORed with the plaintext/ciphertext.
    """
    if len(iv) != BLOCK_SIZE:
        raise ValueError("IV must be exactly 16 bytes.")

    keystream = b""
    current_block = iv

    while len(keystream) < data_length:
        current_block = encrypt_block(current_block, key)
        keystream += current_block

    return keystream[:data_length]


def ofb_encrypt(data, key, iv):
    """
    Encrypt data using OFB mode.

    In OFB mode encryption and decryption are both XOR with the same keystream.
    """
    keystream = generate_keystream(key, iv, len(data))
    return xor_bytes(data, keystream)


def ofb_decrypt(ciphertext, key, iv):
    """
    Decrypt data using OFB mode.

    OFB decryption is the same operation as encryption.
    """
    return ofb_encrypt(ciphertext, key, iv)


def test_ofb():
    """
    Test OFB encryption and decryption.
    """
    key = b"ExampleSerpentKey"
    iv = b"InitialVector123"  # 16 bytes

    plaintext = (
        b"This is a test exam file. "
        b"It contains several questions for authorised students only."
    )

    ciphertext = ofb_encrypt(plaintext, key, iv)
    decrypted = ofb_decrypt(ciphertext, key, iv)

    print("Plaintext :", plaintext)
    print("Ciphertext:", ciphertext.hex())
    print("Decrypted :", decrypted)
    print("Test passed:", decrypted == plaintext)


if __name__ == "__main__":
    test_ofb()