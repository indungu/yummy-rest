"""The recipes endpoints"""
import sys
from flask import request, jsonify, make_response
from flask_restplus import Resource

from .auth import authorization_required
from .models import db, Recipe
from .serializers import recipe
from  .restplus import API

recipes_ns = API.namespace(
    'recipes', description='The enpoints for recipe manipulation',
    path='/category/<int:category_id>/recipes'
)

@recipes_ns.route('')
class GeneralRecipesHandler(Resource):
    """
    This class defines the endpoints for creating a single recipe
    in a particular category or retrieving all the recipes in said
    category
    """

    @authorization_required
    @API.expect(recipe)
    def post(current_user, self, category_id):
        """
        Create a recipe in the specified category

        :param int category_id: The id of the category to which recipe should be added
        """

        if not current_user:
            resp_obj = dict(
                status='Fail!',
                message='Invalid token. Login to use this resource!'
            )
            resp_obj = jsonify(resp_obj)
            return make_response(resp_obj, 401)

        data = request.get_json()        
        category = current_user.categories.filter_by(id=category_id).first()
        if category:
            new_recipe = Recipe(
                name=data['recipe_name'],
                category_id=category_id,
                user_id=current_user.id,
                ingredients=data['ingredients'],
                description=data['description']
            )
            recipe = category.recipes.filter_by(name=data['recipe_name']).first()
            if not recipe:    
                db.session.add(new_recipe)
                db.session.commit()

                resp_obj = {
                    'status': 'Success!',
                    'recipes': [dict(
                        recipe_name=new_recipe.name,
                        recipe_ingredients=new_recipe.ingredients,
                        recipe_description=new_recipe.description,
                        category=new_recipe.category_id,
                        date_created=new_recipe.created_on,
                        date_updated=new_recipe.updated_on,
                        owner=new_recipe.user_id
                    )]
                }
                resp_obj = jsonify(resp_obj)
                return make_response(resp_obj, 201)
            resp_obj = dict(
                status='Fail!',
                message='Recipe already exists!'
            )
            resp_obj = jsonify(resp_obj)
            return make_response(resp_obj, 400)
        resp_obj = dict(
            status='Fail!',
            message='Invalid category!'
        )
        resp_obj = jsonify(resp_obj)
        return make_response(resp_obj, 400)

    @authorization_required
    def get(current_user, self, category_id):
        """
        Retrives a list of the recipes for the category

        :param int category_id: The id of the category whose recipes to be displayed

        :return str status: The status of the request (Success, Fail)

        :return list recipes: The recipes in the category
        """

        if not current_user:
            resp_obj = dict(
                status='Fail!',
                message='Invalid token. Login to use this resource!'
            )
            resp_obj = jsonify(resp_obj)
            return make_response(resp_obj, 401)

        category = current_user.categories.filter_by(id=category_id).first()
        if category:
            recipes = category.recipes.all()

            if not recipes:
                resp_obj = dict(
                    status='Success!',
                    message='No recipes added to this category yet!'
                )
                resp_obj = jsonify(resp_obj)
                return make_response(resp_obj, 200)

            user_recipes = []
            for recipe in recipes:
                rec = dict(
                    recipe_name=recipe.name,
                    recipe_ingredients=recipe.ingredients,
                    recipe_description=recipe.description,
                    date_created=recipe.created_on,
                    date_modified=recipe.updated_on
                )
                user_recipes.append(rec)

            resp_obj = {
                "status": "Success!",
                "recipes": user_recipes
            }
            resp_obj = jsonify(resp_obj)
            return make_response(resp_obj, 200)
        resp_obj = dict(
            status='Fail!',
            message='Invalid category!'
        )
        resp_obj = jsonify(resp_obj)
        return make_response(resp_obj, 400)

