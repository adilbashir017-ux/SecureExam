# portal.py
# Full portal workflow for the Encrypted Student Examination Portal

# ***********************************************************
# portal.py
# Full Portal Workflow
# ***********************************************************
#
# This file connects all project modules into one complete system.
#
# Main workflow:
# 1. Lecturer creates an exam
# 2. The exam is encrypted using SERPENT-style/OFB
# 3. The exam key is delivered only to authorised students
# 4. The encrypted exam is digitally signed
# 5. An authorised student opens the exam
# 6. An unauthorised student is denied access
# 7. An authorised student submits an encrypted answer
# 8. The lecturer decrypts the submitted answer
#
# This file represents the main logic of the Encrypted Student
# Examination Portal.
# ***********************************************************

from utils import (
    get_data_path,
    write_text_file,
    read_text_file,
    write_binary_file,
    read_binary_file,
    save_json,
    load_json,
    generate_random_bytes,
    bytes_to_base64,
    base64_to_bytes,
    print_success,
    print_error
)

from ofb_mode import ofb_encrypt, ofb_decrypt
from users import create_demo_students, print_all_students
from kyber_module import (
    generate_keys_for_all_students,
    deliver_exam_key_to_authorised_students,
    recover_exam_key_for_student
)
from falcon_module import (
    save_system_falcon_keys,
    sign_exam_file,
    verify_exam_signature
)


EXAM_PLAIN_FILE = get_data_path("exam_plain.txt")
EXAM_ENCRYPTED_FILE = get_data_path("exam_encrypted.bin")
EXAM_METADATA_FILE = get_data_path("exam_metadata.json")
LECTURER_EXAM_KEY_FILE = get_data_path("lecturer_exam_key.json")


def create_demo_exam():
    """
    Create a demo exam file.
    This simulates the lecturer uploading an exam paper.
    """

    exam_text = """Encrypted Student Examination Portal - Demo Exam

Course: Data Security and Cryptology

Question 1:
Explain the difference between symmetric encryption and public-key encryption.

Question 2:
Why is a block cipher mode of operation needed?

Question 3:
What is the purpose of a digital signature?

Question 4:
Explain why only authorised students should receive the exam key.
"""

    write_text_file(EXAM_PLAIN_FILE, exam_text)
    print_success("Demo exam file was created.")


def save_lecturer_exam_key(exam_key):
    """
    Save the lecturer/system copy of the exam key.
    This is used later to decrypt submitted answers.
    """

    data = {
        "description": "Private lecturer/system copy of the exam key",
        "exam_key": bytes_to_base64(exam_key)
    }

    save_json(LECTURER_EXAM_KEY_FILE, data)


def load_lecturer_exam_key():
    """
    Load the lecturer/system copy of the exam key.
    """

    data = load_json(LECTURER_EXAM_KEY_FILE, default_value={})

    if not data:
        return None

    return base64_to_bytes(data["exam_key"])


def encrypt_exam_and_get_key():
    """
    Encrypt the exam file using Serpent/OFB.
    Returns the exam key so it can be delivered using Kyber-style key delivery.
    """

    if not EXAM_PLAIN_FILE.exists():
        print_error("Plain exam file does not exist. Create it first.")
        return None

    exam_text = read_text_file(EXAM_PLAIN_FILE)
    exam_bytes = exam_text.encode("utf-8")

    exam_key = generate_random_bytes(16)
    iv = generate_random_bytes(16)

    encrypted_exam = ofb_encrypt(exam_bytes, exam_key, iv)

    write_binary_file(EXAM_ENCRYPTED_FILE, encrypted_exam)

    metadata = {
        "algorithm": "SERPENT-style",
        "mode": "OFB",
        "key_size_bytes": 16,
        "iv": bytes_to_base64(iv),
        "encrypted_exam_file": "exam_encrypted.bin"
    }

    save_json(EXAM_METADATA_FILE, metadata)
    save_lecturer_exam_key(exam_key)

    print_success("Exam was encrypted using Serpent/OFB.")
    print("Encrypted file:", EXAM_ENCRYPTED_FILE)
    print("Metadata file :", EXAM_METADATA_FILE)

    return exam_key


def lecturer_prepare_exam():
    """
    Full lecturer workflow:
    1. Create demo students.
    2. Generate student Kyber-style keys.
    3. Generate system Falcon-style keys.
    4. Create demo exam.
    5. Encrypt exam using Serpent/OFB.
    6. Deliver exam key only to authorised students.
    7. Sign encrypted exam.
    """

    print("Lecturer prepares encrypted exam")
    print("--------------------------------")
    print()

    create_demo_students()
    print()

    print_all_students()
    print()

    generate_keys_for_all_students()
    print()

    save_system_falcon_keys()
    print()

    create_demo_exam()
    print()

    exam_key = encrypt_exam_and_get_key()

    if exam_key is None:
        return

    print()

    deliver_exam_key_to_authorised_students(exam_key)
    print()

    sign_exam_file(EXAM_ENCRYPTED_FILE)
    print()

    print_success("Lecturer workflow completed successfully.")


def student_open_exam(student_id):
    """
    Student tries to open the encrypted exam.

    Steps:
    1. Verify the signature.
    2. Recover exam key using Kyber-style key delivery.
    3. Decrypt the exam using Serpent/OFB.
    """

    print(f"Student {student_id} tries to open the exam")
    print("-------------------------------------------")
    print()

    if not EXAM_ENCRYPTED_FILE.exists():
        print_error("Encrypted exam file does not exist.")
        return

    metadata = load_json(EXAM_METADATA_FILE, default_value={})

    if not metadata:
        print_error("Exam metadata file was not found.")
        return

    print("Step 1: Verifying exam signature...")
    signature_valid = verify_exam_signature(EXAM_ENCRYPTED_FILE)

    if not signature_valid:
        print_error("Access stopped because signature verification failed.")
        return

    print()

    print("Step 2: Recovering exam key using Kyber-style key delivery...")
    exam_key = recover_exam_key_for_student(student_id)

    if exam_key is None:
        print_error("Access denied. Student cannot recover the exam key.")
        return

    print()

    print("Step 3: Decrypting exam using Serpent/OFB...")

    encrypted_exam = read_binary_file(EXAM_ENCRYPTED_FILE)
    iv = base64_to_bytes(metadata["iv"])

    decrypted_bytes = ofb_decrypt(encrypted_exam, exam_key, iv)
    decrypted_text = decrypted_bytes.decode("utf-8")

    output_file_name = f"exam_decrypted_for_student_{student_id}.txt"
    output_path = get_data_path(output_file_name)

    write_text_file(output_path, decrypted_text)

    print_success(f"Student {student_id} successfully opened the exam.")
    print("Decrypted exam saved to:", output_path)
    print()
    print("Exam content:")
    print("-------------")
    print(decrypted_text)


def student_submit_answer(student_id):
    """
    Student submits encrypted answers.

    Steps:
    1. Verify exam signature.
    2. Recover exam key.
    3. Read the student's answer from data/student_answer.txt.
    4. Encrypt answer using Serpent/OFB.
    5. Save encrypted answer and metadata.
    """

    print(f"Student {student_id} submits encrypted answer")
    print("---------------------------------------------")
    print()

    print("Step 1: Verifying exam signature before submission...")
    signature_valid = verify_exam_signature(EXAM_ENCRYPTED_FILE)

    if not signature_valid:
        print_error("Submission stopped because the exam signature is invalid.")
        return

    print()

    print("Step 2: Recovering exam key for answer encryption...")
    exam_key = recover_exam_key_for_student(student_id)

    if exam_key is None:
        print_error("Submission denied. Student cannot recover the exam key.")
        return

    print()

    # The student writes the answer in this file before submission
    student_answer_path = get_data_path("student_answer.txt")

    if not student_answer_path.exists():
        print_error("student_answer.txt was not found in the data folder.")
        return

    answer_text = read_text_file(student_answer_path).strip()

    if answer_text == "":
        print_error("student_answer.txt is empty. Please write the student's answer first.")
        return

    # Add student ID header to the submitted answer
    submitted_answer_text = f"""Encrypted Student Examination Portal - Student Answer

Student ID: {student_id}

{answer_text}
"""

    plain_answer_path = get_data_path(f"answer_plain_{student_id}.txt")
    encrypted_answer_path = get_data_path(f"answer_encrypted_{student_id}.bin")
    answer_metadata_path = get_data_path(f"answer_metadata_{student_id}.json")

    write_text_file(plain_answer_path, submitted_answer_text)

    iv = generate_random_bytes(16)
    encrypted_answer = ofb_encrypt(submitted_answer_text.encode("utf-8"), exam_key, iv)

    write_binary_file(encrypted_answer_path, encrypted_answer)

    metadata = {
        "student_id": student_id,
        "algorithm": "SERPENT-style",
        "mode": "OFB",
        "iv": bytes_to_base64(iv),
        "source_answer_file": "student_answer.txt",
        "encrypted_answer_file": f"answer_encrypted_{student_id}.bin"
    }

    save_json(answer_metadata_path, metadata)

    print_success(f"Student {student_id} answer was encrypted and submitted successfully.")
    print("Source answer file   :", student_answer_path)
    print("Plain answer file    :", plain_answer_path)
    print("Encrypted answer file:", encrypted_answer_path)
    print("Answer metadata file :", answer_metadata_path)

def lecturer_decrypt_answer(student_id):
    """
    Lecturer decrypts the submitted encrypted answer.
    """

    print(f"Lecturer decrypts answer of student {student_id}")
    print("---------------------------------------------")
    print()

    encrypted_answer_path = get_data_path(f"answer_encrypted_{student_id}.bin")
    answer_metadata_path = get_data_path(f"answer_metadata_{student_id}.json")
    decrypted_answer_path = get_data_path(f"answer_decrypted_{student_id}.txt")

    if not encrypted_answer_path.exists():
        print_error("Encrypted answer file does not exist.")
        return

    metadata = load_json(answer_metadata_path, default_value={})

    if not metadata:
        print_error("Answer metadata file was not found.")
        return

    exam_key = load_lecturer_exam_key()

    if exam_key is None:
        print_error("Lecturer exam key was not found.")
        return

    encrypted_answer = read_binary_file(encrypted_answer_path)
    iv = base64_to_bytes(metadata["iv"])

    decrypted_answer_bytes = ofb_decrypt(encrypted_answer, exam_key, iv)
    decrypted_answer_text = decrypted_answer_bytes.decode("utf-8")

    write_text_file(decrypted_answer_path, decrypted_answer_text)

    print_success(f"Answer of student {student_id} was decrypted successfully.")
    print("Decrypted answer file:", decrypted_answer_path)
    print()
    print("Decrypted answer content:")
    print("-------------------------")
    print(decrypted_answer_text)


def test_full_portal_workflow():
    """
    Test the complete workflow:
    1. Lecturer prepares encrypted and signed exam.
    2. Authorised student opens it.
    3. Unauthorised student fails.
    4. Authorised student submits encrypted answer.
    5. Lecturer decrypts answer.
    6. Unauthorised student fails to submit.
    """

    lecturer_prepare_exam()

    print()
    print("*" * 70)
    print()

    student_open_exam("1001")

    print()
    print("*" * 70)
    print()

    student_open_exam("9999")

    print()
    print("*" * 70)
    print()

    student_submit_answer("1001")

    print()
    print("*" * 70)
    print()

    lecturer_decrypt_answer("1001")

    print()
    print("=" * 70)
    print()

    student_submit_answer("9999")