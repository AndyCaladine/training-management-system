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
        email = request.form["email"].strip()
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE email = ? AND is_active = 1",
            (email,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["email"] = user["email"]
            session["role"] = user["role"]

            flash("Login successful", "success")
            return redirect(url_for("home"))

        flash("Incorrect email or password. Please check your details and try again. If you do not yet have an account, please register below.", "error")

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
    

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out", "success")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)

