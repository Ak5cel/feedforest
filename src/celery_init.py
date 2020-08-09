from __future__ import absolute_import, unicode_literals
from celery import Celery


def make_celery(app, celery_obj):
    celery_obj.conf.update(app.config)

    class ContextTask(celery_obj.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_obj.Task = ContextTask
