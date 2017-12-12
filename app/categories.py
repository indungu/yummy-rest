"""The categories endpoints"""
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
                            category_name=name,
                            description=description,
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
