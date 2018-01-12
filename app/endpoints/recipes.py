"""The recipes endpoints"""
from flask import request, jsonify, make_response
from flask_restplus import Resource
from webargs.flaskparser import parser

from app.models import db, Recipe
from app.serializers import recipe
from app.restplus import API
from app.helpers import authorization_required, _clean_name, _pagination
from app.helpers.validators import RecipeSchema
from app.parsers import SEARCH_PAGE_ARGS, _make_args_parser

# Linting exceptions

# pylint: disable=C0103
# pylint: disable=E0213
# pylint: disable=E1101
# pylint: disable=W0613

recipes_ns = API.namespace(
    'recipes', description='The enpoints for recipe manipulation',
    path='/category/<int:category_id>/recipes'
)

args_parser = _make_args_parser(recipes_ns)
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
        data['recipe_name'] = _clean_name(data['recipe_name'])

        # initialize schema object for input validation
        recipe_schema = RecipeSchema()

        # Validate input
        data, errors = recipe_schema.load(data)
        print(data, errors)

        # Raise input validation error notification
        if errors:
            response_obj = dict(
                message="You provided some invalid details.",
                errors=errors
            )
            return make_response(jsonify(response_obj), 422)

        category = current_user.categories.filter_by(id=category_id).first()
        if category:
            new_recipe = Recipe(
                name=data['recipe_name'],
                category_id=category_id,
                user_id=current_user.id,
                ingredients=data['ingredients'],
                description=data['description']
            )
            existing_recipe = category.recipes.filter_by(name=data['recipe_name']).first()
            if not existing_recipe:
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
    @recipes_ns.expect(args_parser)
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

            # search and/or paginate
            args = parser.parse(SEARCH_PAGE_ARGS, request)
            if args:
                try:
                    recipes = category.recipes.filter(
                        Recipe.name.ilike("%" + args['q'] + "%")
                    ).paginate(page=args['page'], per_page=args['per_page'])
                except KeyError:
                    try:
                        recipes = category.recipes.\
                        paginate(page=args['page'], per_page=args['per_page'])
                    except KeyError:
                        recipes = category.recipes.paginate(error_out=False)
            else:
                recipes = category.recipes.paginate(error_out=False)
            pagination_details = _pagination(recipes)
            user_recipes = []
            for a_recipe in recipes.items:
                rec = dict(
                    recipe_name=a_recipe.name,
                    recipe_ingredients=a_recipe.ingredients,
                    recipe_description=a_recipe.description,
                    date_created=a_recipe.created_on,
                    date_modified=a_recipe.updated_on,
                )
                user_recipes.append(rec)

            resp_obj = {
                "status": "Success!",
                "recipes": user_recipes,
                "page_details": pagination_details
            }
            resp_obj = jsonify(resp_obj)
            return make_response(resp_obj, 200)
        resp_obj = dict(
            status='Fail!',
            message='Invalid category!'
        )
        resp_obj = jsonify(resp_obj)
        return make_response(resp_obj, 400)

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
            resp_obj = dict(
                status='Fail!',
                message='Invalid token. Login to use this resource!'
            )
            resp_obj = jsonify(resp_obj)
            return make_response(resp_obj, 401)

        category = current_user.categories.filter_by(id=category_id).first()
        if category:
            selected_recipe = category.recipes.filter_by(id=recipe_id).first()

            # When the recipe requested does not exist
            if not selected_recipe:
                resp_obj = dict(
                    status="Fail!",
                    message="Recipe does not exist!"
                )
                resp_obj = jsonify(resp_obj)
                return make_response(resp_obj, 404)

            # Return the recipe
            resp_obj = {
                "status": "Success!",
                "recipes": [dict(
                    recipe_name=selected_recipe.name,
                    recipe_ingredients=selected_recipe.ingredients,
                    recipe_description=selected_recipe.description,
                    date_created=selected_recipe.created_on,
                    date_updated=selected_recipe.updated_on,
                    category_name=category.name
                )]
            }
            resp_obj = jsonify(resp_obj)
            return make_response(resp_obj, 200)
        # When an invalid category id is provided
        resp_obj = dict(
            status='Fail!',
            message='Category does not exist!'
        )
        resp_obj = jsonify(resp_obj)
        return make_response(resp_obj, 404)

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
            resp_obj = dict(
                status='Fail!',
                message='Invalid token. Login to use this resource!'
            )
            resp_obj = jsonify(resp_obj)
            return make_response(resp_obj, 401)

        category = current_user.categories.filter_by(id=category_id).first()
        if category:
            selected_recipe = category.recipes.filter_by(id=recipe_id).first()

            # When the recipe requested does not exist
            if not selected_recipe:
                resp_obj = dict(
                    status="Fail!",
                    message="Recipe does not exist!"
                )
                resp_obj = jsonify(resp_obj)
                return make_response(resp_obj, 404)

            # Get request data
            data = request.get_json()

            # Update recipe
            selected_recipe.name = data['recipe_name']
            selected_recipe.ingredients = data['ingredients']
            selected_recipe.description = data['description']

            db.session.commit()

            # Return the updated recipe
            resp_obj = {
                "status": "Success!",
                "recipes": [dict(
                    recipe_name=selected_recipe.name,
                    recipe_ingredients=selected_recipe.ingredients,
                    recipe_description=selected_recipe.description,
                    date_created=selected_recipe.created_on,
                    date_updated=selected_recipe.updated_on,
                    category_name=category.name
                )]
            }
            resp_obj = jsonify(resp_obj)
            return make_response(resp_obj, 200)
        # When an invalid category id is provided
        resp_obj = dict(
            status='Fail!',
            message='Category does not exist!'
        )
        resp_obj = jsonify(resp_obj)
        return make_response(resp_obj, 404)

    @authorization_required
    def delete(current_user, self, category_id, recipe_id):
        """
        This returns a specific recipe from the specified category

        :param int category_id: The integer Id of the category\n
        :param int recipe_id: The integer Id of the recipe to be retrieved\n
        :returns json response: An appropriate response depending on the request
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
            selected_recipe = category.recipes.filter_by(id=recipe_id).first()

            # When the recipe requested does not exist
            if not selected_recipe:
                resp_obj = dict(
                    status="Fail!",
                    message="Recipe does not exist!"
                )
                resp_obj = jsonify(resp_obj)
                return make_response(resp_obj, 404)

            name = selected_recipe.name

            # Delete the selected recipe
            db.session.delete(selected_recipe)
            db.session.commit()

            # Render response
            resp_obj = {
                "status": "Success!",
                "message": "Recipe " + name + " was deleted successfully!"
            }
            resp_obj = jsonify(resp_obj)
            return make_response(resp_obj, 200)
        # When an invalid category id is provided
        resp_obj = dict(
            status='Fail!',
            message='Category does not exist!'
        )
        resp_obj = jsonify(resp_obj)
        return make_response(resp_obj, 404)
