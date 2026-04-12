from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from utils.security import generate_reset_token, get_reset_expiry
from config import Config
from utils.db import get_db_connection
from routes.student import student_bp
from routes.admin import admin_bp
from routes.employer import employer_bp
from routes.registration import registration_bp


app = Flask(__name__)
app.config.from_object(Config)


@app.template_filter("format_date")
def format_date(value):
    if not value:
        return ""
    try:
        return datetime.strptime(value, "%Y-%m-%d").strftime("%d %B %Y")
    except:
        return value


app.register_blueprint(student_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(employer_bp)
app.register_blueprint(registration_bp)


@app.route("/")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))

    role = session.get("role")

    if role == "admin":
        return redirect(url_for("admin.admin_dashboard"))
    elif role == "student":
        return redirect(url_for("student.student_dashboard"))
    elif role == "employer":
        return redirect(url_for("employer.employer_dashboard"))

    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute(
            """
            SELECT
                u.*,
                s.first_name AS student_first_name,
                ec.first_name AS employer_first_name,
                ec.last_name AS employer_last_name,
                e.company_name AS employer_company_name
            FROM users u
            LEFT JOIN students s
                ON u.id = s.user_id
            LEFT JOIN employer_contacts ec
                ON u.id = ec.user_id
            LEFT JOIN employers e
                ON ec.employer_id = e.id
            WHERE u.email = ? AND u.is_active = 1
            """,
            (email,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["email"] = user["email"]
            session["role"] = user["role"]

            session["user_name"] = (
                user["student_first_name"]
                or user["employer_first_name"]
                or user["email"]
            )

            flash("Logged in successfully.", "success")
            return redirect(url_for("home"))

        flash(
            "Incorrect email or password. Please check your details and try again. If you do not have an account, please register below.",
            "error",
        )

    return render_template("login.html")

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    reset_link = None
    user_name = None

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()

        if not email:
            flash("Please enter your email address.", "error")
            return render_template(
                "forgot_password.html",
                reset_link=reset_link,
                user_name=user_name
            )

        conn = get_db_connection()
        user = conn.execute(
            """
            SELECT u.*, s.first_name
            FROM users u
            LEFT JOIN students s ON u.id = s.user_id
            WHERE u.email = ? AND u.is_active = 1
            """,
            (email,)
        ).fetchone()

        if user and user["first_name"]:
            user_name = user["first_name"]

        if user:
            token = generate_reset_token()
            expires_at = get_reset_expiry(hours=1)

            conn.execute(
                """
                INSERT INTO password_resets (user_id, token, expires_at)
                VALUES (?, ?, ?)
                """,
                (user["id"], token, expires_at)
            )
            conn.commit()

            reset_link = url_for("reset_password", token=token, _external=True)
            flash("Password reset link generated for this demo account.", "success")
        else:
            flash("If that email exists in the system, a reset link has been generated.", "success")

        conn.close()

    return render_template(
        "forgot_password.html",
        reset_link=reset_link,
        user_name=user_name
    )

@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    conn = get_db_connection()

    reset_row = conn.execute(
        """
        SELECT pr.*, u.email
        FROM password_resets pr
        JOIN users u ON pr.user_id = u.id
        WHERE pr.token = ? AND pr.used_at IS NULL
        """,
        (token,)
    ).fetchone()

    if not reset_row:
        conn.close()
        flash("This password reset link is invalid or has already been used.", "error")
        return redirect(url_for("forgot_password"))

    expires_at = datetime.strptime(reset_row["expires_at"], "%Y-%m-%d %H:%M:%S")
    if datetime.now() > expires_at:
        conn.close()
        flash("This password reset link has expired.", "error")
        return redirect(url_for("forgot_password"))

    if request.method == "POST":
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        errors = []

        if not password:
            errors.append("Password is required.")
        if not confirm_password:
            errors.append("Please confirm your password.")
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

        if errors:
            conn.close()
            for error in errors:
                flash(error, "error")
            return render_template("reset_password.html", token=token)

        password_hash = generate_password_hash(password)

        conn.execute(
            "UPDATE users SET password = ? WHERE id = ?",
            (password_hash, reset_row["user_id"])
        )

        conn.execute(
            "UPDATE password_resets SET used_at = ? WHERE id = ?",
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), reset_row["id"])
        )

        conn.commit()
        conn.close()

        flash("Your password has been reset successfully. Please log in.", "success")
        return redirect(url_for("login"))

    conn.close()
    return render_template("reset_password.html", token=token)

@app.route("/change-details", methods=["GET", "POST"])
def change_details():
    if "user_id" not in session:
        flash("Please log in to access this page.", "error")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    role = session["role"]

    conn = get_db_connection()

    try:
        if role == "student":
            user_details = conn.execute(
                """
                SELECT
                    s.first_name,
                    s.last_name,
                    s.phone,
                    s.date_of_birth,
                    s.address_line_1,
                    s.address_line_2,
                    s.town_city,
                    s.county,
                    s.postcode,
                    s.student_number,
                    s.route_name,
                    s.department,
                    s.job_title,
                    s.cohort,
                    u.email
                FROM students s
                JOIN users u ON s.user_id = u.id
                WHERE s.user_id = ?
                """,
                (user_id,)
            ).fetchone()

            if not user_details:
                flash("Student account details could not be found.", "error")
                return redirect(url_for("home"))

            if request.method == "POST":
                email = request.form.get("email", "").strip().lower()
                phone = request.form.get("phone", "").strip()
                address_line_1 = request.form.get("address_line_1", "").strip()
                address_line_2 = request.form.get("address_line_2", "").strip()
                town_city = request.form.get("town_city", "").strip()
                county = request.form.get("county", "").strip()
                postcode = request.form.get("postcode", "").strip()
                department = request.form.get("department", "").strip()
                job_title = request.form.get("job_title", "").strip()

                errors = []

                if not email:
                    errors.append("Email address is required.")

                if email:
                    existing_email_user = conn.execute(
                        """
                        SELECT id
                        FROM users
                        WHERE email = ? AND id != ?
                        """,
                        (email, user_id)
                    ).fetchone()

                    if existing_email_user:
                        errors.append("That email address is already in use.")

                if errors:
                    for error in errors:
                        flash(error, "error")

                    form_data = {
                        "first_name": user_details["first_name"],
                        "last_name": user_details["last_name"],
                        "date_of_birth": user_details["date_of_birth"],
                        "student_number": user_details["student_number"],
                        "route_name": user_details["route_name"],
                        "cohort": user_details["cohort"],
                        "email": email,
                        "phone": phone,
                        "address_line_1": address_line_1,
                        "address_line_2": address_line_2,
                        "town_city": town_city,
                        "county": county,
                        "postcode": postcode,
                        "department": department,
                        "job_title": job_title,
                    }

                    return render_template(
                        "change_details.html",
                        role=role,
                        user_details=form_data
                    )

                conn.execute(
                    """
                    UPDATE users
                    SET email = ?
                    WHERE id = ?
                    """,
                    (email, user_id)
                )

                conn.execute(
                    """
                    UPDATE students
                    SET
                        phone = ?,
                        address_line_1 = ?,
                        address_line_2 = ?,
                        town_city = ?,
                        county = ?,
                        postcode = ?,
                        department = ?,
                        job_title = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                    """,
                    (
                        phone or None,
                        address_line_1 or None,
                        address_line_2 or None,
                        town_city or None,
                        county or None,
                        postcode or None,
                        department or None,
                        job_title or None,
                        user_id,
                    )
                )

                conn.commit()
                session["email"] = email

                flash("Your details have been updated successfully.", "success")
                return redirect(url_for("home"))

        elif role == "employer":
            flash("Employer change details is still to be built.", "error")
            return redirect(url_for("home"))

        else:
            flash("This account type cannot edit details here.", "error")
            return redirect(url_for("home"))

    finally:
        conn.close()

    return render_template(
        "change_details.html",
        role=role,
        user_details=user_details
    )


@app.route("/change-password", methods=["GET", "POST"])
def change_password():
    if "user_id" not in session:
        flash("Please log in to access this page.", "error")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    conn = get_db_connection()

    try:
        user = conn.execute(
            """
            SELECT id, password
            FROM users
            WHERE id = ? AND is_active = 1
            """,
            (user_id,)
        ).fetchone()

        if not user:
            flash("Your account could not be found.", "error")
            return redirect(url_for("home"))

        if request.method == "POST":
            current_password = request.form.get("current_password", "")
            new_password = request.form.get("new_password", "")
            confirm_password = request.form.get("confirm_password", "")

            errors = []

            if not current_password:
                errors.append("Current password is required.")

            if not new_password:
                errors.append("New password is required.")

            if not confirm_password:
                errors.append("Please confirm your new password.")

            if current_password and not check_password_hash(user["password"], current_password):
                errors.append("Your current password is incorrect.")

            if new_password and len(new_password) < 8:
                errors.append("Password must be at least 8 characters long.")

            if new_password and not any(char.islower() for char in new_password):
                errors.append("Password must include at least one lowercase letter.")

            if new_password and not any(char.isupper() for char in new_password):
                errors.append("Password must include at least one uppercase letter.")

            if new_password and not any(char.isdigit() for char in new_password):
                errors.append("Password must include at least one number.")

            if new_password and not any(not char.isalnum() for char in new_password):
                errors.append("Password must include at least one special character.")

            if new_password and confirm_password and new_password != confirm_password:
                errors.append("New password and confirm password do not match.")

            if current_password and not check_password_hash(user["password"], current_password):
                errors.append("Your current password is incorrect.")

            if new_password and check_password_hash(user["password"], new_password):
                errors.append("Your new password must be different from your current password.")

            if errors:
                for error in errors:
                    flash(error, "error")

                return render_template("change_password.html")

            password_hash = generate_password_hash(new_password)

            conn.execute(
                """
                UPDATE users
                SET password = ?
                WHERE id = ?
                """,
                (password_hash, user_id)
            )
            conn.commit()

            flash("Your password has been changed successfully.", "success")
            return redirect(url_for("home"))

    finally:
        conn.close()

    return render_template("change_password.html")
        
    

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out", "success")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)

