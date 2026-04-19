from flask import Blueprint, render_template, session, redirect, url_for, flash
from utils.db import get_db_connection

employer_bp = Blueprint("employer", __name__, url_prefix="/employer")


@employer_bp.route("/dashboard")
def employer_dashboard():
    """
    Employer dashboard.

    Displays:
    - Grouped carded summary panels
    - list of students linked to this employer
    """

    if "user_id" not in session:
        flash("Please log in to access this page.", "error")
        return redirect(url_for("login"))

    if session.get("role") != "employer":
        flash("Access denied.", "error")
        return redirect(url_for("home"))

    user_id = session["user_id"]

    conn = get_db_connection()

    try:
        employer_row = conn.execute(
            """
            SELECT employer_id
            FROM employer_contacts
            WHERE user_id = ?
            """,
            (user_id,)
        ).fetchone()

        if not employer_row:
            flash("Employer account not linked correctly.", "error")
            return redirect(url_for("home"))

        employer_id = employer_row["employer_id"]

        students = conn.execute(
            """
            SELECT
                s.id,
                s.first_name,
                s.last_name,
                s.student_number,
                s.cohort,
                s.registration_status
            FROM students s
            JOIN training_agreements ta
                ON s.id = ta.student_id
            WHERE ta.employer_id = ?
            ORDER BY s.last_name ASC, s.first_name ASC
            """,
            (employer_id,)
        ).fetchall()

        total_students = len(students)
        active_students = len(
            [s for s in students if (s["registration_status"] or "").lower() == "active"]
        )
        
        stats = {
            "total_students": total_students,
            "active_students": active_students,
            "pending_approval": 0,
            "pending_sign_off": 0,
            "pending_timesheets": 0,
            "pending_learning_records": 0,
            "pending_reviews": 0,
            "pending_agreements": 0,
            "foundation_completed": 0,
            "applied_completed": 0,
            "professional_completed": 0,
            "fully_qualified": 0,
            "overdue_timesheets": 0,
            "no_learning_6_months": 0,
            "overdue_reviews": 0,
            "no_exams_6_months": 0,
        }

    finally:
        conn.close()

    return render_template(
        "employer_dashboard.html",
        students=students,
        stats=stats
    )