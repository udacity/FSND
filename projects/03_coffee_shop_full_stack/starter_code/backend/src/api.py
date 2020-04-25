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
                'drinks': [updated_drink.long()]
            })
    except BaseException:
        abort(422)


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

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource not found"
    }), 404


@app.errorhandler(AuthError)
def auth_error(ex):
    return jsonify({
        "success": False,
        "error": ex.status_code,
        "message": ex.error['code']
    }), 401
