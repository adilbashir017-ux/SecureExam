# serpent.py
# Educational self-contained implementation of a Serpent-style 128-bit block cipher.
# Used as the symmetric encryption component in the project.

# ***********************************************************
# serpent.py
# Educational SERPENT-style Block Cipher
# ***********************************************************
#
# This file implements a self-contained educational block cipher
# inspired by SERPENT.
#
# Main characteristics:
# - 128-bit block size
# - 32 rounds
# - Serpent S-boxes
# - Round keys derived from the main key
# - Reversible linear transformation
#
# The cipher is used as the symmetric encryption component of
# the project and is later combined with OFB mode.
#
# Note:
# This implementation is designed for educational demonstration
# in the course project. It demonstrates the role of SERPENT as
# a symmetric block cipher without using ready-made cryptographic
# toolkits.
# ***********************************************************



from utils import sha256_hash


BLOCK_SIZE = 16          # 128 bits
ROUND_KEY_SIZE = 16      # 128 bits
NUM_ROUNDS = 32


# Serpent S-boxes
S_BOXES = [
    [3, 8, 15, 1, 10, 6, 5, 11, 14, 13, 4, 2, 7, 0, 9, 12],
    [15, 12, 2, 7, 9, 0, 5, 10, 1, 11, 14, 8, 6, 13, 3, 4],
    [8, 6, 7, 9, 3, 12, 10, 15, 13, 1, 14, 4, 0, 11, 5, 2],
    [0, 15, 11, 8, 12, 9, 6, 3, 13, 1, 2, 4, 10, 7, 5, 14],
    [1, 15, 8, 3, 12, 0, 11, 6, 2, 5, 4, 10, 9, 14, 7, 13],
    [15, 5, 2, 11, 4, 10, 9, 12, 0, 3, 14, 8, 13, 6, 7, 1],
    [7, 2, 12, 5, 8, 4, 6, 11, 14, 9, 1, 15, 13, 3, 10, 0],
    [1, 13, 15, 0, 14, 8, 2, 11, 7, 4, 12, 10, 9, 3, 5, 6]
]


def build_inverse_sboxes():
    """
    Build inverse S-boxes for decryption.
    """
    inverse_boxes = []

    for box in S_BOXES:
        inverse = [0] * 16
        for input_value, output_value in enumerate(box):
            inverse[output_value] = input_value
        inverse_boxes.append(inverse)

    return inverse_boxes


INV_S_BOXES = build_inverse_sboxes()


def xor_bytes(a, b):
    """
    XOR two byte strings of equal length.
    """
    return bytes(x ^ y for x, y in zip(a, b))


def apply_sbox(block, box):
    """
    Apply a 4-bit S-box to every nibble in the 128-bit block.
    Each byte contains two nibbles.
    """
    result = bytearray()

    for byte in block:
        high = (byte >> 4) & 0x0F
        low = byte & 0x0F

        new_high = box[high]
        new_low = box[low]

        result.append((new_high << 4) | new_low)

    return bytes(result)


def rotate_left_128(block, shift):
    """
    Rotate a 128-bit block to the left.
    """
    value = int.from_bytes(block, byteorder="big")
    shift = shift % 128

    rotated = ((value << shift) | (value >> (128 - shift))) & ((1 << 128) - 1)

    return rotated.to_bytes(16, byteorder="big")


def rotate_right_128(block, shift):
    """
    Rotate a 128-bit block to the right.
    """
    value = int.from_bytes(block, byteorder="big")
    shift = shift % 128

    rotated = ((value >> shift) | (value << (128 - shift))) & ((1 << 128) - 1)

    return rotated.to_bytes(16, byteorder="big")


def linear_transform(block):
    """
    Simple invertible linear transformation inspired by Serpent diffusion.
    """
    part1 = rotate_left_128(block, 13)
    part2 = rotate_left_128(block, 47)
    mixed = xor_bytes(part1, part2)

    return mixed


def inverse_linear_transform(block):
    """
    Inverse of the selected linear transformation.

    Since:
        LT(x) = ROTL(x,13) XOR ROTL(x,47)

    This simplified transform is not guaranteed to be trivially invertible
    for all possible blocks, so for the project implementation we use
    a different reversible diffusion below.

    This function is kept only for clarity and is not used.
    """
    raise NotImplementedError("Not used in this implementation.")


def split_words(block):
    """
    Split 16-byte block into four 32-bit words.
    """
    return [
        int.from_bytes(block[0:4], "big"),
        int.from_bytes(block[4:8], "big"),
        int.from_bytes(block[8:12], "big"),
        int.from_bytes(block[12:16], "big")
    ]


def join_words(words):
    """
    Join four 32-bit words into 16-byte block.
    """
    return b"".join(word.to_bytes(4, "big") for word in words)


def rotl32(value, shift):
    """
    Rotate 32-bit integer left.
    """
    value &= 0xFFFFFFFF
    shift %= 32
    return ((value << shift) | (value >> (32 - shift))) & 0xFFFFFFFF


def rotr32(value, shift):
    """
    Rotate 32-bit integer right.
    """
    value &= 0xFFFFFFFF
    shift %= 32
    return ((value >> shift) | (value << (32 - shift))) & 0xFFFFFFFF


def serpent_linear_transform(block):
    """
    Serpent-like reversible linear transform on four 32-bit words.
    """
    x0, x1, x2, x3 = split_words(block)

    x0 = rotl32(x0, 13)
    x2 = rotl32(x2, 3)

    x1 = x1 ^ x0 ^ x2
    x3 = x3 ^ x2 ^ ((x0 << 3) & 0xFFFFFFFF)

    x1 = rotl32(x1, 1)
    x3 = rotl32(x3, 7)

    x0 = x0 ^ x1 ^ x3
    x2 = x2 ^ x3 ^ ((x1 << 7) & 0xFFFFFFFF)

    x0 = rotl32(x0, 5)
    x2 = rotl32(x2, 22)

    return join_words([x0, x1, x2, x3])


def serpent_inverse_linear_transform(block):
    """
    Inverse of the Serpent-like linear transform.
    """
    x0, x1, x2, x3 = split_words(block)

    x2 = rotr32(x2, 22)
    x0 = rotr32(x0, 5)

    x2 = x2 ^ x3 ^ ((x1 << 7) & 0xFFFFFFFF)
    x0 = x0 ^ x1 ^ x3

    x3 = rotr32(x3, 7)
    x1 = rotr32(x1, 1)

    x3 = x3 ^ x2 ^ ((x0 << 3) & 0xFFFFFFFF)
    x1 = x1 ^ x0 ^ x2

    x2 = rotr32(x2, 3)
    x0 = rotr32(x0, 13)

    return join_words([x0, x1, x2, x3])


def generate_round_keys(key):
    """
    Generate 33 round keys of 128 bits each.

    The function is self-contained and deterministic:
    the same key always generates the same round keys.
    """
    if not isinstance(key, bytes):
        raise TypeError("Key must be bytes.")

    if len(key) == 0:
        raise ValueError("Key must not be empty.")

    round_keys = []

    seed = key

    for round_index in range(NUM_ROUNDS + 1):
        material = seed + round_index.to_bytes(4, byteorder="big")
        digest1 = sha256_hash(material)
        digest2 = sha256_hash(digest1 + key + round_index.to_bytes(4, byteorder="big"))

        round_key = digest1[:8] + digest2[:8]
        round_keys.append(round_key)

    return round_keys


def pad_key(key):
    """
    Convert any key length into bytes and keep it suitable for round key generation.
    """
    if isinstance(key, str):
        key = key.encode("utf-8")

    if not isinstance(key, bytes):
        raise TypeError("Key must be str or bytes.")

    return key


def encrypt_block(block, key):
    """
    Encrypt one 128-bit block using the Serpent-style cipher.
    """
    if len(block) != BLOCK_SIZE:
        raise ValueError("Block must be exactly 16 bytes.")

    key = pad_key(key)
    round_keys = generate_round_keys(key)

    state = block

    for round_index in range(NUM_ROUNDS):
        state = xor_bytes(state, round_keys[round_index])
        state = apply_sbox(state, S_BOXES[round_index % 8])

        if round_index != NUM_ROUNDS - 1:
            state = serpent_linear_transform(state)

    state = xor_bytes(state, round_keys[NUM_ROUNDS])

    return state


def decrypt_block(block, key):
    """
    Decrypt one 128-bit block using the Serpent-style cipher.
    """
    if len(block) != BLOCK_SIZE:
        raise ValueError("Block must be exactly 16 bytes.")

    key = pad_key(key)
    round_keys = generate_round_keys(key)

    state = xor_bytes(block, round_keys[NUM_ROUNDS])

    for round_index in range(NUM_ROUNDS - 1, -1, -1):
        if round_index != NUM_ROUNDS - 1:
            state = serpent_inverse_linear_transform(state)

        state = apply_sbox(state, INV_S_BOXES[round_index % 8])
        state = xor_bytes(state, round_keys[round_index])

    return state


def test_serpent():
    """
    Test encryption and decryption of one block.
    """
    key = b"ExampleSerpentKey"
    plaintext = b"ExamBlock1234567"  # 16 bytes

    ciphertext = encrypt_block(plaintext, key)
    decrypted = decrypt_block(ciphertext, key)

    print("Plaintext :", plaintext)
    print("Ciphertext:", ciphertext.hex())
    print("Decrypted :", decrypted)
    print("Test passed:", decrypted == plaintext)


if __name__ == "__main__":
    test_serpent()