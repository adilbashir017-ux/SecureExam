# Educational Kyber-style key delivery module.
# Adapted from the original course project.
# This is not a production CRYSTALS-Kyber implementation.

from .utils import (
    base64_to_bytes,
    bytes_to_base64,
    generate_random_bytes,
    sha256_hash,
    xor_bytes,
)


def derive_public_key(private_key: bytes) -> bytes:
    return sha256_hash(private_key)


def kyber_keygen():
    private_key = generate_random_bytes(32)
    public_key = derive_public_key(private_key)
    return public_key, private_key


def derive_shared_mask(public_key: bytes, encapsulation_random: bytes) -> bytes:
    return sha256_hash(public_key + encapsulation_random)


def kyber_encapsulate(public_key: bytes, exam_key: bytes):
    encapsulation_random = generate_random_bytes(32)
    mask = derive_shared_mask(public_key, encapsulation_random)
    encrypted_exam_key = xor_bytes(exam_key, mask[: len(exam_key)])
    return {
        "encapsulation_random": bytes_to_base64(encapsulation_random),
        "encrypted_exam_key": bytes_to_base64(encrypted_exam_key),
    }


def kyber_decapsulate(private_key: bytes, package: dict) -> bytes:
    public_key = derive_public_key(private_key)
    encapsulation_random = base64_to_bytes(package["encapsulation_random"])
    encrypted_exam_key = base64_to_bytes(package["encrypted_exam_key"])
    mask = derive_shared_mask(public_key, encapsulation_random)
    return xor_bytes(encrypted_exam_key, mask[: len(encrypted_exam_key)])
