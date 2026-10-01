# main.py
# Encrypted Student Examination Portal
# Final console menu for project demo

# ***********************************************************
# Encrypted Student Examination Portal
# Main Entry Point
# ***********************************************************
#
# Course: Data Security and Cryptology
#
# Project Topic:
# Topic 23: Encrypted Student Examination Portal
#
# Cryptographic Components:
# - SERPENT-style block cipher in OFB mode
# - CRYSTALS-Kyber-style key delivery mechanism
# - Falcon-style digital signature mechanism
#
# Description:
# This file contains the final console menu of the project.
# The user can run the complete system from here using Spyder.
#
# Main menu options:
# 1. Lecturer prepares encrypted exam
# 2. Student opens exam
# 3. Student submits encrypted answer
# 4. Lecturer decrypts student answer
# 5. Tampering test
# 6. Run full demo
# 0. Exit
# ***********************************************************


from shutil import copyfile

from utils import get_data_path, print_error
from portal import (
    lecturer_prepare_exam,
    student_open_exam,
    student_submit_answer,
    lecturer_decrypt_answer,
    test_full_portal_workflow
)
from falcon_module import (
    verify_exam_signature,
    tamper_with_file
)


def print_menu():
    """
    Print the main menu.
    """
    print()
    print("*" * 70)
    print("Encrypted Student Examination Portal")
    print("*" * 70)
    print("1. Lecturer prepares encrypted exam")
    print("2. Student opens exam")
    print("3. Student submits encrypted answer")
    print("4. Lecturer decrypts student answer")
    print("5. Tampering test")
    print("6. Run full demo")
    print("0. Exit")
    print("*" * 70)


def run_tampering_test():
    """
    Test that a modified encrypted exam fails signature verification.
    The original encrypted exam is not modified.
    """

    original_exam_path = get_data_path("exam_encrypted.bin")
    tampered_exam_path = get_data_path("exam_encrypted_tampered.bin")

    if not original_exam_path.exists():
        print_error("Encrypted exam file does not exist. Run option 1 first.")
        return

    # Copy original encrypted exam to a separate tampered file
    copyfile(original_exam_path, tampered_exam_path)

    print()
    print("Verifying original encrypted exam:")
    original_result = verify_exam_signature(original_exam_path)
    print("Original signature valid:", original_result)

    print()
    tamper_with_file(tampered_exam_path)

    print()
    print("Verifying tampered encrypted exam:")
    tampered_result = verify_exam_signature(tampered_exam_path)
    print("Tampered signature valid:", tampered_result)


def main():
    """
    Main program loop.
    """

    while True:
        print_menu()
        choice = input("Choose an option: ").strip()

        print()

        if choice == "1":
            lecturer_prepare_exam()

        elif choice == "2":
            student_id = input("Enter student ID: ").strip()
            student_open_exam(student_id)

        elif choice == "3":
            student_id = input("Enter student ID: ").strip()
            student_submit_answer(student_id)

        elif choice == "4":
            student_id = input("Enter student ID: ").strip()
            lecturer_decrypt_answer(student_id)

        elif choice == "5":
            run_tampering_test()

        elif choice == "6":
            test_full_portal_workflow()

        elif choice == "0":
            print("Exiting the system. Goodbye.")
            break

        else:
            print_error("Invalid option. Please choose a number from the menu.")


if __name__ == "__main__":
    main()