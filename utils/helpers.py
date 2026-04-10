import random


def generate_student_number(conn):
    while True:
        student_number = f"STU-{random.randint(100000, 999999)}"
        existing = conn.execute(
            "SELECT id FROM students WHERE student_number = ?",
            (student_number,),
        ).fetchone()

        if not existing:
            return student_number