"""Arguement parsers"""

from flask_restplus import reqparse

# Linting exceptions

# pylint: disable=C0103

auth_header = reqparse.RequestParser()
auth_header.add_argument('Authorization', type=str, location='headers', required=True)
