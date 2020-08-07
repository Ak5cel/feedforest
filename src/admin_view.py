from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import redirect, url_for, request, flash
from . import db, admin
from .models import Topic, RSSFeed, Article, User, UserRole


class AdminView(ModelView):
    """Limit access to just admin users
    Lowest access level = 'admin'
    """

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


class RSSFeedAdminView(AdminView):
    column_filters=[
        'rss_link',
        'site_name',
        'site_url',
        'updated_on',
        'topic_id'
    ]
    can_export=True


class ArticleAdminView(AdminView):
    column_filters=[
        'title',
        'refreshed_on',
        'published_on',
        'topic_id',
        'rssfeed_id'
    ]
    can_export=True


class UserAdminView(AdminView):
    column_exclude_list=['password_hash', ]
    column_filters=[
        'username',
        'email',
        'email_verified',
        'email_frequency',
        'role_id'
    ]


admin.add_view(AdminView(Topic, db.session))
admin.add_view(RSSFeedAdminView(RSSFeed, db.session))
admin.add_view(ArticleAdminView(Article, db.session))
admin.add_view(UserAdminView(User, db.session))
admin.add_view(AdminView(UserRole, db.session))
