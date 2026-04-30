from flask import Blueprint, render_template, session
from app.services.auth_service import login_required
from app.models.db import get_main_db

manager_bp = Blueprint("manager", __name__, url_prefix="/manager")

@manager_bp.route("/dashboard")
@login_required("manager")
def dashboard():
    branch_id = session.get("branch_id")

    conn = get_main_db()
    cur = conn.cursor()

    branch_filter = ""
    params = []

    if branch_id:
        branch_filter = "WHERE br.branch_id = %s"
        params.append(branch_id)

    cur.execute(f"""
        SELECT 
            br.branch_name,
            d.district_name,
            COUNT(DISTINCT c.customer_id) AS total_customers,
            COUNT(DISTINCT b.bill_id) AS total_bills,
            COALESCE(SUM(m.usage_units),0) AS total_usage,
            COALESCE(SUM(b.total_amount),0) AS total_billed,
            COALESCE(SUM(p.amount_paid),0) AS total_paid,
            COALESCE(SUM(b.total_amount),0) - COALESCE(SUM(p.amount_paid),0) AS outstanding_balance,
            ROUND(
                CASE 
                    WHEN COALESCE(SUM(b.total_amount),0) = 0 THEN 0
                    ELSE (COALESCE(SUM(p.amount_paid),0) / COALESCE(SUM(b.total_amount),0)) * 100
                END, 2
            ) AS collection_rate
        FROM branches br
        JOIN districts d ON d.district_id = br.district_id
        LEFT JOIN customers c ON c.branch_id = br.branch_id
        LEFT JOIN bills b ON b.customer_id = c.customer_id
        LEFT JOIN meter_readings m ON m.reading_id = b.reading_id
        LEFT JOIN payments p ON p.bill_id = b.bill_id
        {branch_filter}
        GROUP BY br.branch_name, d.district_name
        ORDER BY total_billed DESC, br.branch_name
    """, tuple(params))
    branch_performance = cur.fetchall()

    cur.execute(f"""
        SELECT
            COUNT(DISTINCT c.customer_id) AS customers,
            COUNT(DISTINCT b.bill_id) AS bills,
            COALESCE(SUM(m.usage_units),0) AS usage,
            COALESCE(SUM(b.total_amount),0) AS billed,
            COALESCE(SUM(p.amount_paid),0) AS paid,
            COALESCE(SUM(b.total_amount),0) - COALESCE(SUM(p.amount_paid),0) AS outstanding
        FROM branches br
        LEFT JOIN customers c ON c.branch_id = br.branch_id
        LEFT JOIN bills b ON b.customer_id = c.customer_id
        LEFT JOIN meter_readings m ON m.reading_id = b.reading_id
        LEFT JOIN payments p ON p.bill_id = b.bill_id
        {branch_filter}
    """, tuple(params))
    totals = cur.fetchone()

    cur.execute(f"""
        SELECT 
            b.billing_month,
            COUNT(*) AS total_bills,
            COALESCE(SUM(m.usage_units),0) AS total_usage,
            COALESCE(SUM(b.total_amount),0) AS total_billed,
            COALESCE(SUM(p.amount_paid),0) AS paid_value,
            COALESCE(SUM(b.total_amount),0) - COALESCE(SUM(p.amount_paid),0) AS outstanding_value
        FROM branches br
        JOIN customers c ON c.branch_id = br.branch_id
        JOIN bills b ON b.customer_id = c.customer_id
        JOIN meter_readings m ON m.reading_id = b.reading_id
        LEFT JOIN payments p ON p.bill_id = b.bill_id
        {branch_filter}
        GROUP BY b.billing_month
        ORDER BY MAX(b.created_at) DESC
        LIMIT 12
    """, tuple(params))
    usage_reports = cur.fetchall()

    cur.execute(f"""
        SELECT 
            DATE(b.created_at) AS report_date,
            COUNT(*) AS total_bills,
            COALESCE(SUM(m.usage_units),0) AS usage_units,
            COALESCE(SUM(b.total_amount),0) AS billed_amount
        FROM branches br
        JOIN customers c ON c.branch_id = br.branch_id
        JOIN bills b ON b.customer_id = c.customer_id
        JOIN meter_readings m ON m.reading_id = b.reading_id
        {branch_filter}
        GROUP BY DATE(b.created_at)
        ORDER BY report_date DESC
        LIMIT 10
    """, tuple(params))
    daily_performance = cur.fetchall()

    cur.execute(f"""
        SELECT 
            br.branch_name,
            d.district_name,
            COUNT(l.report_id) AS total_reports,
            SUM(CASE WHEN l.report_status = 'reported' THEN 1 ELSE 0 END) AS open_reports,
            SUM(CASE WHEN l.report_status <> 'reported' THEN 1 ELSE 0 END) AS resolved_reports
        FROM branches br
        JOIN districts d ON d.district_id = br.district_id
        LEFT JOIN customers c ON c.branch_id = br.branch_id
        LEFT JOIN leakage_reports l ON l.customer_id = c.customer_id
        {branch_filter}
        GROUP BY br.branch_name, d.district_name
        ORDER BY total_reports DESC, br.branch_name
    """, tuple(params))
    service_performance = cur.fetchall()

    cur.execute(f"""
        SELECT l.report_id, c.full_name, br.branch_name, d.district_name, l.location, l.report_status, l.reported_at
        FROM branches br
        JOIN districts d ON d.district_id = br.district_id
        JOIN customers c ON c.branch_id = br.branch_id
        JOIN leakage_reports l ON l.customer_id = c.customer_id
        {branch_filter}
        ORDER BY l.reported_at DESC
        LIMIT 10
    """, tuple(params))
    leakage_reports = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "manager/dashboard.html",
        usage_reports=usage_reports,
        branch_performance=branch_performance,
        totals=totals,
        daily_performance=daily_performance,
        service_performance=service_performance,
        leakage_reports=leakage_reports
    )