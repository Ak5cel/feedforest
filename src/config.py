import os
import json

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    if os.environ.get('FLASK_ENV', None):
        CONFIG_FILE_PATH = os.environ.get('FEEDFOREST_CONFIG_FILE_PATH')
        with open(CONFIG_FILE_PATH) as config_file:
            config = json.load(config_file)

        SECRET_KEY = config.get('SECRET_KEY') or '666b601b6739add4b3c04df94d9fe4f1'
        SQLALCHEMY_DATABASE_URI = config.get('SQLALCHEMY_DATABASE_URI') or \
            'sqlite:///' + os.path.join(basedir, 'app.db')

        MAIL_SERVER = config.get('MAIL_SERVER')
        MAIL_PORT = config.get('MAIL_PORT')
        MAIL_USE_TLS = config.get('MAIL_USE_TLS')
        MAIL_USERNAME = config.get('MAIL_USERNAME')
        MAIL_PASSWORD = config.get('MAIL_PASSWORD')


class DevConfig(ProductionConfig):
    if os.environ.get('FLASK_ENV', None):
        DEBUG = True


class TestingConfig(Config):
    # Enable the TESTING flag to disable the error catching during request handling
    # so that you get better error reports when performing test requests against the application.
    TESTING = True

    SECRET_KEY = '666b601b6739add4b3c04df94d9fe4f1'

    # Disable CSRF tokens in the Forms (only valid for testing purposes!)
    WTF_CSRF_ENABLED = False

    # Use an in-memory sqlite database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # + join(_cwd, 'testing.db')

    # Bcrypt algorithm hashing rounds (reduced for testing purposes only!)
    BCRYPT_LOG_ROUNDS = 4
