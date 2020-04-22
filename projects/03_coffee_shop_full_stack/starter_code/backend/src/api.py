import os
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
'''
db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['GET'])
def get_drinks_short():
    all_drinks = Drink.query.all()
    drink_list = []
    for drink in all_drinks:
        drink_list.append(drink.short())
    return jsonify({
        'success': True,
        'drinks': drink_list
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
def get_drinks_detail(payload):
    drink_list = []
    all_drinks = Drink.query.all()
    for drink in all_drinks:
        drink_list.append(drink.long())
    return jsonify({
        'success': True,
        'drinks': drink_list
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
def post_drinks(payload):
    body = request.get_json()

    if body is None:
        abort(404)

    else:
        new_title = body.get('title', None)
        new_recipe = body.get('recipe', None)

        try:
            drink = Drink(
                title=new_title,
                recipe=json.dumps(new_recipe)
            )
            drink.insert()

            return jsonify({
                "success": True,
                "drinks": drink.long()
            })
        except BaseException:
            abort(422)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        done - it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(payload, drink_id):
    body = request.get_json()

    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if drink is None:
            abort(404)

        elif body is None:
            abort(404)

        else:
            if 'title' in body:
                drink.title = body.get('title')

            elif 'recipe' in body:
                drink.recipe = json.dumps(body.get('recipe'))

            drink.update()

            #show updated drink
            updated_drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

            return jsonify({
                "success": True,
                'drinks': updated_drink.long()
            })
    except BaseException:
        abort(422)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        done - it should respond with a 404 error if <id> is not found
        done - it should delete the corresponding row for <id>
        done - it should require the 'delete:drinks' permission
        done - returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, drink_id):
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if drink == None:
        abort(404)
    else:
        try:
            drink.delete()
            return jsonify({
                'success': True,
                'delete': drink_id
            })
        except BaseException:
            abort(422)


## Error Handling
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

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''


@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource not found"
    }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''


@app.errorhandler(AuthError)
def auth_error(ex):
    return jsonify({
        "success": False,
        "error": ex.status_code,
        "message": ex.error['code']
    }), 401
