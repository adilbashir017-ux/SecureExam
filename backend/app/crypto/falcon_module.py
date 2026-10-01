# falcon_module.py
# Educational Falcon-style digital signature module.
# This is NOT the full official Falcon standard.
#
# Purpose in the project:
# - The system signs the encrypted exam.
# - Students verify the signature before opening the exam.
# - If the encrypted exam is modified, verification fails.
#
# Digital signature rule demonstrated:
# - Private key signs.
# - Public key verifies.
#
# Falcon-style educational idea:
# - The message is hashed first with SHA-256.
# - The private key contains a short secret vector.
# - The public key contains a public verification vector.
# - The signature contains a short response vector.
# - Verification checks that the signature matches the message hash
#   and the public key, and also checks that the signature is short.
#
# Important note:
# This is an educational self-contained implementation for a course project.
# It demonstrates the role of Falcon as a digital signature scheme.
# It does not implement full official Falcon, NTRU lattices, FFT,
# or Gaussian sampling.


import json

from .utils import (
    generate_random_bytes,
    sha256_hash,
    bytes_to_base64,
    base64_to_bytes,
)

# Educational parameters.
# Falcon also uses q = 12289, so we keep this value for a closer educational style.
Q = 12289
N = 64

# Size of the short random vector used while signing.
Y_BOUND = 1024

# Maximum allowed size for the signature response vector.
Z_BOUND = 1100

# Number of non-zero positions in the challenge vector.
CHALLENGE_WEIGHT = 16


def _json_to_bytes(data):
    """
    Convert a Python dictionary to bytes.
    We store keys and signatures as JSON bytes, and then Base64 them in files.
    """
    return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("utf-8")


def _bytes_to_json(data_bytes):
    """
    Convert JSON bytes back to a Python dictionary.
    """
    return json.loads(data_bytes.decode("utf-8"))


def _expand_bytes(seed, output_length):
    """
    Expand a seed into many pseudo-random bytes using repeated SHA-256.

    This is not a crypto toolkit.
    It only uses the SHA-256 helper already used in the project.
    """
    result = b""
    counter = 0

    while len(result) < output_length:
        counter_bytes = counter.to_bytes(4, "big")
        result += sha256_hash(seed + counter_bytes)
        counter += 1

    return result[:output_length]


def _vector_to_bytes_mod_q(vector):
    """
    Convert a vector modulo q to bytes.
    Used inside hashing for the challenge.
    """
    output = b""

    for value in vector:
        output += int(value % Q).to_bytes(2, "big")

    return output


def _generate_public_a(seed):
    """
    Generate a public vector A from a public seed.

    In real lattice-based signatures, public algebraic structures are used.
    Here we use a simple public vector for an educational version.
    """
    raw = _expand_bytes(seed + b"A", N * 2)
    a = []

    for i in range(N):
        value = int.from_bytes(raw[2 * i: 2 * i + 2], "big") % Q

        if value == 0:
            value = 1

        a.append(value)

    return a


def _generate_short_secret_vector():
    """
    Generate a short private vector s with values from {-1, 0, 1}.
    This is the private signing secret.
    """
    while True:
        raw = generate_random_bytes(N)
        s = []

        for byte in raw:
            s.append((byte % 3) - 1)

        if any(value != 0 for value in s):
            return s


def _generate_short_y_vector():
    """
    Generate a short random vector y used during signing.
    """
    raw = generate_random_bytes(N * 2)
    y = []

    for i in range(N):
        value = int.from_bytes(raw[2 * i: 2 * i + 2], "big")
        value = (value % (2 * Y_BOUND + 1)) - Y_BOUND
        y.append(value)

    return y


def _hash_to_challenge(message_digest, salt, w_vector):
    """
    Convert the message digest, salt, and public commitment vector w
    into a sparse challenge vector c.

    The challenge vector contains mostly zeros and a few values from {-1, 1}.
    This is an educational version of the Fiat-Shamir idea used in
    lattice-style signatures.
    """
    challenge = [0] * N
    needed = CHALLENGE_WEIGHT

    seed = message_digest + salt + _vector_to_bytes_mod_q(w_vector)
    stream = _expand_bytes(seed + b"challenge", 512)

    index = 0
    stream_position = 0

    while needed > 0:
        if stream_position + 2 >= len(stream):
            stream += _expand_bytes(seed + b"extra" + index.to_bytes(4, "big"), 512)
            index += 1

        position = stream[stream_position] % N
        sign_bit = stream[stream_position + 1] & 1
        stream_position += 2

        if challenge[position] == 0:
            challenge[position] = 1 if sign_bit == 0 else -1
            needed -= 1

    return challenge


def _compute_public_key_vector(a, s):
    """
    Compute public verification vector t = A * s mod q.

    Private key: s
    Public key: seed for A and t
    """
    t = []

    for ai, si in zip(a, s):
        t.append((ai * si) % Q)

    return t


def _encode_public_key(public_seed, t):
    """
    Encode the public verification key.
    """
    data = {
        "algorithm": "Educational Falcon-style signature",
        "type": "public_key",
        "q": Q,
        "n": N,
        "public_seed": bytes_to_base64(public_seed),
        "t": t
    }

    return _json_to_bytes(data)


def _encode_private_key(public_seed, s, t):
    """
    Encode the private signing key.

    The private key contains the short secret vector s.
    It also stores public data for convenience.
    """
    data = {
        "algorithm": "Educational Falcon-style signature",
        "type": "private_key",
        "q": Q,
        "n": N,
        "public_seed": bytes_to_base64(public_seed),
        "s": s,
        "t": t
    }

    return _json_to_bytes(data)


def derive_public_key(private_key):
    """
    Derive the matching public key from the private key.

    Unlike the old version, the public key is not used to create the signature.
    The private key contains the secret vector s.
    """
    private_data = _bytes_to_json(private_key)

    public_seed = base64_to_bytes(private_data["public_seed"])
    t = private_data["t"]

    return _encode_public_key(public_seed, t)


def falcon_keygen():
    """
    Generate an educational Falcon-style signing key pair.

    Returns:
    - public_key: used for verification.
    - private_key: used for signing.
    """
    public_seed = generate_random_bytes(32)

    a = _generate_public_a(public_seed)
    s = _generate_short_secret_vector()
    t = _compute_public_key_vector(a, s)

    public_key = _encode_public_key(public_seed, t)
    private_key = _encode_private_key(public_seed, s, t)

    return public_key, private_key

def falcon_sign(message_bytes, private_key):
    """
    Sign a message using the private key.

    Correct digital signature flow:
    1. Hash the original message.
    2. Use the private signing key to create the signature.
    3. Return the digital signature.

    In this educational lattice-style construction:
    - s is the private short vector.
    - y is a random short vector.
    - w = A * y mod q.
    - c = Hash(message_digest, salt, w).
    - z = y + c * s.
    - The signature is (salt, c, z).
    """
    private_data = _bytes_to_json(private_key)

    if private_data.get("type") != "private_key":
        raise ValueError("Invalid private key format.")

    public_seed = base64_to_bytes(private_data["public_seed"])
    s = private_data["s"]

    a = _generate_public_a(public_seed)
    message_digest = sha256_hash(message_bytes)

    while True:
        salt = generate_random_bytes(40)
        y = _generate_short_y_vector()

        # Public commitment w = A * y mod q
        w = []
        for ai, yi in zip(a, y):
            w.append((ai * yi) % Q)

        # Challenge derived from the message hash and commitment
        c = _hash_to_challenge(message_digest, salt, w)

        # Private-key signing step: z = y + c * s
        z = []
        for yi, ci, si in zip(y, c, s):
            z.append(yi + ci * si)

        # Keep signature short, like the idea of Falcon verification.
        if all(abs(value) <= Z_BOUND for value in z):
            signature_data = {
                "algorithm": "Educational Falcon-style signature",
                "type": "signature",
                "q": Q,
                "n": N,
                "message_hash_sha256": message_digest.hex(),
                "salt": bytes_to_base64(salt),
                "challenge": c,
                "z": z
            }

            return _json_to_bytes(signature_data)


def falcon_verify(message_bytes, signature, public_key):
    """
    Verify a signature using the public key.

    Correct digital signature flow:
    1. Hash the received message.
    2. Use the public key and the signature to check validity.
    3. If the message was modified, verification fails.

    Verification idea:
    From the signature z and challenge c, compute:

        w' = A * z - c * t mod q

    Since t = A * s and z = y + c * s:

        w' = A * (y + c*s) - c*(A*s)
           = A*y

    Then recompute the challenge from the message hash and w'.
    If the recomputed challenge equals the signature challenge, the signature is valid.
    """
    try:
        public_data = _bytes_to_json(public_key)
        signature_data = _bytes_to_json(signature)

        if public_data.get("type") != "public_key":
            return False

        if signature_data.get("type") != "signature":
            return False

        if public_data.get("q") != Q or public_data.get("n") != N:
            return False

        if signature_data.get("q") != Q or signature_data.get("n") != N:
            return False

        public_seed = base64_to_bytes(public_data["public_seed"])
        t = public_data["t"]

        salt = base64_to_bytes(signature_data["salt"])
        c = signature_data["challenge"]
        z = signature_data["z"]

        if len(t) != N or len(c) != N or len(z) != N:
            return False

        if not all(value in [-1, 0, 1] for value in c):
            return False

        if sum(1 for value in c if value != 0) != CHALLENGE_WEIGHT:
            return False

        if not all(abs(value) <= Z_BOUND for value in z):
            return False

        a = _generate_public_a(public_seed)
        message_digest = sha256_hash(message_bytes)

        # Optional extra check against the stored message hash in the signature.
        if signature_data.get("message_hash_sha256") != message_digest.hex():
            return False

        # Reconstruct w' = A*z - c*t mod q
        w_prime = []
        for ai, zi, ci, ti in zip(a, z, c, t):
            value = (ai * zi - ci * ti) % Q
            w_prime.append(value)

        expected_c = _hash_to_challenge(message_digest, salt, w_prime)

        return expected_c == c

    except Exception:
        return False
