"""App intance configs"""

import os
# Linting exceptions

# pylint: disable=C0103
# pylint: disable=W0702
# pylint: disable=W0703
# pylint: disable=R0903
# pylint: disable=E1101

basedir = os.path.abspath(os.path.dirname(__file__))
database_url = os.environ.get('DATABASE_URL', 'postgresql://localhost/')
database_name = os.environ.get('DATABASE_NAME', 'yummy_rest')

class BaseConfig:
    """Base configuration."""
    # Flask APP configs
    SECRET_KEY = os.environ.get("SECRET_KEY", "\xe6.]`\x99\x07\x1ap\xff\xb7c\xf0\xea*\xba{")
    DEBUG = False
    # SQLAlchemy configs
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Flask-RESTPlus Configs
    SWAGGER_UI_DOC_EXPANSION = 'list'
    RESTPLUS_VALIDATE = True
    RESTPLUS_MASK_SWAGGER = False
    ERROR_404_HELP = False


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = database_url + database_name


class TestingConfig(BaseConfig):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = database_url + database_name + '_test'
    PRESERVE_CONTEXT_ON_EXCEPTION = False


class ProductionConfig(BaseConfig):
    """Production configuration."""
    SECRET_KEY = 'my_precious'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = database_url

app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}
