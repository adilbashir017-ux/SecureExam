from app.crypto.falcon_module import falcon_sign, falcon_verify
from app.crypto.kyber_module import kyber_decapsulate, kyber_encapsulate
from app.crypto.ofb_mode import ofb_decrypt, ofb_encrypt
from app.crypto.utils import generate_random_bytes


def prepare_encrypted_exam(
    exam_text: str,
    authorized_student_public_keys: dict[int, bytes],
    falcon_private_key: bytes,
):
    if not exam_text.strip():
        raise ValueError("Exam content cannot be empty")

    exam_bytes = exam_text.encode("utf-8")
    exam_key = generate_random_bytes(16)
    exam_iv = generate_random_bytes(16)
    encrypted_exam = ofb_encrypt(exam_bytes, exam_key, exam_iv)

    protected_exam_keys = {
        student_id: kyber_encapsulate(public_key, exam_key)
        for student_id, public_key in authorized_student_public_keys.items()
    }

    signature = falcon_sign(encrypted_exam, falcon_private_key)

    return {
        "exam_key": exam_key,
        "exam_iv": exam_iv,
        "encrypted_exam": encrypted_exam,
        "protected_exam_keys": protected_exam_keys,
        "signature": signature,
    }


def open_exam_for_student(
    encrypted_exam: bytes,
    exam_iv: bytes,
    exam_signature: bytes,
    falcon_public_key: bytes,
    student_private_key: bytes | None,
    protected_exam_key: dict | None,
):
    signature_valid = falcon_verify(
        encrypted_exam,
        exam_signature,
        falcon_public_key,
    )

    if not signature_valid:
        return {
            "signature_valid": False,
            "key_available": False,
            "decryption_successful": False,
            "exam_content": None,
            "encrypted_content": encrypted_exam.hex(),
        }

    if protected_exam_key is None or student_private_key is None:
        return {
            "signature_valid": True,
            "key_available": False,
            "decryption_successful": False,
            "exam_content": None,
            "encrypted_content": encrypted_exam.hex(),
        }

    try:
        exam_key = kyber_decapsulate(student_private_key, protected_exam_key)
        decrypted = ofb_decrypt(encrypted_exam, exam_key, exam_iv).decode("utf-8")
    except (KeyError, TypeError, ValueError, UnicodeDecodeError):
        return {
            "signature_valid": True,
            "key_available": True,
            "decryption_successful": False,
            "exam_content": None,
            "encrypted_content": encrypted_exam.hex(),
        }

    return {
        "signature_valid": True,
        "key_available": True,
        "decryption_successful": True,
        "exam_content": decrypted,
        "encrypted_content": encrypted_exam.hex(),
    }


def encrypt_student_submission(
    student_id: int,
    answer_text: str,
    encrypted_exam: bytes,
    exam_signature: bytes,
    falcon_public_key: bytes,
    student_private_key: bytes,
    protected_exam_key: dict | None,
):
    if not answer_text.strip():
        raise ValueError("Answer cannot be empty")

    if not falcon_verify(encrypted_exam, exam_signature, falcon_public_key):
        raise ValueError("Submission stopped because the exam signature is invalid")

    if protected_exam_key is None:
        raise PermissionError("Submission denied. Student cannot recover the exam key")

    exam_key = kyber_decapsulate(student_private_key, protected_exam_key)

    payload = (
        "Encrypted Student Examination Portal - Student Answer\n\n"
        f"Student ID: {student_id}\n\n"
        f"{answer_text}"
    ).encode("utf-8")

    answer_iv = generate_random_bytes(16)
    encrypted_answer = ofb_encrypt(payload, exam_key, answer_iv)

    return {
        "student_id": student_id,
        "answer_iv": answer_iv,
        "encrypted_answer": encrypted_answer,
    }


def decrypt_student_submission(
    encrypted_answer: bytes,
    answer_iv: bytes,
    lecturer_exam_key: bytes,
):
    return ofb_decrypt(
        encrypted_answer,
        lecturer_exam_key,
        answer_iv,
    ).decode("utf-8")
