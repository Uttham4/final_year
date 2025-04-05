from flask import Blueprint
from .user import users_bp
from .payment import payments_bp
from .student import students_bp
from .auth import auth_bp

def register_blueprints(app):
    app.register_blueprint(users_bp, url_prefix="/users")
    app.register_blueprint(payments_bp, url_prefix="/payments")
    app.register_blueprint(students_bp, url_prefix="/students")
    app.register_blueprint(auth_bp, url_prefix="/auth")
