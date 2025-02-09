import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from utils import db


app = Flask(__name__)

config_path = os.environ.get(
    "FLASK_CONFIG", os.path.join(os.path.dirname(__file__), "dev.conf")
)

if os.path.exists(config_path):
    app.config.from_pyfile(config_path)
else:
    raise RuntimeError(f"Config file {config_path} not found!")

db.init_app(app)

from models import User, Car
from routes import *


def create_database():
    with app.app_context():
        db.create_all()
        print("Database checked/created!")


if __name__ == "__main__":
    create_database()
    app.run(debug=True)
