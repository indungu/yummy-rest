"""Arguement parsers"""

from webargs import fields

# Lint exception

# pylint: disable=E1101

# Args validation parser
SEARCH_PAGE_ARGS = {
    'q': fields.String(),
    'page': fields.Integer(),
    'per_page': fields.Integer()
}

# args documentation helper function
def _make_args_parser(namespace):
    """
    This function receives a namespace object and returns
    a parser that can be documented for a particular enpoint/resource

    :param object of :class: Namespace:
    :returns object of :class: RequestParser:
    """

    args_parser = namespace.parser()
    args_parser.add_argument('q', type=str, help='Search query string', location='url')
    args_parser.add_argument('page', default=1, type=int, help='Active page', location='url')
    args_parser.add_argument(
        'per_page', default=5, type=int, help="The number of items to display", location='url'
    )
    return args_parser
