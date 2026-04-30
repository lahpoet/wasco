from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from app.services.auth_service import login_required
from app.models.db import get_main_db

customer_bp = Blueprint("customer", __name__, url_prefix="/customer")

@customer_bp.route("/dashboard")
@login_required("customer")
def dashboard():
    customer_id = session.get("customer_id")
    conn = get_main_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT c.account_number, c.full_name, c.address, d.district_name
        FROM customers c
        JOIN districts d ON d.district_id = c.district_id
        WHERE c.customer_id = %s
    """, (customer_id,))
    customer = cur.fetchone()

    cur.execute("""
        SELECT 
               b.bill_id,
               b.billing_month,
               m.usage_units,
               b.total_amount,
               b.payment_status,
               b.due_date,
               COALESCE(SUM(p.amount_paid), 0) AS amount_paid,
               (b.total_amount - COALESCE(SUM(p.amount_paid), 0)) AS balance
        FROM bills b
        JOIN meter_readings m ON m.reading_id = b.reading_id
        LEFT JOIN payments p ON p.bill_id = b.bill_id
        WHERE b.customer_id = %s
        GROUP BY b.bill_id, m.usage_units
        ORDER BY b.due_date DESC
    """, (customer_id,))
    bills = cur.fetchall()

    cur.execute("""
        SELECT reading_month, previous_reading, current_reading, usage_units, reading_date
        FROM meter_readings
        WHERE customer_id = %s
        ORDER BY reading_date DESC
        LIMIT 6
    """, (customer_id,))
    readings = cur.fetchall()

    cur.close()
    conn.close()
    return render_template("customer/dashboard.html", customer=customer, bills=bills, readings=readings)

@customer_bp.route("/payment/<int:bill_id>", methods=["POST"])
@login_required("customer")
def record_payment(bill_id):
    customer_id = session.get("customer_id")
    amount = request.form.get("amount")
    method = request.form.get("method")

    conn = get_main_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO payments (bill_id, customer_id, amount_paid, payment_method, payment_reference)
        VALUES (%s, %s, %s, %s, CONCAT('PAY-', EXTRACT(EPOCH FROM NOW())::BIGINT))
    """, (bill_id, customer_id, amount, method))

    cur.execute("""
        UPDATE bills
        SET payment_status = CASE
            WHEN (SELECT COALESCE(SUM(amount_paid),0) FROM payments WHERE bill_id=%s) >= total_amount THEN 'paid'
            WHEN (SELECT COALESCE(SUM(amount_paid),0) FROM payments WHERE bill_id=%s) > 0 THEN 'partial'
            ELSE 'unpaid'
        END
        WHERE bill_id=%s
    """, (bill_id, bill_id, bill_id))

    conn.commit()
    cur.close()
    conn.close()

    flash("Payment was recorded successfully.", "success")
    return redirect(url_for("customer.dashboard"))

@customer_bp.route("/report-leakage", methods=["POST"])
@login_required("customer")
def report_leakage():
    customer_id = session.get("customer_id")
    location = request.form.get("location")
    description = request.form.get("description")

    conn = get_main_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO leakage_reports (customer_id, location, description)
        VALUES (%s, %s, %s)
    """, (customer_id, location, description))
    conn.commit()
    cur.close()
    conn.close()

    flash("Leakage report submitted successfully.", "success")
    return redirect(url_for("customer.dashboard"))