import pytest
from flask import url_for
from flask_login import current_user
from src import create_app, db
from src.models import User, UserRole


@pytest.fixture(autouse=True)
def disable_network_emails(monkeypatch):
    def stunted_send_email():
        pass
    monkeypatch.setattr(User, "send_email_verification_email", lambda *args, **kwargs: stunted_send_email())
    monkeypatch.setattr(User, "send_email_change_email", lambda *args, **kwargs: stunted_send_email())
    monkeypatch.setattr(User, "send_password_reset_email", lambda *args, **kwargs: stunted_send_email())


@pytest.fixture()
def client():
    flask_app = create_app()

    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    testing_client = flask_app.test_client()

    # Establish an application context before running the tests.
    app_ctx = flask_app.app_context()
    app_ctx.push()

    req_ctx = flask_app.test_request_context()
    req_ctx.push()

    # db.create_all()

    # # Add user roles now to avoid errors while creating users later
    # role1 = UserRole(role_name='admin')
    # role2 = UserRole(role_name='user')
    # db.session.add_all([role1, role2])
    # db.session.commit()

    yield testing_client

    # db.drop_all()
    req_ctx.pop()
    app_ctx.pop()


@pytest.fixture()
def init_database():
    db.create_all()

    # Add user roles now to avoid errors while creating users later
    role1 = UserRole(role_name='admin')
    role2 = UserRole(role_name='user')
    db.session.add_all([role1, role2])
    db.session.commit()

    yield db

    db.drop_all()


@pytest.fixture()
def existing_user():
    """Add a user to the database and return this user"""

    user = User(username="JohnDoe1",
                email="john_doe1@sample.com",
                password_hash=User.hash_password("password123"),
                email_verified=True)
    db.session.add(user)
    db.session.commit()
    yield user
