# users.py
# User and student management for the Encrypted Student Examination Portal

# ***********************************************************
# users.py
# Student Management and Authorisation
# ***********************************************************
#
# This file manages the demo users of the examination portal.
#
# Demo students:
# - 1001: Alice Student, authorised
# - 1002: Bob Student, authorised
# - 9999: Eve Attacker, not authorised
#
# The authorisation status is used to decide whether a student
# is allowed to receive the encrypted exam key.
# ***********************************************************

from utils import (
    get_data_path,
    save_json,
    load_json,
    print_success,
    print_error
)


STUDENTS_FILE = get_data_path("students.json")


def create_demo_students():
    """
    Create demo students for the project.
    Some students are authorised and one is not authorised.
    """

    students = {
        "1001": {
            "student_id": "1001",
            "name": "Alice Student",
            "authorised": True
        },
        "1002": {
            "student_id": "1002",
            "name": "Bob Student",
            "authorised": True
        },
        "9999": {
            "student_id": "9999",
            "name": "Eve Attacker",
            "authorised": False
        }
    }

    save_json(STUDENTS_FILE, students)
    print_success("Demo students created successfully.")


def load_students():
    """
    Load students from students.json.
    """
    return load_json(STUDENTS_FILE, default_value={})


def get_student(student_id):
    """
    Return a student by student_id.
    If the student does not exist, return None.
    """
    students = load_students()
    return students.get(student_id)


def is_authorised(student_id):
    """
    Check if a student is authorised to access the exam.
    """
    student = get_student(student_id)

    if student is None:
        return False

    return student.get("authorised", False)


def print_all_students():
    """
    Print all students in the system.
    """
    students = load_students()

    if not students:
        print_error("No students found. Please initialize demo students first.")
        return

    print("Students in the system:")
    print("-----------------------")

    for student_id, student in students.items():
        status = "Authorised" if student["authorised"] else "Not authorised"
        print(f"ID: {student_id} | Name: {student['name']} | Status: {status}")


def print_student_status(student_id):
    """
    Print whether a specific student is authorised or not.
    """
    student = get_student(student_id)

    if student is None:
        print_error("Student was not found.")
        return

    if student["authorised"]:
        print_success(f"Student {student_id} is authorised to access the exam.")
    else:
        print_error(f"Student {student_id} is NOT authorised to access the exam.")