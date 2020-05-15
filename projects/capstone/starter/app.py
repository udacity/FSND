import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import setup_db, Actor, Movie
from auth.auth import AuthError, requires_auth

def format_list(selection_query):
    item_list = [item.format() for item in selection_query]
    return item_list


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    @app.route('/')
    def get_greeting():
        greeting = 'it works!'
        return greeting

    @app.route('/actors')
    @requires_auth('read:actors')
    def get_actors(payload):
        actor_list = []
        actors = Actor.query.all()

        for actor in actors:
            actor_list.append(actor.format())

        return jsonify({
            'status_code': 200,
            'success': True,
            'number_of_actors': len(actor_list),
            'actor_list': actor_list
        })

    @app.route('/movies')
    @requires_auth('read:movies')
    def get_movies(payload):
        movie_list = []
        movies = Movie.query.all()

        for movie in movies:
            movie_list.append(movie.format())

        return jsonify({
            'status_code': 200,
            'success': True,
            'number_of_movies': len(movie_list),
            'movie_list': movie_list
        })

    @app.route('/actors', methods=['POST'])
    @requires_auth('post:actors')
    def post_to_actors(payload):
        body = request.get_json()

        new_name = body.get('name', None)
        new_age = body.get('age', None)
        new_gender = body.get('gender', None)

        try:
            actor = Actor(
                name=new_name,
                age=new_age,
                gender=new_gender
            )
            actor.insert()

            actor_list = format_list(Actor.query.all())

            return jsonify({
                'success': True,
                'created_id': actor.id,
                'actor_list': actor_list,
                'number_of_actors': len(actor_list)
            })

        except BaseException:
            abort(422)

    @app.route('/movies', methods=['POST'])
    @requires_auth('post:movies')
    def post_to_movies(payload):
        body = request.get_json()
        print(body)

        new_title = body.get('title', None)
        new_release_date = body.get('release_date', None)

        try:
            movie = Movie(
                title=new_title,
                release_date=new_release_date,
            )
            movie.insert()

            movie_list = format_list(Movie.query.all())

            return jsonify({
                'success': True,
                'created_id': movie.id,
                'movie_list': movie_list,
                'number_of_movies': len(movie_list)
            })

        except BaseException:
            abort(422)

    @app.route('/actors/<int:actor_id>', methods=['DELETE'])
    @requires_auth('delete:actors')
    def delete_actor(payload, actor_id):
        actor = Actor.query.filter(Actor.id == actor_id).one_or_none()

        if actor is None:
            abort(404)

        else:
            try:
                actor.delete()

                return jsonify({
                    'status_code': 200,
                    'success': True,
                    'number_of_actors': len(Actor.query.all())
                })
            except BaseException:
                abort(422)

    @app.route('/movies/<int:movie_id>', methods=['DELETE'])
    @requires_auth('delete:movies')
    def delete_movie(payload, movie_id):

        movie = Movie.query.filter(Movie.id == movie_id).one_or_none()

        if movie is None:
            abort(404)

        else:
            try:
                movie.delete()
                return jsonify({
                    'status_code': 200,
                    'success': True,
                    'number_of_movies': len(Movie.query.all())
                })
            except BaseException:
                abort(422)

    @app.route('/actors/<int:actor_id>', methods=['PATCH'])
    @requires_auth('patch:actors')
    def update_actors(payload, actor_id):
        body = request.get_json()
        actor = Actor.query.filter(Actor.id == actor_id).one_or_none()

        if actor is None:
            abort(404)

        elif body is None:
            abort(404)

        else:
            try:
                if 'name' in body:
                    actor.name = body.get('name')

                if 'age' in body:
                    actor.age = body.get('age')

                if 'gender' in body:
                    actor.gender = body.get('gender')

                actor.update()

                updated_actor = Actor.query.filter(Actor.id == actor_id).one_or_none()

                return jsonify({
                    'success': True,
                    'actor': updated_actor.format(),
                    'status_code': 200
                })
            except BaseException:
                abort(422)

    @app.route('/movies/<int:movie_id>', methods=['PATCH'])
    @requires_auth('patch:movies')
    def update_movie(payload, movie_id):
        body = request.get_json()
        movie = Movie.query.filter(Movie.id == movie_id).one_or_none()

        if movie is None:
            abort(404)

        if body is None:
            abort(404)

        else:
            try:
                if 'title' in body:
                    movie.title = body.get('title')

                if 'release_date' in body:
                    movie.release_date = body.get('release_date')

                movie.update()

                updated_movie = Movie.query.filter(Movie.id == movie_id).one_or_none()

                return jsonify({
                    'success': True,
                    'movie': updated_movie.format(),
                    'status_code': 200
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
    def not_found(error):
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

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
