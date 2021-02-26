import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import setup_db, Movie, Actor, Casting
from auth.auth import AuthError, requires_auth


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  CORS(app)
  setup_db(app)

  # access home page
  @app.route('/', methods=['GET'])
  def home():
    return jsonify({
      'success': True
    })

  # Public Endpoint fetch actors involved in a movie by movie id
  @app.route('/casting/<int:movie_id>', methods=['GET'])
  def get_actors_in_movie(movie_id):
    try:
      movie = Movie.query.filter(Movie.id == movie_id).one_or_none()

      if movie is None:
        abort(404)
      else: 
        actors = Actor.query.join(Casting).with_entities(Actor.name).filter(Actor.id==Casting.actor_id).filter(Casting.movie_id==movie_id).order_by(Casting.actor_id).all()
        #actors = Actor.query.join(Casting).filter(Actor.id==Casting.actor_id).filter(Casting.movie_id==movie_id).order_by(Casting.actor_id).all()
    # actors = Casting.query.join(Actor).filter(Casting.actor_id==Actor.id).filter(Casting.)


        return jsonify({
          'success': True,
          'movie_id': movie_id,
          'actors': [i for [i] in actors]
        })
    except Exception:
      abort(422)

# fetch all actors
  @app.route('/actors', methods=['GET'])
  @requires_auth('get:actors')
  def get_actors(jwt):
    try:
      actors = Actor.query.with_entities(Actor.id, Actor.name, Actor.age, Actor.gender).order_by(Actor.id).all()

      return jsonify({
        'success': True,
        'actors': actors
      })

    except Exception:
      abort(422)

# fetch all movies
  @app.route('/movies', methods=['GET'])
  @requires_auth('get:movies')
  def get_movies(jwt):
    try:
      movies = Movie.query.with_entities(Movie.id, Movie.title, Movie.release_date).order_by(Movie.id).all()

      return jsonify({
        'success': True,
        'movies': movies
      })

    except Exception:
      abort(422)

# remove actors by id
  @app.route('/actors/<int:actor_id>', methods=['DELETE'])
  @requires_auth('delete:actors')
  def delete_actor(jwt, actor_id):
    try:
      actor = Actor.query.filter(Actor.id == actor_id).one_or_none()

      if actor is None:
        abort(404)
      else:
        actor.delete()

      return jsonify({
        'success': True,
        'delete': actor_id
      })

    except Exception:
      abort(422)

# remove movies by id
  @app.route('/movies/<int:movie_id>', methods=['DELETE'])
  @requires_auth('delete:movies')
  def delete_movie(jwt, movie_id):
    try:
      movie = Movie.query.filter(Movie.id == movie_id).one_or_none()

      if movie is None:
        abort(404)
      else:
        movie.delete()

      return jsonify({
        'success': True,
        'delete': movie_id
      })

    except Exception:
      abort(422)

# create actors
  @app.route('/actors/add', methods=['POST'])
  @requires_auth('post:actors')
  def create_actor(jwt):
    if len(request.form) == 0:
      data = request.get_json()
      if len(data) == 0:
        abort(400)
      name = data['name']
      age = data['age']
      gender = data['gender']
    else:
      data = request.form
      name = data.get('name')
      age = data.get('age')
      gender = data.get('gender')

    new_actor = Actor(None, name, age, gender)
    try:
      new_actor.insert()
      return jsonify({
        'success': True,
         'add': {
           'name': name,
           'age': age,
           'gender': gender
         }
      })
    except:
      abort(422)

# create movies
  @app.route('/movies/add', methods=['POST'])
  @requires_auth('post:movies')
  def create_movie(jwt):
    if len(request.form) == 0: 
      data = request.get_json()    
      if len(data) == 0:
        abort(400)
      title = data['title']
      release_date = data['release_date']
    else:
      data = request.form
      title = data.get('title')
      release_date = data.get('release_date')
    new_movie = Movie(None, title, release_date)
    try:
      new_movie.insert()
      return jsonify({
        'success': True,
        'add': {
          'title': title,
          'release_date': release_date
        }
      })
    except:
      abort(422)

# assign actor to movie
  @app.route('/casting/add', methods=['POST'])
  @requires_auth('post:casting')
  def assign_actor_to_movie(jwt):
    data = request.get_json()
    movie_id = data.get('movie_id')
    actor_id = data.get('actor_id')

    new_casting = Casting(None, movie_id, actor_id)

    try:
      new_casting.insert()
      return jsonify({
        'success': True,
        'add': {
          'movie': movie_id,
          'actor': actor_id
        }
      })
    except Exception:
      abort(422)      

# update actors by id
  @app.route('/actors/<int:actor_id>', methods=['PATCH'])
  @requires_auth('patch:actors')
  def update_actor(jwt, actor_id):
    actor = Actor.query.filter_by(id=actor_id).one_or_none()
    if actor is None:
      abort(404)
    else:
      if len(request.form) == 0:  #get json data
        data = request.get_json()
        if(data.get('name')):
          actor.name = data.get('name')
        if(data.get('age')):
          actor.age = data.get('age')
        if(data.get('gender')):
          actor.gender = data.get('gender')
      else:   # get form data
        data = request.form
        actor.name = data['name']
        actor.age = data['age']
        actor.gender = data['gender']

    try:
      actor.update()
      return jsonify({
        'success': True,
        'update': actor_id
      })
    except:
      abort(422)

# update movies by id
  @app.route('/movies/<int:movie_id>', methods=['PATCH'])
  @requires_auth('patch:movies')
  def update_movie(jwt, movie_id):
    movie = Movie.query.filter_by(id=movie_id).one_or_none()
    if movie is None:
      abort(404)
    else:
      if len(request.form) == 0:
        data = request.get_json()
        if(data.get('title')):
          movie.title = data.get('title')
        if(data.get('release_date')):
          movie.release_date = data.get('release_date')
        else:
          data = request.form
          movie.title = data['movie']
          movie.release_date = data['release_date']

    try:
      movie.update()
      return jsonify({
        'success': True,
        'update': movie_id
      })
    except:
      abort(422)



  """ error handlers """
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'Resource Not Found'
    }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': 'Unprocessable'
    }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message': 'Bad Request'
    }), 400

  @app.errorhandler(500)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 500,
      'message': 'Internal Server Error'
    }), 500


  @app.errorhandler(401)
  def unauthorized(error):
      return jsonify({
          "success": False,
          "error": 401,
          "message": "Unauthorized"
      }), 401


  @app.errorhandler(403)
  def forbidden(error):
      return jsonify({
          "success": False,
          "error": 403,
          "message": "Forbidden"
      }), 403


# @app.errorhandler(AuthError)
# def autherror(Exception):
#     return jsonify({
#         "success": False,
#         "error": 401,
#         "message": "Authorization Error"
#     }), 401
  @app.errorhandler(AuthError)
  def handle_auth_error(e):
    response = jsonify(e.error)
    response.status_code = e.status_code
    return response


  return app



app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)