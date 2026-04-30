from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.services.auth_service import authenticate_user

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = authenticate_user(username, password)

        if user:
            session.clear()
            session["user_id"] = user["user_id"]
            session["customer_id"] = user["customer_id"]
            session["username"] = user["username"]
            session["full_name"] = user["full_name"]
            session["role"] = user["role"]
            session["branch_id"] = user.get("branch_id")

            if user["role"] == "admin":
                return redirect(url_for("admin.dashboard"))
            if user["role"] == "manager":
                return redirect(url_for("manager.dashboard"))
            return redirect(url_for("customer.dashboard"))

        flash("Invalid username or password.", "error")

    return render_template("auth/login.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("public.index"))