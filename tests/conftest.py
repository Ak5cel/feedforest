import os
import tempfile

import pytest
from src import create_app, db
from src.models import User, UserRole

from .test_config import TestConfig


@pytest.fixture()
def client():
    flask_app = create_app(config_class=TestConfig)

    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    testing_client = flask_app.test_client()

    # Establish an application context before running the tests.
    app_ctx = flask_app.app_context()
    app_ctx.push()

    req_ctx = flask_app.test_request_context()
    req_ctx.push()

    db.create_all()

    # Add user roles now to avoid errors while creating users later
    role1 = UserRole(role_name='admin')
    role2 = UserRole(role_name='user')
    db.session.add_all([role1, role2])
    db.session.commit()

    yield testing_client

    db.drop_all()
    req_ctx.pop()
    app_ctx.pop()


@pytest.fixture()
def sample_users():
    """Add two sample users to the User table"""

    user1 = User(username="JohnDoe1",
                 email="john_doe1@sample.com",
                 password_hash=User.hash_password("password1"),
                 email_verified=True)
    user2 = User(username="JohnDoe2",
                 email="john_doe2@sample.com",
                 password_hash=User.hash_password("password2"),
                 email_verified=True)
    db.session.add(user1)
    db.session.add(user2)
    db.session.commit()
