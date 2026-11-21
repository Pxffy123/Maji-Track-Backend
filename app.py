

import click
from flask import Flask, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
from config import Config
from extensions import init_extensions

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
    
    @app.route("/openapi.yaml")
    def openapi():
        return send_from_directory(app.root_path, "openapi.yaml")

    SWAGGER_URL = "/docs"
    API_URL = "/openapi.yaml"

    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={"app_name": "Maji-Track API"}
    )

    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    # Initialize extensions
    init_extensions(app)

    # Register route blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(submissions_bp, url_prefix="/api/submissions")
    app.register_blueprint(reports_bp, url_prefix="/api/reports")
    app.register_blueprint(districts_bp, url_prefix="/api/districts")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")

    
    
    @app.route("/")
    def home():
        return {"message": "Maji-Track Backend is running"}

    # Usage: flask --app app make-admin someone@example.com
    @app.cli.command("make-admin")
    @click.argument("email")
    def make_admin(email):
        """Give an existing, registered user the admin role."""
        from extensions import db
        from models import User

        user = User.query.filter_by(email=email.strip().lower()).first()
        if not user:
            raise click.ClickException(f"No user found with email {email}")
        user.role = "admin"
        db.session.commit()
        click.echo(f"{user.email} is now an admin.")

    return app

app = create_app()


if __name__ == "__main__":
    app.run(debug=True, port=5555)
