from flask import Blueprint, render_template
from app.models.db import get_main_db

public_bp = Blueprint("public", __name__)

@public_bp.route("/")
def index():
    rates = []
    try:
        conn = get_main_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT rate_tier, min_usage, max_usage, cost_per_unit
            FROM billing_rates
            ORDER BY min_usage
        """)
        rates = cur.fetchall()
        cur.close()
        conn.close()
    except Exception:
        rates = []

    return render_template("public/index.html", rates=rates)

@public_bp.route("/services")
def services():
    return render_template("public/services.html")