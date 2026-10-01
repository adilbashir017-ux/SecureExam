from app.crypto.falcon_module import falcon_keygen
from app.crypto.kyber_module import kyber_keygen
from app.services.crypto_service import (
    decrypt_student_submission,
    encrypt_student_submission,
    open_exam_for_student,
    prepare_encrypted_exam,
)


def test_full_crypto_workflow():
    alice_public, alice_private = kyber_keygen()
    _, eve_private = kyber_keygen()
    falcon_public, falcon_private = falcon_keygen()

    original_exam = "Question 1: Explain symmetric encryption."
    prepared = prepare_encrypted_exam(original_exam, {1001: alice_public}, falcon_private)

    alice = open_exam_for_student(
        prepared["encrypted_exam"],
        prepared["exam_iv"],
        prepared["signature"],
        falcon_public,
        alice_private,
        prepared["protected_exam_keys"][1001],
    )
    assert alice["decryption_successful"] is True
    assert alice["exam_content"] == original_exam

    eve = open_exam_for_student(
        prepared["encrypted_exam"],
        prepared["exam_iv"],
        prepared["signature"],
        falcon_public,
        eve_private,
        None,
    )
    assert eve["decryption_successful"] is False
    assert eve["exam_content"] is None

    tampered = open_exam_for_student(
        prepared["encrypted_exam"] + b"TAMPERED",
        prepared["exam_iv"],
        prepared["signature"],
        falcon_public,
        alice_private,
        prepared["protected_exam_keys"][1001],
    )
    assert tampered["signature_valid"] is False

    submission = encrypt_student_submission(
        1001,
        "My answer",
        prepared["encrypted_exam"],
        prepared["signature"],
        falcon_public,
        alice_private,
        prepared["protected_exam_keys"][1001],
    )
    plaintext = decrypt_student_submission(
        submission["encrypted_answer"],
        submission["answer_iv"],
        prepared["exam_key"],
    )
    assert "My answer" in plaintext
