from functools import wraps
from flask import session, redirect, url_for, flash
from werkzeug.security import check_password_hash
from app.models.db import get_main_db

def authenticate_user(username, password):
    conn = get_main_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            u.user_id,
            u.customer_id,
            u.username,
            COALESCE(c.full_name, u.username) AS full_name,
            u.password_hash,
            u.role,
            u.branch_id
        FROM users u
        LEFT JOIN customers c ON c.customer_id = u.customer_id
        WHERE u.username = %s
    """, (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if not user:
        return None

    if check_password_hash(user["password_hash"], password):
        return user

    return None

def login_required(role=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                flash("Please sign in to continue.", "error")
                return redirect(url_for("auth.login"))

            if role and session.get("role") != role:
                flash("You do not have permission to access that area.", "error")
                return redirect(url_for("auth.login"))

            return func(*args, **kwargs)
        return wrapper
    return decorator