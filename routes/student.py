from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, make_response
from weasyprint import HTML

from utils.db import get_db_connection

student_bp = Blueprint("student", __name__)

#Helper function for reviewer
def get_primary_reviewer(conn, employer_id):
    if not employer_id:
        return None

    return conn.execute(
        """
        SELECT *
        FROM employer_contacts
        WHERE employer_id = ?
        AND is_primary_contact = 1
        AND registration_status = 'active'
        LIMIT 1
        """,
        (employer_id,)
    ).fetchone()


def get_reviewer_full_name(reviewer):
    if not reviewer:
        return ""

    first_name = (reviewer["first_name"] or "").strip()
    last_name = (reviewer["last_name"] or "").strip()
    return f"{first_name} {last_name}".strip()

#Student logic to maintan the student application dashboard. 
@student_bp.route("/student")
def student_dashboard():
    if "user_id" not in session or session.get("role") != "student":
        return redirect(url_for("login"))

    conn = get_db_connection()

    student = conn.execute(
        "SELECT * FROM students WHERE user_id = ?",
        (session["user_id"],)
    ).fetchone()

    agreement = None
    employer = None
    reviewer = None
    timesheets = []
    learning_records = []
    exam_results = []
    periodic_reviews = []

    approved_days = 0
    draft_days = 0
    rejected_days = 0
    total_counted_days = 0

    learning_approved_hours = 0
    learning_draft_submitted_hours = 0
    learning_rejected_hours = 0
    learning_total_counted_hours = 0

    foundation_passed = 0
    applied_passed = 0
    professional_passed = 0
    total_passed = 0

    timesheet_draft_count = 0
    timesheet_submitted_count = 0
    timesheet_approved_count = 0
    timesheet_rejected_count = 0

    learning_draft_count = 0
    learning_submitted_count = 0
    learning_approved_count = 0
    learning_rejected_count = 0

    foundation_total = 0
    applied_total = 0
    professional_total = 0

    review_draft_count = 0
    review_submitted_count = 0
    review_approved_count = 0
    review_rejected_count = 0

    if student:
        agreement = conn.execute(
            "SELECT * FROM training_agreements WHERE student_id = ?",
            (student["id"],)
        ).fetchone()

        if student["employer_id"]:
            employer = conn.execute(
                "SELECT * FROM employers WHERE id = ?",
                (student["employer_id"],)
            ).fetchone()

            reviewer = get_primary_reviewer(conn, student["employer_id"])

        timesheets = conn.execute(
            """
            SELECT * FROM timesheets
            WHERE student_id = ?
            ORDER BY start_date DESC
            """,
            (student["id"],)
        ).fetchall()

        for ts in timesheets:
            days = ts["total_days"] or 0
            status = ts["approval_status"]

            if status == "approved":
                approved_days += days
                total_counted_days += days
                timesheet_approved_count += 1
            elif status == "draft":
                draft_days += days
                total_counted_days += days
                timesheet_draft_count += 1
            elif status == "submitted":
                draft_days += days
                total_counted_days += days
                timesheet_submitted_count += 1
            elif status == "rejected":
                rejected_days += days
                timesheet_rejected_count += 1

        learning_records = conn.execute(
            """
            SELECT * FROM learning_records
            WHERE student_id = ?
            ORDER BY date_started DESC
            """,
            (student["id"],)
        ).fetchall()

        for record in learning_records:
            hours = record["hours_spent"] or 0
            review_status = record["review_status"]

            if review_status == "approved":
                learning_approved_hours += hours
                learning_total_counted_hours += hours
                learning_approved_count += 1
            elif review_status == "draft":
                learning_draft_submitted_hours += hours
                learning_total_counted_hours += hours
                learning_draft_count += 1
            elif review_status == "submitted":
                learning_draft_submitted_hours += hours
                learning_total_counted_hours += hours
                learning_submitted_count += 1
            elif review_status == "rejected":
                learning_rejected_hours += hours
                learning_rejected_count += 1

        exam_results = conn.execute(
            """
            SELECT
                ser.id,
                em.level_name,
                em.module_code,
                em.module_name,
                em.display_order,
                ser.exam_date,
                ser.result_status,
                ser.score,
                ser.examiner_feedback
            FROM student_exam_results ser
            JOIN exam_modules em
                ON ser.exam_module_id = em.id
            WHERE ser.student_id = ?
            ORDER BY
                CASE em.level_name
                    WHEN 'Foundation' THEN 1
                    WHEN 'Applied' THEN 2
                    WHEN 'Professional' THEN 3
                    ELSE 4
                END,
                em.display_order
            """,
            (student["id"],)
        ).fetchall()

        for exam in exam_results:
            if exam["level_name"] == "Foundation":
                foundation_total += 1
            elif exam["level_name"] == "Applied":
                applied_total += 1
            elif exam["level_name"] == "Professional":
                professional_total += 1

            if exam["result_status"] == "passed":
                total_passed += 1

                if exam["level_name"] == "Foundation":
                    foundation_passed += 1
                elif exam["level_name"] == "Applied":
                    applied_passed += 1
                elif exam["level_name"] == "Professional":
                    professional_passed += 1

        periodic_reviews = conn.execute(
            """
            SELECT * FROM periodic_reviews
            WHERE student_id = ?
            ORDER BY review_start_date DESC
            """,
            (student["id"],)
        ).fetchall()

        for review in periodic_reviews:
            status = review["review_status"]

            if status == "draft":
                review_draft_count += 1
            elif status == "submitted":
                review_submitted_count += 1
            elif status == "approved":
                review_approved_count += 1
            elif status == "rejected":
                review_rejected_count += 1

    conn.close()

    return render_template(
        "student_dashboard.html",
        student=student,
        agreement=agreement,
        employer=employer,
        reviewer=reviewer,
        timesheets=timesheets,
        learning_records=learning_records,
        exam_results=exam_results,
        periodic_reviews=periodic_reviews,
        approved_days=approved_days,
        draft_days=draft_days,
        rejected_days=rejected_days,
        total_counted_days=total_counted_days,
        learning_approved_hours=learning_approved_hours,
        learning_draft_submitted_hours=learning_draft_submitted_hours,
        learning_rejected_hours=learning_rejected_hours,
        learning_total_counted_hours=learning_total_counted_hours,
        foundation_passed=foundation_passed,
        applied_passed=applied_passed,
        professional_passed=professional_passed,
        total_passed=total_passed,
        timesheet_draft_count=timesheet_draft_count,
        timesheet_submitted_count=timesheet_submitted_count,
        timesheet_approved_count=timesheet_approved_count,
        timesheet_rejected_count=timesheet_rejected_count,
        learning_draft_count=learning_draft_count,
        learning_submitted_count=learning_submitted_count,
        learning_approved_count=learning_approved_count,
        learning_rejected_count=learning_rejected_count,
        foundation_total=foundation_total,
        applied_total=applied_total,
        professional_total=professional_total,
        review_draft_count=review_draft_count,
        review_submitted_count=review_submitted_count,
        review_approved_count=review_approved_count,
        review_rejected_count=review_rejected_count
    )

#Function for the time tracker helper for timesheets
@student_bp.route("/student/time-tracker")
def time_tracker():
    if "user_id" not in session or session.get("role") != "student":
        return redirect(url_for("login"))

    conn = get_db_connection()

    student = conn.execute(
        "SELECT * FROM students WHERE user_id = ?",
        (session["user_id"],)
    ).fetchone()

    if not student:
        conn.close()
        flash("No student profile found.", "error")
        return redirect(url_for("student.student_dashboard"))

    employer = None
    reviewer = None

    if student["employer_id"]:
        employer = conn.execute(
            "SELECT * FROM employers WHERE id = ?",
            (student["employer_id"],)
        ).fetchone()

        reviewer = get_primary_reviewer(conn, student["employer_id"])

    tracker_entries = conn.execute(
        """
        SELECT *
        FROM time_tracker_entries
        WHERE student_id = ?
        AND timesheet_id IS NULL
        ORDER BY entry_date DESC, id DESC
        """,
        (student["id"],)
    ).fetchall()

    conn.close()

    return render_template(
        "time_tracker.html",
        student=student,
        employer=employer,
        reviewer=reviewer,
        tracker_entries=tracker_entries
    )

@student_bp.route("/student/time-tracker/add", methods=["POST"])
def add_time_tracker_entry():
    if "user_id" not in session or session.get("role") != "student":
        return redirect(url_for("login"))

    entry_date = request.form["entry_date"]
    hours = request.form["hours"]
    description = request.form.get("description", "").strip()

    conn = get_db_connection()

    student = conn.execute(
        "SELECT * FROM students WHERE user_id = ?",
        (session["user_id"],)
    ).fetchone()

    if not student:
        conn.close()
        flash("No student profile found.", "error")
        return redirect(url_for("student.student_dashboard"))

    try:
        hours_value = float(hours)
        if hours_value <= 0:
            raise ValueError
    except ValueError:
        conn.close()
        flash("Hours must be greater than 0.", "error")
        return redirect(url_for("student.time_tracker"))

    conn.execute(
        """
        INSERT INTO time_tracker_entries (
            student_id, entry_date, hours, description
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            student["id"],
            entry_date,
            hours_value,
            description or None
        )
    )

    conn.commit()
    conn.close()

    flash("Time entry added.", "success")
    return redirect(url_for("student.time_tracker"))

#Convert function to change timesheet entries 
@student_bp.route("/student/time-tracker/convert", methods=["POST"])
def convert_time_tracker():
    if "user_id" not in session or session.get("role") != "student":
        return redirect(url_for("login"))

    selected_ids = request.form.getlist("selected_entries")
    reviewer_name = request.form.get("reviewer_name", "").strip()

    if not selected_ids:
        flash("Please select at least one tracker entry.", "error")
        return redirect(url_for("student.time_tracker"))

    if not reviewer_name:
        flash("Please choose a reviewer.", "error")
        return redirect(url_for("student.time_tracker"))

    conn = get_db_connection()

    student = conn.execute(
        "SELECT * FROM students WHERE user_id = ?",
        (session["user_id"],)
    ).fetchone()

    if not student:
        conn.close()
        flash("No student profile found.", "error")
        return redirect(url_for("student.student_dashboard"))

    agreement = conn.execute(
        "SELECT * FROM training_agreements WHERE student_id = ?",
        (student["id"],)
    ).fetchone()

    if not agreement:
        conn.close()
        flash("No training agreement found.", "error")
        return redirect(url_for("student.student_dashboard"))

    employer = None
    reviewer = None

    if student["employer_id"]:
        employer = conn.execute(
            "SELECT * FROM employers WHERE id = ?",
            (student["employer_id"],)
        ).fetchone()

        reviewer = get_primary_reviewer(conn, student["employer_id"])

    if not employer:
        conn.close()
        flash("No linked employer found.", "error")
        return redirect(url_for("student.time_tracker"))

    if not reviewer:
        conn.close()
        flash("No active primary reviewer found for your employer.", "error")
        return redirect(url_for("student.time_tracker"))

    allowed_reviewer = get_reviewer_full_name(reviewer)

    if reviewer_name != allowed_reviewer:
        conn.close()
        flash("You can only convert to your linked employer reviewer.", "error")
        return redirect(url_for("student.time_tracker"))

    placeholders = ",".join("?" for _ in selected_ids)

    tracker_entries = conn.execute(
        f"""
        SELECT *
        FROM time_tracker_entries
        WHERE id IN ({placeholders})
        AND student_id = ?
        AND timesheet_id IS NULL
        ORDER BY entry_date ASC, id ASC
        """,
        (*selected_ids, student["id"])
    ).fetchall()

    if not tracker_entries:
        conn.close()
        flash("No valid tracker entries were found.", "error")
        return redirect(url_for("student.time_tracker"))

    last_timesheet = conn.execute(
        """
        SELECT * FROM timesheets
        WHERE student_id = ?
        ORDER BY end_date DESC
        LIMIT 1
        """,
        (student["id"],)
    ).fetchone()

    if last_timesheet:
        default_start_date = (
            datetime.strptime(last_timesheet["end_date"], "%Y-%m-%d") + timedelta(days=1)
        ).strftime("%Y-%m-%d")
    else:
        default_start_date = agreement["start_date"]

    start_date = default_start_date
    end_date = tracker_entries[-1]["entry_date"]

    total_hours = sum((entry["hours"] or 0) for entry in tracker_entries)
    total_days = round(total_hours / 7, 2)

    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")

    if end_dt < start_dt:
        conn.close()
        flash("Selected tracker entries end before the next allowed timesheet start date.", "error")
        return redirect(url_for("student.time_tracker"))

    if end_dt > start_dt + timedelta(days=183):
        conn.close()
        flash("Your timesheet entry cannot be more than 6 months.", "error")
        return redirect(url_for("student.time_tracker"))

    agreement_start = datetime.strptime(agreement["start_date"], "%Y-%m-%d")
    agreement_end = datetime.strptime(agreement["end_date"], "%Y-%m-%d")

    if start_dt < agreement_start or end_dt > agreement_end:
        conn.close()
        flash("Timesheet dates must be within your agreement dates.", "error")
        return redirect(url_for("student.time_tracker"))

    overlapping = conn.execute(
        """
        SELECT * FROM timesheets
        WHERE student_id = ?
        AND NOT (
            end_date < ? OR start_date > ?
        )
        """,
        (student["id"], start_date, end_date)
    ).fetchone()

    if overlapping:
        conn.close()
        flash("Your entry overlaps an existing timesheet entry.", "error")
        return redirect(url_for("student.time_tracker"))

    cursor = conn.execute(
        """
        INSERT INTO timesheets (
            student_id, agreement_id, start_date, end_date, total_days, reviewer_name
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            student["id"],
            agreement["id"],
            start_date,
            end_date,
            total_days,
            reviewer_name
        )
    )

    timesheet_id = cursor.lastrowid

    valid_ids = [entry["id"] for entry in tracker_entries]
    valid_placeholders = ",".join("?" for _ in valid_ids)

    conn.execute(
        f"""
        UPDATE time_tracker_entries
        SET timesheet_id = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id IN ({valid_placeholders})
        AND student_id = ?
        """,
        (timesheet_id, *valid_ids, student["id"])
    )

    conn.commit()
    conn.close()

    flash("Tracker entries converted into a timesheet successfully.", "success")
    return redirect(url_for("student.student_dashboard"))

#Function for the Timesheet Add
@student_bp.route("/student/timesheets/add", methods=["GET", "POST"])
def add_timesheet():
    if "user_id" not in session or session.get("role") != "student":
        return redirect(url_for("login"))

    conn = get_db_connection()

    student = conn.execute(
        "SELECT * FROM students WHERE user_id = ?",
        (session["user_id"],)
    ).fetchone()

    if not student:
        conn.close()
        flash("No student profile found.", "error")
        return redirect(url_for("student.student_dashboard"))

    agreement = conn.execute(
        "SELECT * FROM training_agreements WHERE student_id = ?",
        (student["id"],)
    ).fetchone()

    if not agreement:
        conn.close()
        flash("No training agreement found.", "error")
        return redirect(url_for("student.student_dashboard"))

    last_timesheet = conn.execute(
        """
        SELECT * FROM timesheets
        WHERE student_id = ?
        ORDER BY end_date DESC
        LIMIT 1
        """,
        (student["id"],)
    ).fetchone()

    if last_timesheet:
        default_start_date = (
            datetime.strptime(last_timesheet["end_date"], "%Y-%m-%d") + timedelta(days=1)
        ).strftime("%Y-%m-%d")
    else:
        default_start_date = agreement["start_date"]

    if request.method == "POST":
        start_date = default_start_date
        end_date = request.form["end_date"]
        total_days = request.form["total_days"]
        reviewer_name = request.form["reviewer_name"]

        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        if end_dt < start_dt:
            conn.close()
            return render_template(
                "add_timesheet.html",
                student=student,
                agreement=agreement,
                default_start_date=default_start_date,
                error="End date cannot be before the start date.",
                error_field="end_date",
                form_data=request.form
            )

        if end_dt > start_dt + timedelta(days=183):
            conn.close()
            return render_template(
                "add_timesheet.html",
                student=student,
                agreement=agreement,
                default_start_date=default_start_date,
                error="Your timesheet entry cannot be more than 6 months.",
                error_field="end_date",
                form_data=request.form
            )

        agreement_start = datetime.strptime(agreement["start_date"], "%Y-%m-%d")
        agreement_end = datetime.strptime(agreement["end_date"], "%Y-%m-%d")

        if start_dt < agreement_start or end_dt > agreement_end:
            conn.close()
            return render_template(
                "add_timesheet.html",
                student=student,
                agreement=agreement,
                default_start_date=default_start_date,
                error="Timesheet dates must be within your agreement dates.",
                error_field="end_date",
                form_data=request.form
            )

        overlapping = conn.execute(
            """
            SELECT * FROM timesheets
            WHERE student_id = ?
            AND NOT (
                end_date < ? OR start_date > ?
            )
            """,
            (student["id"], start_date, end_date)
        ).fetchone()

        if overlapping:
            conn.close()
            return render_template(
                "add_timesheet.html",
                student=student,
                agreement=agreement,
                default_start_date=default_start_date,
                error="Your entry overlaps an existing timesheet entry.",
                error_field="end_date",
                form_data=request.form
            )

        conn.execute(
            """
            INSERT INTO timesheets (
                student_id, agreement_id, start_date, end_date, total_days, reviewer_name
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                student["id"],
                agreement["id"],
                start_date,
                end_date,
                total_days,
                reviewer_name
            )
        )
        conn.commit()
        conn.close()

        flash("Timesheet added successfully.", "success")
        return redirect(url_for("student.student_dashboard"))

    conn.close()
    return render_template(
        "add_timesheet.html",
        student=student,
        agreement=agreement,
        default_start_date=default_start_date,
        error=None,
        error_field=None,
        form_data=None
    )


@student_bp.route("/student/timesheets/<int:timesheet_id>/edit", methods=["GET", "POST"])
def edit_timesheet(timesheet_id):
    if "user_id" not in session or session.get("role") != "student":
        return redirect(url_for("login"))

    conn = get_db_connection()

    student = conn.execute(
        "SELECT * FROM students WHERE user_id = ?",
        (session["user_id"],)
    ).fetchone()

    if not student:
        conn.close()
        flash("No student profile found.", "error")
        return redirect(url_for("student.student_dashboard"))

    agreement = conn.execute(
        "SELECT * FROM training_agreements WHERE student_id = ?",
        (student["id"],)
    ).fetchone()

    timesheet = conn.execute(
        """
        SELECT * FROM timesheets
        WHERE id = ? AND student_id = ?
        """,
        (timesheet_id, student["id"])
    ).fetchone()

    if not timesheet:
        conn.close()
        flash("Timesheet not found.", "error")
        return redirect(url_for("student.student_dashboard"))

    if timesheet["approval_status"] == "approved":
        conn.close()
        flash("Approved timesheets cannot be edited.", "error")
        return redirect(url_for("student.student_dashboard"))

    if request.method == "POST":
        end_date = request.form["end_date"]
        total_days = request.form["total_days"]
        reviewer_name = request.form["reviewer_name"]

        start_date = timesheet["start_date"]

        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        if end_dt < start_dt:
            conn.close()
            return render_template(
                "edit_timesheet.html",
                timesheet=timesheet,
                agreement=agreement,
                error="End date cannot be before the start date.",
                error_field="end_date",
                form_data=request.form
            )

        if end_dt > start_dt + timedelta(days=183):
            conn.close()
            return render_template(
                "edit_timesheet.html",
                timesheet=timesheet,
                agreement=agreement,
                error="Your timesheet entry cannot be more than 6 months.",
                error_field="end_date",
                form_data=request.form
            )

        agreement_start = datetime.strptime(agreement["start_date"], "%Y-%m-%d")
        agreement_end = datetime.strptime(agreement["end_date"], "%Y-%m-%d")

        if start_dt < agreement_start or end_dt > agreement_end:
            conn.close()
            return render_template(
                "edit_timesheet.html",
                timesheet=timesheet,
                agreement=agreement,
                error="Timesheet dates must be within your agreement dates.",
                error_field="end_date",
                form_data=request.form
            )

        overlapping = conn.execute(
            """
            SELECT * FROM timesheets
            WHERE student_id = ?
            AND id != ?
            AND NOT (
                end_date < ? OR start_date > ?
            )
            """,
            (student["id"], timesheet["id"], start_date, end_date)
        ).fetchone()

        if overlapping:
            conn.close()
            return render_template(
                "edit_timesheet.html",
                timesheet=timesheet,
                agreement=agreement,
                error="Your entry overlaps an existing timesheet entry.",
                error_field="end_date",
                form_data=request.form
            )

        conn.execute(
            """
            UPDATE timesheets
            SET end_date = ?, total_days = ?, reviewer_name = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (end_date, total_days, reviewer_name, timesheet["id"])
        )
        conn.commit()
        conn.close()

        flash("Timesheet updated successfully.", "success")
        return redirect(url_for("student.student_dashboard"))

    conn.close()
    return render_template(
        "edit_timesheet.html",
        timesheet=timesheet,
        agreement=agreement,
        error=None,
        error_field=None,
        form_data=None
    )


@student_bp.route("/student/submit-agreement", methods=["POST"])
def submit_agreement():
    if "user_id" not in session or session.get("role") != "student":
        return redirect(url_for("login"))

    conn = get_db_connection()

    student = conn.execute(
        "SELECT * FROM students WHERE user_id = ?",
        (session["user_id"],)
    ).fetchone()

    if student:
        conn.execute(
            """
            UPDATE training_agreements
            SET signed_by_student = 1,
                agreement_status = 'submitted',
                updated_at = CURRENT_TIMESTAMP
            WHERE student_id = ?
            """,
            (student["id"],)
        )
        conn.commit()
        flash("Training agreement submitted successfully.", "success")

    conn.close()
    return redirect(url_for("student.student_dashboard"))


@student_bp.route("/student/timesheets/submit", methods=["POST"])
def submit_timesheets():
    if "user_id" not in session or session.get("role") != "student":
        return redirect(url_for("login"))

    selected_ids = request.form.getlist("selected_timesheets")
    reviewer_name = request.form.get("reviewer_name", "").strip()

    if not selected_ids:
        flash("Please select at least one draft timesheet.", "error")
        return redirect(url_for("student.student_dashboard"))

    if not reviewer_name:
        flash("Please choose a reviewer.", "error")
        return redirect(url_for("student.student_dashboard"))

    conn = get_db_connection()

    student = conn.execute(
        "SELECT * FROM students WHERE user_id = ?",
        (session["user_id"],)
    ).fetchone()

    if not student:
        conn.close()
        flash("No student profile found.", "error")
        return redirect(url_for("student.student_dashboard"))

        employer = None
        reviewer = None

        if student["employer_id"]:
            employer = conn.execute(
                "SELECT * FROM employers WHERE id = ?",
                (student["employer_id"],)
            ).fetchone()

            reviewer = get_primary_reviewer(conn, student["employer_id"])

        if not employer:
            conn.close()
            flash("No linked employer found.", "error")
            return redirect(url_for("student.student_dashboard"))

        if not reviewer:
            conn.close()
            flash("No active primary reviewer found for your employer.", "error")
            return redirect(url_for("student.student_dashboard"))

        allowed_reviewer = get_reviewer_full_name(reviewer)

    if reviewer_name != allowed_reviewer:
        conn.close()
        flash("You can only submit to your linked employer reviewer.", "error")
        return redirect(url_for("student.student_dashboard"))

    placeholders = ",".join("?" for _ in selected_ids)

    rows = conn.execute(
        f"""
        SELECT * FROM timesheets
        WHERE id IN ({placeholders})
        AND student_id = ?
        """,
        (*selected_ids, student["id"])
    ).fetchall()

    if not rows:
        conn.close()
        flash("No valid timesheets were found.", "error")
        return redirect(url_for("student.student_dashboard"))

    valid_ids = [str(row["id"]) for row in rows if row["approval_status"] == "draft"]

    if not valid_ids:
        conn.close()
        flash("Only draft timesheets can be submitted.", "error")
        return redirect(url_for("student.student_dashboard"))

    valid_placeholders = ",".join("?" for _ in valid_ids)

    conn.execute(
        f"""
        UPDATE timesheets
        SET approval_status = 'submitted',
            reviewer_name = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id IN ({valid_placeholders})
        AND student_id = ?
        AND approval_status = 'draft'
        """,
        (reviewer_name, *valid_ids, student["id"])
    )

    conn.commit()
    conn.close()

    flash("Selected timesheets submitted for review.", "success")
    return redirect(url_for("student.student_dashboard"))


@student_bp.route("/student/learning/add", methods=["GET", "POST"])
def add_learning_record():
    if "user_id" not in session or session.get("role") != "student":
        return redirect(url_for("login"))

    conn = get_db_connection()

    student = conn.execute(
        "SELECT * FROM students WHERE user_id = ?",
        (session["user_id"],)
    ).fetchone()

    if not student:
        conn.close()
        flash("No student profile found.", "error")
        return redirect(url_for("student.student_dashboard"))

    if request.method == "POST":
        date_started = request.form["date_started"]
        course_title = request.form["course_title"].strip()
        training_category = request.form["training_category"]
        learning_outcomes = request.form["learning_outcomes"].strip()
        date_completed = request.form["date_completed"].strip()
        hours_spent = request.form["hours_spent"].strip()
        status = request.form["status"]
        certification_expiry_date = request.form["certification_expiry_date"].strip()
        notes = request.form["notes"].strip()

        if not date_started:
            conn.close()
            return render_template(
                "add_learning_record.html",
                error="Please enter a start date.",
                error_field="date_started",
                form_data=request.form
            )

        if not course_title:
            conn.close()
            return render_template(
                "add_learning_record.html",
                error="Please enter a course title.",
                error_field="course_title",
                form_data=request.form
            )

        if len(learning_outcomes) < 50:
            conn.close()
            return render_template(
                "add_learning_record.html",
                error="Learning outcomes should be meaningful.",
                error_field="learning_outcomes",
                form_data=request.form
            )

        try:
            hours_value = float(hours_spent)
            if hours_value <= 0:
                raise ValueError
        except ValueError:
            conn.close()
            return render_template(
                "add_learning_record.html",
                error="Hours must be greater than 0.",
                error_field="hours_spent",
                form_data=request.form
            )

        if date_completed:
            try:
                start_dt = datetime.strptime(date_started, "%Y-%m-%d")
                end_dt = datetime.strptime(date_completed, "%Y-%m-%d")

                if end_dt < start_dt:
                    conn.close()
                    return render_template(
                        "add_learning_record.html",
                        error="Completed date cannot be before start date.",
                        error_field="date_completed",
                        form_data=request.form
                    )
            except ValueError:
                pass

        conn.execute(
            """
            INSERT INTO learning_records (
                student_id, date_started, course_title, training_category,
                learning_outcomes, date_completed, hours_spent,
                status, review_status, certification_expiry_date,
                notes, employer_feedback, reviewer_name
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                student["id"],
                date_started,
                course_title,
                training_category,
                learning_outcomes,
                date_completed or None,
                hours_value,
                status,
                "draft",
                certification_expiry_date or None,
                notes or None,
                None,
                None
            )
        )

        conn.commit()
        conn.close()

        flash("Learning record added successfully.", "success")
        return redirect(url_for("student.student_dashboard"))

    conn.close()
    return render_template(
        "add_learning_record.html",
        error=None,
        error_field=None,
        form_data=None
    )


@student_bp.route("/student/learning/<int:record_id>/edit", methods=["GET", "POST"])
def edit_learning_record(record_id):
    if "user_id" not in session or session.get("role") != "student":
        return redirect(url_for("login"))

    conn = get_db_connection()

    student = conn.execute(
        "SELECT * FROM students WHERE user_id = ?",
        (session["user_id"],)
    ).fetchone()

    if not student:
        conn.close()
        flash("No student profile found.", "error")
        return redirect(url_for("student.student_dashboard"))

    record = conn.execute(
        """
        SELECT * FROM learning_records
        WHERE id = ? AND student_id = ?
        """,
        (record_id, student["id"])
    ).fetchone()

    if not record:
        conn.close()
        flash("Learning record not found.", "error")
        return redirect(url_for("student.student_dashboard"))

    if record["review_status"] not in ["draft", "rejected"]:
        conn.close()
        flash("This learning record is view only.", "error")
        return redirect(url_for("student.view_learning_record", record_id=record["id"]))

    if request.method == "POST":
        date_started = request.form["date_started"]
        course_title = request.form["course_title"].strip()
        training_category = request.form["training_category"]
        learning_outcomes = request.form["learning_outcomes"].strip()
        date_completed = request.form["date_completed"].strip()
        hours_spent = request.form["hours_spent"].strip()
        status = request.form["status"]
        certification_expiry_date = request.form["certification_expiry_date"].strip()
        notes = request.form["notes"].strip()

        if not date_started:
            conn.close()
            return render_template(
                "edit_learning_record.html",
                record=record,
                error="Please enter a start date.",
                error_field="date_started",
                form_data=request.form
            )

        if not course_title:
            conn.close()
            return render_template(
                "edit_learning_record.html",
                record=record,
                error="Please enter a course title.",
                error_field="course_title",
                form_data=request.form
            )

        allowed_categories = [
            "Personal Development",
            "Professional Soft Skills",
            "Professional Technical Skills"
        ]

        if training_category not in allowed_categories:
            conn.close()
            return render_template(
                "edit_learning_record.html",
                record=record,
                error="Please select a valid training category.",
                error_field="training_category",
                form_data=request.form
            )

        if len(learning_outcomes) < 20:
            conn.close()
            return render_template(
                "edit_learning_record.html",
                record=record,
                error="Learning outcomes should be specific and meaningful.",
                error_field="learning_outcomes",
                form_data=request.form
            )

        try:
            hours_value = float(hours_spent)
            if hours_value <= 0:
                raise ValueError
        except ValueError:
            conn.close()
            return render_template(
                "edit_learning_record.html",
                record=record,
                error="Hours spent must be a number greater than 0.",
                error_field="hours_spent",
                form_data=request.form
            )

        if date_completed:
            try:
                started_dt = datetime.strptime(date_started, "%Y-%m-%d")
                completed_dt = datetime.strptime(date_completed, "%Y-%m-%d")

                if completed_dt < started_dt:
                    conn.close()
                    return render_template(
                        "edit_learning_record.html",
                        record=record,
                        error="Date completed cannot be before the start date.",
                        error_field="date_completed",
                        form_data=request.form
                    )
            except ValueError:
                conn.close()
                return render_template(
                    "edit_learning_record.html",
                    record=record,
                    error="Please enter valid dates.",
                    error_field="date_completed",
                    form_data=request.form
                )

        conn.execute(
            """
            UPDATE learning_records
            SET date_started = ?,
                course_title = ?,
                training_category = ?,
                learning_outcomes = ?,
                date_completed = ?,
                hours_spent = ?,
                status = ?,
                certification_expiry_date = ?,
                notes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND student_id = ?
            """,
            (
                date_started,
                course_title,
                training_category,
                learning_outcomes,
                date_completed or None,
                hours_value,
                status,
                certification_expiry_date or None,
                notes or None,
                record["id"],
                student["id"]
            )
        )

        conn.commit()
        conn.close()

        flash("Learning record updated successfully.", "success")
        return redirect(url_for("student.student_dashboard"))

    conn.close()
    return render_template(
        "edit_learning_record.html",
        record=record,
        error=None,
        error_field=None,
        form_data=None
    )


@student_bp.route("/student/learning/<int:record_id>")
def view_learning_record(record_id):
    if "user_id" not in session or session.get("role") != "student":
        return redirect(url_for("login"))

    conn = get_db_connection()

    student = conn.execute(
        "SELECT * FROM students WHERE user_id = ?",
        (session["user_id"],)
    ).fetchone()

    if not student:
        conn.close()
        flash("No student profile found.", "error")
        return redirect(url_for("student.student_dashboard"))

    record = conn.execute(
        """
        SELECT * FROM learning_records
        WHERE id = ? AND student_id = ?
        """,
        (record_id, student["id"])
    ).fetchone()

    conn.close()

    if not record:
        flash("Learning record not found.", "error")
        return redirect(url_for("student.student_dashboard"))

    return render_template("view_learning_record.html", record=record)


@student_bp.route("/student/learning/submit", methods=["POST"])
def submit_learning_records():
    if "user_id" not in session or session.get("role") != "student":
        return redirect(url_for("login"))

    selected_ids = request.form.getlist("selected_learning_records")
    reviewer_name = request.form.get("reviewer_name", "").strip()

    if not selected_ids:
        flash("Please select at least one draft learning record.", "error")
        return redirect(url_for("student.student_dashboard"))

    if not reviewer_name:
        flash("Please choose a reviewer.", "error")
        return redirect(url_for("student.student_dashboard"))

    conn = get_db_connection()

    student = conn.execute(
        "SELECT * FROM students WHERE user_id = ?",
        (session["user_id"],)
    ).fetchone()

    if not student:
        conn.close()
        flash("No student profile found.", "error")
        return redirect(url_for("student.student_dashboard"))

    employer = None
    reviewer = None

    if student["employer_id"]:
        employer = conn.execute(
            "SELECT * FROM employers WHERE id = ?",
            (student["employer_id"],)
        ).fetchone()

        reviewer = get_primary_reviewer(conn, student["employer_id"])

    if not employer:
        conn.close()
        flash("No linked employer found.", "error")
        return redirect(url_for("student.student_dashboard"))

    if not reviewer:
        conn.close()
        flash("No active primary reviewer found for your employer.", "error")
        return redirect(url_for("student.student_dashboard"))

    allowed_reviewer = get_reviewer_full_name(reviewer)

    if reviewer_name != allowed_reviewer:
        conn.close()
        flash("You can only submit to your linked employer reviewer.", "error")
        return redirect(url_for("student.student_dashboard"))

    placeholders = ",".join("?" for _ in selected_ids)

    rows = conn.execute(
        f"""
        SELECT * FROM learning_records
        WHERE id IN ({placeholders})
        AND student_id = ?
        """,
        (*selected_ids, student["id"])
    ).fetchall()

    if not rows:
        conn.close()
        flash("No valid learning records were found.", "error")
        return redirect(url_for("student.student_dashboard"))

    valid_ids = [str(row["id"]) for row in rows if row["review_status"] == "draft"]

    if not valid_ids:
        conn.close()
        flash("Only draft learning records can be submitted.", "error")
        return redirect(url_for("student.student_dashboard"))

    valid_placeholders = ",".join("?" for _ in valid_ids)

    conn.execute(
        f"""
        UPDATE learning_records
        SET review_status = 'submitted',
            reviewer_name = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id IN ({valid_placeholders})
        AND student_id = ?
        AND review_status = 'draft'
        """,
        (reviewer_name, *valid_ids, student["id"])
    )

    conn.commit()
    conn.close()

    flash("Selected learning records submitted for review.", "success")
    return redirect(url_for("student.student_dashboard"))


@student_bp.route("/student/exams/<int:result_id>")
def view_exam_result(result_id):
    if "user_id" not in session or session.get("role") != "student":
        return redirect(url_for("login"))

    conn = get_db_connection()

    student = conn.execute(
        "SELECT * FROM students WHERE user_id = ?",
        (session["user_id"],)
    ).fetchone()

    if not student:
        conn.close()
        flash("No student profile found.", "error")
        return redirect(url_for("student.student_dashboard"))

    exam = conn.execute(
        """
        SELECT
            ser.id,
            em.level_name,
            em.module_code,
            em.module_name,
            ser.exam_date,
            ser.result_status,
            ser.score,
            ser.examiner_feedback
        FROM student_exam_results ser
        JOIN exam_modules em
            ON ser.exam_module_id = em.id
        WHERE ser.id = ? AND ser.student_id = ?
        """,
        (result_id, student["id"])
    ).fetchone()

    conn.close()

    if not exam:
        flash("Exam result not found.", "error")
        return redirect(url_for("student.student_dashboard"))

    return render_template("view_exam_result.html", exam=exam)


@student_bp.route("/student/reviews/add", methods=["GET", "POST"])
def add_periodic_review():
    if "user_id" not in session or session.get("role") != "student":
        return redirect(url_for("login"))

    conn = get_db_connection()

    student = conn.execute(
        "SELECT * FROM students WHERE user_id = ?",
        (session["user_id"],)
    ).fetchone()

    if not student:
        conn.close()
        flash("No student profile found.", "error")
        return redirect(url_for("student.student_dashboard"))

    agreement = conn.execute(
        "SELECT * FROM training_agreements WHERE student_id = ?",
        (student["id"],)
    ).fetchone()

    if not agreement:
        conn.close()
        flash("No training agreement found.", "error")
        return redirect(url_for("student.student_dashboard"))

    employer = None
    reviewer = None

    if student["employer_id"]:
        employer = conn.execute(
            "SELECT * FROM employers WHERE id = ?",
            (student["employer_id"],)
        ).fetchone()

    reviewer = get_primary_reviewer(conn, student["employer_id"])

    last_review = conn.execute(
        """
        SELECT * FROM periodic_reviews
        WHERE student_id = ?
        ORDER BY review_end_date DESC
        LIMIT 1
        """,
        (student["id"],)
    ).fetchone()

    agreement_start = datetime.strptime(agreement["start_date"], "%Y-%m-%d")
    agreement_end = datetime.strptime(agreement["end_date"], "%Y-%m-%d")

    if last_review:
        default_start_dt = datetime.strptime(last_review["review_end_date"], "%Y-%m-%d") + timedelta(days=1)
    else:
        default_start_dt = agreement_start

    default_end_dt = default_start_dt + relativedelta(months=6) - timedelta(days=1)

    if default_end_dt > agreement_end:
        default_end_dt = agreement_end

    default_start_date = default_start_dt.strftime("%Y-%m-%d")
    default_end_date = default_end_dt.strftime("%Y-%m-%d")

    review_timesheets = conn.execute(
        """
        SELECT *
        FROM timesheets
        WHERE student_id = ?
        AND NOT (
            end_date < ? OR start_date > ?
        )
        ORDER BY start_date DESC
        """,
        (student["id"], default_start_date, default_end_date)
    ).fetchall()

    review_learning_records = conn.execute(
        """
        SELECT *
        FROM learning_records
        WHERE student_id = ?
        AND (
            (date_started BETWEEN ? AND ?)
            OR
            (date_completed IS NOT NULL AND date_completed BETWEEN ? AND ?)
        )
        ORDER BY date_started DESC
        """,
        (
            student["id"],
            default_start_date,
            default_end_date,
            default_start_date,
            default_end_date
        )
    ).fetchall()

    review_exams = conn.execute(
        """
        SELECT
            ser.id,
            em.level_name,
            em.module_code,
            em.module_name,
            ser.exam_date,
            ser.result_status,
            ser.score
        FROM student_exam_results ser
        JOIN exam_modules em
            ON ser.exam_module_id = em.id
        WHERE ser.student_id = ?
        AND ser.exam_date IS NOT NULL
        AND ser.exam_date BETWEEN ? AND ?
        ORDER BY ser.exam_date DESC
        """,
        (student["id"], default_start_date, default_end_date)
    ).fetchall()

    review_timesheet_days = 0
    review_learning_hours = 0
    review_exams_passed = 0
    review_pending_items = 0

    for ts in review_timesheets:
        review_timesheet_days += ts["total_days"] or 0
        if ts["approval_status"] in ("draft", "submitted"):
            review_pending_items += 1

    for record in review_learning_records:
        review_learning_hours += record["hours_spent"] or 0
        if record["review_status"] in ("draft", "submitted"):
            review_pending_items += 1

    for exam in review_exams:
        if exam["result_status"] == "passed":
            review_exams_passed += 1

    if request.method == "POST":
        review_start_date = default_start_date
        review_end_date = default_end_date
        student_reflection = request.form["student_reflection"].strip()
        achievements_last_period = request.form["achievements_last_period"].strip()
        challenges_last_period = request.form["challenges_last_period"].strip()
        goals_next_period = request.form["goals_next_period"].strip()
        support_needed = request.form["support_needed"].strip()

        review_fields = {
            "student_reflection": student_reflection,
            "achievements_last_period": achievements_last_period,
            "challenges_last_period": challenges_last_period,
            "goals_next_period": goals_next_period,
            "support_needed": support_needed,
        }

        field_labels = {
            "student_reflection": "Student reflection",
            "achievements_last_period": "Achievements in the last 6 months",
            "challenges_last_period": "Challenges in the last 6 months",
            "goals_next_period": "Goals for the next 6 months",
            "support_needed": "Support needed",
        }

        for field_name, field_value in review_fields.items():
            if len(field_value) < 50:
                conn.close()
                return render_template(
                    "add_periodic_review.html",
                    agreement=agreement,
                    employer=employer,
                    default_start_date=default_start_date,
                    default_end_date=default_end_date,
                    review_timesheets=review_timesheets,
                    review_learning_records=review_learning_records,
                    review_exams=review_exams,
                    review_timesheet_days=review_timesheet_days,
                    review_learning_hours=review_learning_hours,
                    review_exams_passed=review_exams_passed,
                    review_pending_items=review_pending_items,
                    error=f"{field_labels[field_name]} should be at least 50 characters.",
                    error_field=field_name,
                    form_data=request.form
                )

        conn.execute(
            """
            INSERT INTO periodic_reviews (
                student_id,
                employer_id,
                review_start_date,
                review_end_date,
                student_reflection,
                achievements_last_period,
                challenges_last_period,
                goals_next_period,
                support_needed,
                employer_name,
                review_status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                student["id"],
                student["employer_id"],
                review_start_date,
                review_end_date,
                student_reflection,
                achievements_last_period or None,
                challenges_last_period or None,
                goals_next_period or None,
                support_needed or None,
                get_reviewer_full_name(reviewer) if reviewer else None,
                "draft"
            )
        )

        conn.commit()
        conn.close()

        flash("Periodic review added successfully.", "success")
        return redirect(url_for("student.student_dashboard"))

    conn.close()
    return render_template(
        "add_periodic_review.html",
        agreement=agreement,
        employer=employer,
        default_start_date=default_start_date,
        default_end_date=default_end_date,
        review_timesheets=review_timesheets,
        review_learning_records=review_learning_records,
        review_exams=review_exams,
        review_timesheet_days=review_timesheet_days,
        review_learning_hours=review_learning_hours,
        review_exams_passed=review_exams_passed,
        review_pending_items=review_pending_items,
        error=None,
        error_field=None,
        form_data=None
    )


@student_bp.route("/student/reviews/<int:review_id>/edit", methods=["GET", "POST"])
def edit_periodic_review(review_id):
    if "user_id" not in session or session.get("role") != "student":
        return redirect(url_for("login"))

    conn = get_db_connection()

    student = conn.execute(
        "SELECT * FROM students WHERE user_id = ?",
        (session["user_id"],)
    ).fetchone()

    if not student:
        conn.close()
        flash("No student profile found.", "error")
        return redirect(url_for("student.student_dashboard"))

    review = conn.execute(
        """
        SELECT * FROM periodic_reviews
        WHERE id = ? AND student_id = ?
        """,
        (review_id, student["id"])
    ).fetchone()

    if not review:
        conn.close()
        flash("Periodic review not found.", "error")
        return redirect(url_for("student.student_dashboard"))

    if review["review_status"] not in ["draft", "rejected"]:
        conn.close()
        flash("This periodic review is view only.", "error")
        return redirect(url_for("student.view_periodic_review", review_id=review["id"]))

    review_start_date = review["review_start_date"]
    review_end_date = review["review_end_date"]

    review_timesheets = conn.execute(
        """
        SELECT *
        FROM timesheets
        WHERE student_id = ?
        AND NOT (
            end_date < ? OR start_date > ?
        )
        ORDER BY start_date DESC
        """,
        (student["id"], review_start_date, review_end_date)
    ).fetchall()

    review_learning_records = conn.execute(
        """
        SELECT *
        FROM learning_records
        WHERE student_id = ?
        AND (
            (date_started BETWEEN ? AND ?)
            OR
            (date_completed IS NOT NULL AND date_completed BETWEEN ? AND ?)
        )
        ORDER BY date_started DESC
        """,
        (
            student["id"],
            review_start_date,
            review_end_date,
            review_start_date,
            review_end_date
        )
    ).fetchall()

    review_exams = conn.execute(
        """
        SELECT
            ser.id,
            em.level_name,
            em.module_code,
            em.module_name,
            ser.exam_date,
            ser.result_status,
            ser.score
        FROM student_exam_results ser
        JOIN exam_modules em
            ON ser.exam_module_id = em.id
        WHERE ser.student_id = ?
        AND ser.exam_date IS NOT NULL
        AND ser.exam_date BETWEEN ? AND ?
        ORDER BY ser.exam_date DESC
        """,
        (student["id"], review_start_date, review_end_date)
    ).fetchall()

    review_timesheet_days = 0
    review_learning_hours = 0
    review_exams_passed = 0
    review_pending_items = 0

    for ts in review_timesheets:
        review_timesheet_days += ts["total_days"] or 0
        if ts["approval_status"] in ("draft", "submitted"):
            review_pending_items += 1

    for record in review_learning_records:
        review_learning_hours += record["hours_spent"] or 0
        if record["review_status"] in ("draft", "submitted"):
            review_pending_items += 1

    for exam in review_exams:
        if exam["result_status"] == "passed":
            review_exams_passed += 1

    if request.method == "POST":
        student_reflection = request.form["student_reflection"].strip()
        achievements_last_period = request.form["achievements_last_period"].strip()
        challenges_last_period = request.form["challenges_last_period"].strip()
        goals_next_period = request.form["goals_next_period"].strip()
        support_needed = request.form["support_needed"].strip()

        review_fields = {
            "student_reflection": student_reflection,
            "achievements_last_period": achievements_last_period,
            "challenges_last_period": challenges_last_period,
            "goals_next_period": goals_next_period,
            "support_needed": support_needed,
        }

        field_labels = {
            "student_reflection": "Student reflection",
            "achievements_last_period": "Achievements in the last 6 months",
            "challenges_last_period": "Challenges in the last 6 months",
            "goals_next_period": "Goals for the next 6 months",
            "support_needed": "Support needed",
        }

        for field_name, field_value in review_fields.items():
            if len(field_value) < 50:
                conn.close()
                return render_template(
                    "edit_periodic_review.html",
                    review=review,
                    review_timesheets=review_timesheets,
                    review_learning_records=review_learning_records,
                    review_exams=review_exams,
                    review_timesheet_days=review_timesheet_days,
                    review_learning_hours=review_learning_hours,
                    review_exams_passed=review_exams_passed,
                    review_pending_items=review_pending_items,
                    error=f"{field_labels[field_name]} should be at least 50 characters.",
                    error_field=field_name,
                    form_data=request.form
                )

        conn.execute(
            """
            UPDATE periodic_reviews
            SET student_reflection = ?,
                achievements_last_period = ?,
                challenges_last_period = ?,
                goals_next_period = ?,
                support_needed = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND student_id = ?
            """,
            (
                student_reflection,
                achievements_last_period or None,
                challenges_last_period or None,
                goals_next_period or None,
                support_needed or None,
                review["id"],
                student["id"]
            )
        )

        conn.commit()
        conn.close()

        flash("Periodic review updated successfully.", "success")
        return redirect(url_for("student.student_dashboard"))

    conn.close()
    return render_template(
        "edit_periodic_review.html",
        review=review,
        review_timesheets=review_timesheets,
        review_learning_records=review_learning_records,
        review_exams=review_exams,
        review_timesheet_days=review_timesheet_days,
        review_learning_hours=review_learning_hours,
        review_exams_passed=review_exams_passed,
        review_pending_items=review_pending_items,
        error=None,
        error_field=None,
        form_data=None
    )


@student_bp.route("/student/reviews/<int:review_id>")
def view_periodic_review(review_id):
    if "user_id" not in session or session.get("role") != "student":
        return redirect(url_for("login"))

    conn = get_db_connection()

    student = conn.execute(
        "SELECT * FROM students WHERE user_id = ?",
        (session["user_id"],)
    ).fetchone()

    if not student:
        conn.close()
        flash("No student profile found.", "error")
        return redirect(url_for("student.student_dashboard"))

    review = conn.execute(
        """
        SELECT * FROM periodic_reviews
        WHERE id = ? AND student_id = ?
        """,
        (review_id, student["id"])
    ).fetchone()

    conn.close()

    if not review:
        flash("Periodic review not found.", "error")
        return redirect(url_for("student.student_dashboard"))

    return render_template("view_periodic_review.html", review=review)


@student_bp.route("/student/reviews/submit", methods=["POST"])
def submit_periodic_reviews():
    if "user_id" not in session or session.get("role") != "student":
        return redirect(url_for("login"))

    selected_ids = request.form.getlist("selected_periodic_reviews")
    reviewer_name = request.form.get("reviewer_name", "").strip()

    if not selected_ids:
        flash("Please select at least one draft periodic review.", "error")
        return redirect(url_for("student.student_dashboard"))

    if not reviewer_name:
        flash("Please choose a reviewer.", "error")
        return redirect(url_for("student.student_dashboard"))

    conn = get_db_connection()

    student = conn.execute(
        "SELECT * FROM students WHERE user_id = ?",
        (session["user_id"],)
    ).fetchone()

    if not student:
        conn.close()
        flash("No student profile found.", "error")
        return redirect(url_for("student.student_dashboard"))

    employer = None
    reviewer = None

    if student["employer_id"]:
        employer = conn.execute(
            "SELECT * FROM employers WHERE id = ?",
            (student["employer_id"],)
        ).fetchone()

        reviewer = get_primary_reviewer(conn, student["employer_id"])

    if not employer:
        conn.close()
        flash("No linked employer found.", "error")
        return redirect(url_for("student.student_dashboard"))

    if not reviewer:
        conn.close()
        flash("No active primary reviewer found for your employer.", "error")
        return redirect(url_for("student.student_dashboard"))

    allowed_reviewer = get_reviewer_full_name(reviewer)

    if reviewer_name != allowed_reviewer:
        conn.close()
        flash("You can only submit to your linked employer reviewer.", "error")
        return redirect(url_for("student.student_dashboard"))

    placeholders = ",".join("?" for _ in selected_ids)

    rows = conn.execute(
        f"""
        SELECT * FROM periodic_reviews
        WHERE id IN ({placeholders})
        AND student_id = ?
        """,
        (*selected_ids, student["id"])
    ).fetchall()

    if not rows:
        conn.close()
        flash("No valid periodic reviews were found.", "error")
        return redirect(url_for("student.student_dashboard"))

    valid_ids = [str(row["id"]) for row in rows if row["review_status"] == "draft"]

    if not valid_ids:
        conn.close()
        flash("Only draft periodic reviews can be submitted.", "error")
        return redirect(url_for("student.student_dashboard"))

    valid_placeholders = ",".join("?" for _ in valid_ids)

    conn.execute(
        f"""
        UPDATE periodic_reviews
        SET review_status = 'submitted',
            employer_name = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id IN ({valid_placeholders})
        AND student_id = ?
        AND review_status = 'draft'
        """,
        (reviewer_name, *valid_ids, student["id"])
    )

    conn.commit()
    conn.close()

    flash("Selected periodic reviews submitted for review.", "success")
    return redirect(url_for("student.student_dashboard"))


@student_bp.route("/student/export")
def student_export_options():
    if "user_id" not in session or session.get("role") != "student":
        return redirect(url_for("login"))

    return render_template("student_export_options.html")


@student_bp.route("/student/export/pdf", methods=["POST"])
def export_student_pdf():
    if "user_id" not in session or session.get("role") != "student":
        return redirect(url_for("login"))

    selected_sections = request.form.getlist("sections")

    if not selected_sections:
        flash("Please select at least one section to export.", "error")
        return redirect(url_for("student.student_export_options"))

    conn = get_db_connection()

    student = conn.execute(
        "SELECT * FROM students WHERE user_id = ?",
        (session["user_id"],)
    ).fetchone()

    if not student:
        conn.close()
        flash("No student profile found.", "error")
        return redirect(url_for("student.student_dashboard"))

    agreement = conn.execute(
        "SELECT * FROM training_agreements WHERE student_id = ?",
        (student["id"],)
    ).fetchone()

    employer = None
    if student["employer_id"]:
        employer = conn.execute(
            "SELECT * FROM employers WHERE id = ?",
            (student["employer_id"],)
        ).fetchone()

    timesheets = []
    learning_records = []
    exam_results = []
    periodic_reviews = []

    if "timesheets" in selected_sections:
        timesheets = conn.execute(
            """
            SELECT * FROM timesheets
            WHERE student_id = ?
            ORDER BY start_date DESC
            """,
            (student["id"],)
        ).fetchall()

    if "learning" in selected_sections:
        learning_records = conn.execute(
            """
            SELECT * FROM learning_records
            WHERE student_id = ?
            ORDER BY date_started DESC
            """,
            (student["id"],)
        ).fetchall()

    if "exams" in selected_sections:
        exam_results = conn.execute(
            """
            SELECT
                ser.id,
                em.level_name,
                em.module_code,
                em.module_name,
                em.display_order,
                ser.exam_date,
                ser.result_status,
                ser.score,
                ser.examiner_feedback
            FROM student_exam_results ser
            JOIN exam_modules em
                ON ser.exam_module_id = em.id
            WHERE ser.student_id = ?
            ORDER BY
                CASE em.level_name
                    WHEN 'Foundation' THEN 1
                    WHEN 'Applied' THEN 2
                    WHEN 'Professional' THEN 3
                    ELSE 4
                END,
                em.display_order
            """,
            (student["id"],)
        ).fetchall()

    if "reviews" in selected_sections:
        periodic_reviews = conn.execute(
            """
            SELECT * FROM periodic_reviews
            WHERE student_id = ?
            ORDER BY review_start_date DESC
            """,
            (student["id"],)
        ).fetchall()

    conn.close()

    rendered = render_template(
        "student_export_pdf.html",
        student=student,
        agreement=agreement,
        employer=employer,
        selected_sections=selected_sections,
        timesheets=timesheets,
        learning_records=learning_records,
        exam_results=exam_results,
        periodic_reviews=periodic_reviews,
        generated_at=datetime.now().strftime("%d %B %Y %H:%M")
    )

    pdf = HTML(string=rendered, base_url=request.url_root).write_pdf()

    filename = f"{student['first_name']}_{student['last_name']}_training_export.pdf".replace(" ", "_")

    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response

