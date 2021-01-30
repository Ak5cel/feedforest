import time
from flask import url_for
from flask_login import current_user

from src.models import User, UserRole


def login(client, email, password, follow_redirects=True):
    return client.post(
        url_for('auth.login'),
        data=dict(
            email=email,
            password=password,
        ),
        follow_redirects=follow_redirects
    )


def test_existing_user_can_login(client, init_database, existing_user):
    with client:
        response = login(client, existing_user.email, 'password123', follow_redirects=False)
        assert current_user.is_authenticated
        assert current_user.id == existing_user.id
        assert response.status_code == 302
        assert response.headers['Location'] == url_for('user.my_feeds', _external=True)


def test_invalid_user_cannot_login(client, init_database):
    with client:
        response = login(client, 'some-email@sample.com', 'password123', follow_redirects=False)
        assert current_user.is_anonymous
        assert b"Login unsuccessful. Please check if you are using a \
                verified email and the correct password." in response.data


def test_prevent_authenticated_user_trying_to_login(client, init_database, existing_user):
    with client:
        login(client, existing_user.email, 'password123', follow_redirects=False)
        assert current_user.is_authenticated
        response = login(client, existing_user.email, 'password123', follow_redirects=False)
        assert response.status_code == 302
        assert response.headers['Location'] == url_for('user.my_feeds', _external=True)
        assert current_user.is_authenticated


def test_user_logout(client, init_database, existing_user):
    with client:
        login(client, existing_user.email, 'password123', follow_redirects=False)
        assert current_user.is_authenticated
        response = client.get(url_for('auth.logout'))
        assert current_user.is_anonymous
        assert response.status_code == 302
        assert response.headers['Location'] == url_for('general.home', _external=True)


def test_valid_new_user_can_signup(client, init_database):
    form_data = dict(
        username='JohnDoeNew',
        email='akhilaficel@gmail.com',
        password='password123',
        confirm_password='password123',
        accept_terms=True
    )

    with client:
        response = client.post(url_for('auth.signup'), data=form_data, follow_redirects=False)
        assert response.status_code == 200
        assert b"Account created successfully" in response.data
        assert not current_user.is_authenticated

        new_users = User.query.all()
        assert len(new_users) == 1

        new_user = new_users[0]
        assert new_user.username == form_data['username']
        assert new_user.email == form_data['email']
        assert new_user.password_hash != form_data['password']
        assert not new_user.email_verified
        assert new_user.email_frequency is None
        assert new_user.role_id == UserRole.get_default_role_id()


def test_prevent_duplicate_username_signup(client, init_database, existing_user):
    form_data = dict(
        username=existing_user.username,
        email='new_email@sample.com',
        password='password123',
        confirm_password='password123',
        accept_terms=True
    )

    with client:
        response = client.post(url_for('auth.signup'), data=form_data, follow_redirects=False)
        assert response.status_code == 200
        assert b"That username is taken" in response.data
        assert current_user.is_anonymous

        users = User.query.all()
        assert len(users) == 1
        assert users[0].id == existing_user.id


def test_prevent_duplicate_email_signup(client, init_database, existing_user):
    form_data = dict(
        username='JohnDoeNew',
        email=existing_user.email,
        password='password123',
        confirm_password='password123',
        accept_terms=True
    )

    with client:
        response = client.post(url_for('auth.signup'), data=form_data, follow_redirects=False)
        assert response.status_code == 200
        assert b"That email is taken" in response.data
        assert current_user.is_anonymous

        users = User.query.all()
        assert len(users) == 1
        assert users[0].id == existing_user.id


def test_prevent_missing_fields_signup(client, init_database, existing_user):
    form_data = dict(
        username='',
        email='',
        password='',
        confirm_password='',
        accept_terms=False
    )

    with client:
        response = client.post(url_for('auth.signup'), data=form_data, follow_redirects=False)
        assert response.status_code == 200
        assert current_user.is_anonymous

        users = User.query.all()
        assert len(users) == 1
        assert users[0].id == existing_user.id


def test_prevent_invalid_fields_signup(client, init_database, existing_user):
    form_data = dict(
        username='Jo',
        email='NotAnEmail',
        password='short',
        confirm_password='diff',
        accept_terms=True
    )

    with client:
        response = client.post(url_for('auth.signup'), data=form_data, follow_redirects=False)
        assert response.status_code == 200
        assert current_user.is_anonymous

        users = User.query.all()
        assert len(users) == 1
        assert users[0].id == existing_user.id

        assert b"Username must be between 3 and 30 characters long" in response.data
        assert b"Not a valid email address" in response.data
        assert b"Password must be between 10 and 50 characters long" in response.data
        assert b"Field must be equal to password" in response.data


def test_prevent_authenticated_user_trying_to_signup(client, init_database, existing_user):
    with client:
        login(client, existing_user.email, 'password123', follow_redirects=False)
        assert current_user.is_authenticated

        form_data = dict(
            username='Jo',
            email='NotAnEmail',
            password='short',
            confirm_password='diff',
            accept_terms=True
        )

        response = client.post(url_for('auth.signup'), data=form_data, follow_redirects=False)
        assert response.status_code == 302
        assert response.headers['Location'] == url_for('user.my_feeds', _external=True)
        assert current_user.is_authenticated


def test_request_password_reset_redirects_to_login(client, init_database, existing_user):
    with client:
        response = client.post(url_for('auth.request_password_reset'),
                               data=dict(email=existing_user.email),
                               follow_redirects=False
                               )

        assert response.status_code == 302
        assert response.headers['Location'] == url_for('auth.login', _external=True)


def test_request_password_reset_flash_message(client, init_database, existing_user):
    with client:
        response = client.post(url_for('auth.request_password_reset'),
                               data=dict(email=existing_user.email),
                               follow_redirects=True
                               )

        assert response.status_code == 200
        assert b"Please check your email for a link to reset your password." in response.data


def test_request_password_reset_with_invalid_email(client, init_database):
    with client:
        response = client.post(url_for('auth.request_password_reset'),
                               data=dict(email='NotAnEmail'),
                               follow_redirects=True
                               )

        assert response.status_code == 200
        assert b"Not a valid email address" in response.data


def test_request_password_reset_without_registering(client, init_database):
    with client:
        response = client.post(url_for('auth.request_password_reset'),
                               data=dict(email='NotAnEmail'),
                               follow_redirects=True
                               )

        assert response.status_code == 200
        assert b"No account found with that email" in response.data


def test_reset_password_with_valid_token(client, init_database, existing_user):
    with client:
        form_data = dict(
            password='new_password',
            confirm_password='new_password'
        )
        token = existing_user.generate_token(expires_sec=1800)
        old_pw_hash = existing_user.password_hash
        response = client.post(url_for('auth.reset_password_with_token', token=token),
                               data=form_data,
                               follow_redirects=True
                               )

        modified_user = User.query.filter_by(email=existing_user.email).first()
        new_pw_hash = modified_user.password_hash
        assert old_pw_hash != new_pw_hash
        assert response.status_code == 200
        assert b"Your password has been reset. You may now login." in response.data


def test_reset_password_with_expired_token(client, init_database, existing_user):
    with client:
        form_data = dict(
            password='new_password',
            confirm_password='new_password'
        )
        token = existing_user.generate_token(expires_sec=1)
        time.sleep(2)
        old_pw_hash = existing_user.password_hash
        response = client.post(url_for('auth.reset_password_with_token', token=token),
                               data=form_data,
                               follow_redirects=True
                               )

        modified_user = User.query.filter_by(email=existing_user.email).first()
        new_pw_hash = modified_user.password_hash
        assert old_pw_hash == new_pw_hash
        assert response.status_code == 200
        assert b"Token expired or invalid" in response.data


def test_verify_email_with_valid_token(client, init_database, existing_user):
    with client:
        token = existing_user.generate_token(expires_sec=1800)
        existing_user.email_verified = False
        init_database.session.commit()
        response = client.get(url_for('auth.verify_email', token=token),
                              follow_redirects=True
                              )

        modified_user = User.query.filter_by(email=existing_user.email).first()
        assert modified_user.email_verified
        assert response.status_code == 200
        assert b"Email verified" in response.data


def test_verify_email_with_invalid_token(client, init_database, existing_user):
    with client:
        token = existing_user.generate_token(expires_sec=1)
        time.sleep(2)
        existing_user.email_verified = False
        init_database.session.commit()
        response = client.get(url_for('auth.verify_email', token=token),
                              follow_redirects=True
                              )

        modified_user = User.query.filter_by(email=existing_user.email).first()
        assert not modified_user.email_verified
        assert response.status_code == 200
        assert b"Token expired or invalid" in response.data


def test_verify_and_change_new_email_with_valid_token(client, init_database, existing_user):
    with client:
        token = existing_user.generate_token_with_email('john_doe_new@sample.com')
        old_email = existing_user.email
        response = client.get(url_for('auth.verify_new_email', token=token),
                              follow_redirects=True
                              )

        modified_user = User.query.filter_by(email=existing_user.email).first()
        new_email = modified_user.email
        assert old_email != new_email
        assert new_email == 'john_doe_new@sample.com'
        assert response.status_code == 200
        assert b"Email changed" in response.data
