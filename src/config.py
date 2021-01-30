import os
import json
basedir = os.path.abspath(os.path.dirname(__file__))

if not os.environ.get('TESTING'):
    CONFIG_FILE_PATH = os.environ.get('FEEDFOREST_CONFIG_FILE_PATH')

    with open(CONFIG_FILE_PATH) as config_file:
        config = json.load(config_file)
else:
    config = {}


class Config(object):
    SECRET_KEY = config.get('SECRET_KEY') or '666b601b6739add4b3c04df94d9fe4f1'
    SQLALCHEMY_DATABASE_URI = config.get('SQLALCHEMY_DATABASE_URI') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = config.get('MAIL_SERVER')
    MAIL_PORT = config.get('MAIL_PORT')
    MAIL_USE_TLS = config.get('MAIL_USE_TLS')
    MAIL_USERNAME = config.get('MAIL_USERNAME')
    MAIL_PASSWORD = config.get('MAIL_PASSWORD')
