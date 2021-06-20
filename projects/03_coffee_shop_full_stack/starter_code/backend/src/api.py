import os
import sys
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def get_drinks():
    try:
        short_drinks = []
        drinks = Drink.query.order_by(Drink.id).all()
        for drink in drinks:
            short_drinks.append(drink.short())
        return jsonify({
            "success": True,
            "drinks": short_drinks
        })

    except:
        abort(400)

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def drink_details(payload):
    try:
        long_drinks = []
        drinks = Drink.query.order_by(Drink.id).all()
        for drink in drinks:
            long_drinks.append(drink.long())
        return jsonify({
            "success": True,
            "drinks": long_drinks
        })

    except:
        print(sys.exc_info())
        abort(400)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drink(payload):
    try:
        # Create a new drink
        body = request.get_json()
        drinkTitle = body['title']
        drinkRecipe = body['recipe']

        # Create and insert the new drink
        newDrink = Drink(
            title=drinkTitle,
            recipe=json.dumps(drinkRecipe)
        )
        newDrink.insert()

        drinkSelection = Drink.query.order_by(Drink.id).all()
        newDrinkSelection = []

        for drink in drinkSelection:
            newDrinkSelection.append(drink.long())
        return jsonify({
            "success": True,
            "drinks": newDrinkSelection
        })

    except:
        print(sys.exc_info())
        abort(400)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(payload, drink_id):
    try:
        body = request.get_json()
        drink = Drink.query.get(drink_id)

        if not drink:
            abort(404)

        # Get the json body to update the drink
        drinkTitle = body['title']
        drinkRecipe = body['recipe']
        drink.recipe = json.dumps(drinkRecipe)
        drink.title = drinkTitle
        drink.update()

        # Get the updated drink selection
        drinkSelection = Drink.query.order_by(Drink.id).all()
        newDrinkSelection = []

        for drink in drinkSelection:
            newDrinkSelection.append(drink.long())

        return jsonify({
            "success": True,
            "drinks": newDrinkSelection
        })

    except:
        abort(400)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    try:
        drink = Drink.query.get(drink_id)

        if not drink:
            abort(404)

        # Get the json body to update the drink
        drink.delete()

        # Get the updated drink selection
        drinkSelection = Drink.query.order_by(Drink.id).all()
        drinkSelection = []

        for drink in drinkSelection:
            drinkSelection.append(drink.long())

        return jsonify({
            "success": True,
            "drinks": drinkSelection
        })

    except:
        abort(400)

# Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request."
    }, 400)

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Unauthorized."
    }, 401)

@app.errorhandler(403)
def forbidden_error(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "Content Forbidden."
    }, 403)

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def no_resource(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "Resource not found"
    }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
# @app.errorhandler(403)
# def auth_error(error):
#     return jsonify({
#         "success": False
#         "code": "authorization_header_missing",
#         "description": "Authorization header is expected."
#     }, 403)