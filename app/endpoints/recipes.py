"""The recipes endpoints"""
from flask import request, jsonify, make_response
from flask_restplus import Resource
from webargs.flaskparser import parser

from app.models import db, Recipe
from app.serializers import recipe
from app.restplus import API
from app.helpers import (
    authorization_required, _clean_name, _pagination, is_unauthorized,
    make_payload
)
from app.helpers.validators import RecipeSchema
from app.parsers import SEARCH_PAGE_ARGS, make_args_parser

# Linting exceptions

# pylint: disable=C0103
# pylint: disable=E0213
# pylint: disable=E1101
# pylint: disable=W0613

recipes_ns = API.namespace(
    'recipes', description='The enpoints for recipe manipulation',
    path='/category/<int:category_id>/recipes'
)

args_parser = make_args_parser(recipes_ns)
def _does_not_exist():
    """Returns recipe does not exist message"""
    response_payload = dict(
        message="Recipe does not exist!"
    )
    response_payload = jsonify(response_payload)
    return make_response(response_payload, 404)

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
            return is_unauthorized()

        request_payload = request.get_json()
        request_payload['name'] = _clean_name(request_payload['name'])
        # initialize schema object for input validation
        recipe_schema = RecipeSchema()
        # Validate input
        request_payload, errors = recipe_schema.load(request_payload)
        # Raise input validation error notification
        if errors:
            response_payload = dict(
                message="You provided some invalid details.",
                errors=errors
            )
            return make_response(jsonify(response_payload), 422)
        category = current_user.categories.filter_by(id=category_id).first()
        if category:
            new_recipe = Recipe(
                name=request_payload['name'],
                category_id=category_id,
                user_id=current_user.id,
                ingredients=request_payload['ingredients'],
                description=request_payload['description']
            )
            existing_recipe = category.recipes.filter_by(
                name=request_payload['name']
            ).first()
            if not existing_recipe:
                db.session.add(new_recipe)
                db.session.commit()
                response_payload = {
                    'recipes': [make_payload(recipe=new_recipe)]
                }
                response_payload = jsonify(response_payload)
                return make_response(response_payload, 201)
            response_payload = dict(
                message='Recipe already exists!'
            )
            response_payload = jsonify(response_payload)
            return make_response(response_payload, 400)
        response_payload = dict(
            message='Invalid category!'
        )
        response_payload = jsonify(response_payload)
        return make_response(response_payload, 400)

    @authorization_required
    @recipes_ns.expect(args_parser)
    def get(current_user, self, category_id):
        """
        Retrives a list of the recipes for the category

        :param int category_id: The id of the category whose recipes to be displayed\n
        :return str status: The status of the request (Success, Fail)\n
        :return list recipes: The recipes in the category
        """

        if not current_user:
            return is_unauthorized()

        category = current_user.categories.filter_by(id=category_id).first()
        if category:
            recipes = category.recipes.all()

            if not recipes:
                response_payload = dict(
                    message='No recipes added to this category yet!'
                )
                response_payload = jsonify(response_payload)
                return make_response(response_payload, 404)

            # search and/or paginate
            args = parser.parse(SEARCH_PAGE_ARGS, request)
            if 'q' in args:
                try:
                    recipes = current_user.recipes.filter(
                        Recipe.name.ilike("%" + args['q'] + "%"),
                        Recipe.category_id == category.id
                    ).paginate(page=args['page'], per_page=args['per_page'], error_out=False)
                except KeyError:
                    recipes = current_user.recipes.filter(
                        Recipe.name.ilike("%" + args['q'] + "%"),
                        Recipe.category_id == category.id
                    ).paginate(page=1, per_page=5)
            else:
                recipes = category.recipes.paginate(per_page=2)
            base_url = request.base_url
            if 'q' in args:
                pagination_details = _pagination(recipes, base_url, q=args['q'])
            else:
                pagination_details = _pagination(recipes, base_url)
            user_recipes = []
            for current_recipe in recipes.items:
                this_recipe = make_payload(recipe=current_recipe)
                user_recipes.append(this_recipe)
            if user_recipes:
                response_payload = {
                    "recipes": user_recipes,
                    "page_details": pagination_details
                }
                return make_response(jsonify(response_payload), 200)
            response_payload = {
                "message": "Recipe does not exist."
            }
            return make_response(jsonify(response_payload), 400)
        response_payload = dict(
            message='Invalid category!'
        )
        response_payload = jsonify(response_payload)
        return make_response(response_payload, 400)

@recipes_ns.route('/<int:recipe_id>')
class SingleRecipeHandler(Resource):
    """
    This resource defines the single recipe handler endpoints
    It contains the READ, UPDATE and DELETE functionality
    """

    @authorization_required
    def get(current_user, self, category_id, recipe_id):
        """
        This returns a specific recipe from the specified category

        :param int category_id: The integer Id of the category\n
        :param int recipe_id: The integer Id of the recipe to be retrieved\n
        :returns json response: An appropriate response depending on the request
        """

        if not current_user:
            return is_unauthorized()

        category = current_user.categories.filter_by(id=category_id).first()
        if category:
            selected_recipe = category.recipes.filter_by(id=recipe_id).first()

            # When the recipe requested does not exist
            if not selected_recipe:
                return _does_not_exist()

            # Return the recipe
            response_payload = {
                "recipes": [make_payload(recipe=selected_recipe)]
            }
            response_payload = jsonify(response_payload)
            return make_response(response_payload, 200)
        # When an invalid category id is provided
        response_payload = dict(
            message='Category does not exist!'
        )
        response_payload = jsonify(response_payload)
        return make_response(response_payload, 404)

    @authorization_required
    @API.expect(recipe)
    def put(current_user, self, category_id, recipe_id):
        """
        This returns a specific recipe from the specified category

        :param int category_id: The integer Id of the category\n
        :param int recipe_id: The integer Id of the recipe to be retrieved\n
        :returns json response: An appropriate response depending on the request
        """
        if not current_user:
            return is_unauthorized()

        category = current_user.categories.filter_by(id=category_id).first()
        if category:
            selected_recipe = category.recipes.filter_by(id=recipe_id).first()

            # When the recipe requested does not exist
            if not selected_recipe:
                return _does_not_exist()
            # Get request data
            request_payload = request.get_json()
            new_recipe_name = _clean_name(request_payload['name'])
            # Check if name provided is of an existing recipe
            existing_recipe = current_user.recipes.filter(
                Recipe.name == new_recipe_name,
                Recipe.id != selected_recipe.id
            ).first()
            if not existing_recipe:
                if new_recipe_name != selected_recipe.name:
                    old_recipe_name = selected_recipe.name
                    # Update recipe
                    selected_recipe.name = new_recipe_name
                    selected_recipe.ingredients = request_payload['ingredients']
                    selected_recipe.description = request_payload['description']

                    db.session.commit()

                    # Return appropriate message saying the recipe was updated
                    response_payload = {
                        "message": "Recipe '{}' was successfully updated to '{}'.".format(
                            old_recipe_name, new_recipe_name
                        )
                    }
                else:
                    selected_recipe.ingredients = request_payload['ingredients']
                    selected_recipe.description = request_payload['description']

                    db.session.commit()

                    # Return appropriate message saying the recipe was updated
                    response_payload = {
                        "message": "Recipe '{}' was successfully updated.".format(
                            selected_recipe.name
                        ),
                        "recipe": make_payload(recipe=selected_recipe)
                    }
                response_payload = jsonify(response_payload)
                return make_response(response_payload, 200)
        # When an invalid category id is provided
        response_payload = dict(
            message='Category does not exist!'
        )
        response_payload = jsonify(response_payload)
        return make_response(response_payload, 404)

    @authorization_required
    def delete(current_user, self, category_id, recipe_id):
        """
        This returns a specific recipe from the specified category

        :param int category_id: The integer Id of the category\n
        :param int recipe_id: The integer Id of the recipe to be retrieved\n
        :returns json response: An appropriate response depending on the request
        """
        if not current_user:
            return is_unauthorized()

        category = current_user.categories.filter_by(id=category_id).first()
        if category:
            selected_recipe = category.recipes.filter_by(id=recipe_id).first()
            # When the recipe requested does not exist
            if not selected_recipe:
                return _does_not_exist()
            name = selected_recipe.name
            # Delete the selected recipe
            db.session.delete(selected_recipe)
            db.session.commit()
            # Render response
            response_payload = {
                "message": "Recipe " + name + " was deleted successfully!"
            }
            response_payload = jsonify(response_payload)
            return make_response(response_payload, 200)
        # When an invalid category id is provided
        response_payload = dict(
            message='Category does not exist!'
        )
        response_payload = jsonify(response_payload)
        return make_response(response_payload, 404)
