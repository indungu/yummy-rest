"""Arguement parsers"""

from flask_restplus import reqparse

auth_header = reqparse.RequestParser()
auth_header.add_argument('access_token', type=str, location='headers')