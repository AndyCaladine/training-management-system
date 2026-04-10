import os
import sqlite3
from werkzeug.security import generate_password_hash

DATABASE_PATH = "instance/database.db"

def init_database():
    os.makedirs("instance", exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.execute("PRAGMA foreign_keys = ON")

    with open("schema.sql", "r") as f:
        connection.executescript(f.read())

    admin_password = generate_password_hash("Admin123!")
    connection.execute(
        """
        INSERT INTO users (email, password, role)
        VALUES (?, ?, ?)
        """,
        ("admin@example.com", admin_password, "admin")
    )

    employer_password = generate_password_hash("Employer123!")
    connection.execute(
        """
        INSERT INTO users (email, password, role)
        VALUES (?, ?, ?)
        """,
        ("employer@example.com", employer_password, "employer")
    )
    employer_user_id = connection.execute(
        "SELECT id FROM users WHERE email = ?",
        ("employer@example.com",)
    ).fetchone()[0]

    connection.execute(
        """
        INSERT INTO employers (user_id, company_name, contact_name, contact_email)
        VALUES (?, ?, ?, ?)
        """,
        (employer_user_id, "Example Training LTD", "Jane Smith", "jane@example.com")
    )
    employer_id = connection.execute(
        "SELECT id FROM employers WHERE user_id = ?",
        (employer_user_id,)
    ).fetchone()[0]

    student_password = generate_password_hash("Student123!")
    connection.execute(
        """
        INSERT INTO users (email, password, role)
        VALUES (?, ?, ?)
        """,
        ("student@example.com", student_password, "student")
    )
    student_user_id = connection.execute(
        "SELECT id FROM users WHERE email = ?",
        ("student@example.com",)
    ).fetchone()[0]

    connection.execute(
        """
        INSERT INTO students (
            user_id, first_name, last_name, student_number, employer_id, route_name, registration_status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (student_user_id, "Bob", "Jones", "STU1001", employer_id, "Standard Route", "active")
    )

    student_id = connection.execute(
        "SELECT id FROM students WHERE user_id = ?",
        (student_user_id,)
    ).fetchone()[0]

    connection.execute(
        """
        INSERT INTO training_agreements (
            student_id,
            employer_id,
            agreement_status,
            start_date,
            end_date,
            duration_years,
            duration_months,
            duration_days,
            signed_by_student,
            signed_by_employer,
            student_signed_at,
            employer_signed_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            student_id,
            employer_id,
            "draft",
            "2026-04-21",
            "2029-03-31",
            2,
            11,
            10,
            0,
            0,
            None,
            None
        )
    )

    connection.execute(
        """
        INSERT INTO learning_records (
            student_id,
            date_started,
            course_title,
            training_category,
            learning_outcomes,
            date_completed,
            hours_spent,
            status,
            review_status,
            certification_expiry_date,
            notes,
            employer_feedback,
            reviewer_name
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            student_id,
            "2026-04-10",
            "Professional Communication Essentials",
            "Professional Soft Skills",
            "Improve stakeholder communication by using clearer written updates and more structured meeting notes.",
            "2026-04-15",
            6.5,
            "completed",
            "draft",
            None,
            "Focused on communication with managers and colleagues.",
            None,
            None
        )
    )

    exam_modules = [
        ("Foundation", "FND101", "Business Fundamentals", 1),
        ("Foundation", "FND102", "Ethics and Professional Standards", 2),
        ("Foundation", "FND103", "Financial Reporting Basics", 3),
        ("Foundation", "FND104", "Management Information", 4),
        ("Foundation", "FND105", "Tax Principles", 5),
        ("Foundation", "FND106", "Digital and Data Essentials", 6),
        ("Applied", "APP201", "Financial Reporting", 1),
        ("Applied", "APP202", "Audit and Assurance", 2),
        ("Applied", "APP203", "Business Planning", 3),
        ("Applied", "APP204", "Performance Management", 4),
        ("Applied", "APP205", "Tax Compliance", 5),
        ("Applied", "APP206", "Systems and Controls", 6),
        ("Professional", "PRO301", "Strategic Reporting", 1),
        ("Professional", "PRO302", "Advanced Assurance", 2),
        ("Professional", "PRO303", "Strategic Business Planning", 3),
        ("Professional", "PRO304", "Leadership and Decision Making", 4),
        ("Professional", "PRO305", "Risk, Governance and Compliance", 5),
        ("Professional", "PRO306", "Data, Technology and Innovation", 6),
    ]

    connection.executemany(
        """
        INSERT INTO exam_modules (level_name, module_code, module_name, display_order)
        VALUES (?, ?, ?, ?)
        """,
        exam_modules
    )

    exam_result_rows = connection.execute(
        """
        SELECT id, module_code
        FROM exam_modules
        WHERE module_code IN ('FND101', 'FND102', 'FND103', 'APP201', 'APP202', 'PRO301')
        """
    ).fetchall()

    exam_module_lookup = {row[1]: row[0] for row in exam_result_rows}

    student_exam_results = [
        (student_id, exam_module_lookup["FND101"], "2026-01-15", "passed", 78, "Strong understanding of core business concepts."),
        (student_id, exam_module_lookup["FND102"], "2026-02-10", "passed", 71, "Good awareness of ethics principles. Could improve application depth."),
        (student_id, exam_module_lookup["FND103"], "2026-03-05", "failed", 42, "Needs stronger accuracy in financial statement interpretation."),
        (student_id, exam_module_lookup["APP201"], "2026-06-20", "booked", None, None),
        (student_id, exam_module_lookup["APP202"], None, "not_attempted", None, None),
        (student_id, exam_module_lookup["PRO301"], None, "not_attempted", None, None),
    ]

    connection.executemany(
        """
        INSERT INTO student_exam_results (
            student_id,
            exam_module_id,
            exam_date,
            result_status,
            score,
            examiner_feedback
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        student_exam_results
    )

    connection.execute(
        """
        INSERT INTO student_access_codes (code, employer_id, is_active)
        VALUES (?, ?, ?)
        """,
        ("STU-DEMO-2026", employer_id, 1)
    )

    connection.execute(
        """
        INSERT INTO employer_access_codes (code, company_name, is_active)
        VALUES (?, ?, ?)
        """,
        ("EMP-DEMO-2026", "Example Training LTD", 1)
    )

    connection.commit()
    connection.close()
    print("Database initialised successfully.")

if __name__ == "__main__":
    init_database()