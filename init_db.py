import os
import sqlite3
from werkzeug.security import generate_password_hash

DATABASE_PATH = "instance/database.db"


def init_database():
    """
    Main entry point for rebuilding the database from scratch.

    This is the file I want future me to be able to open,
    understand quickly, and extend without a headache.
    """
    ensure_instance_folder_exists()

    connection = sqlite3.connect(DATABASE_PATH)
    connection.execute("PRAGMA foreign_keys = ON")

    try:
        rebuild_schema(connection)

        # Seed order matters.
        # Get the core structure in first, then build relationships on top.
        seed_users(connection)
        seed_employers(connection)
        seed_employer_allowed_domains(connection)
        seed_employer_access_codes(connection)
        seed_employer_contacts(connection)

        seed_exam_modules(connection)

        seed_students(connection)
        seed_student_access_codes(connection)
        seed_employer_student_assignments(connection)

        seed_training_agreements(connection)
        seed_learning_records(connection)
        seed_student_exam_results(connection)

        connection.commit()
        print("Database initialised successfully.")

    except Exception as error:
        connection.rollback()
        print(f"Database initialisation failed: {error}")
        raise

    finally:
        connection.close()


# ============================================================
# Setup helpers
# ============================================================

def ensure_instance_folder_exists():
    """Create the instance folder if it does not already exist."""
    os.makedirs("instance", exist_ok=True)


def rebuild_schema(connection):
    """
    Rebuild the database using schema.sql.

    Nice and simple:
    - open schema file
    - execute the whole lot
    - start fresh
    """
    with open("schema.sql", "r", encoding="utf-8") as schema_file:
        connection.executescript(schema_file.read())


# ============================================================
# Lookup helpers
# ============================================================

def fetch_user_id(connection, email):
    """Get a user id from an email address."""
    row = connection.execute(
        "SELECT id FROM users WHERE email = ?",
        (email,)
    ).fetchone()

    if not row:
        raise ValueError(f"User not found for email: {email}")

    return row[0]


def fetch_employer_id(connection, company_name):
    """Get an employer id from a company name."""
    row = connection.execute(
        "SELECT id FROM employers WHERE company_name = ?",
        (company_name,)
    ).fetchone()

    if not row:
        raise ValueError(f"Employer not found for company_name: {company_name}")

    return row[0]


def fetch_student_id(connection, student_number):
    """Get a student id from a student number."""
    row = connection.execute(
        "SELECT id FROM students WHERE student_number = ?",
        (student_number,)
    ).fetchone()

    if not row:
        raise ValueError(f"Student not found for student_number: {student_number}")

    return row[0]


def fetch_employer_contact_id(connection, work_email):
    """Get an employer contact id from their work email."""
    row = connection.execute(
        "SELECT id FROM employer_contacts WHERE work_email = ?",
        (work_email,)
    ).fetchone()

    if not row:
        raise ValueError(f"Employer contact not found for work_email: {work_email}")

    return row[0]


def fetch_exam_module_id(connection, module_code):
    """Get an exam module id from the module code."""
    row = connection.execute(
        "SELECT id FROM exam_modules WHERE module_code = ?",
        (module_code,)
    ).fetchone()

    if not row:
        raise ValueError(f"Exam module not found for module_code: {module_code}")

    return row[0]


# ============================================================
# Seed: users
# ============================================================

def seed_users(connection):
    """
    Seed core login accounts.

    users is intentionally lean.
    It is just auth and role info.
    All the interesting human stuff belongs in profile tables.
    """
    users = [
        ("admin@example.com", "Admin123!", "admin"),
        ("jane.smith@exampletraining.co.uk", "Employer123!", "employer"),
        ("mark.evans@exampletraining.co.uk", "Employer123!", "employer"),
        ("laura.reid@northfieldtech.co.uk", "Employer123!", "employer"),
        ("peter.walsh@greenbridge.org.uk", "Employer123!", "employer"),
        ("sophie.turner@brightpathfinance.co.uk", "Employer123!", "employer"),
        ("david.hughes@brightpathgroup.co.uk", "Employer123!", "employer"),
        ("bob.jones@studentdemo.co.uk", "Student123!", "student"),
        ("amy.wilson@studentdemo.co.uk", "Student123!", "student"),
        ("josh.taylor@studentdemo.co.uk", "Student123!", "student"),
        ("chloe.bennett@studentdemo.co.uk", "Student123!", "student"),
        ("liam.parker@studentdemo.co.uk", "Student123!", "student"),
        ("emma.carter@studentdemo.co.uk", "Student123!", "student"),
    ]

    for email, raw_password, role in users:
        connection.execute(
            """
            INSERT INTO users (email, password, role)
            VALUES (?, ?, ?)
            """,
            (email, generate_password_hash(raw_password), role)
        )


# ============================================================
# Seed: employers
# ============================================================

def seed_employers(connection):
    """
    Seed employer organisations.

    These are company records, not people.
    That separation is doing a lot of heavy lifting now.
    """
    employers = [
        ("Example Training Ltd", "ETL-001", "exampletraining.co.uk", 1),
        ("Northfield Tech Solutions", "NTS-002", "northfieldtech.co.uk", 1),
        ("Greenbridge Housing Association", "GHA-003", "greenbridge.org.uk", 1),
        ("BrightPath Finance Group", "BFG-004", "brightpathfinance.co.uk", 1),
    ]

    connection.executemany(
        """
        INSERT INTO employers (company_name, company_number, primary_domain, is_active)
        VALUES (?, ?, ?, ?)
        """,
        employers
    )


def seed_employer_allowed_domains(connection):
    """
    Seed allowed email domains for employer self-registration.

    This is one of those bits that makes the app feel a lot more real.
    Work email means work email.
    """
    allowed_domains = [
        ("Example Training Ltd", "exampletraining.co.uk", 1),
        ("Northfield Tech Solutions", "northfieldtech.co.uk", 1),
        ("Greenbridge Housing Association", "greenbridge.org.uk", 1),
        ("BrightPath Finance Group", "brightpathfinance.co.uk", 1),
        ("BrightPath Finance Group", "brightpathgroup.co.uk", 1),
    ]

    rows_to_insert = []

    for company_name, domain_name, is_active in allowed_domains:
        employer_id = fetch_employer_id(connection, company_name)
        rows_to_insert.append((employer_id, domain_name, is_active))

    connection.executemany(
        """
        INSERT INTO employer_allowed_domains (employer_id, domain_name, is_active)
        VALUES (?, ?, ?)
        """,
        rows_to_insert
    )


def seed_employer_access_codes(connection):
    """
    Seed employer access codes.

    Mix in a few different states so validation can actually be tested,
    not just the happy path.
    """
    access_codes = [
        ("EMP-ETL-2026", "Example Training Ltd", 1, 0, None),
        ("EMP-NTS-2026", "Northfield Tech Solutions", 1, 0, None),
        ("EMP-GHA-2026", "Greenbridge Housing Association", 1, 0, None),
        ("EMP-BFG-2026", "BrightPath Finance Group", 1, 1, None),
        ("EMP-BFG-INACTIVE", "BrightPath Finance Group", 0, 0, None),
    ]

    rows_to_insert = []

    for code, company_name, is_active, is_single_use, expires_at in access_codes:
        employer_id = fetch_employer_id(connection, company_name)
        rows_to_insert.append(
            (code, employer_id, is_active, is_single_use, expires_at)
        )

    connection.executemany(
        """
        INSERT INTO employer_access_codes (
            code,
            employer_id,
            is_active,
            is_single_use,
            expires_at
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        rows_to_insert
    )


def seed_employer_contacts(connection):
    """
    Seed employer portal users.

    A mix of statuses here is intentional.
    If demo data is too perfect, it hides problems instead of helping.
    """
    employer_contacts = [
        (
            "jane.smith@exampletraining.co.uk",
            "Example Training Ltd",
            "Jane",
            "Smith",
            "Training Manager",
            "Learning and Development",
            "EMP-ETL-001",
            "jane.smith@exampletraining.co.uk",
            "01604 555101",
            None,
            "email",
            "active",
            1,
            "2026-04-01 09:00:00",
            "2026-05-01 09:00:00",
            "2026-04-01 09:00:00",
            None,
            None,
            "2026-04-01 09:00:00",
            "2026-04-01 09:00:00",
        ),
        (
            "mark.evans@exampletraining.co.uk",
            "Example Training Ltd",
            "Mark",
            "Evans",
            "Operations Supervisor",
            "Operations",
            "EMP-ETL-002",
            "mark.evans@exampletraining.co.uk",
            "01604 555102",
            "07700 900001",
            "phone",
            "active",
            0,
            "2026-03-15 09:00:00",
            "2026-04-15 09:00:00",
            "2026-03-15 09:00:00",
            None,
            None,
            "2026-03-15 09:00:00",
            "2026-03-15 09:00:00",
        ),
        (
            "laura.reid@northfieldtech.co.uk",
            "Northfield Tech Solutions",
            "Laura",
            "Reid",
            "Digital Skills Lead",
            "Technology",
            "EMP-NTS-001",
            "laura.reid@northfieldtech.co.uk",
            "01908 555201",
            None,
            "email",
            "active",
            1,
            "2026-03-20 10:00:00",
            "2026-04-20 10:00:00",
            "2026-03-20 10:00:00",
            None,
            None,
            "2026-03-20 10:00:00",
            "2026-03-20 10:00:00",
        ),
        (
            "peter.walsh@greenbridge.org.uk",
            "Greenbridge Housing Association",
            "Peter",
            "Walsh",
            "Team Leader",
            "Housing Services",
            "EMP-GHA-001",
            "peter.walsh@greenbridge.org.uk",
            "01234 555301",
            None,
            "email",
            "inactive",
            1,
            "2025-08-01 09:00:00",
            "2025-09-01 09:00:00",
            "2025-08-01 09:00:00",
            "2026-04-01 09:00:00",
            "inactive_account",
            "2025-08-01 09:00:00",
            "2025-08-01 09:00:00",
        ),
        (
            "sophie.turner@brightpathfinance.co.uk",
            "BrightPath Finance Group",
            "Sophie",
            "Turner",
            "People Development Manager",
            "People Team",
            "EMP-BFG-001",
            "sophie.turner@brightpathfinance.co.uk",
            "0207 555401",
            None,
            "email",
            "active",
            1,
            "2026-04-02 09:00:00",
            "2026-05-02 09:00:00",
            "2026-04-02 09:00:00",
            None,
            None,
            "2026-04-02 09:00:00",
            "2026-04-02 09:00:00",
        ),
        (
            "david.hughes@brightpathgroup.co.uk",
            "BrightPath Finance Group",
            "David",
            "Hughes",
            "Finance Operations Lead",
            "Finance",
            "EMP-BFG-002",
            "david.hughes@brightpathgroup.co.uk",
            "0207 555402",
            "07700 900002",
            "phone",
            "locked",
            0,
            "2026-02-10 09:00:00",
            "2026-03-10 09:00:00",
            "2026-02-10 09:00:00",
            "2026-04-05 10:30:00",
            "gdpr_confirmation_failed",
            "2026-02-10 09:00:00",
            "2026-02-10 09:00:00",
        ),
    ]

    rows_to_insert = []

    for (
        user_email,
        company_name,
        first_name,
        last_name,
        job_title,
        department,
        employee_reference,
        work_email,
        work_phone,
        secondary_phone,
        preferred_contact_method,
        registration_status,
        is_primary_contact,
        gdpr_confirmed_at,
        gdpr_confirmation_due_at,
        last_login_at,
        locked_at,
        lock_reason,
        terms_agreed_at,
        gdpr_agreed_at,
    ) in employer_contacts:
        user_id = fetch_user_id(connection, user_email)
        employer_id = fetch_employer_id(connection, company_name)

        rows_to_insert.append(
            (
                user_id,
                employer_id,
                first_name,
                last_name,
                job_title,
                department,
                employee_reference,
                work_email,
                work_phone,
                secondary_phone,
                preferred_contact_method,
                registration_status,
                is_primary_contact,
                gdpr_confirmed_at,
                gdpr_confirmation_due_at,
                last_login_at,
                locked_at,
                lock_reason,
                terms_agreed_at,
                gdpr_agreed_at,
            )
        )

    connection.executemany(
        """
        INSERT INTO employer_contacts (
            user_id,
            employer_id,
            first_name,
            last_name,
            job_title,
            department,
            employee_reference,
            work_email,
            work_phone,
            secondary_phone,
            preferred_contact_method,
            registration_status,
            is_primary_contact,
            gdpr_confirmed_at,
            gdpr_confirmation_due_at,
            last_login_at,
            locked_at,
            lock_reason,
            terms_agreed_at,
            gdpr_agreed_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows_to_insert
    )


# ============================================================
# Seed: exam modules
# ============================================================

def seed_exam_modules(connection):
    """
    Shared exam list used across the whole system.

    Seed once, link many times.
    """
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


# ============================================================
# Seed: students
# ============================================================

def seed_students(connection):
    """
    Seed student profiles.

    A bit of variation here goes a long way.
    Different employers, roles, departments, and statuses
    make the dashboards and filters actually worth testing.
    """
    students = [
        (
            "bob.jones@studentdemo.co.uk",
            "Example Training Ltd",
            "Bob",
            "Jones",
            "STU1001",
            "Standard Route",
            "Finance",
            "Trainee Accountant",
            "Apr 2026 Cohort",
            "07123 456789",
            "2001-06-14",
            "12 Market Street",
            "Flat 2",
            "Northampton",
            "Northamptonshire",
            "NN1 1AA",
            "active",
        ),
        (
            "amy.wilson@studentdemo.co.uk",
            "Example Training Ltd",
            "Amy",
            "Wilson",
            "STU1002",
            "Standard Route",
            "Operations",
            "Business Administrator",
            "Apr 2026 Cohort",
            "07123 000111",
            "2000-09-21",
            "44 High Street",
            None,
            "Wellingborough",
            "Northamptonshire",
            "NN8 1BD",
            "active",
        ),
        (
            "josh.taylor@studentdemo.co.uk",
            "Northfield Tech Solutions",
            "Josh",
            "Taylor",
            "STU1003",
            "Digital Route",
            "Technology",
            "IT Support Analyst",
            "Mar 2026 Cohort",
            "07123 222333",
            "2002-01-11",
            "7 Meadow Close",
            None,
            "Milton Keynes",
            "Buckinghamshire",
            "MK9 3AB",
            "active",
        ),
        (
            "chloe.bennett@studentdemo.co.uk",
            "Greenbridge Housing Association",
            "Chloe",
            "Bennett",
            "STU1004",
            "Housing Route",
            "Housing Services",
            "Housing Support Officer",
            "Jan 2026 Cohort",
            "07123 444555",
            "1999-11-30",
            "19 Oak Road",
            "Apt 4",
            "Bedford",
            "Bedfordshire",
            "MK40 2TT",
            "inactive",
        ),
        (
            "liam.parker@studentdemo.co.uk",
            "BrightPath Finance Group",
            "Liam",
            "Parker",
            "STU1005",
            "Finance Route",
            "Finance",
            "Accounts Assistant",
            "Feb 2026 Cohort",
            "07123 666777",
            "2001-03-18",
            "88 Station Road",
            None,
            "London",
            "Greater London",
            "E1 4PX",
            "active",
        ),
        (
            "emma.carter@studentdemo.co.uk",
            "BrightPath Finance Group",
            "Emma",
            "Carter",
            "STU1006",
            "Leadership Route",
            "People Team",
            "HR Coordinator",
            "Apr 2026 Cohort",
            "07123 888999",
            "1998-07-07",
            "3 Cedar Avenue",
            None,
            "Luton",
            "Bedfordshire",
            "LU1 2QR",
            "pending",
        ),
    ]

    rows_to_insert = []

    for (
        user_email,
        company_name,
        first_name,
        last_name,
        student_number,
        route_name,
        department,
        job_title,
        cohort,
        phone,
        date_of_birth,
        address_line_1,
        address_line_2,
        town_city,
        county,
        postcode,
        registration_status,
    ) in students:
        user_id = fetch_user_id(connection, user_email)
        employer_id = fetch_employer_id(connection, company_name)

        rows_to_insert.append(
            (
                user_id,
                first_name,
                last_name,
                student_number,
                employer_id,
                route_name,
                department,
                job_title,
                cohort,
                phone,
                date_of_birth,
                address_line_1,
                address_line_2,
                town_city,
                county,
                postcode,
                registration_status,
            )
        )

    connection.executemany(
        """
        INSERT INTO students (
            user_id,
            first_name,
            last_name,
            student_number,
            employer_id,
            route_name,
            department,
            job_title,
            cohort,
            phone,
            date_of_birth,
            address_line_1,
            address_line_2,
            town_city,
            county,
            postcode,
            registration_status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows_to_insert
    )


def seed_student_access_codes(connection):
    """
    Seed student access codes.

    Again, not just one nice clean active code.
    Give yourself something to test against.
    """
    student_access_codes = [
        ("STU-ETL-2026", "Example Training Ltd", 1, None),
        ("STU-NTS-2026", "Northfield Tech Solutions", 1, None),
        ("STU-GHA-2026", "Greenbridge Housing Association", 1, None),
        ("STU-BFG-2026", "BrightPath Finance Group", 1, None),
        ("STU-BFG-INACTIVE", "BrightPath Finance Group", 0, None),
    ]

    rows_to_insert = []

    for code, company_name, is_active, expires_at in student_access_codes:
        employer_id = fetch_employer_id(connection, company_name)
        rows_to_insert.append((code, employer_id, is_active, expires_at))

    connection.executemany(
        """
        INSERT INTO student_access_codes (
            code,
            employer_id,
            is_active,
            expires_at
        )
        VALUES (?, ?, ?, ?)
        """,
        rows_to_insert
    )


def seed_employer_student_assignments(connection):
    """
    Link employer contacts to students.

    This is where the employer portal starts to feel like a real thing
    instead of just a login screen with a nice hat on.
    """
    assignments = [
        ("jane.smith@exampletraining.co.uk", "STU1001", 1, 1, "2026-04-01 09:00:00", None),
        ("mark.evans@exampletraining.co.uk", "STU1002", 1, 1, "2026-04-01 09:15:00", None),
        ("laura.reid@northfieldtech.co.uk", "STU1003", 1, 1, "2026-03-20 10:15:00", None),
        ("peter.walsh@greenbridge.org.uk", "STU1004", 1, 1, "2026-01-10 08:30:00", None),
        ("sophie.turner@brightpathfinance.co.uk", "STU1005", 1, 1, "2026-02-12 09:00:00", None),
        ("david.hughes@brightpathgroup.co.uk", "STU1006", 0, 1, "2026-02-12 09:20:00", None),
    ]

    admin_user_id = fetch_user_id(connection, "admin@example.com")

    rows_to_insert = []

    for (
        work_email,
        student_number,
        is_primary_contact,
        is_active,
        assigned_at,
        removed_at,
    ) in assignments:
        employer_contact_id = fetch_employer_contact_id(connection, work_email)
        student_id = fetch_student_id(connection, student_number)

        rows_to_insert.append(
            (
                employer_contact_id,
                student_id,
                is_primary_contact,
                is_active,
                assigned_at,
                removed_at,
                admin_user_id,
            )
        )

    connection.executemany(
        """
        INSERT INTO employer_student_assignments (
            employer_contact_id,
            student_id,
            is_primary_contact,
            is_active,
            assigned_at,
            removed_at,
            created_by_user_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        rows_to_insert
    )


# ============================================================
# Seed: agreements and learning
# ============================================================

def seed_training_agreements(connection):
    """
    Seed training agreements with a spread of statuses.

    Real systems are never all draft or all approved.
    A decent mix makes the UI and reporting far more believable.
    """
    agreements = [
        ("STU1001", "Example Training Ltd", "draft", "2026-04-21", "2029-03-31", 2, 11, 10, 0, 0, None, None),
        ("STU1002", "Example Training Ltd", "submitted", "2026-04-10", "2029-04-09", 3, 0, 0, 1, 0, "2026-04-10 11:00:00", None),
        ("STU1003", "Northfield Tech Solutions", "approved", "2026-03-01", "2029-02-28", 3, 0, 0, 1, 1, "2026-03-01 09:00:00", "2026-03-03 14:00:00"),
        ("STU1004", "Greenbridge Housing Association", "rejected", "2026-01-15", "2029-01-14", 3, 0, 0, 1, 0, "2026-01-15 10:00:00", None),
        ("STU1005", "BrightPath Finance Group", "approved", "2026-02-20", "2029-02-19", 3, 0, 0, 1, 1, "2026-02-20 13:00:00", "2026-02-22 16:00:00"),
        ("STU1006", "BrightPath Finance Group", "draft", "2026-04-05", "2029-04-04", 3, 0, 0, 0, 0, None, None),
    ]

    rows_to_insert = []

    for (
        student_number,
        company_name,
        agreement_status,
        start_date,
        end_date,
        duration_years,
        duration_months,
        duration_days,
        signed_by_student,
        signed_by_employer,
        student_signed_at,
        employer_signed_at,
    ) in agreements:
        student_id = fetch_student_id(connection, student_number)
        employer_id = fetch_employer_id(connection, company_name)

        rows_to_insert.append(
            (
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
                employer_signed_at,
            )
        )

    connection.executemany(
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
        rows_to_insert
    )


def seed_learning_records(connection):
    """
    Seed learning activity.

    Mixture is the name of the game:
    completed, planned, in progress, reviewed, not reviewed.
    """
    learning_records = [
        (
            "STU1001",
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
            None,
        ),
        (
            "STU1002",
            "2026-04-12",
            "Time Management for Workplace Productivity",
            "Personal Development",
            "Build stronger daily planning habits and reduce missed deadlines.",
            None,
            3.0,
            "in_progress",
            "draft",
            None,
            "Early progress looks promising.",
            None,
            None,
        ),
        (
            "STU1003",
            "2026-03-05",
            "Cyber Security Fundamentals",
            "Professional Technical Skills",
            "Understand the principles of secure systems, passwords, phishing awareness and access control.",
            "2026-03-12",
            8.0,
            "completed",
            "approved",
            "2027-03-12",
            "Useful foundation course for digital support work.",
            "Good engagement and strong practical understanding.",
            "Laura Reid",
        ),
        (
            "STU1004",
            "2026-01-20",
            "Customer Care in Housing Support",
            "Professional Soft Skills",
            "Develop stronger communication and empathy when working with tenants and service users.",
            "2026-01-28",
            5.5,
            "completed",
            "rejected",
            None,
            "Student completed course but reflection was too thin.",
            "Please expand on how this changed your day-to-day approach.",
            "Peter Walsh",
        ),
        (
            "STU1005",
            "2026-02-25",
            "Excel for Finance Teams",
            "Professional Technical Skills",
            "Use formulas, lookups and structured data handling for finance tasks.",
            "2026-03-02",
            7.0,
            "completed",
            "approved",
            None,
            "Very relevant to current job role.",
            "Clear improvement in spreadsheet confidence.",
            "Sophie Turner",
        ),
        (
            "STU1006",
            "2026-04-07",
            "Introduction to People Practice",
            "Professional Technical Skills",
            "Understand the basics of HR administration, employee support and people processes.",
            None,
            2.5,
            "planned",
            "draft",
            None,
            "Seeded as a newer learner record for a pending student.",
            None,
            None,
        ),
    ]

    rows_to_insert = []

    for (
        student_number,
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
        reviewer_name,
    ) in learning_records:
        student_id = fetch_student_id(connection, student_number)

        rows_to_insert.append(
            (
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
                reviewer_name,
            )
        )

    connection.executemany(
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
        rows_to_insert
    )


def seed_student_exam_results(connection):
    """
    Seed exam results with a more realistic spread of outcomes.

    The aim here is to make the exam tracker actually worth looking at.
    Different students show different stages of progress:
    - mixed results
    - level completion
    - full qualification completion
    - bookings
    - fails
    - not attempted
    """
    student_exam_results = [
        # ========================================================
        # Bob Jones - mixed journey
        # Some passes, one fail, one booking, some untouched
        # ========================================================
        ("STU1001", "FND101", "2026-01-15", "passed", 78, "Strong understanding of core business concepts."),
        ("STU1001", "FND102", "2026-02-10", "passed", 71, "Good awareness of ethics principles. Could improve application depth."),
        ("STU1001", "FND103", "2026-03-05", "failed", 42, "Needs stronger accuracy in financial statement interpretation."),
        ("STU1001", "APP201", "2026-06-20", "booked", None, None),
        ("STU1001", "APP202", None, "not_attempted", None, None),
        ("STU1001", "PRO301", None, "not_attempted", None, None),

        # ========================================================
        # Amy Wilson - Foundation level fully passed
        # Great for showing a whole level complete with green ticks
        # ========================================================
        ("STU1002", "FND101", "2026-01-12", "passed", 74, "Good core understanding shown."),
        ("STU1002", "FND102", "2026-01-28", "passed", 69, "Clear and steady performance."),
        ("STU1002", "FND103", "2026-02-14", "passed", 73, "Strong improvement in financial basics."),
        ("STU1002", "FND104", "2026-03-01", "passed", 76, "Good use of management information principles."),
        ("STU1002", "FND105", "2026-03-18", "passed", 70, "Solid understanding of tax principles."),
        ("STU1002", "FND106", "2026-04-02", "passed", 79, "Very confident with digital and data essentials."),
        ("STU1002", "APP201", None, "not_attempted", None, None),
        ("STU1002", "APP202", None, "not_attempted", None, None),
        ("STU1002", "APP203", None, "not_attempted", None, None),
        ("STU1002", "APP204", None, "not_attempted", None, None),
        ("STU1002", "APP205", None, "not_attempted", None, None),
        ("STU1002", "APP206", None, "not_attempted", None, None),
        ("STU1002", "PRO301", None, "not_attempted", None, None),
        ("STU1002", "PRO302", None, "not_attempted", None, None),
        ("STU1002", "PRO303", None, "not_attempted", None, None),
        ("STU1002", "PRO304", None, "not_attempted", None, None),
        ("STU1002", "PRO305", None, "not_attempted", None, None),
        ("STU1002", "PRO306", None, "not_attempted", None, None),

        # ========================================================
        # Josh Taylor - Foundation and Applied fully passed
        # Strong progressing learner, nearly there
        # ========================================================
        ("STU1003", "FND101", "2025-11-10", "passed", 80, "Excellent grasp of business fundamentals."),
        ("STU1003", "FND102", "2025-11-28", "passed", 77, "Strong ethical understanding."),
        ("STU1003", "FND103", "2025-12-15", "passed", 74, "Accurate and consistent financial knowledge."),
        ("STU1003", "FND104", "2026-01-05", "passed", 79, "Very good use of management information."),
        ("STU1003", "FND105", "2026-01-19", "passed", 75, "Good tax knowledge and application."),
        ("STU1003", "FND106", "2026-02-02", "passed", 81, "Very strong digital confidence."),

        ("STU1003", "APP201", "2026-02-25", "passed", 72, "Good financial reporting ability."),
        ("STU1003", "APP202", "2026-03-10", "passed", 70, "Steady performance in audit principles."),
        ("STU1003", "APP203", "2026-03-24", "passed", 74, "Clear planning and decision-making shown."),
        ("STU1003", "APP204", "2026-04-07", "passed", 76, "Good analytical thinking."),
        ("STU1003", "APP205", "2026-04-21", "passed", 73, "Strong tax compliance understanding."),
        ("STU1003", "APP206", "2026-05-05", "passed", 78, "Very capable with systems and controls."),

        ("STU1003", "PRO301", "2026-06-10", "booked", None, None),
        ("STU1003", "PRO302", None, "not_attempted", None, None),
        ("STU1003", "PRO303", None, "not_attempted", None, None),
        ("STU1003", "PRO304", None, "not_attempted", None, None),
        ("STU1003", "PRO305", None, "not_attempted", None, None),
        ("STU1003", "PRO306", None, "not_attempted", None, None),

        # ========================================================
        # Chloe Bennett - struggling learner
        # Good for showing fails, sat, and not attempted
        # ========================================================
        ("STU1004", "FND101", "2026-01-18", "failed", 38, "Needs stronger core understanding."),
        ("STU1004", "FND102", "2026-02-14", "failed", 39, "Needs more confidence applying ethical principles in context."),
        ("STU1004", "FND103", "2026-03-04", "sat", 51, "Awaiting final moderation and review."),
        ("STU1004", "FND104", None, "not_attempted", None, None),
        ("STU1004", "FND105", None, "not_attempted", None, None),
        ("STU1004", "FND106", None, "not_attempted", None, None),
        ("STU1004", "APP201", None, "not_attempted", None, None),
        ("STU1004", "APP202", None, "not_attempted", None, None),
        ("STU1004", "APP203", None, "not_attempted", None, None),
        ("STU1004", "APP204", None, "not_attempted", None, None),
        ("STU1004", "APP205", None, "not_attempted", None, None),
        ("STU1004", "APP206", None, "not_attempted", None, None),
        ("STU1004", "PRO301", None, "not_attempted", None, None),
        ("STU1004", "PRO302", None, "not_attempted", None, None),
        ("STU1004", "PRO303", None, "not_attempted", None, None),
        ("STU1004", "PRO304", None, "not_attempted", None, None),
        ("STU1004", "PRO305", None, "not_attempted", None, None),
        ("STU1004", "PRO306", None, "not_attempted", None, None),

        # ========================================================
        # Liam Parker - full green tick show-off record
        # Every module passed across all levels
        # Perfect for proving the full completion view works
        # ========================================================
        ("STU1005", "FND101", "2025-09-10", "passed", 82, "Excellent performance."),
        ("STU1005", "FND102", "2025-09-24", "passed", 79, "Very strong ethical awareness."),
        ("STU1005", "FND103", "2025-10-08", "passed", 77, "Accurate and confident work."),
        ("STU1005", "FND104", "2025-10-22", "passed", 80, "Great use of management information."),
        ("STU1005", "FND105", "2025-11-05", "passed", 76, "Strong application of tax principles."),
        ("STU1005", "FND106", "2025-11-19", "passed", 84, "Very strong digital capability."),

        ("STU1005", "APP201", "2025-12-03", "passed", 78, "Strong finance reporting skills demonstrated."),
        ("STU1005", "APP202", "2025-12-17", "passed", 75, "Confident audit and assurance understanding."),
        ("STU1005", "APP203", "2026-01-07", "passed", 77, "Very capable business planning approach."),
        ("STU1005", "APP204", "2026-01-21", "passed", 79, "Solid analytical thinking."),
        ("STU1005", "APP205", "2026-02-04", "passed", 74, "Good compliance understanding."),
        ("STU1005", "APP206", "2026-02-18", "passed", 81, "Excellent systems awareness."),

        ("STU1005", "PRO301", "2026-03-04", "passed", 76, "Strong strategic reporting work."),
        ("STU1005", "PRO302", "2026-03-18", "passed", 73, "Clear assurance knowledge."),
        ("STU1005", "PRO303", "2026-04-01", "passed", 78, "Very capable strategic thinking."),
        ("STU1005", "PRO304", "2026-04-15", "passed", 80, "Excellent leadership judgement."),
        ("STU1005", "PRO305", "2026-04-29", "passed", 77, "Very good governance awareness."),
        ("STU1005", "PRO306", "2026-05-13", "passed", 83, "Excellent use of data and innovation concepts."),

        # ========================================================
        # Emma Carter - brand new learner
        # Mostly untouched tracker, with one booking to show movement
        # ========================================================
        ("STU1006", "FND101", None, "not_attempted", None, None),
        ("STU1006", "FND102", None, "not_attempted", None, None),
        ("STU1006", "FND103", None, "not_attempted", None, None),
        ("STU1006", "FND104", None, "not_attempted", None, None),
        ("STU1006", "FND105", None, "not_attempted", None, None),
        ("STU1006", "FND106", "2026-06-05", "booked", None, None),
        ("STU1006", "APP201", None, "not_attempted", None, None),
        ("STU1006", "APP202", None, "not_attempted", None, None),
        ("STU1006", "APP203", None, "not_attempted", None, None),
        ("STU1006", "APP204", None, "not_attempted", None, None),
        ("STU1006", "APP205", None, "not_attempted", None, None),
        ("STU1006", "APP206", None, "not_attempted", None, None),
        ("STU1006", "PRO301", None, "not_attempted", None, None),
        ("STU1006", "PRO302", None, "not_attempted", None, None),
        ("STU1006", "PRO303", None, "not_attempted", None, None),
        ("STU1006", "PRO304", None, "not_attempted", None, None),
        ("STU1006", "PRO305", None, "not_attempted", None, None),
        ("STU1006", "PRO306", None, "not_attempted", None, None),
    ]

    rows_to_insert = []

    for (
        student_number,
        module_code,
        exam_date,
        result_status,
        score,
        examiner_feedback,
    ) in student_exam_results:
        student_id = fetch_student_id(connection, student_number)
        exam_module_id = fetch_exam_module_id(connection, module_code)

        rows_to_insert.append(
            (
                student_id,
                exam_module_id,
                exam_date,
                result_status,
                score,
                examiner_feedback,
            )
        )

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
        rows_to_insert
    )


if __name__ == "__main__":
    init_database()