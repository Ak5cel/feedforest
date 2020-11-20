import os
import tempfile

import pytest
from src import create_app, db
from src.models import User, UserRole

from .test_config import TestConfig


@pytest.fixture
def client():
    """Create and return a test client with sqlite database"""

    app = create_app(config_class=TestConfig)

    with app.test_client() as client:
        with app.app_context():
            db.create_all()

            # Add user roles now to avoid errors while creating users later
            role1 = UserRole(role_name='admin')
            role2 = UserRole(role_name='user')
            db.session.add_all([role1, role2])
            db.session.commit()
            yield client

            db.drop_all()


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
