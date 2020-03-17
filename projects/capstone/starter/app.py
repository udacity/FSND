import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import db, setup_db, Actor, Movie
from auth import AuthError, requires_auth

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)

  return app

APP = create_app()

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8080, debug=True)

@APP.route('/actors', methods=['GET'])
@requires_auth('get:actors')
def get_actors(token):
  try:
    actors = Actor.query.order_by('id').all()

    if len(actors) == 0:
      abort(404)

    formatted_actors = [actor.format() for actor in actors]
    return jsonify({
      'actors': formatted_actors,
      'success': True
    }), 200

  except Exception:
    abort(422)

@APP.route('/movies', methods=['GET'])
@requires_auth('get:movies')
def get_movies(token):
  try:
    movies = Movie.query.order_by('id').all()

    if len(movies) == 0:
      abort(404)

    formatted_movies = [movie.format() for movie in movies]
    return jsonify({
      'movies': formatted_movies,
      'success': True
    }), 200

  except Exception:
    abort(422)

@APP.route('/actors/<id>', methods=['PATCH'])
@requires_auth('patch:actor')
def update_actor(token, id):
    body = request.get_json()
    actor = Actor.query.get(id)

    if body == None:
      abort(404)

    if actor == None:
        abort(404)

    try:
      if 'name' in body:
        actor.name = body['name']
      
      if 'age' in body:
        actor.age = body['age']

      if 'gender' in body:
        actor.gender = body['gender']

      db.session.commit()

    except:
      db.session.rollback()
      abort(422)

    finally:
      db.session.close()

    return jsonify({
      'success': True
    }), 200

@APP.route('/movies/<id>', methods=['PATCH'])
@requires_auth('patch:movie')
def update_movie(token, id):
  body = request.get_json()
  movie = Movie.query.get(id)

  if body == None:
      abort(404)

  if movie == None:
      abort(404)

  try:
    if 'title' in body:
      movie.title = body['title']

    if 'release_date' in body:
      movie.release_date = body['release_date']

    db.session.commit()

  except:
    db.session.rollback()
    abort(422)

  finally:
    db.session.close()

  return jsonify({
    'success': True
  }), 200

@APP.route('/actors', methods=['POST'])
@requires_auth('post:actor')
def add_actor(token):
  body = request.get_json()

  if body == None:
    abort(404)

  name = body['name']
  age = body['age']
  gender = body['gender']
  
  try:
    new_actor = Actor(name=name, age=age, gender=gender)
    db.session.add(new_actor)
    db.session.commit()
    new_id = new_actor.id

  except:
    db.session.rollback()
    abort(422)

  finally:
    db.session.close()

  return jsonify({
    'id': new_id,
    'success': True
  }), 201

@APP.route('/movies', methods=['POST'])
@requires_auth('post:movie')
def add_movie(token):
  body = request.get_json()

  if body == None:
    abort(404)

  title = body['title']
  release_date = body['release_date']

  try:
    new_movie = Movie(title=title, release_date=release_date)
    db.session.add(new_movie)
    db.session.commit()
    new_id = new_movie.id

  except:
    db.session.rollback()
    abort(422)

  finally:
    db.session.close()

  return jsonify({
    'id': new_id,
    'success': True
  }), 201

@APP.route('/actors/<id>', methods=['DELETE'])
@requires_auth('delete:actor')
def delete_actor(token, id):
  actor = Actor.query.get(id)

  if actor == None:
    abort(404)

  try:
    db.session.delete(actor)
    db.session.commit()

  except:
    db.session.rollback()
    abort(422)

  finally:
    db.session.close()

  return jsonify({
    'success': True
  }), 200

@APP.route('/movies/<id>', methods=['DELETE'])
@requires_auth('delete:movie')
def delete_movie(token, id):
  movie = Movie.query.get(id)

  if movie == None:
    abort(404)

  try:
    db.session.delete(movie)
    db.session.commit()

  except:
    db.session.rollback()
    abort(422)

  finally:
    db.session.close()

    return jsonify({
      'success': True
    }), 200

@APP.errorhandler(404)
def not_found(error):
  return jsonify({
    "success": False, 
    "error": 404,
    "message": "not found"
    }), 404

@APP.errorhandler(422)
def unprocessable(error):
  return jsonify({
    "success": False, 
    "error": 422,
    "message": "unprocessable"
    }), 422

@APP.errorhandler(AuthError)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
    }), 401
