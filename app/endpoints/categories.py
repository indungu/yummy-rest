"""The categories endpoints"""
from flask import request, jsonify, make_response
from flask_restplus import Resource
from webargs.flaskparser import parser

from app.helpers import authorization_required, _pagination, _clean_name
from app.helpers.validators import CategorySchema
from app.models import db, Category
from app.parsers import SEARCH_PAGE_ARGS, _make_args_parser
from app.restplus import API
from app.serializers import category

# Lint exceptions

# pylint: disable=C0103
# pylint: disable=W0702
# pylint: disable=W0703
# pylint: disable=W0613
# pylint: disable=W0622
# pylint: disable=E1101
# pylint: disable=E0213
# pylint: disable=R0201

categories_ns = API.namespace(
    'category', description='Contains endpoints for recipe categories.',
    path='/category'
)

args_parser = _make_args_parser(categories_ns)

@categories_ns.route('')
class CategoryHandler(Resource):
    """This resource gets all categories or adds a new one."""

    @authorization_required
    @API.expect(category)
    def post(current_user, self):
        """Add Recipe Category"""

        if current_user:
            # get request data
            request_payload = request.get_json()

            # initialize validation schema
            category_schema = CategorySchema()

            request_payload, errors = category_schema.load(request_payload)

            if errors:
                return make_response(jsonify(dict(errors=errors)), 422)

            category_name = _clean_name(request_payload['category_name'])

            # check if category exists
            existing_category = current_user.categories.filter_by(
                name=category_name
            ).first()
            if not existing_category:
                name = category_name
                owner = current_user.id
                description = request_payload['description']

                # Add new category
                try:
                    new_category = Category(name, owner, description)
                    db.session.add(new_category)
                    db.session.commit()
                    response_payload = {
                        "categories": [dict(
                            category_id=new_category.id,
                            category_name=new_category.name,
                            description=new_category.description,
                            owner_id=owner,
                            date_created=new_category.created_on,
                            date_updated=new_category.updated_on
                        )]
                    }
                    response_payload = jsonify(response_payload)
                    return make_response(response_payload, 201)
                except:
                    response_payload = dict(
                        message="Some error occured. Please try again later."
                    )
                    response_payload = jsonify(response_payload)
                    return make_response(response_payload, 501)
            response_payload = dict(
                message="The category already exists!"
            )
            response_payload = jsonify(response_payload)
            return make_response(response_payload, 400)
        response_payload = dict(
            message='Login to use this resource!'
        )
        response_payload = jsonify(response_payload)
        return make_response(response_payload, 401)

    @categories_ns.expect(args_parser)
    @authorization_required
    def get(current_user, self):
        """Returns a list of user's recipe categories"""

        if current_user:
            if not current_user.categories.all():
                return make_response( \
            jsonify({'message': 'No categories exist. Please create some.'}))
            # parse args if provided
            args = parser.parse(SEARCH_PAGE_ARGS, request)
            if 'q' in args:
                try:
                    all_categories = current_user.categories.filter(
                        Category.name.ilike("%" + args['q'] + "%")
                    ).paginate(page=args['page'], per_page=args['per_page'], error_out=False)
                except KeyError:
                    all_categories = current_user.categories.filter(
                        Category.name.ilike("%" + args['q'] + "%")
                    ).paginate(page=1, per_page=5)
            else:
                all_categories = current_user.categories.paginate(error_out=False)
            pagination_details = _pagination(all_categories)
            categories = []
            for cat in all_categories.items:
                catg = dict(
                    category_id=cat.id,
                    category_name=cat.name,
                    description=cat.description,
                    date_created=cat.created_on,
                    date_updated=cat.updated_on
                )
                categories.append(catg)
            if categories:
                response_payload = {
                    "categories": categories,
                    "page_details": pagination_details
                }
            else:
                response_payload = {
                    "message": "Page does not exist."
                }
            return make_response(jsonify(response_payload), 200)
        response_payload = dict(
            message='Login to use this resource!'
        )
        response_payload = jsonify(response_payload)
        return make_response(response_payload, 401)

@categories_ns.route('/<int:id>')
class SingleCategoryResource(Resource):
    """
    This resource handles the Read, Update and Delete functionality
    on a single Recipe category
    """

    @authorization_required
    def get(current_user, self, id):
        """
        Returns the specified category

        :param: id (int)
        """
        if not current_user:
            response_payload = dict(
                message='Invalid token. Login to use this resource!'
            )
            response_payload = jsonify(response_payload)
            return make_response(response_payload, 401)

        # retrieve specified category
        specified_category = current_user.categories.filter_by(id=id).first()

        if specified_category:
            response_payload = {
                "categories": [dict(
                    category_id=specified_category.id,
                    category_name=specified_category.name,
                    description=specified_category.description,
                    date_created=specified_category.created_on,
                    date_updated=specified_category.updated_on
                )]
            }
            response_payload = jsonify(response_payload)
            return make_response(response_payload, 200)
        response_payload = dict(
            message="Sorry, category does not exist!"
        )
        response_payload = jsonify(response_payload)
        return make_response(response_payload, 404)

    @authorization_required
    @API.expect(category)
    def put(current_user, self, id):
        """
        Updates the specified category

        :param: id (int)
        """
        if not current_user:
            response_payload = dict(
                message='Invalid token. Login to use this resource!'
            )
            response_payload = jsonify(response_payload)
            return make_response(response_payload, 401)

        # retrieve specified category
        specified_category = current_user.categories.filter_by(id=id).first()

        if specified_category:
            # Get request data
            request_payload = request.get_json()

            # format new name
            new_category_name = _clean_name(request_payload['category_name'])

            # Ensure the category name does not match that any of the user's
            # existing category apart from the one they are editing
            existing_category = current_user.categories.filter(
                Category.name == _clean_name(request_payload['category_name']),
                Category.id != specified_category.id
            ).first()

            # return appropriate response
            if not existing_category:
                if new_category_name != specified_category.name:
                    old_category_name = specified_category.name
                    specified_category.name = new_category_name
                    specified_category.description = request_payload['description']
                    db.session.commit()
                    response_payload = dict(
                        message="Category '{}' was successfully updated to '{}'.".format(
                            old_category_name, specified_category.name
                        )
                    )
                else:
                    specified_category.description = request_payload['description']
                    db.session.commit()
                    response_payload = dict(
                        message="Category '{}' was successfully updated.".format(
                            specified_category.name
                        )
                    )
                response_payload = jsonify(response_payload)
                return make_response(response_payload, 200)
            response_payload = dict(
                message="Category already exists, please use a different name."
            )
            return make_response(jsonify(response_payload), 401)

        response_payload = dict(
            message="Sorry, category does not exist!"
        )
        response_payload = jsonify(response_payload)
        return make_response(response_payload, 404)

    @authorization_required
    def delete(current_user, self, id):
        """
        Deletes the specified category

        :param: id (int)
        """
        if not current_user:
            response_payload = dict(
                message='Invalid token. Login to use this resource!'
            )
            response_payload = jsonify(response_payload)
            return make_response(response_payload, 401)

        # retrieve specified category
        specified_category = current_user.categories.filter_by(id=id).first()

        if specified_category:
            category_name = specified_category.name
            db.session.delete(specified_category)
            db.session.commit()

            response_payload = {
                "message": "Category '{}' was deleted successfully.".format(category_name)
            }
            response_payload = jsonify(response_payload)
            return make_response(response_payload, 200)
        response_payload = dict(
            message="Sorry, category does not exist!"
        )
        response_payload = jsonify(response_payload)
        return make_response(response_payload, 404)
