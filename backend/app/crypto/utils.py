import base64
import hashlib
import secrets


def xor_bytes(data1: bytes, data2: bytes) -> bytes:
    return bytes(a ^ b for a, b in zip(data1, data2))


def generate_random_bytes(length: int) -> bytes:
    return secrets.token_bytes(length)


def sha256_hash(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def bytes_to_base64(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")


def base64_to_bytes(data_string: str) -> bytes:
    return base64.b64decode(data_string.encode("utf-8"))
