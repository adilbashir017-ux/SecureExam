# utils.py
# Helper functions for the Encrypted Student Examination Portal

# ***********************************************************
# utils.py
# General Utility Functions
# ***********************************************************
#
# This file contains helper functions used by the whole project:
# - Reading and writing text files
# - Reading and writing binary files
# - Loading and saving JSON files
# - Base64 conversion for saving bytes in JSON
# - SHA-256 hashing
# - XOR operation on bytes
# - Secure random byte generation
#
# These functions are not high-level cryptographic toolkits.
# They are basic Python utilities used to support the system.
# ***********************************************************

import json
import hashlib
import secrets
import base64
from pathlib import Path


# Base project directory
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


def ensure_data_dir():
    """
    Make sure that the data folder exists.
    """
    DATA_DIR.mkdir(exist_ok=True)


def read_text_file(file_path):
    """
    Read a text file using UTF-8 encoding.
    """
    file_path = Path(file_path)
    return file_path.read_text(encoding="utf-8")


def write_text_file(file_path, content):
    """
    Write text content to a file using UTF-8 encoding.
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")


def read_binary_file(file_path):
    """
    Read a binary file.
    """
    file_path = Path(file_path)
    return file_path.read_bytes()


def write_binary_file(file_path, data):
    """
    Write bytes to a binary file.
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(data)


def load_json(file_path, default_value=None):
    """
    Load JSON data from a file.
    If the file is empty or does not exist, return default_value.
    """
    file_path = Path(file_path)

    if default_value is None:
        default_value = {}

    if not file_path.exists():
        return default_value

    content = file_path.read_text(encoding="utf-8").strip()

    if content == "":
        return default_value

    return json.loads(content)


def save_json(file_path, data):
    """
    Save data to a JSON file in a readable format.
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def xor_bytes(data1, data2):
    """
    XOR two byte strings.
    The result length is the minimum length of the two inputs.
    """
    return bytes(a ^ b for a, b in zip(data1, data2))


def generate_random_bytes(length):
    """
    Generate cryptographically strong random bytes.
    Used for keys and IV values.
    """
    return secrets.token_bytes(length)


def sha256_hash(data):
    """
    Calculate SHA-256 hash of bytes.
    Returns bytes.
    """
    return hashlib.sha256(data).digest()


def sha256_hex(data):
    """
    Calculate SHA-256 hash of bytes.
    Returns hexadecimal string.
    """
    return hashlib.sha256(data).hexdigest()


def bytes_to_base64(data):
    """
    Convert bytes to base64 string, useful for saving bytes in JSON.
    """
    return base64.b64encode(data).decode("utf-8")


def base64_to_bytes(data_string):
    """
    Convert base64 string back to bytes.
    """
    return base64.b64decode(data_string.encode("utf-8"))


def get_data_path(file_name):
    """
    Return full path inside the data folder.
    """
    ensure_data_dir()
    return DATA_DIR / file_name


def print_success(message):
    """
    Print a success message.
    """
    print("[OK]", message)


def print_error(message):
    """
    Print an error message.
    """
    print("[ERROR]", message)