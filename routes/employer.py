from flask import Blueprint, render_template

employer_bp = Blueprint("employer", __name__)

#Placeholder for the employer dashboard
@employer_bp.route("/employer")
def employer_dashboard():
    return render_template("/employer_dashboard.html")

