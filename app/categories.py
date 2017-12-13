"""The categories endpoints"""
import sys
from flask import request, jsonify, make_response
from flask_restplus import Resource

from .auth import authorization_required
from .models import db, Category, User
from .serializers import category
from .restplus import API

categories_ns = API.namespace('category', description='Contains endpoints for recipe categories.')

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
            print(category, file=sys.stdout)
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
                            owner=owner
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
                    description=cat.description
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