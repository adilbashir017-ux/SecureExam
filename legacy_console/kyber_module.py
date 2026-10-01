# kyber_module.py
# Educational Kyber-style key delivery module.
# It demonstrates public-key based delivery of the symmetric exam key.

# ***********************************************************
# kyber_module.py
# Educational CRYSTALS-Kyber-style Key Delivery
# ***********************************************************
#
# This file implements a simplified educational key delivery
# mechanism inspired by the role of CRYSTALS-Kyber.
#
# Purpose in the project:
# - Each student receives a public/private key pair
# - The system protects the exam key using the student's public key
# - Only authorised students receive a protected exam key
# - The student uses the private key to recover the exam key
#
# Important note:
# This is an educational self-contained implementation for the
# course project. It demonstrates the role of Kyber as a key
# delivery / key encapsulation mechanism without using ready-made
# cryptographic libraries.
# ***********************************************************

from utils import (
    get_data_path,
    save_json,
    load_json,
    generate_random_bytes,
    sha256_hash,
    xor_bytes,
    bytes_to_base64,
    base64_to_bytes,
    print_success,
    print_error
)

from users import load_students, is_authorised


KYBER_KEYS_FILE = get_data_path("kyber_student_keys.json")
DELIVERED_KEYS_FILE = get_data_path("delivered_keys.json")


def derive_public_key(private_key):
    """
    Derive a public key from a private key using SHA-256.
    This is a simplified educational construction.
    """
    return sha256_hash(private_key)


def kyber_keygen():
    """
    Generate a simplified Kyber-style key pair.
    """
    private_key = generate_random_bytes(32)
    public_key = derive_public_key(private_key)

    return public_key, private_key


def derive_shared_mask(public_key, encapsulation_random):
    """
    Derive a shared mask from public key and random encapsulation value.
    This mask is used to protect the exam key.
    """
    return sha256_hash(public_key + encapsulation_random)


def kyber_encapsulate(public_key, exam_key):
    """
    Protect the exam key using the student's public key.

    Returns:
        protected_key package containing:
        - encapsulation_random
        - encrypted_exam_key
    """
    encapsulation_random = generate_random_bytes(32)
    mask = derive_shared_mask(public_key, encapsulation_random)

    encrypted_exam_key = xor_bytes(exam_key, mask[:len(exam_key)])

    package = {
        "encapsulation_random": bytes_to_base64(encapsulation_random),
        "encrypted_exam_key": bytes_to_base64(encrypted_exam_key)
    }

    return package


def kyber_decapsulate(private_key, package):
    """
    Recover the exam key using the student's private key.
    """
    public_key = derive_public_key(private_key)

    encapsulation_random = base64_to_bytes(package["encapsulation_random"])
    encrypted_exam_key = base64_to_bytes(package["encrypted_exam_key"])

    mask = derive_shared_mask(public_key, encapsulation_random)

    exam_key = xor_bytes(encrypted_exam_key, mask[:len(encrypted_exam_key)])

    return exam_key


def generate_keys_for_all_students():
    """
    Generate Kyber-style key pairs for all students in students.json.
    """
    students = load_students()

    if not students:
        print_error("No students found. Please create demo students first.")
        return

    student_keys = {}

    for student_id, student in students.items():
        public_key, private_key = kyber_keygen()

        student_keys[student_id] = {
            "student_id": student_id,
            "name": student["name"],
            "authorised": student["authorised"],
            "public_key": bytes_to_base64(public_key),
            "private_key": bytes_to_base64(private_key)
        }

    save_json(KYBER_KEYS_FILE, student_keys)
    print_success("Kyber-style key pairs were generated for all students.")


def load_student_keys():
    """
    Load all student Kyber-style keys.
    """
    return load_json(KYBER_KEYS_FILE, default_value={})


def get_student_key_pair(student_id):
    """
    Return a student's key pair from the key file.
    """
    student_keys = load_student_keys()
    return student_keys.get(student_id)


def deliver_exam_key_to_authorised_students(exam_key):
    """
    Deliver the exam key only to authorised students.
    Each authorised student receives a protected version of the exam key.
    """

    student_keys = load_student_keys()

    if not student_keys:
        print_error("Student Kyber-style keys were not found. Generate them first.")
        return

    delivered_keys = {}

    for student_id, key_info in student_keys.items():
        if is_authorised(student_id):
            public_key = base64_to_bytes(key_info["public_key"])
            package = kyber_encapsulate(public_key, exam_key)

            delivered_keys[student_id] = {
                "student_id": student_id,
                "name": key_info["name"],
                "protected_exam_key": package
            }

    save_json(DELIVERED_KEYS_FILE, delivered_keys)

    print_success("Exam key was delivered only to authorised students.")
    print("Number of authorised students who received the key:", len(delivered_keys))


def recover_exam_key_for_student(student_id):
    """
    Try to recover the exam key for a specific student.
    If the student is not authorised or no key was delivered, return None.
    """

    delivered_keys = load_json(DELIVERED_KEYS_FILE, default_value={})
    student_key_pair = get_student_key_pair(student_id)

    if student_key_pair is None:
        print_error("Student key pair was not found.")
        return None

    if student_id not in delivered_keys:
        print_error("No delivered exam key found for this student. Access denied.")
        return None

    private_key = base64_to_bytes(student_key_pair["private_key"])
    package = delivered_keys[student_id]["protected_exam_key"]

    recovered_key = kyber_decapsulate(private_key, package)

    print_success(f"Student {student_id} successfully recovered the exam key.")
    return recovered_key


def test_kyber_key_delivery():
    """
    Test the simplified Kyber-style key delivery mechanism.
    """

    print("Testing Kyber-style key delivery...")
    print()

    generate_keys_for_all_students()
    print()

    exam_key = generate_random_bytes(16)
    print("Original exam key:", exam_key.hex())
    print()

    deliver_exam_key_to_authorised_students(exam_key)
    print()

    recovered_1001 = recover_exam_key_for_student("1001")
    print("Student 1001 key correct:", recovered_1001 == exam_key)
    print()

    recovered_1002 = recover_exam_key_for_student("1002")
    print("Student 1002 key correct:", recovered_1002 == exam_key)
    print()

    recovered_9999 = recover_exam_key_for_student("9999")
    print("Student 9999 recovered key:", recovered_9999)