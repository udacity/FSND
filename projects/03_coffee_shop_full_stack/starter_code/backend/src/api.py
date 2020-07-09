import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth, setup_auth

app = Flask(__name__)


setup_db(app)
setup_auth(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
#db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = Drink.query.all()
    formatted_drinks = [drink.short() for drink in drinks]
    # for drink in drinks:
    #    app.logger.info("Drink: " + str(drink.title) + " Recipe: " + str(drink.recipe))

    return jsonify({
        'success': True,
        'drinks': formatted_drinks
    })



'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''



@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    #print(jwt)
    setup_auth(app)
    app.logger.info('reached drinks detail function')
    drinks = Drink.query.all()
    formatted_drinks = [drink.long() for drink in drinks]

    return jsonify({
        'success': True,
        'drinks': formatted_drinks
    })


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
def create_drink(jwt):
    body = request.get_json()
    #app.logger.info('Body:' + body)
    title = body['title']

    recipe = body['recipe']
    drink_recipe = []
    app.logger.info("recipe")
    app.logger.info(recipe)

    if type(recipe) is dict:
        ingredient_name = recipe['name']
        ingredient_color = recipe['color']
        ingredient_parts = recipe['parts']
        drink_recipe.append({
                'name': ingredient_name,
                'color': ingredient_color,
                'parts': ingredient_parts
            })
    else:
        for ingredient in recipe:
            ingredient_name = ingredient['name']
            ingredient_color = ingredient['color']
            ingredient_parts = ingredient['parts']
            drink_recipe.append({
                'name': ingredient_name,
                'color': ingredient_color,
                'parts': ingredient_parts
            })

    json_drink_recipe = json.dumps(drink_recipe)

    drink = Drink(title=title, recipe=json_drink_recipe)
    app.logger.info(json_drink_recipe)

    drink.insert()


    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })


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
def update_drink(jwt, drink_id):
    token = request.headers['Authorization']
    app.logger.info('Token: ' + token)
    body = request.get_json()
    drink = Drink.query.get(drink_id)
    if drink is None:
        abort(404)

    drink_recipe = []

    if 'title' in body:
        drink.title = body['title']

    if 'recipe' in body:

        for ingredient in body['recipe']:
            ingredient_name = ingredient['name']
            ingredient_color = ingredient['color']
            ingredient_parts = ingredient['parts']
            drink_recipe.append({
                'name': ingredient_name,
                'color': ingredient_color,
                'parts': ingredient_parts
            })


        json_drink_recipe = json.dumps(drink_recipe)
        drink.recipe = json_drink_recipe

    drink.update()

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })


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
def delete_drink(jwt, drink_id):
    app.logger.info(drink_id)

    drink = Drink.query.get(drink_id)
    if drink is None:
        abort(404)

    app.logger.info(drink)
    drink.delete()
    return jsonify({
        'success': True,
        'delete': drink_id
    })

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


@app.errorhandler(401)
def unauthorized(err):
    return jsonify({
        'success': False,
        'error': 401,
        'message': err.description
    }), 401

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def not_found(err):
    return jsonify({
        "success": False,
        "error": 404,
        "message": err.description
    }), 404




'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def authentication_error(err):
    return jsonify({
        'success': False,
        'error': err.status_code,
        'message': err.error
    }), err.status_code
