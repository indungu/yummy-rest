"""The categories endpoints"""
import sys
from flask import request, jsonify, make_response
from flask_restplus import Resource

from .auth import authorization_required
from .models import db, Category
from .serializers import category
from .restplus import API

categories_ns = API.namespace(
    'category', description='Contains endpoints for recipe categories.',
    path='/category'
)

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

            # check if category exists
            category = Category.query.filter_by(name=data['category_name']).first()
            if not category:
                name = data['category_name']
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

    @authorization_required
    def get(current_user, self):
        """Returns a list of user's recipe categories"""

        if current_user:
            all_categories = Category.query.filter_by(user_id=current_user.id)
            categories = []
            for cat in all_categories:
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
                "message": "Success!"
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
        category = Category.query.filter_by(id=id).first()

        if category:
            resp_obj = {
                "categories": [dict(
                    category_id=category.id,
                    category_name=category.name,
                    category_description=category.description,
                    date_created=category.created_on,
                    date_updated=category.updated_on
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
        category = Category.query.filter_by(id=id).first()

        if category:
            # Get request data
            data = request.get_json()

            # Update category data
            category.name = data['category_name']
            category.description = data['description']
            db.session.commit()

            resp_obj = {
                "categories": [dict(
                    category_id=category.id,
                    category_name=category.name,
                    category_description=category.description,
                    date_created=category.created_on,
                    date_updated=category.updated_on
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
        category = Category.query.filter_by(id=id).first()

        if category:
            db.session.delete(category)
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
