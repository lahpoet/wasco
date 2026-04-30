from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from app.services.auth_service import login_required
from app.models.db import get_main_db
from app.services.sync_service import sync_postgres_to_mysql

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/dashboard")
@login_required("admin")
def dashboard():
    conn = get_main_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) AS count FROM customers")
    total_customers = cur.fetchone()["count"]

    cur.execute("SELECT COUNT(*) AS count FROM bills WHERE payment_status <> 'paid'")
    outstanding_bills = cur.fetchone()["count"]

    cur.execute("SELECT COALESCE(SUM(total_amount),0) AS total FROM bills")
    total_billed = cur.fetchone()["total"]

    cur.execute("SELECT COALESCE(SUM(usage_units),0) AS total_usage FROM meter_readings")
    total_usage_units = cur.fetchone()["total_usage"]

    cur.execute("""
        SELECT 
            c.customer_id, 
            c.account_number, 
            c.full_name, 
            c.phone, 
            c.email, 
            d.district_name,
            br.branch_name
        FROM customers c
        JOIN districts d ON d.district_id = c.district_id
        LEFT JOIN branches br ON br.branch_id = c.branch_id
        ORDER BY c.customer_id DESC
    """)
    customers = cur.fetchall()

    cur.execute("""
        SELECT br.branch_id, br.branch_name, d.district_name
        FROM branches br
        JOIN districts d ON d.district_id = br.district_id
        ORDER BY br.branch_name
    """)
    branches = cur.fetchall()

    cur.execute("""
        SELECT district_id, district_name
        FROM districts
        ORDER BY district_name
    """)
    districts = cur.fetchall()

    cur.execute("""
        SELECT rate_id, rate_tier, min_usage, max_usage, cost_per_unit
        FROM billing_rates
        ORDER BY min_usage
    """)
    rates = cur.fetchall()

    cur.execute("""
        SELECT 
            b.bill_id,
            c.account_number,
            c.full_name,
            b.billing_month,
            m.previous_reading,
            m.current_reading,
            m.usage_units,
            b.total_amount,
            b.payment_status,
            b.due_date
        FROM bills b
        JOIN customers c ON c.customer_id = b.customer_id
        JOIN meter_readings m ON m.reading_id = b.reading_id
        ORDER BY b.bill_id DESC
        LIMIT 20
    """)
    bills = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("admin/dashboard.html",
                           total_customers=total_customers,
                           outstanding_bills=outstanding_bills,
                           total_billed=total_billed,
                           total_usage_units=total_usage_units,
                           customers=customers,
                           rates=rates,
                           bills=bills,
                           branches=branches,
                           districts=districts)

@admin_bp.route("/sync/mysql", methods=["POST"])
@login_required("admin")
def sync_mysql():
    try:
        result = sync_postgres_to_mysql()
        total = sum(result.values())
        flash(f"Reporting database synced successfully. {total} records checked/copied.", "success")
    except Exception as error:
        flash(f"Sync failed: {error}", "error")

    return redirect(url_for("admin.dashboard"))

@admin_bp.route("/customers/add", methods=["POST"])
@login_required("admin")
def add_customer():
    full_name = request.form.get("full_name", "").strip()
    account_number = request.form.get("account_number", "").strip()
    phone = request.form.get("phone", "").strip()
    email = request.form.get("email", "").strip()
    address = request.form.get("address", "").strip()
    district_id = request.form.get("district_id", "").strip()
    branch_id = request.form.get("branch_id", "").strip()

    if not account_number:
        flash("Account number is required.", "error")
        return redirect(url_for("admin.dashboard"))

    if not full_name:
        flash("Customer full name is required.", "error")
        return redirect(url_for("admin.dashboard"))

    if not address:
        flash("Customer address is required.", "error")
        return redirect(url_for("admin.dashboard"))

    if not district_id:
        flash("Please select a district.", "error")
        return redirect(url_for("admin.dashboard"))

    if not branch_id:
        flash("Please select a branch.", "error")
        return redirect(url_for("admin.dashboard"))

    try:
        conn = get_main_db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO customers (account_number, full_name, phone, email, address, district_id, branch_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (account_number, full_name, phone, email, address, district_id, branch_id))

        conn.commit()
        cur.close()
        conn.close()

        flash("Customer account created successfully.", "success")

    except Exception as error:
        flash(f"Customer could not be saved: {error}", "error")

    return redirect(url_for("admin.dashboard"))

    if not full_name:
        flash("Customer full name is required.", "error")
        return redirect(url_for("admin.dashboard"))

    if not address:
        flash("Customer address is required.", "error")
        return redirect(url_for("admin.dashboard"))

    if not district_id:
        flash("Please select a district.", "error")
        return redirect(url_for("admin.dashboard"))

    try:
        conn = get_main_db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO customers (account_number, full_name, phone, email, address, district_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (account_number, full_name, phone, email, address, district_id))

        conn.commit()
        cur.close()
        conn.close()

        flash("Customer account created successfully.", "success")

    except Exception as error:
        flash(f"Customer could not be saved: {error}", "error")

    return redirect(url_for("admin.dashboard"))

@admin_bp.route("/branches/add", methods=["POST"])
@login_required("admin")
def add_branch():
    branch_name = request.form.get("branch_name", "").strip()
    district_id = request.form.get("district_id", "").strip()
    location = request.form.get("location", "").strip()
    phone = request.form.get("phone", "").strip()
    email = request.form.get("email", "").strip()

    if not branch_name:
        flash("Branch name is required.", "error")
        return redirect(url_for("admin.dashboard"))

    if not district_id:
        flash("District is required.", "error")
        return redirect(url_for("admin.dashboard"))

    if not location:
        flash("Branch location is required.", "error")
        return redirect(url_for("admin.dashboard"))

    try:
        conn = get_main_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO branches (branch_name, district_id, location, phone, email)
            VALUES (%s, %s, %s, %s, %s)
        """, (branch_name, district_id, location, phone, email))
        conn.commit()
        cur.close()
        conn.close()
        flash("Branch created successfully.", "success")
    except Exception as error:
        flash(f"Branch could not be saved: {error}", "error")

    return redirect(url_for("admin.dashboard"))

@admin_bp.route("/rates/add", methods=["POST"])
@login_required("admin")
def add_rate():
    conn = get_main_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO billing_rates (rate_tier, min_usage, max_usage, cost_per_unit)
        VALUES (%s,%s,%s,%s)
    """, (
        request.form.get("rate_tier"),
        request.form.get("min_usage"),
        request.form.get("max_usage") or None,
        request.form.get("cost_per_unit")
    ))
    conn.commit()
    cur.close()
    conn.close()
    flash("Billing rate saved successfully.", "success")
    return redirect(url_for("admin.dashboard"))

@admin_bp.route("/usage/assign", methods=["POST"])
@login_required("admin")
def assign_usage():
    customer_id = request.form.get("customer_id", "").strip()
    billing_month = request.form.get("billing_month", "").strip()
    previous_reading = request.form.get("previous_reading", "").strip()
    current_reading = request.form.get("current_reading", "").strip()
    due_date = request.form.get("due_date", "").strip()

    if not customer_id:
        flash("Please select a customer.", "error")
        return redirect(url_for("admin.dashboard"))

    if not billing_month:
        flash("Billing month is required.", "error")
        return redirect(url_for("admin.dashboard"))

    if not previous_reading or not current_reading:
        flash("Previous and current meter readings are required.", "error")
        return redirect(url_for("admin.dashboard"))

    if not due_date:
        flash("Due date is required.", "error")
        return redirect(url_for("admin.dashboard"))

    try:
        previous_value = float(previous_reading)
        current_value = float(current_reading)

        if current_value < previous_value:
            flash("Current reading cannot be less than previous reading.", "error")
            return redirect(url_for("admin.dashboard"))

        usage_units = current_value - previous_value

        conn = get_main_db()
        cur = conn.cursor()

        # Get the correct billing rate according to usage units.
        cur.execute("""
            SELECT cost_per_unit
            FROM billing_rates
            WHERE %s >= min_usage
              AND (%s <= max_usage OR max_usage IS NULL)
            ORDER BY min_usage DESC
            LIMIT 1
        """, (usage_units, usage_units))

        rate = cur.fetchone()

        if not rate:
            flash("No billing rate found for this water usage range.", "error")
            cur.close()
            conn.close()
            return redirect(url_for("admin.dashboard"))

        cost_per_unit = float(rate["cost_per_unit"])
        total_amount = usage_units * cost_per_unit

        # Save meter reading.
        cur.execute("""
            INSERT INTO meter_readings (customer_id, reading_month, previous_reading, current_reading)
            VALUES (%s, %s, %s, %s)
            RETURNING reading_id
        """, (customer_id, billing_month, previous_reading, current_reading))

        reading_id = cur.fetchone()["reading_id"]

        # Create bill from calculated usage and amount.
        cur.execute("""
            INSERT INTO bills (customer_id, reading_id, billing_month, total_amount, payment_status, due_date)
            VALUES (%s, %s, %s, %s, 'unpaid', %s)
        """, (customer_id, reading_id, billing_month, round(total_amount, 2), due_date))

        # Create notification.
        cur.execute("""
            INSERT INTO notifications (customer_id, bill_id, message, notification_type, status)
            VALUES (
                %s,
                CURRVAL(pg_get_serial_sequence('bills', 'bill_id')),
                %s,
                'Billing',
                'pending'
            )
        """, (
            customer_id,
            f"Your {billing_month} water usage is {usage_units:.2f} units. Amount due is M {total_amount:.2f}."
        ))

        conn.commit()
        cur.close()
        conn.close()

        flash(f"Water usage assigned successfully. Usage: {usage_units:.2f} units. Amount owed: M {total_amount:.2f}.", "success")

    except Exception as error:
        flash(f"Water usage could not be assigned: {error}", "error")

    return redirect(url_for("admin.dashboard"))

    if not billing_month:
        flash("Billing month is required.", "error")
        return redirect(url_for("admin.dashboard"))

    if not previous_reading or not current_reading:
        flash("Previous and current meter readings are required.", "error")
        return redirect(url_for("admin.dashboard"))

    if not total_amount:
        flash("Total bill amount is required.", "error")
        return redirect(url_for("admin.dashboard"))

    if not due_date:
        flash("Due date is required.", "error")
        return redirect(url_for("admin.dashboard"))

    try:
        previous_value = float(previous_reading)
        current_value = float(current_reading)
        amount_value = float(total_amount)

        if current_value < previous_value:
            flash("Current reading cannot be less than previous reading.", "error")
            return redirect(url_for("admin.dashboard"))

        if amount_value <= 0:
            flash("Bill amount must be greater than zero.", "error")
            return redirect(url_for("admin.dashboard"))

        conn = get_main_db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO meter_readings (customer_id, reading_month, previous_reading, current_reading)
            VALUES (%s, %s, %s, %s)
            RETURNING reading_id
        """, (customer_id, billing_month, previous_reading, current_reading))

        reading_id = cur.fetchone()["reading_id"]

        cur.execute("""
            INSERT INTO bills (customer_id, reading_id, billing_month, total_amount, payment_status, due_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (customer_id, reading_id, billing_month, total_amount, payment_status, due_date))

        conn.commit()
        cur.close()
        conn.close()

        flash("Bill assigned to customer successfully.", "success")

    except Exception as error:
        flash(f"Bill could not be assigned: {error}", "error")

    return redirect(url_for("admin.dashboard"))

@admin_bp.route("/users/add", methods=["POST"])
@login_required("admin")
def add_user():
    conn = get_main_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (customer_id, username, password_hash, role, branch_id)
        VALUES (%s,%s,%s,%s,%s)
    """, (
        request.form.get("customer_id") or None,
        request.form.get("username"),
        generate_password_hash(request.form.get("password")),
        request.form.get("role"),
        request.form.get("branch_id") or None
    ))
    conn.commit()
    cur.close()
    conn.close()
    flash("System user created successfully.", "success")
    return redirect(url_for("admin.dashboard"))