from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_cors import CORS

db = SQLAlchemy()

jwt = JWTManager()


migrate = Migrate()

cors = CORS()

def init_extensions(app):
    """
    Connect all our extensions to the Flask application.
    This function is called when the application starts.
    """

    db.init_app(app)

    jwt.init_app(app)

    migrate.init_app(app, db)

    cors.init_app(
        app,
        resources={
            r"/*": {
                "origins": ["http://localhost:5173"]
            }
        }
    )
