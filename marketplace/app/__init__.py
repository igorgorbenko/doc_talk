# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS


db = SQLAlchemy()
ma = Marshmallow()


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object('app.config.Config')
    app.config['UPLOAD_FOLDER'] = './tmp_images/'

    db.init_app(app)
    ma.init_app(app)

    with app.app_context():
        from . import models
        db.create_all()

    return app
