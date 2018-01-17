"""The categories endpoints"""
import sys
from flask import request, jsonify, make_response
from flask_restplus import Resource
from webargs.flaskparser import parser

from app.helpers import authorization_required, _pagination
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
            data = request.get_json()

            # initialize validation schema
            category_schema = CategorySchema()

            data, errors = category_schema.load(data)

            if errors:
                reponse_obj = dict(
                    message='You entered some invalid details.',
                    errors=errors
                )
                return make_response(jsonify(reponse_obj), 422)

            category_name = data['category_name'].lower()

            # check if category exists
            existing_category = current_user.categories.filter_by(
                name=category_name
            ).first()
            if not existing_category:
                name = category_name
                owner = current_user.id
                description = data['description']

                # Add new category
                try:
                    new_category = Category(name, owner, description)
                    db.session.add(new_category)
                    db.session.commit()
                    resp_obj = {
                        "categories": [dict(
                            category_id=new_category.id,
                            category_name=new_category.name,
                            description=new_category.description,
                            owner=owner,
                            date_created=new_category.created_on,
                            date_updated=new_category.updated_on
                        )],
                        "status": "Success!"
                    }
                    resp_obj = jsonify(resp_obj)
                    return make_response(resp_obj, 201)
                except:
                    resp_obj = dict(
                        message="Some error occured!",
                        status="Error"
                    )
                    resp_obj = jsonify(resp_obj)
                    return make_response(resp_obj, 501)
            resp_obj = dict(
                message="The category already exists!",
                status="Fail!"
            )
            resp_obj = jsonify(resp_obj)
            return make_response(resp_obj, 400)
        resp_obj = dict(
            status="Fail!",
            message='Login to use this resource!'
        )
        resp_obj = jsonify(resp_obj)
        return make_response(resp_obj, 401)

    @categories_ns.expect(args_parser)
    @authorization_required
    def get(current_user, self):
        """Returns a list of user's recipe categories"""

        if current_user:
            # parse args if provided
            args = parser.parse(SEARCH_PAGE_ARGS, request)
            if args:
                try:
                    all_categories = current_user.categories.filter(
                        Category.name.ilike("%" + args['q'] + "%")
                    ).paginate(page=args['page'], per_page=args['per_page'])
                except KeyError:
                    try:
                        all_categories = current_user.categories. \
                        paginate(page=args['page'], per_page=args['per_page'])
                    except KeyError:
                        all_categories = current_user.categories.paginate(error_out=False)
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
            resp_obj = {
                "categories": categories,
                "message": "Success!",
                "page_details": pagination_details
            }
            return make_response(jsonify(resp_obj), 200)
        resp_obj = dict(
            status="Fail!",
            message='Login to use this resource!'
        )
        resp_obj = jsonify(resp_obj)
        return make_response(resp_obj, 401)

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
            print(current_user, file=sys.stdout)
            resp_obj = dict(
                status="Fail!",
                message='Invalid token. Login to use this resource!'
            )
            resp_obj = jsonify(resp_obj)
            return make_response(resp_obj, 401)

        # retrieve specified category
        specified_category = Category.query.filter_by(id=id).first()

        if specified_category:
            resp_obj = {
                "categories": [dict(
                    category_id=specified_category.id,
                    category_name=specified_category.name,
                    category_description=specified_category.description,
                    date_created=specified_category.created_on,
                    date_updated=specified_category.updated_on
                )],
                "status": "Success!"
            }
            resp_obj = jsonify(resp_obj)
            return make_response(resp_obj, 200)
        resp_obj = dict(
            message="Sorry, category does not exist!",
            status="Fail!"
        )
        resp_obj = jsonify(resp_obj)
        return make_response(resp_obj, 404)

    @authorization_required
    @API.expect(category)
    def put(current_user, self, id):
        """
        Updates the specified category

        :param: id (int)
        """
        if not current_user:
            print(current_user, file=sys.stdout)
            resp_obj = dict(
                status="Fail!",
                message='Invalid token. Login to use this resource!'
            )
            resp_obj = jsonify(resp_obj)
            return make_response(resp_obj, 401)

        # retrieve specified category
        specified_category = current_user.categories.filter_by(id=id).first()

        if specified_category:
            # Get request data
            data = request.get_json()

            # Update category data
            specified_category.name = data['category_name']
            specified_category.description = data['description']
            db.session.commit()

            resp_obj = {
                "categories": [dict(
                    category_id=specified_category.id,
                    category_name=specified_category.name,
                    category_description=specified_category.description,
                    date_created=specified_category.created_on,
                    date_updated=specified_category.updated_on
                )],
                "status": "Success!"
            }
            resp_obj = jsonify(resp_obj)
            return make_response(resp_obj, 200)
        resp_obj = dict(
            message="Sorry, category does not exist!",
            status="Fail!"
        )
        resp_obj = jsonify(resp_obj)
        return make_response(resp_obj, 404)

    @authorization_required
    def delete(current_user, self, id):
        """
        Deletes the specified category

        :param: id (int)
        """
        if not current_user:
            print(current_user, file=sys.stdout)
            resp_obj = dict(
                status="Fail!",
                message='Invalid token. Login to use this resource!'
            )
            resp_obj = jsonify(resp_obj)
            return make_response(resp_obj, 401)

        # retrieve specified category
        specified_category = current_user.categories.filter_by(id=id).first()

        if specified_category:
            db.session.delete(specified_category)
            db.session.commit()

            resp_obj = {
                "status": "Success!"
            }
            resp_obj = jsonify(resp_obj)
            return make_response(resp_obj, 200)
        resp_obj = dict(
            message="Sorry, category does not exist!",
            status="Fail!"
        )
        resp_obj = jsonify(resp_obj)
        return make_response(resp_obj, 404)
