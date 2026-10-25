import os
from functools import wraps
from io import BytesIO
from datetime import date

import qrcode
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, session, send_file, abort
)
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from werkzeug.security import generate_password_hash, check_password_hash

from db_config import get_db_connection


app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")
if not app.secret_key:
    raise RuntimeError("FLASK_SECRET_KEY environment variable set nahi hai.")

ADMIN_USERNAME = os.environ.get("BUSPASS_ADMIN_USER")
ADMIN_PASSWORD = os.environ.get("BUSPASS_ADMIN_PASSWORD")

if not ADMIN_USERNAME or not ADMIN_PASSWORD:
    raise RuntimeError(
        "BUSPASS_ADMIN_USER aur BUSPASS_ADMIN_PASSWORD environment variables set karo."
    )

ADMIN_PASSWORD_HASH = generate_password_hash(ADMIN_PASSWORD)


def init_db():
    """Check the MySQL connection without modifying existing data."""
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
    finally:
        connection.close()


def login_required(view_function):
    @wraps(view_function)
    def wrapped_view(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return view_function(*args, **kwargs)
    return wrapped_view


@app.route("/", methods=["GET", "POST"])
def home():
    message = None
    success = False

    if request.method == "POST":
        name = request.form.get("full_name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        category = request.form.get("category", "").strip()
        address = request.form.get("address", "").strip()
        route = request.form.get("route", "").strip()
        pass_type = request.form.get("pass_type", "").strip()
        start_date = request.form.get("start_date", "").strip()

        if not all([name, phone, route, pass_type]):
            message = "Please fill in all required fields."
        elif not (phone.isdigit() and len(phone) == 10):
            message = "Please enter a valid 10-digit phone number."
        elif route not in ["Route A", "Route B", "Route C"]:
            message = "Please select a valid bus route."
        elif pass_type not in ["Daily", "Monthly", "Quarterly"]:
            message = "Please select a valid pass type."
        else:
            connection = None
            cursor = None

            try:
                connection = get_db_connection()
                cursor = connection.cursor()

                cursor.execute("""
                    INSERT INTO applications (
                        full_name, phone, email, category,
                        address, route, pass_type, start_date
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    name, phone, email, category,
                    address, route, pass_type, start_date or None
                ))

                application_id = cursor.lastrowid
                connection.commit()

                message = (
                    f"Thank you, {name}! Your application ID is "
                    f"BP{application_id:04d}. "
                    "Your application is pending review."
                )
                success = True

            except Exception:
                if connection is not None:
                    connection.rollback()
                app.logger.exception("Application submission failed")
                message = "Application could not be submitted. Please try again."

            finally:
                if cursor is not None:
                    cursor.close()
                if connection is not None:
                    connection.close()

    return render_template("index.html", message=message, success=success)


@app.route("/track", methods=["GET", "POST"])
def track_application():
    application = None
    error = None

    if request.method == "POST":
        application_id = request.form.get(
            "application_id", ""
        ).strip().upper()

        if application_id.startswith("BP") and application_id[2:].isdigit():
            record_id = int(application_id[2:])
            connection = None
            cursor = None

            try:
                connection = get_db_connection()
                cursor = connection.cursor(dictionary=True)

                cursor.execute("""
                    SELECT id, full_name, route, pass_type, status, created_at
                    FROM applications
                    WHERE id = %s
                """, (record_id,))

                application = cursor.fetchone()

            except Exception:
                app.logger.exception("Application tracking failed")
                error = "Unable to retrieve application. Please try again."

            finally:
                if cursor is not None:
                    cursor.close()
                if connection is not None:
                    connection.close()

        if application is None and error is None:
            error = "Application not found. Please check your Application ID."

    return render_template(
        "track.html",
        application=application,
        error=error
    )


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if session.get("admin_logged_in"):
        return redirect(url_for("admin"))

    error = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if (
            username == ADMIN_USERNAME
            and check_password_hash(ADMIN_PASSWORD_HASH, password)
        ):
            session.clear()
            session["admin_logged_in"] = True
            return redirect(url_for("admin"))

        error = "Invalid username or password. Please try again."

    return render_template("admin_login.html", error=error)


@app.route("/admin")
@login_required
def admin():
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM applications
            ORDER BY id DESC
        """)
        applications = cursor.fetchall()

        cursor.execute("""
            SELECT
                COUNT(*) AS total,
                COALESCE(SUM(status = 'Pending'), 0) AS pending,
                COALESCE(SUM(status = 'Approved'), 0) AS approved,
                COALESCE(SUM(status = 'Rejected'), 0) AS rejected
            FROM applications
        """)
        stats = cursor.fetchone()

    except Exception:
        app.logger.exception("Admin dashboard query failed")
        return "Unable to load the admin dashboard. Check the application logs.", 500

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

    return render_template(
        "admin.html",
        applications=applications,
        stats=stats
    )


@app.route("/admin/update/<int:application_id>", methods=["POST"])
@login_required
def update_application(application_id):
    status = request.form.get("status", "")

    if status not in ["Approved", "Rejected"]:
        flash("Invalid status selected.")
        return redirect(url_for("admin"))

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE applications
            SET status = %s
            WHERE id = %s
        """, (status, application_id))

        if cursor.rowcount == 0:
            connection.rollback()
            flash("Application not found.")
        else:
            connection.commit()
            flash(f"Application BP{application_id:04d} marked {status}.")

    except Exception:
        if connection is not None:
            connection.rollback()
        app.logger.exception("Application status update failed")
        flash("Could not update application status. Please try again.")

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

    return redirect(url_for("admin"))


@app.route("/download-pass/<int:application_id>")
def download_bus_pass(application_id):
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, full_name, phone, route, pass_type, start_date, status
            FROM applications
            WHERE id = %s
        """, (application_id,))

        application = cursor.fetchone()

    except Exception:
        app.logger.exception("Bus pass lookup failed")
        return "Unable to retrieve bus pass. Please try again.", 500

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

    if application is None:
        abort(404)

    if application["status"] != "Approved":
        return "Bus pass is available only for approved applications.", 403

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    pdf.setFillColorRGB(0.94, 0.97, 1)
    pdf.rect(0, 0, width, height, fill=1, stroke=0)

    pdf.setFillColorRGB(0.04, 0.15, 0.32)
    pdf.rect(0, height - 150, width, 150, fill=1, stroke=0)

    pdf.setFillColorRGB(1, 1, 1)
    pdf.setFont("Helvetica-Bold", 23)
    pdf.drawCentredString(width / 2, height - 55, "BUS PASS")

    pdf.setFont("Helvetica", 12)
    pdf.drawCentredString(
        width / 2, height - 82,
        "CLOUD-BASED BUS PASS MANAGEMENT SYSTEM"
    )

    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawCentredString(
        width / 2, height - 115,
        f"PASS ID: BP{application['id']:04d}"
    )

    left = 55
    y = height - 205

    pdf.setFillColorRGB(1, 1, 1)
    pdf.roundRect(left, 280, width - 110, y - 280, 14, fill=1, stroke=0)

    details = [
        ("PASS HOLDER", application["full_name"]),
        ("PHONE NUMBER", application["phone"]),
        ("BUS ROUTE", application["route"]),
        ("PASS TYPE", application["pass_type"]),
        (
            "START DATE",
            application["start_date"].strftime("%d-%m-%Y")
            if application["start_date"] else "Not specified"
        ),
        ("ISSUE DATE", date.today().strftime("%d-%m-%Y")),
        ("STATUS", "APPROVED"),
    ]

    current_y = y - 35

    for label, value in details:
        pdf.setFillColorRGB(0.35, 0.42, 0.52)
        pdf.setFont("Helvetica-Bold", 9)
        pdf.drawString(left + 22, current_y, label)

        pdf.setFillColorRGB(0.08, 0.16, 0.29)
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawString(left + 22, current_y - 20, str(value))
        current_y -= 58

    pdf.setFillColorRGB(0.04, 0.15, 0.32)
    pdf.rect(0, 0, width, 65, fill=1, stroke=0)

    pdf.setFillColorRGB(1, 1, 1)
    pdf.setFont("Helvetica", 9)
    pdf.drawCentredString(
        width / 2, 38, "Please carry this pass while travelling."
    )
    pdf.drawCentredString(
        width / 2, 22, "Computer-generated pass | Bus Pass System"
    )

    verification_url = url_for(
        "verify_bus_pass",
        application_id=application["id"],
        _external=True
    )

    qr_image = qrcode.make(verification_url)
    qr_buffer = BytesIO()
    qr_image.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)

    pdf.setFillColorRGB(0.08, 0.16, 0.29)
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawCentredString(width - 102, 185, "SCAN TO VERIFY")
    pdf.drawImage(
        ImageReader(qr_buffer),
        width - 145, 90,
        width=85, height=85,
        preserveAspectRatio=True,
        mask="auto"
    )

    pdf.save()
    buffer.seek(0)

    return send_file(
        buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"BusPass_BP{application['id']:04d}.pdf"
    )


@app.route("/verify-pass/<int:application_id>")
def verify_bus_pass(application_id):
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, full_name, route, pass_type, start_date, status
            FROM applications
            WHERE id = %s
        """, (application_id,))

        application = cursor.fetchone()

    except Exception:
        app.logger.exception("Pass verification lookup failed")
        return "Unable to verify bus pass. Please try again.", 500

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

    if application is None:
        return render_template("verify_pass.html", application=None), 404

    return render_template("verify_pass.html", application=application)

@app.route("/admin/logout", methods=["POST"])
@login_required
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)