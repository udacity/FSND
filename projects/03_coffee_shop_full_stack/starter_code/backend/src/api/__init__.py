import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from database.models import db_drop_and_create_all, setup_db, Drink
from auth.auth import AuthError, requires_auth

def create_app():
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    '''
    @TODO uncomment the following line to initialize the datbase
    !! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
    !! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
    '''
    #db_drop_and_create_all()

    ## ROUTES

    # @app.route("/")
    # def home():
    #     return "this is home route"

    '''
    TODO implement endpoint
        GET /drinks
            it should be a public endpoint
            it should contain only the drink.short() data representation
        returns status code 200 and json {"success": True, "drinks": drinks_short} where drinks is the list of drinks
            or appropriate status code indicating reason for failure
    '''
    @app.route('/drinks', methods = ['GET'])
    def get_drinks_short():
        try: 
            drinks_detailed = Drink.query.with_entities(Drink.id, Drink.title, Drink.recipe).order_by(Drink.id).all()
            # drink = Drink(drinks[0].title, drinks[0].recipe)
            # drinks_detailed = [Drink(x.id, x.title,x.recipe) for x in drinks_query]
            drinks = [Drink(x.id,x.title,x.recipe)for x in drinks_detailed]
            drinks_short = [x.short() for x in drinks]

            return jsonify({
                "success": True,
                "drinks": drinks_short
            })
        except:
            abort(422)

    '''
    @TODO implement endpoint
        GET /drinks-detail
            it should require the 'get:drinks-detail' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink_list} where drinks is the list of drinks
            or appropriate status code indicating reason for failure
    '''
    @app.route('/drinks-detail', methods = ['GET'])
    @requires_auth('get:drinks-detail')
    def get_drinks_long(jwt):
        try: 
            drinks_detailed = Drink.query.with_entities(Drink.id, Drink.title, Drink.recipe).order_by(Drink.id).all()
            drinks = []

            for i in range(len(drinks_detailed)):
                recipe = json.loads(drinks_detailed[i].recipe)
                drink = {'id': drinks_detailed[i].id, 'title': drinks_detailed[i].title, 'recipe': recipe}
                drinks.append(drink)
                # drink = {i+1: {'id': drinks_detailed[i].id, 'title': drinks_detailed[i].title, 'recipe': drinks_detailed[i].recipe}}
            # drinks = [Drink(x.id, x.title,x.recipe) for x in drinks_detailed]

            #drink_list = json.dumps(drinks)

            return jsonify({
                "success": True,
                "drinks": drinks
            })
        except:
            abort(422)


    '''
    @TODO implement endpoint
        POST /drinks
            it should create a new row in the drinks table
            it should require the 'post:drinks' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
            or appropriate status code indicating reason for failure
    '''
    @app.route('/drinks', methods = ['POST'])
    @requires_auth('post:drinks')
    def add_drink(jwt):
        data = request.get_json()
        str_recipe = json.dumps(data['recipe'])
        new_drink = Drink(None, data['title'], str_recipe)
        try:
            new_drink.insert()
            drink = Drink.query.with_entities(Drink.id).filter(Drink.title==data['title']).one_or_none()
            return jsonify({
            'success': True,
            'drinks': [{'id':drink.id, 'title':data['title'],'recipe':data['recipe']}]
            })
        except:
            abort(422)


    '''
    TODO implement endpoint
        PATCH /drinks/<id>
            where <id> is the existing model id
            it should respond with a 404 error if <id> is not found
            it should update the corresponding row for <id>
            it should require the 'patch:drinks' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
            or appropriate status code indicating reason for failure
    '''
    @app.route('/drinks/<id>', methods = ['PATCH'])
    @requires_auth('patch:drinks')
    def update_drink(jwt,id):
        data = request.get_json()
        str_recipe = json.dumps(data['recipe'])
        updated_drink = Drink(id, data['title'], str_recipe)
        try:
            updated_drink.update()
            return jsonify({
                'success': True,
                'drinks': [{'id':id,'title':data['title'],'recipe':data['recipe']}]
            })
        except:
            abort(422)
        

    '''
    TODO implement endpoint
        DELETE /drinks/<id>
            where <id> is the existing model id
            it should respond with a 404 error if <id> is not found
            it should delete the corresponding row for <id>
            it should require the 'delete:drinks' permission
        returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
            or appropriate status code indicating reason for failure
    '''
    @app.route('/drinks/<id>', methods = ['DELETE'])
    @requires_auth('delete:drinks')
    def delete_drink(jwt,id):
        try:
            drink = Drink.query.with_entities(Drink.id,Drink.title,Drink.recipe).filter(Drink.id==id).one_or_none()
            if drink is None:
                abort(404)

            drink_to_delete = Drink(drink.id,drink.title,drink.recipe)
            drink_to_delete.delete()
            return jsonify({
                    'success': True,
                    'delete': id
            })
        except:
            abort(422)
                

    ## Error Handling

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
                        "success": False, 
                        "error": 422,
                        "message": "unprocessable"
                        }), 422

    '''
    TODO implement error handlers using the @app.errorhandler(error) decorator
        each error handler should return (with approprate messages):
                jsonify({
                        "success": False, 
                        "error": 404,
                        "message": "resource not found"
                        }), 404

    '''

    '''
    TODO implement error handler for 404
        error handler should conform to general task above 
    '''
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource Not Found"
        }), 404


    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request"
        }), 400

    @app.errorhandler(500)
    def Internal_Server_Error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal Server Error"
        }), 500

    '''
    TODO implement error handler for AuthError
        error handler should conform to general task above 
    '''
    @app.errorhandler(401)
    def Unauthorized_Error(error):
        return jsonify({
            "success": False,
            "error": 401,
            "message": "Unauthorized"
        }), 401

    return app