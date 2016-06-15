import pytest
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy


@pytest.fixture(scope="session")
def app():
    app = Flask(__name__)
    SQLAlchemy(app)
    return app

app = app()


def test_variant_search():
    return True
