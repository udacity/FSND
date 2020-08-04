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
@TODO uncomment the following line to initialize the database
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()


# ROUTES


@app.route('/drinks', methods=['GET'])
def get_drinks():
    """
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    :return:
        either
            status code 200 and
            json {"success": True, "drinks": drinks}
                where drinks is the list of drinks
        or
            appropriate status code indicating reason for failure
    """
    all_drinks = Drink.query.all()
    drinks = [drink.short() for drink in all_drinks]
    body = {
        "success": True,
        "drinks": drinks
    }
    return jsonify(body)


@app.route("/drinks-detail", methods=["GET"])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    """
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    :return:
        either
            status code 200 and
            json {"success": True, "drinks": drinks}
                where drinks is the list of drinks
        or
            appropriate status code indicating reason for failure
    """
    all_drinks = Drink.query.all()
    if len(all_drinks) == 0:
        abort(404, "no drinks found")
    drinks = [drink.long() for drink in all_drinks]
    body = {
        "success": True,
        "drinks": drinks
    }
    return jsonify(body)


@app.route("/drinks", methods=["POST"])
@requires_auth('post:drinks')
def post_drinks(payload):
    """
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    :return:
        either
            status code 200 and
            json {"success": True, "drinks": drinks}
                where drinks is the list of drinks
        or
            appropriate status code indicating reason for failure
    """
    try:
        data = json.loads(request.data)
    except json.decoder.JSONDecodeError as e:
        abort(400, f'json required, got: {request.data}')

    req_recipe_data = data.get('recipe')
    req_title = data.get('title')

    try:
        if req_recipe_data and req_title:
            req_recipe = json.dumps(data.get('recipe'))
            new_drink = Drink(title=req_title, recipe=req_recipe)
            new_drink.insert()
            body = {
                "success": True,
                "drinks": new_drink.long()
            }
            return jsonify(body)
        else:
            abort(422, 'requires json containing recipe and title')
    except Exception as e:
        print(e)
        if "sqlite3.IntegrityError: UNIQUE constraint failed":
            abort(422, f'drink with title: {req_title} already exists')
        raise e


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth("patch:drinks")
def patch_drinks(payload, drink_id):
    """
    Updates an existing drink
    :param drink_id: id of drink to patch
    :return: status code 200 and json {"success": True, "drinks": drink}
                where drink an array containing only the updated drink
             or appropriate status code indicating reason for failure
    """
    try:
        data = json.loads(request.data)
    except json.decoder.JSONDecodeError as e:
        abort(400, f'json required, got: {request.data}')

    req_recipe_data = data.get('recipe')
    req_title = data.get('title')

    try:
        this_drink = Drink.query.filter(Drink.id==drink_id).one_or_none()
        if not isinstance(this_drink, Drink):
            abort(404, f'Drink with id: {drink_id} not found')
        if req_recipe_data:
            req_recipe = json.dumps(data.get('recipe'))
            this_drink.recipe = req_recipe
        if req_title:
            this_drink.title = req_title
        this_drink.update()
        body = {
            "success": True,
            "drinks": [this_drink.long()]
        }
        return jsonify(body)
    except Exception as e:
        raise e


@app.route("/drinks/<int:drink_id>", methods=['DELETE'])
@requires_auth("delete:drinks")
def delete_drinks(payload, drink_id):
    """
    Updates an existing drink
    :param drink_id: id of drink to delete
    :return: status code 200 and json {"success": True, "delete": id}
                where id is the id of the deleted record
             or appropriate status code indicating reason for failure
    """
    try:
        this_drink = Drink.query.filter(Drink.id==drink_id).one_or_none()
        if not isinstance(this_drink, Drink):
            abort(404, f'Drink with id: {drink_id} not found')
        this_drink.delete()
        body = {
            "success": True,
            "drinks": drink_id
        }
        return jsonify(body)
    except Exception as e:
        abort(422, f"Failed to delete Drink with id: {drink_id} due to: {e}")


# Error Handling


@app.errorhandler(404)
def not_found(error):
    base_message = 'NotFound'
    if hasattr(error, 'description'):
        message = f'{base_message}: {str(error.description)}'
    else:
        message = base_message
    return jsonify({
        'success': False,
        'error': 404,
        'message': message
    }), 404


@app.errorhandler(422)
def unprocessable(error):
    base_message = 'Unprocessable'
    if hasattr(error, 'description'):
        message = f'{base_message}: {str(error.description)}'
    else:
        message = base_message
    return jsonify({
        'success': False,
        'error': 422,
        'message': message
    }), 422


@app.errorhandler(AuthError)
def authorization_error(e):
    return jsonify({
        'success': False,
        'error': e.status_code,
        'message': e.error
    }), e.status_code


if __name__ == "__main__":
    app.run()