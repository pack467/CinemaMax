from flask import Flask, session, redirect, url_for, request
from config import SECRET_KEY
from app.auth import auth
from app.main import main

def create_app():
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )
    app.secret_key = SECRET_KEY
    app.register_blueprint(auth)
    app.register_blueprint(main)

    @app.before_request
    def require_login():
        # Daftar endpoint yang boleh diakses tanpa login
        allowed_routes = [
            'auth.login',
            'auth.register',
            'static'
        ]
        # Jika user belum login dan endpoint bukan di allowed_routes, redirect ke login
        if 'user_id' not in session and request.endpoint not in allowed_routes:
            return redirect(url_for('auth.login'))

    return app
