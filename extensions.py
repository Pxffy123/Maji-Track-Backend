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
            "origins": [
                "http://localhost:5173",
                "https://maji-track.netlify.app"
            ]
        }
    },
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    )
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        secure=True
    )
