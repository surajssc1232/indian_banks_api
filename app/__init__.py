from flask import Flask
import logging
from .config import Config
from .models import db
from .routes import register_routes
from .database import init_database

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    logging.basicConfig(level=logging.INFO)

    register_routes(app)

    with app.app_context():
        init_database(app)

    return app
