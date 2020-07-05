import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or '666b601b6739add4b3c04df94d9fe4f1'

    db_path = os.path.join(os.path.dirname(__file__), 'app.db')
    db_uri = 'sqlite:///{}'.format(db_path)
    SQLALCHEMY_DATABASE_URI = db_uri

    MAIL_SERVER = 'smtp-mail.outlook.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USER')
    MAIL_PASSWORD = os.environ.get('MAIL_PASS')
