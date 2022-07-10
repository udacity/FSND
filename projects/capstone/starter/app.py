import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import setup_db, Actor, Movie
from auth import requires_auth, check_permissions

ACTORS_PER_PAGE = 10
MOVIES_PER_PAGE = 10

def create_app(test_config = None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)

  @app.after_request
  def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type, Authorization')
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET, POST, PATCH, DELETE, OPTIONS')
        return response

  @app.route('/')
  def get_greeting():
      greeting = "Hello There!!!" 
      return greeting

  # Gets all the Actors, 10 Actors per page

  @app.route('/actors', methods = ['GET'])
  @requires_auth('get:actors')
  def getActors():
    try: 
      allActors = Actor.query.order_by(Actor.id).all()
      page = request.args.get('page', 1, type=int)
      start = (page - 1) * 10
      end = start + 10
      selectedActors = [actor.format() for actor in allActors]
      pagedActors = selectedActors[start:end]
      return jsonify({
          'success': True,
          'actors': pagedActors,
          'totalActors': len(allActors),
      })
    except Exception:
      abort(404)

  # Gets all the Movies, 10 Movies per page

  @app.route('/movies', methods = ['GET'])
  @requires_auth('get:movies')
  def getMovies():
    try: 
      allMovies = Movie.query.order_by(Movie.id).all()
      page = request.args.get('page', 1, type=int)
      start = (page - 1) * 10
      end = start + 10
      selectedMovies = [actor.format() for actor in allMovies]
      pagedMovies = selectedMovies[start:end]
      return jsonify({
          'success': True,
          'movies': pagedMovies,
          'totalMovies': len(allMovies),
      })
    except Exception:
      abort(404)

  # Insert An Actor

  @app.route('/actors', methods=['POST'])
  @requires_auth('post:actors')
  def post_actor():
      body = request.get_json()
      if body is None:
        abort(405)

      if body.get('name') is None or body.get('age') is None or body.get('gender') is None:
        abort(405)
        
      try:
        new_name = body.get('name')
        new_age = body.get('age')
        new_gender = body.get('gender')
        actor = Actor(
              name = new_name,
              age = new_age,
              gender = new_gender)
        actor.insert()
        return jsonify({
            'success': True,
            'added_actor': actor.id
        })
      except BaseException:
          abort(404)
      

  # Update An Actor

  @app.route('/actors/<actor_id>', methods=['PATCH'])
  @requires_auth('patch:actor')
  def update_actor(actor_id):
    actor = Actor.query.filter(Actor.id == actor_id).first()
    if not actor:
      abort(404)
    body = request.get_json()
    if body is None:
      abort(422)
    try:
        if 'name' in body:
          actor.name = body['name']
        if 'age' in body:
          actor.age = body['age']
        if 'gender' in body:
          actor.gender = body['gender']
        actor.update()
        return jsonify({
            'success': True,
            'updated_actor': actor.id
        })
    except BaseException:
        abort(404)


  # Delete An Actor

  @app.route('/actors/<actor_id>', methods=['DELETE'])
  @requires_auth('delete:actor')
  def delete_actor(actor_id):
      try:
          question = Actor.query.get(actor_id)
          question.delete()
          return jsonify({
              'success': True,
              'deleted_question': actor_id
          })
      except BaseException:
          abort(404)

  # Error Handlers: 401, 403, 404, 405

  @app.errorhandler(401)
  def unauthorised(error):
    return jsonify({
      "success": False,
      "error": 401,
      "msg": "Unauthorised :("
    }), 401

  @app.errorhandler(403)
  def unauthorised(error):
    return jsonify({
      "success": False,
      "error": 403,
      "msg": "Access Forbidden :("
    }), 403

  @app.errorhandler(404)
  def unauthorised(error):
    return jsonify({
      "success": False,
      "error": 404,
      "msg": "Not Found :("
    }), 404

  @app.errorhandler(405)
  def unauthorised(error):
    return jsonify({
      "success": False,
      "error": 405,
      "msg": "Method Not Allowed :("
    }), 405


  return app

APP = create_app()

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8080, debug=True)