import cloudinary
import os
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_cors import CORS

db = SQLAlchemy()

jwt = JWTManager()


migrate = Migrate()

cors = CORS()

def init_extensions(app):

    db.init_app(app)

    jwt.init_app(app)

    migrate.init_app(app, db)

    cors.init_app(
    app,
    resources={
        r"/*": {
            "origins": app.config["CORS_ORIGINS"]
        }
    }
)
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        secure=True
    )
