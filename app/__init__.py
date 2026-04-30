from flask import Flask
from dotenv import load_dotenv
import os

def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "change-this-secret-key")

    from app.controllers.public_controller import public_bp
    from app.controllers.auth_controller import auth_bp
    from app.controllers.customer_controller import customer_bp
    from app.controllers.admin_controller import admin_bp
    from app.controllers.manager_controller import manager_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(manager_bp)

    return app