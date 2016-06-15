from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

# create app, configure, and create routes


def create_app(config_object):
    app = Flask(__name__)
    if config_object:
        app.config.from_object(config_object)
    return app
