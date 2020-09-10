from __future__ import absolute_import, unicode_literals
from celery import Celery


def make_celery(app, celery_obj):
    """Add flask app context to celery.Task"""
    celery_obj.conf.update(app.config)
    
    TaskBase = celery_obj.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery_obj.Task = ContextTask
