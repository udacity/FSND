import os
from flask import Flask, request, jsonify, abort, make_response
from sqlalchemy import exc
import json
from flask_cors import CORS

from models import db_drop_and_create_all, setup_db, Movie, Actor
from auth import AuthError, requires_auth
from config import Config


def create_app():
    # create app
    app = Flask(__name__)

    app.config.from_object("config.Config")

    # setup db
    setup_db(app)

    # set up cors for app. allows all origins
    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    db_drop_and_create_all()

    # decorate response with headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,POST,DELETE,OPTIONS"
        )

        return response

    ## ROUTES
    """
        GET /drinks
            it should be a public endpoint
            it should contain only the drink.short() data representation
        returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
            or appropriate status code indicating reason for failure
    """

    @app.route("/actors")
    def get_actors():
        actors = Actor.query.all()

        res = make_response(jsonify({"success": True, "actors": actors}), 200)

        return res

    """
        GET /drinks-detail
            it should require the 'get:drinks-detail' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
            or appropriate status code indicating reason for failure
    """

    @app.route("/drinks-detail")
    @requires_auth("get:drinks-detail")
    def get_drinks_detail(payload):
        drinks = [drink.long() for drink in Drink.query.all()]

        res = make_response(jsonify({"success": True, "drinks": drinks}), 200)

        return res

    """
        POST /drinks
            it should create a new row in the drinks table
            it should require the 'post:drinks' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
            or appropriate status code indicating reason for failure
    """

    @app.route("/drinks", methods=["POST"])
    @requires_auth("post:drinks")
    def create_drink(payload):
        # get drink info from payload
        body = request.get_json()

        # get title and recipe
        title = body.get("title")
        recipe = body.get("recipe")
        recipe_items = recipe.items()

        # enforce required fields validation
        if not all([title, recipe]):
            abort(400, description="Required fields are missing")
        elif len(recipe_items) != 3:
            abort(400, description="Required fields are missing")

        # create Drink and insert to db
        new_drink = Drink(title=title, recipe=json.dumps(recipe))
        # add to db
        new_drink.insert()

        return jsonify({"success": True, "drinks": [new_drink.long()]})

    """
    implement endpoint
        PATCH /drinks/<id>
            where <id> is the existing model id
            it should respond with a 404 error if <id> is not found
            it should update the corresponding row for <id>
            it should require the 'patch:drinks' permission
            it should contain the drink.long() data representation
            returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing
            or appropriate status code indicating reason for failure
    """

    @app.route("/drinks/<int:drink_id>", methods=["PATCH"])
    @requires_auth("patch:drinks")
    def update_drink(payload, drink_id):
        body = request.get_json()

        # check to see if drink exists
        drink = Drink.query.filter_by(id=drink_id).first_or_404()

        if not any([body.get("title"), body.get("recipe")]):
            abort(400, description="Required fields are missing")
        elif ("recipe" in body) and not (
            all(
                any([item["color"], item["name"], item["parts"]])
                for item in body["recipe"]
            )
        ):
            abort(400, description="Required fields are missing")

        new_drink = drink

        # check the body for parts of drink
        for k, v in body.items():
            if k == "title":
                new_drink.title = v
            elif k == "recipe":
                new_drink.recipe = json.dumps(v)

        new_drink.update()

        return jsonify({"success": True, "drinks": [new_drink.long()]})

        # check for required parts of payload

    """
    implement endpoint
        DELETE /drinks/<id>
            where <id> is the existing model id
            it should respond with a 404 error if <id> is not found
            it should delete the corresponding row for <id>
            it should require the 'delete:drinks' permission
        returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
            or appropriate status code indicating reason for failure
    """

    @app.route("/drinks/<int:drink_id>", methods=["DELETE"])
    @requires_auth("delete:drinks")
    def delete_drink(payload, drink_id):
        # get drink or 404
        drink = Drink.query.filter_by(id=drink_id).first_or_404()

        drink.delete()

        res = make_response(jsonify({"success": True, "delete": drink_id}), 200)

        return res

    ## Error Handling
    """
    Example error handling for unprocessable entity
    """

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify(
                {"success": False, "error": 422, "message": "unprocessable"}
            ),
            422,
        )

    """
    implement error handlers using the @app.errorhandler(error) decorator
        each error handler should return (with approprate messages):
                 jsonify({
                        "success": False, 
                        "error": 404,
                        "message": "resource not found"
                        }), 404

    """

    """
    error handler should conform to general task above 
    """

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify(
                {
                    "success": False,
                    "error": 404,
                    "message": "resource not found",
                },
            ),
            404,
        )

    """
    implement error handler for AuthError
    error handler should conform to general task above 
    """

    # @app.errorhandler(403)
    # def unauthorized(error):
    #     return (
    #         jsonify(
    #             {"succcess": False, "error": 403, "message": "unauthorized"},
    #         ),
    #         403,
    #     )

    @app.errorhandler(AuthError)
    def handle_auth_error(ex):
        res = jsonify(ex.error)
        res.status_code = ex.status_code

        return res

    return app
