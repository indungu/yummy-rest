"""RESTPLus API init"""
from flask_restplus import Api

# Linting exception
# pylint: disable=C0103

# Setup authorization
authorization = {
    'apiKey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}

API = Api(
    version='1.0', title="Yummy REST",
    description="REST API implementation of the Yummy Recipes using Flask and PostgreSQL",
    authorizations=authorization
)
