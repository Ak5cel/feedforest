from flask import Flask, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
from flask_admin import Admin, AdminIndexView
from celery import Celery
from .config import Config
from .celery_init import make_celery


db = SQLAlchemy()
migrate = Migrate(db)
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

celery = Celery(
    __name__,
    backend='rpc://',
    broker='pyamqp://guest@localhost//',
    include=['src.tasks']
)


class MyAdminIndexView(AdminIndexView):
    """Limit access to admin index page"""

    def is_accessible(self):
        return current_user.is_authenticated \
            and current_user.role.role_name == 'admin'

    def inaccessible_callback(self, name, **kwargs):
        if not current_user.is_authenticated:
            # redirect to login page if user doesn't has not logged in
            flash('Authorized access only. Please login first.', 'warning')
            return redirect(url_for('auth.login', next=request.full_path))
        if current_user.role.role_name != 'admin':
            # redirect to home page if user doesn't have access
            flash('You do not have access to that page.', 'danger')
            return redirect(url_for('general.home', next=request.full_path))


admin = Admin(index_view=MyAdminIndexView())

from . import models, tasks, celery_init
from .auth import forms, routes
from .general import forms, routes
from .user import forms, routes


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    migrate.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    admin.init_app(app)
    make_celery(app, celery)
    from .auth.routes import auth
    from .general.routes import general
    from .user.routes import user
    app.register_blueprint(auth)
    app.register_blueprint(general)
    app.register_blueprint(user)

    return app
