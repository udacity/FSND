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
# db_drop_and_create_all()

## ROUTES ##
## GET /drinks
# returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
#   or appropriate status code indicating reason for failure
@app.route('/drinks', methods=['GET'])
def get_drinks():
    all_drinks = Drink.query.all()

    if len(all_drinks) == 0:
        abort(404)

    drinks = [drink.short() for drink in all_drinks]
    return jsonify({
        "success": True,
        "drinks": drinks
    }) 

## GET /drinks-detail
# returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
#   or appropriate status code indicating reason for failure
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drink_details(jwt):
    all_drinks = Drink.query.all()
    
    if len(all_drinks) == 0:
        abort(404)

    drinks = [drink.long() for drink in all_drinks] 
    return jsonify({
        'success': True,
        'drinks': drinks
    }) 

## POST /drinks
# returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
#   or appropriate status code indicating reason for failure
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(jwt):
    body = request.get_json()

    if body == None:
        abort(404)

    new_title = body.get('title')
    new_recipe = body.get('recipe')

    try:
        new_drink = Drink(title=new_title, recipe=json.dumps(new_recipe))
        new_drink.insert()
        drink = new_drink.long()

        return jsonify({
            'success': True,
            'drinks': drink
        }) 

    except:
        abort(404)

## PATCH /drinks/<id>
# returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
#   or appropriate status code indicating reason for failure
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(jwt, drink_id):
    body = request.get_json()
    selected_drink = Drink.query.get(drink_id)

    if selected_drink == None:
        abort(404)

    if body == None:
        abort(404)

    try:
        selected_drink.title = body.get('title')
        selected_drink.recipe = json.dumps(body.get('recipe'))
        selected_drink.update()

        return jsonify({
            'success': True,
            'drinks': [selected_drink.long()]
        }) 

    except:
        abort(404)

## DELETE /drinks/<id>
# returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
#   or appropriate status code indicating reason for failure
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, drink_id):
    selected_drink = Drink.query.get(drink_id)

    if selected_drink == None:
        abort(404)

    try:
        selected_drink.delete()

        return jsonify({
            'success': True,
            'delete': drink_id
        }) 

    except:
        abort(404)


## Error Handling
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

@app.errorhandler(404)
def notfound(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "not found"
    }), 404

@app.errorhandler(AuthError)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
    }), 401
