DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS employers;
DROP TABLE IF EXISTS training_agreements;
DROP TABLE IF EXISTS timesheets;
DROP TABLE IF EXISTS learning_records;
DROP TABLE IF EXISTS exam_modules;
DROP TABLE IF EXISTS student_exam_results;
DROP TABLE IF EXISTS periodic_reviews;
DROP TABLE IF EXISTS student_access_codes;
DROP TABLE IF EXISTS employer_access_codes;
DROP TABLE IF EXISTS password_resets;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'student', 'employer')),
    is_active INT NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP 
);

CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INT NOT NULL UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    student_number TEXT UNIQUE,
    employer_id INT,
    route_name TEXT,
    phone TEXT,
    date_of_birth TEXT,
    address_line_1 TEXT,
    address_line_2 TEXT,
    town_city TEXT,
    county TEXT,
    postcode TEXT,
    registration_status TEXT NOT NULL DEFAULT 'pending' CHECK (
        registration_status IN ('pending', 'active', 'inactive')
    ),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, 
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (employer_id) REFERENCES employers(id)
);

CREATE TABLE employers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INT UNIQUE,
    company_name TEXT NOT NULL,
    contact_name TEXT,
    contact_email TEXT, 
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) 
);

CREATE TABLE password_resets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INT NOT NULL,
    token TEXT NOT NULL UNIQUE,
    expires_at TEXT NOT NULL,
    used_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE student_access_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    employer_id INT NOT NULL,
    is_active INT NOT NULL DEFAULT 1,
    expires_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employer_id) REFERENCES employers(id)
);

CREATE TABLE employer_access_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    company_name TEXT NOT NULL,
    is_active INT NOT NULL DEFAULT 1,
    expires_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE training_agreements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INT NOT NULL,
    employer_id INT NOT NULL,
    agreement_status TEXT NOT NULL DEFAULT 'draft' CHECK(agreement_status IN ('draft', 'submitted', 'approved', 'rejected')),
    start_date TEXT,
    end_date TEXT,
    duration_years INTEGER NOT NULL DEFAULT 0,
    duration_months INTEGER NOT NULL DEFAULT 0,
    duration_days INTEGER NOT NULL DEFAULT 0,
    signed_by_student INT NOT NULL DEFAULT 0,
    signed_by_employer INT NOT NULL DEFAULT 0,
    student_signed_at TEXT,
    employer_signed_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (employer_id) REFERENCES employers(id)
);


CREATE TABLE timesheets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INT NOT NULL,
    agreement_id INT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    total_days INT NOT NULL,
    reviewer_name TEXT,
    approval_status TEXT NOT NULL DEFAULT 'draft' CHECK(approval_status IN ('draft', 'submitted', 'approved', 'rejected')),
    employer_comments TEXT,
    approved_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (agreement_id) REFERENCES training_agreements(id) 
);

CREATE TABLE learning_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    date_started TEXT NOT NULL,
    course_title TEXT NOT NULL,
    training_category TEXT NOT NULL CHECK (
        training_category IN (
            'Personal Development',
            'Professional Soft Skills',
            'Professional Technical Skills'
        )
    ),
    learning_outcomes TEXT NOT NULL,
    date_completed TEXT,
    hours_spent REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'planned' CHECK (
        status IN ('planned', 'in_progress', 'completed')
    ),
    review_status TEXT NOT NULL DEFAULT 'draft' CHECK (
        review_status IN ('draft', 'submitted', 'approved', 'rejected')
    ),
    certification_expiry_date TEXT,
    notes TEXT,
    employer_feedback TEXT,
    reviewer_name TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id)
);

CREATE TABLE exam_modules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    level_name TEXT NOT NULL CHECK(level_name IN ('Foundation', 'Applied', 'Professional')),
    module_code TEXT NOT NULL UNIQUE,
    module_name TEXT NOT NULL,
    display_order INT NOT NULL
);

CREATE TABLE student_exam_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INT NOT NULL,
    exam_module_id INT NOT NULL,
    exam_date TEXT,
    result_status TEXT NOT NULL DEFAULT 'not_attempted' CHECK (
        result_status IN ('not_attempted', 'booked', 'sat', 'passed', 'failed')
    ),
    score REAL,
    examiner_feedback TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (exam_module_id) REFERENCES exam_modules(id),
    UNIQUE(student_id, exam_module_id)
);

CREATE TABLE periodic_reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INT NOT NULL,
    employer_id INT NOT NULL,
    review_start_date TEXT NOT NULL,
    review_end_date TEXT NOT NULL,
    student_reflection TEXT,
    achievements_last_period TEXT,
    challenges_last_period TEXT,
    goals_next_period TEXT,
    support_needed TEXT,
    employer_feedback TEXT,
    employer_name TEXT,
    review_status TEXT NOT NULL DEFAULT 'draft' CHECK (
        review_status IN ('draft', 'submitted', 'approved', 'rejected')
    ),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (employer_id) REFERENCES employers(id)
);

