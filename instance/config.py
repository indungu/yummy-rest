"""App intance configs"""
# Flask App Config
DEBUG = True
SECRET_KEY = "\xe6.]`\x99\x07\x1ap\xff\xb7c\xf0\xea*\xba{"

# SQLAlchemy Configs
SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/yummy_rest_db'

# Flask-RESTPlus Configs
SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_VALIDATE = True
RESTPLUS_MASK_SWAGGER = False
ERROR_404_HELP = False
