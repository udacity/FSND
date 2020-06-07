import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from flask_migrate import Migrate
from .database.models import db, db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth
import traceback


def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    CORS(app)
    if test_config:
        app.config.from_mapping(test_config)

    '''
    @TODO uncomment the following line to initialize the datbase
    !! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
    !! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
    '''
    db_drop_and_create_all()
    Migrate(app, db)

    # ROUTES
    @app.route('/')
    @requires_auth('get:drinks-detail')  # no public endpoint
    def index(payload):
        return 'Permission granted'

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
        drinks = [drink.short() for drink in db.session.query(Drink).all()]

        # Newer version of Flask can return dicts with a 200 status code
        return {"success": True, "drinks": drinks}

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
    def get_drinks_detail(payload):
        drinks = [drink.long() for drink in db.session.query(Drink).all()]

        return {'success': True, 'drinks': drinks}
    '''
    @TODO implement endpoint
        POST /drinks
            it should create a new row in the drinks table
            it should require the 'post:drinks' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
            or appropriate status code indicating reason for failure

        accepts as input:
            {
                "title": "Water3",
                "recipe": {
                    "name": "Water",
                    "color": "blue",
                    "parts": 1
            }
}
    '''
    @app.route('/drinks', methods=['POST'])
    @requires_auth('post:drinks')
    def post_drink(payload):
        data = request.get_json()
        if isinstance(data, str):  # ensure data is object of type dict
            data = json.loads(data)

        # Verify format & validity of request body to return helpful error codes to users
        if len(data.keys()) > 2:
            abort(400, description={'code': 'malformatted',
                                    'description': 'Too many keys in JSON body.'})
        if len(data.keys()) < 2:
            abort(400, description={'code': 'malformatted',
                                    'description': 'Too few keys in JSON body.'})
        if not all(req_attribute in data
                   for req_attribute in ['title', 'recipe']):
            abort(400, description={'code': 'missing_required_attribute',
                                    'description': 'A required key was missing in JSON body.'})

        # Verify if new entry, to protect data hygiene
        duplicates_result = Drink.query.filter(
            Drink.title.ilike(data['title'].lower())).all()
        if len(duplicates_result) > 0:
            abort(
                402,
                description={'code': 'duplicate_insertion',
                             'description': 'An entry was already present.'})

        try:
            # wrap dict into list as supported type of recipe col
            data['recipe'] = json.dumps([data['recipe']])
            new_drink = Drink(
                title=data['title'],
                recipe=json.dumps(data['recipe']))
            new_drink.insert()
            drinks = [drink.long() for drink in db.session.query(Drink).all()]
            added = db.session.query(Drink).filter_by(
                title=data['title']).first()
            return {'success': True, 'new_drink': added.short(), 'drinks': drinks}
        except Exception as e:
            db.session.rollback()
            print('rolled back because of error:', e)
            print(traceback.print_exc())
        finally:
            db.session.close()
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
    @app.route('/drinks/<drink_id>', methods=['PATCH'])
    @requires_auth('patch:drinks')
    def update_drink(payload, drink_id):
        # Parse data from JSON body
        data = request.get_json()
        if isinstance(data, str):
            data = json.loads(data)

        # Verify if request formatted well
        if not data:
            abort(400)
        # Verify if resource's present
        update_drink = db.session.query(Drink).get(drink_id)
        if update_drink is None:
            abort(404)
        # Update drink dynamically to allow JSON body to have multiple keys
        for key in data.keys():
            try:
                setattr(update_drink, key, data[key])
                db.session.commit()
                drinks = [drink.long()
                          for drink in db.session.query(Drink).all()]
                return {'success': True, 'updated': update_drink.short(), 'drinks': drinks}
            except Exception as e:
                print('Could not update', key)
                db.session.rollback()
                print('Rolled back db session')
                print(traceback.print_exc())
                abort(400)
            finally:
                db.session.close()

    '''
    @TODO implement error handler for AuthError
        error handler should conform to general task above
    '''
    @ app.errorhandler(401)
    def unauthorized(error):
        return {
            "success": False,
            "error": 401,
            "message": "unauthorized",
            "error_type": error.description['code'],
            "additional_info": error.description['description']
        }, 401
    return app


# ROUTES


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


# Error Handling
'''
Example error handling for unprocessable entity
'''


# @app.errorhandler(422)
# def unprocessable(error):
#     return jsonify({
#         "success": False,
#         "error": 422,
#         "message": "unprocessable"
# }), 422


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
