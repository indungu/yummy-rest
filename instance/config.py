"""App intance configs"""
# Flask App Config
DEBUG = True
SECRET_KEY = "my_h@lleLluyh@"

# SQLAlchemy Configs
SQLALCHEMY_DATABASE_URI = 'postgres://su:password@localhost:5432/yummy_rest_db'

# Flask-RESTPlus Configs
SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_VALIDATE = True
RESTPLUS_MASK_SWAGGER = False
ERROR_404_HELP = False
