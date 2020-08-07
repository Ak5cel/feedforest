import os
from flask import Flask, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
from flask_admin import Admin, AdminIndexView

from .config import Config
from .celery_init import make_celery

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


celery = make_celery(app)


class MyAdminIndexView(AdminIndexView):
    """Limit access to admin pages"""

    def is_accessible(self):
        return current_user.is_authenticated \
            and current_user.role.role_name == 'admin'

    def inaccessible_callback(self, name, **kwargs):
        if not current_user.is_authenticated:
            # redirect to login page if user doesn't has not logged in
            flash('Authorized access only. Please login first.', 'warning')
            return redirect(url_for('login', next=request.full_path))
        if current_user.role.role_name != 'admin':
            # redirect to home page if user doesn't have access
            flash('You do not have access to that page.', 'danger')
            return redirect(url_for('home', next=request.full_path))


admin = Admin(app, index_view=MyAdminIndexView())

from . import routes, models, tasks, admin_view
import feedparser
