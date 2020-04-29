import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import setup_db, Actor, Movie


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
            'num_of_actors': len(actor_list),
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
            'num_of_movies': len(movie_list),
            'actors_list': movie_lsit
        })

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
