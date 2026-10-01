Encrypted Student Examination Portal
====================================

Course:
Data Security and Cryptology

Project Topic:
Topic 23: Encrypted Student Examination Portal

Cryptographic Components:
- Symmetric Encryption: SERPENT-style block cipher in OFB mode
- Key Delivery: CRYSTALS-Kyber-style key delivery mechanism
- Digital Signature: Falcon-style signature mechanism

Project Description:
This project implements a secure student examination portal for delivering and collecting encrypted examination papers.
The system ensures that only authorised students can access the exam questions and submit encrypted answers.

Main Security Goals:
1. Confidentiality:
   The examination paper is encrypted using a symmetric block cipher in OFB mode.

2. Authorised Access:
   The exam key is delivered only to authorised students using a public-key based key delivery mechanism.

3. Integrity and Authenticity:
   The encrypted exam is signed digitally. If the encrypted file is modified, signature verification fails.

4. Secure Submission:
   A student answer is read from data/student_answer.txt, encrypted, and submitted to the lecturer.
   The lecturer can decrypt the submitted answer using the system copy of the exam key.

How to Run in Spyder:
1. Open Spyder.
2. Open the file main.py.
3. Run main.py.
4. Use the console menu.

Menu Options:
1. Lecturer prepares encrypted exam
   - Creates demo students
   - Generates student key pairs
   - Generates system signing keys
   - Creates an exam file
   - Encrypts the exam using Serpent/OFB
   - Delivers the exam key only to authorised students
   - Signs the encrypted exam

2. Student opens exam
   - Enter student ID 1001 or 1002 to simulate an authorised student
   - Enter student ID 9999 to simulate an unauthorised student
   - The system verifies the signature, recovers the key if authorised, and decrypts the exam

3. Student submits encrypted answer
   - Before choosing this option, write the student's answer in data/student_answer.txt
   - Use student ID 1001 or 1002 for successful submission
   - Student ID 9999 will fail because the student is not authorised

4. Lecturer decrypts student answer
   - Enter the student ID whose answer was submitted
   - Example: 1001

5. Tampering test
   - Copies the encrypted exam
   - Modifies the copy
   - Shows that signature verification succeeds for the original and fails for the modified file

6. Run full demo
   - Runs the complete system workflow automatically

0. Exit

Demo Students:
- 1001: Alice Student, authorised
- 1002: Bob Student, authorised
- 9999: Eve Attacker, not authorised

Main Source Files:
- main.py: Console menu and program entry point
- portal.py: Full portal workflow
- users.py: Student management and authorisation
- utils.py: File I/O, JSON, Base64, SHA-256, XOR, random bytes
- serpent.py: Educational Serpent-style 128-bit block cipher
- ofb_mode.py: OFB mode built on top of the block cipher
- kyber_module.py: Educational Kyber-style key delivery module
- falcon_module.py: Educational Falcon-style digital signature module

Important Notes:
- The project is implemented in Python.
- The system uses files for input and output instead of a GUI.
- GUI is not required for this project.
- The implementation does not use high-level cryptographic toolkits such as Python's cryptography package.
- Hashing and random byte generation are implemented using standard Python modules.
- The Serpent, Kyber, and Falcon modules are educational self-contained implementations designed to demonstrate the required cryptographic roles in the system.

Recommended Demo Order:
1. Choose option 1 to prepare the encrypted exam.
2. Choose option 2 with student ID 1001.
3. Choose option 2 with student ID 9999.
4. Write an answer in data/student_answer.txt.
5. Choose option 3 with student ID 1001.
6. Choose option 4 with student ID 1001.
7. Choose option 5 to demonstrate tampering detection.
