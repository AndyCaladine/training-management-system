from datetime import datetime, timedelta

from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import generate_password_hash

from utils.db import get_db_connection
from utils.helpers import generate_student_number
from utils.demo_addresses import DEMO_ADDRESSES


registration_bp = Blueprint("registration", __name__)


@registration_bp.route("/register")
def register():
    return render_template("registration_dashboard.html")


@registration_bp.route("/register/student", methods=["GET", "POST"])
def register_student():
    if request.method == "POST":
        access_code = request.form.get("access_code", "").strip()
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        date_of_birth = request.form.get("date_of_birth", "").strip()
        postcode = request.form.get("postcode", "").strip()
        address_select = request.form.get("address_select", "").strip()
        address_line_1 = request.form.get("address_line_1", "").strip()
        address_line_2 = request.form.get("address_line_2", "").strip()
        town_city = request.form.get("town_city", "").strip()
        county = request.form.get("county", "").strip()
        country = request.form.get("country", "").strip() or "United Kingdom"
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        route_name = request.form.get("route_name", "").strip()
        department = request.form.get("department", "").strip()
        job_title = request.form.get("job_title", "").strip()
        start_date = request.form.get("start_date", "").strip()
        terms_agreed = request.form.get("terms_agreed")
        gdpr_agreed = request.form.get("gdpr_agreed")

        try:
            duration_years = int(request.form.get("years", 0) or 0)
        except ValueError:
            duration_years = 0

        try:
            duration_months = int(request.form.get("months", 0) or 0)
        except ValueError:
            duration_months = 0

        try:
            duration_days = int(request.form.get("days", 0) or 0)
        except ValueError:
            duration_days = 0

        errors = []
        conn = get_db_connection()

        try:
            access_row = conn.execute(
                """
                SELECT
                    sac.id,
                    sac.code,
                    sac.is_active,
                    sac.expires_at,
                    sac.employer_id,
                    e.company_name
                FROM student_access_codes sac
                JOIN employers e ON sac.employer_id = e.id
                WHERE sac.code = ?
                """,
                (access_code,),
            ).fetchone()

            if not access_code:
                errors.append("Access code is required.")
            elif not access_row:
                errors.append("Access code not recognised.")
            elif int(access_row["is_active"]) != 1:
                errors.append("This access code is inactive.")

            if not first_name:
                errors.append("First name is required.")

            if not last_name:
                errors.append("Last name is required.")

            if not email:
                errors.append("Email address is required.")

            if not password:
                errors.append("Password is required.")

            if not confirm_password:
                errors.append("Please confirm your password.")

            if not start_date:
                errors.append("Agreement start date is required.")

            if not route_name:
                errors.append("Training route is required.")

            if password and len(password) < 8:
                errors.append("Password must be at least 8 characters long.")

            if password and not any(char.islower() for char in password):
                errors.append("Password must include at least one lowercase letter.")

            if password and not any(char.isupper() for char in password):
                errors.append("Password must include at least one uppercase letter.")

            if password and not any(char.isdigit() for char in password):
                errors.append("Password must include at least one number.")

            if password and not any(not char.isalnum() for char in password):
                errors.append("Password must include at least one special character.")

            if password and confirm_password and password != confirm_password:
                errors.append("Password and confirm password do not match.")

            if duration_years < 0 or duration_months < 0 or duration_days < 0:
                errors.append("Agreement duration cannot contain negative values.")

            if duration_months > 11:
                errors.append("Months cannot be greater than 11.")

            if duration_days > 31:
                errors.append("Days cannot be greater than 31.")

            if duration_years == 0 and duration_months == 0 and duration_days == 0:
                errors.append("Agreement duration must be greater than zero.")

            if not terms_agreed:
                errors.append("You must agree to the Terms & Conditions.")

            if not gdpr_agreed:
                errors.append("You must confirm the Student Data Notice.")

            if date_of_birth:
                try:
                    datetime.strptime(date_of_birth, "%Y-%m-%d")
                except ValueError:
                    errors.append("Date of birth is not valid.")

            start_date_obj = None
            if start_date:
                try:
                    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
                except ValueError:
                    errors.append("Agreement start date is not valid.")

            cohort = None
            if start_date_obj:
                cohort = start_date_obj.strftime("%b %Y Cohort")

            existing_user = None
            if email:
                existing_user = conn.execute(
                    "SELECT id FROM users WHERE email = ?",
                    (email,),
                ).fetchone()

                if existing_user:
                    errors.append("An account already exists for that email address.")

            end_date = None
            if start_date_obj and not errors:
                end_date_obj = start_date_obj.replace(
                    year=start_date_obj.year + duration_years
                )

                month = end_date_obj.month - 1 + duration_months
                year = end_date_obj.year + month // 12
                month = month % 12 + 1
                day = min(end_date_obj.day, 28)

                end_date_obj = end_date_obj.replace(
                    year=year,
                    month=month,
                    day=day,
                )

                end_date_obj = end_date_obj + timedelta(days=duration_days)
                end_date = end_date_obj.strftime("%Y-%m-%d")

            if errors:
                form_data = request.form.to_dict()

                for error in errors:
                    flash(error, "error")

                return render_template("register_student.html", form_data=form_data)

            employer_id = access_row["employer_id"]
            password_hash = generate_password_hash(password)
            student_number = generate_student_number(conn)

            user_cursor = conn.execute(
                """
                INSERT INTO users (email, password, role, is_active)
                VALUES (?, ?, ?, ?)
                """,
                (email, password_hash, "student", 1),
            )
            user_id = user_cursor.lastrowid

            student_cursor = conn.execute(
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
                (
                    user_id,
                    first_name,
                    last_name,
                    student_number,
                    employer_id,
                    route_name,
                    department or None,
                    job_title or None,
                    cohort,
                    phone or None,
                    date_of_birth or None,
                    address_line_1 or None,
                    address_line_2 or None,
                    town_city or None,
                    county or None,
                    postcode or None,
                    "active",
                ),
            )
            student_id = student_cursor.lastrowid

            signed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            conn.execute(
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
                    start_date,
                    end_date,
                    duration_years,
                    duration_months,
                    duration_days,
                    1,
                    0,
                    signed_at,
                    None,
                ),
            )

            conn.commit()

            session["user_id"] = user_id
            session["email"] = email
            session["role"] = "student"
            session["user_name"] = first_name

            flash("Account created successfully.", "success")
            return redirect(url_for("student.student_dashboard"))

        finally:
            conn.close()

    return render_template("register_student.html")


@registration_bp.route("/register/student/access-code-lookup", methods=["POST"])
def student_access_code_lookup():
    data = request.get_json(silent=True) or {}
    access_code = (data.get("access_code") or "").strip()

    if not access_code:
        return jsonify(
            {
                "valid": False,
                "message": "Please enter an access code.",
            }
        ), 400

    conn = get_db_connection()

    try:
        code_row = conn.execute(
            """
            SELECT
                sac.id,
                sac.code,
                sac.is_active,
                sac.expires_at,
                sac.employer_id,
                e.company_name
            FROM student_access_codes sac
            JOIN employers e ON sac.employer_id = e.id
            WHERE sac.code = ?
            """,
            (access_code,),
        ).fetchone()
    finally:
        conn.close()

    if not code_row:
        return jsonify(
            {
                "valid": False,
                "message": "Access code not recognised.",
            }
        ), 404

    if int(code_row["is_active"]) != 1:
        return jsonify(
            {
                "valid": False,
                "message": "This access code is inactive.",
            }
        ), 400

    return jsonify(
        {
            "valid": True,
            "employer_name": code_row["company_name"],
            "message": "Access code accepted.",
        }
    )


@registration_bp.route("/register/student/address-lookup", methods=["POST"])
def student_address_lookup():
    data = request.get_json(silent=True) or {}
    postcode = (data.get("postcode") or "").strip().upper()

    if not postcode:
        return jsonify({
            "success": False,
            "message": "Please enter a postcode."
        }), 400

    normalised_postcode = " ".join(postcode.split())

    matching_addresses = [
        address for address in DEMO_ADDRESSES
        if address["postcode"].upper() == normalised_postcode
    ]

    if not matching_addresses:
        return jsonify({
            "success": False,
            "message": "No demo addresses found for that postcode. Please use the demo postcode list or enter your address manually."
        }), 404

    formatted_addresses = []
    for address in matching_addresses:
        label_parts = [
            address.get("address_line_1", "").strip(),
            address.get("address_line_2", "").strip(),
            address.get("town_city", "").strip(),
            address.get("county", "").strip(),
            address.get("postcode", "").strip(),
        ]
        label = ", ".join(part for part in label_parts if part)

        formatted_addresses.append({
            "label": label,
            "address_line_1": address.get("address_line_1", "").strip(),
            "address_line_2": address.get("address_line_2", "").strip(),
            "town_city": address.get("town_city", "").strip(),
            "county": address.get("county", "").strip(),
            "postcode": address.get("postcode", "").strip(),
        })

    return jsonify({
        "success": True,
        "message": f"{len(formatted_addresses)} demo address(es) found.",
        "addresses": formatted_addresses
    })


@registration_bp.route("/register/demo-postcodes")
def demo_postcodes():
    sorted_addresses = sorted(DEMO_ADDRESSES, key=lambda x: x["postcode"])
    return render_template("demo_postcodes.html", addresses=sorted_addresses)


@registration_bp.route("/register/demo-access-codes")
def demo_access_codes():
    conn = get_db_connection()

    try:
        student_codes = conn.execute(
            """
            SELECT
                sac.code,
                sac.is_active,
                sac.expires_at,
                sac.created_at,
                sac.updated_at,
                e.company_name
            FROM student_access_codes sac
            JOIN employers e ON sac.employer_id = e.id
            ORDER BY sac.created_at DESC, sac.code ASC
            """
        ).fetchall()

        employer_codes = conn.execute(
            """
            SELECT
                code,
                company_name,
                is_active,
                expires_at,
                created_at,
                updated_at
            FROM employer_access_codes
            ORDER BY created_at DESC, code ASC
            """
        ).fetchall()
    finally:
        conn.close()

    return render_template(
        "demo_access_codes.html",
        student_codes=student_codes,
        employer_codes=employer_codes
    )


@registration_bp.route("/register/employer", methods=["GET", "POST"])
def register_employer():
    return render_template("register_employer.html")