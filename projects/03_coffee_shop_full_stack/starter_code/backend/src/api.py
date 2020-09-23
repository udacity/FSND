import os
from flask import Flask, request, jsonify, abort, make_response
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth


def create_app():
    # create app
    app = Flask(__name__)

    # setup db
    setup_db(app)

    # set up cors for app. allows all origins
    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    """
    @TODO uncomment the following line to initialize the datbase
    !! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
    !! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
    """
    # idk wtf this is
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
        response.headers.add("Access-Control-Allow-Credentials", "true")

        return response

    ## ROUTES
    """
    @TODO implement endpoint
        GET /drinks
            it should be a public endpoint
            it should contain only the drink.short() data representation
        returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
            or appropriate status code indicating reason for failure
    """

    @app.route("/drinks")
    def get_drinks():
        drinks = Drink.query.all()

        formatted_drinks = [drink.short() for drink in drinks]

        res = make_response(
            jsonify({"success": True, "drinks": formatted_drinks}), 200
        )

        return res

    """
    @TODO implement endpoint
        GET /drinks-detail
            it should require the 'get:drinks-detail' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
            or appropriate status code indicating reason for failure
    """

    """
    @TODO implement endpoint
        POST /drinks
            it should create a new row in the drinks table
            it should require the 'post:drinks' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
            or appropriate status code indicating reason for failure
    """

    """
    @TODO implement endpoint
        PATCH /drinks/<id>
            where <id> is the existing model id
            it should respond with a 404 error if <id> is not found
            it should update the corresponding row for <id>
            it should require the 'patch:drinks' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
            or appropriate status code indicating reason for failure
    """

    """
    @TODO implement endpoint
        DELETE /drinks/<id>
            where <id> is the existing model id
            it should respond with a 404 error if <id> is not found
            it should delete the corresponding row for <id>
            it should require the 'delete:drinks' permission
        returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
            or appropriate status code indicating reason for failure
    """

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
    @TODO implement error handlers using the @app.errorhandler(error) decorator
        each error handler should return (with approprate messages):
                 jsonify({
                        "success": False, 
                        "error": 404,
                        "message": "resource not found"
                        }), 404

    """

    """
    @TODO implement error handler for 404
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
    @TODO implement error handler for AuthError
        error handler should conform to general task above 
    """

    @app.errorhandler(403)
    def unauthorized(error):
        return (
            jsonify(
                {"succcess": False, "error": 403, "message": "unauthorized"},
            ),
            403,
        )

    return app
