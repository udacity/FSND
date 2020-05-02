import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import setup_db, Actor, Movie


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
    def get_actors():
        actor_list = []
        actors = Actor.query.all()

        for actor in actors:
            actor_list.append(actor.format())

        return jsonify({
            'status_code': 200,
            'success': True,
            'number_of_actors': len(actor_list),
            'actors_list': actor_list
        })

    @app.route('/movies')
    def get_movies():
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
    def post_to_actors():
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
    def post_to_movies():
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
    def delete_actor(actor_id):
        actor = Actor.query.filter(Actor.id == actor_id).one_or_none()

        if actor is None:
            abort(404)

        else:
            try:
                actor.delete()

                return jsonify({
                    'status_code': 200,
                    'success': True,
                    'total_actors': len(Actor.query.all())
                })
            except BaseException:
                abort(422)

    @app.route('/movies/<int:movie_id>', methods=['DELETE'])
    def delete_movie(movie_id):

        movie = Movie.query.filter(Movie.id == movie_id).one_or_none()

        if movie is None:
            abort(404)

        else:
            try:
                movie.delete()
                return jsonify({
                    'status_code': 200,
                    'success': True,
                    'total_movies': len(Movie.query.all())
                })
            except BaseException:
                abort(422)

    @app.route('/actors/<int:actor_id>', methods=['PATCH'])
    def update_actors(actor_id):
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
                    'actor': updated_actor.format()
                })
            except BaseException:
                abort(422)

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
