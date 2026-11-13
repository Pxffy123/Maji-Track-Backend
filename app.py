
from flask import Flask

from config import Config
from extensions import db, jwt, bcrypt

# Import route blueprints
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.submissions import submissions_bp
from routes.reports import reports_bp
from routes.districts import districts_bp
from routes.dashboard import dashboard_bp


def create_app():
    app = Flask(__name__)

    # Load application configuration
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)

    # Register route blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(submissions_bp, url_prefix="/api/submissions")
    app.register_blueprint(reports_bp, url_prefix="/api/reports")
    app.register_blueprint(districts_bp, url_prefix="/api/districts")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, port=5555)
