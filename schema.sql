-- ============================================================
-- Training Management System - Database Schema
-- ============================================================
-- Author: Andy Caladine
-- Schema Version: v0.3
-- Milestone: Employer Portal Foundations
--
-- Overview:
-- Core database schema for a Flask-based training management system.
-- Designed as a portfolio project but structured to reflect
-- real-world application design and scalability.
--
-- Key Design Principles:
-- - Separation of concerns (auth vs profile data)
-- - Relational integrity and auditability
-- - Real-world workflow modelling (students, employers, training)
--
-- Core Structure:
-- - users = authentication and roles only
-- - students = student profile data
-- - employers = organisation records
-- - employer_contacts = employer portal users
-- - access codes = controlled self-registration
--
-- Notes for future me:
-- Keep this file clean and intentional.
-- If it starts to feel messy, it probably means the data model needs refactoring.
-- ============================================================


-- ============================================================
-- Drop existing tables
-- ============================================================
-- This rebuilds the database from scratch.
-- Tables are dropped in dependency order (children first)
-- to avoid foreign key issues.
-- ============================================================

DROP TABLE IF EXISTS employer_student_assignments;
DROP TABLE IF EXISTS employer_contact_unlock_requests;
DROP TABLE IF EXISTS employer_contacts;
DROP TABLE IF EXISTS employer_allowed_domains;
DROP TABLE IF EXISTS training_agreements;
DROP TABLE IF EXISTS timesheets;
DROP TABLE IF EXISTS learning_records;
DROP TABLE IF EXISTS student_exam_results;
DROP TABLE IF EXISTS periodic_reviews;
DROP TABLE IF EXISTS student_access_codes;
DROP TABLE IF EXISTS employer_access_codes;
DROP TABLE IF EXISTS password_resets;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS employers;
DROP TABLE IF EXISTS exam_modules;
DROP TABLE IF EXISTS users;


-- ============================================================
-- Core login table
-- ============================================================
-- This table is deliberately lean.
-- It stores only what is needed for authentication and role control.
-- Profile-specific data lives elsewhere.
-- ============================================================

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('admin', 'student', 'employer')),
    is_active INT NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- Employer organisations
-- ============================================================
-- This represents the company / organisation itself.
-- It does NOT represent an individual contact person.
--
-- That separation matters because one employer can have:
-- - many contacts
-- - many students
-- - many access codes
-- ============================================================

CREATE TABLE employers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL UNIQUE,
    company_number TEXT,
    primary_domain TEXT,
    is_active INT NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- Student profiles
-- ============================================================
-- Each student links back to one login account in users.
-- employer_id is optional because a student record may exist
-- before being fully tied to an employer, depending on workflow.
-- ============================================================

CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INT NOT NULL UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    student_number TEXT UNIQUE,
    employer_id INT,
    route_name TEXT,
    department TEXT,
    job_title TEXT,
    cohort TEXT,
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


-- ============================================================
-- Password reset tokens
-- ============================================================
-- Standard reset flow table.
-- Tokens should be one-time use and time-limited.
-- ============================================================

CREATE TABLE password_resets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INT NOT NULL,
    token TEXT NOT NULL UNIQUE,
    expires_at TEXT NOT NULL,
    used_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);


-- ============================================================
-- Student self-registration access codes
-- ============================================================
-- These codes are given to students so they can register
-- against the correct employer.
-- ============================================================

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


-- ============================================================
-- Employer self-registration access codes
-- ============================================================
-- These are used by employer contacts to self-register.
-- The code links directly to the employer record.
--
-- is_single_use gives flexibility for future behaviour:
-- - 0 = reusable code
-- - 1 = one-time code
-- ============================================================

CREATE TABLE employer_access_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    employer_id INT NOT NULL,
    is_active INT NOT NULL DEFAULT 1,
    is_single_use INT NOT NULL DEFAULT 0,
    expires_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employer_id) REFERENCES employers(id)
);


-- ============================================================
-- Allowed employer email domains
-- ============================================================
-- Employer contacts must register using a work email address.
-- This table controls which domains are valid for each employer.
--
-- Example:
-- - company.co.uk
-- - group.company.co.uk
--
-- This helps reduce the risk of someone registering with
-- a personal or unrelated email address.
-- ============================================================

CREATE TABLE employer_allowed_domains (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employer_id INT NOT NULL,
    domain_name TEXT NOT NULL,
    is_active INT NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employer_id) REFERENCES employers(id),
    UNIQUE (employer_id, domain_name)
);


-- ============================================================
-- Employer contact profiles
-- ============================================================
-- This is one of the key design tables in the system.
--
-- Why it exists:
-- - employers = companies
-- - employer_contacts = people at those companies
-- - users = login accounts
--
-- This separation makes the employer portal much more realistic.
-- One company can have many contacts, and each contact can have
-- their own login, status, permissions, and student assignments.
-- ============================================================

CREATE TABLE employer_contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INT NOT NULL UNIQUE,
    employer_id INT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    job_title TEXT NOT NULL,
    department TEXT,
    employee_reference TEXT,
    work_email TEXT NOT NULL UNIQUE,
    work_phone TEXT,
    secondary_phone TEXT,
    preferred_contact_method TEXT CHECK (
        preferred_contact_method IN ('email', 'phone')
    ),
    registration_status TEXT NOT NULL DEFAULT 'pending' CHECK (
        registration_status IN ('pending', 'active', 'inactive', 'locked')
    ),
    is_primary_contact INT NOT NULL DEFAULT 0,

    -- GDPR / access review tracking
    gdpr_confirmed_at TEXT,
    gdpr_confirmation_due_at TEXT,

    -- Account activity / lock tracking
    last_login_at TEXT,
    locked_at TEXT,
    lock_reason TEXT CHECK (
        lock_reason IN (
            'gdpr_confirmation_failed',
            'inactive_account',
            'admin_locked',
            'employer_access_revoked'
        )
    ),

    -- Agreement timestamps
    terms_agreed_at TEXT,
    gdpr_agreed_at TEXT,

    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (employer_id) REFERENCES employers(id)
);


-- ============================================================
-- Employer unlock requests
-- ============================================================
-- If an employer contact is locked out, they can request
-- an access review instead of being stuck with no route back in.
--
-- This supports the future flow where:
-- - account gets locked
-- - user sees locked message
-- - user submits request with reason and contact number
-- - admin reviews and decides what happens next
-- ============================================================

CREATE TABLE employer_contact_unlock_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employer_contact_id INT NOT NULL,
    reason TEXT NOT NULL,
    contact_number TEXT NOT NULL,
    request_status TEXT NOT NULL DEFAULT 'pending' CHECK (
        request_status IN ('pending', 'approved', 'rejected')
    ),
    requested_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TEXT,
    reviewed_by_user_id INT,
    admin_notes TEXT,
    FOREIGN KEY (employer_contact_id) REFERENCES employer_contacts(id),
    FOREIGN KEY (reviewed_by_user_id) REFERENCES users(id)
);


-- ============================================================
-- Employer contact to student assignments
-- ============================================================
-- This table links employer contacts to the students they manage.
--
-- Why a separate table?
-- Because one employer contact can manage many students,
-- and one student could potentially be linked to multiple
-- employer contacts if the business rules ever allow it.
--
-- The primary contact flag gives flexibility without forcing
-- the whole relationship into a single field somewhere else.
-- ============================================================

CREATE TABLE employer_student_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employer_contact_id INT NOT NULL,
    student_id INT NOT NULL,
    is_primary_contact INT NOT NULL DEFAULT 0,
    is_active INT NOT NULL DEFAULT 1,
    assigned_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    removed_at TEXT,
    created_by_user_id INT,
    FOREIGN KEY (employer_contact_id) REFERENCES employer_contacts(id),
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (created_by_user_id) REFERENCES users(id),
    UNIQUE (employer_contact_id, student_id)
);


-- ============================================================
-- Training agreements
-- ============================================================
-- This sits between the student and employer relationship
-- and tracks the agreement lifecycle.
-- ============================================================

CREATE TABLE training_agreements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INT NOT NULL,
    employer_id INT NOT NULL,
    agreement_status TEXT NOT NULL DEFAULT 'draft' CHECK (
        agreement_status IN ('draft', 'submitted', 'approved', 'rejected')
    ),
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


-- ============================================================
-- Timesheets
-- ============================================================
-- Stores student timesheet periods and the employer-side review
-- outcome for that submission.
-- ============================================================

CREATE TABLE timesheets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INT NOT NULL,
    agreement_id INT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    total_days INT NOT NULL,
    reviewer_name TEXT,
    approval_status TEXT NOT NULL DEFAULT 'draft' CHECK (
        approval_status IN ('draft', 'submitted', 'approved', 'rejected')
    ),
    employer_comments TEXT,
    approved_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (agreement_id) REFERENCES training_agreements(id)
);


-- ============================================================
-- Learning records
-- ============================================================
-- Tracks formal and informal learning activity completed by students.
-- ============================================================

CREATE TABLE learning_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INT NOT NULL,
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


-- ============================================================
-- Exam modules
-- ============================================================
-- Shared exam module list used across all students.
-- ============================================================

CREATE TABLE exam_modules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    level_name TEXT NOT NULL CHECK (
        level_name IN ('Foundation', 'Applied', 'Professional')
    ),
    module_code TEXT NOT NULL UNIQUE,
    module_name TEXT NOT NULL,
    display_order INT NOT NULL
);


-- ============================================================
-- Student exam results
-- ============================================================
-- One row per student per exam module.
-- The UNIQUE constraint prevents duplicate records for the same
-- module against the same student.
-- ============================================================

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
    UNIQUE (student_id, exam_module_id)
);


-- ============================================================
-- Periodic reviews
-- ============================================================
-- Stores the structured review cycle between student and employer.
-- ============================================================

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