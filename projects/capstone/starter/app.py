import os
from flask import Flask, request, abort, jsonify, redirect, url_for, session, render_template
import requests
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import setup_db, Actor, Movie
from auth.auth import AuthError, requires_auth, setup_auth, set_current_token
from dotenv import load_dotenv, find_dotenv
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode
import http.client

AUTH0_DOMAIN = 'dev-md-8ge9f.us.auth0.com'
AUTH0_AUDIENCE = 'movie_producer'
AUTH0_CLIENT_ID = 'FxBGhksxly32jgz0V7A7KdiazMScOpSk'
AUTH0_CLIENT_SECRET = 'CPRiVbCsacuO2AKnwgS8t-XQl1gw5W3bDQeEpSR5aMqFrSDRxNwMGiYEx5xqDixJ'
AUTH0_CALLBACK = 'http://localhost:5000/login/callback'
API_BASEURL = f'http://{AUTH0_DOMAIN}'

LOGOUT_LINK = 'http://dev-md-8ge9f.us.auth0.com/v2/logout?returnTo=http://localhost:5000&client_id=FxBGhksxly32jgz0V7A7KdiazMScOpSk'

EXECUTIVE_TOKEN = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IndaUHJBLTNkemg4M05EU19ndjdyNiJ9.eyJpc3MiOiJodHRwczovL2Rldi1tZC04Z2U5Zi51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NWYwMjE2NGRhMWY2MDMwMDE5YjA3YTJmIiwiYXVkIjoibW92aWVfcHJvZHVjZXIiLCJpYXQiOjE1OTQ0MDQwNzksImV4cCI6MTU5NDQ5MDQ3OSwiYXpwIjoiRnhCR2hrc3hseTMyamd6MFY3QTdLZGlhek1TY09wU2siLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImRlbGV0ZTphY3RvcnMiLCJkZWxldGU6bW92aWVzIiwiZ2V0OmFjdG9ycyIsImdldDptb3ZpZXMiLCJwYXRjaDphY3RvcnMiLCJwYXRjaDptb3ZpZXMiLCJwb3N0OmFjdG9ycyIsInBvc3Q6bW92aWVzIl19.RQs5jWa7yvFEy1q58B-gy76Vtw48T16OHMHXqOcDeVufs_hJ0h-iy3J8dXKne9Cz7TRMiobvvHkrSBqGF1XOT3X4SYyAOgXdu45YgUdVZigpgnH-4SHSCeP6SEK0UZaNvncXioznfvUIXFrQQHW3sZXBtQaSUFFEEYhD50Gy3gdm6dd9Jq2fBtkXW6cHkEtqoVqYdPkiFhtMLCD8KNbk0t3vA6PiXOgFV6S5Rtlq2s08nh3jYz98ZwSLlg96wtQSdKLc6jXU6snWOGrRecWosozD_6mt5knmUPc4CmwUUOY0Xg0Io3sw1PM38SfQRL3DbvMbYaZPTChxnYSe_oN71g'
CASTING_DIRECTOR = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IndaUHJBLTNkemg4M05EU19ndjdyNiJ9.eyJpc3MiOiJodHRwczovL2Rldi1tZC04Z2U5Zi51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NWYwNzdjMGZmZDMwZTIwMDEzNjY1MDA1IiwiYXVkIjoibW92aWVfcHJvZHVjZXIiLCJpYXQiOjE1OTQ0MDU3NzgsImV4cCI6MTU5NDQ5MjE3OCwiYXpwIjoiRnhCR2hrc3hseTMyamd6MFY3QTdLZGlhek1TY09wU2siLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImRlbGV0ZTphY3RvcnMiLCJnZXQ6YWN0b3JzIiwiZ2V0Om1vdmllcyIsInBhdGNoOmFjdG9ycyIsInBvc3Q6YWN0b3JzIl19.pi_5whggjUTeazg80Jd66x0Et7fgn6DC828M2vKaVT0Fy5A2GpjPe6WQtHKLHF8Sf0_r-SUGpNTjakp44xBEZxEeTMft3qS6beHTfhU2Y1Op3K1bD2ExNBS5dEZYCBCFNzs3WBHXGgKQaACww82BnSE4kK0lYsZKMLl4k1jMKtxi_ZsS_RuS-MTMrMHiKClIPzssTuh3Bb7fWBpb1fPAPYCN3c6vWonBAJqeKKI4Q2PInYw1jlS68OKJFOWSkNUNzvJKwVJWhrqzk-IvPvbdjuhz24on5_BoB3PmOjTk7xr_KAT9WH5gXuhaFPc5zIT1_3pSWmwPy4ensHAWvRCRHw'
ASSISTANT_DIRECTOR = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IndaUHJBLTNkemg4M05EU19ndjdyNiJ9.eyJpc3MiOiJodHRwczovL2Rldi1tZC04Z2U5Zi51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NWYwOGIzNGVhMTViN2IwMDEzNjIwOWJhIiwiYXVkIjoibW92aWVfcHJvZHVjZXIiLCJpYXQiOjE1OTQ0MDU5NjUsImV4cCI6MTU5NDQ5MjM2NSwiYXpwIjoiRnhCR2hrc3hseTMyamd6MFY3QTdLZGlhek1TY09wU2siLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImdldDphY3RvcnMiLCJnZXQ6bW92aWVzIl19.mS-xrmUbuFuQ5b7iV_mZlaoZ2wBRFbq5tpDS2z5VfGDE-yeILHxoGvqgClqX7G2P1HVrHjnwKI5oTtIskmZp_u5zvucbPYaYDn2iOVOw7exJFDeAOKKMo6zs3kGyDD2XdrWIqCA6CxoJQ5_GkMItkorhy-1GEQgb5FdARrbinUZ_fDB0u8LZiR1jpu7DvuPgD8e6XWdTij6SDhkfXmzvZHRkpi-TOT96OdhYj2cR5wFCKjj82CPllCWkDnw8ebGqsvRXluXUKzwXbIVqL8sjSvgtVqzs7qok-CO_bkp3YZuf0_RWRD7FVX1oRaBmp0InD2dmWzTn8PKcPirZXlWufg'


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    app.secret_key = 'super secret key'
    database_connection = 'postgresql://postgres:adil1234@localhost:5432/capstonedb'
    setup_db(app, database_connection)
    setup_auth(app)
    CORS(app)
    current_token = None
    oauth = OAuth(app)
    auth0 = oauth.register(
        'auth0',
        client_id=AUTH0_CLIENT_ID,
        client_secret=AUTH0_CLIENT_SECRET,
        api_base_url=API_BASEURL,
        access_token_url=f'{API_BASEURL}/oauth/token',
        authorize_url=f'{API_BASEURL}/authorize')

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    def get_app():
      return app

    @app.route('/')
    def index():
        return("Hello worlds")

    @app.route('/show-token')
    def show_token():
      return jsonify({
        'token': current_token
      })

    @app.route('/login')
    def login_redirect():
        return auth0.authorize_redirect(redirect_uri='http://localhost:5000/login/callback', audience='movie_producer', response_type='token')
        # webbrowser.open(f'https://{AUTH0_DOMAIN}/authorize?audience={AUTH0_AUDIENCE}&response_type=token&client_id={AUTH0_CLIENT_ID}&redirect_uri={AUTH0_CALLBACK}')
        # return("You are logged in!")

    @app.route('/login/callback')
    def login_callback():
        #access_token = request.args.get('access_token')
        #access_token = auth0.get('access_token')
        app.logger.info(request.get_data())

        # auth0.authorize_access_token()
        app.logger.info('successfully logged in!')
        # auth0.authorize_access_token()
        return render_template('login_callback.html')

    @app.route('/logout')
    def logout():
        session.clear()
        #LOGOUT_LINK = 'http://dev-md-8ge9f.us.auth0.com/v2/logout?returnTo=http://localhost:5000&client_id=FxBGhksxly32jgz0V7A7KdiazMScOpSk'

        #params = {'returnTo': 'http://localhost:5000', 'client_id': 'FxBGhksxly32jgz0V7A7KdiazMScOpSk'}
        #r = requests.get(AUTH0_DOMAIN + '/v2/logout', params=params)
        # return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))
        return 'Successfully logged out!'

    @app.route('/login/get_access_token', methods=['POST'])
    def get_access_token():
        token = str(request.get_data())
        token = token.split('=')[1][:-1]
        app.logger.info(token)
        current_token = token
        set_current_token(token)
        return redirect('/')

    @app.route('/actors', methods=['GET'])
    @requires_auth('get:actors')
    def get_actors(jwt):
        actors = Actor.query.all()

        formatted_actors = [actor.format() for actor in actors]

        return jsonify({
            'success': True,
            'actors': formatted_actors
        })

    @app.route('/movies', methods=['GET'])
    @requires_auth('get:movies')
    def get_movies(jwt):
        movies = Movie.query.all()

        formatted_movies = [movie.format() for movie in movies]

        return jsonify({
            'success': True,
            'movies': formatted_movies
        })

    @app.route('/actors', methods=['POST'])
    @requires_auth('post:actors')
    def post_actor(jwt):
        body = request.get_json()

        name = body['name']
        age = body['age']
        gender = body['gender']

        if len(name) == 0:
            abort(404)

        actor = Actor(name=name, age=age, gender=gender)
        actor.insert()

        return jsonify({
            'success': True,
            'actor': actor.format()
        })

    @app.route('/movies', methods=['POST'])
    @requires_auth('post:movies')
    def post_movie(jwt):
        body = request.get_json()

        title = body['title']
        release_date = body['release_date']

        if len(title) == 0:
            abort(404)

        movie = Movie(title=title, release_date=release_date)
        movie.insert()

        return jsonify({
            'success': True,
            'movie': movie.format()
        })

    @app.route('/actors/<int:actor_id>', methods=['PATCH'])
    @requires_auth('patch:actors')
    def update_actor(jwt, actor_id):
        actor = Actor.query.get(actor_id)

        if actor is None:
            abort(404)

        body = request.get_json()

        actor.name = body['name']
        actor.age = body['age']
        actor.gender = body['gender']

        actor.update()

        return jsonify({
            'success': True,
            'actor': actor.format()
        })

    @app.route('/movies/<int:movie_id>', methods=['PATCH'])
    @requires_auth('patch:movies')
    def update_movie(jwt, movie_id):
        movie = Movie.query.get(movie_id)

        if movie is None:
            abort(404)

        body = request.get_json()

        movie.title = body['title']
        movie.release_date = body['release_date']

        movie.update()

        return jsonify({
            'success': True,
            'movie': movie.format()
        })

    @app.route('/actors/<int:actor_id>', methods=['DELETE'])
    @requires_auth('delete:actors')
    def delete_actor(jwt, actor_id):


        app.logger.info("GOING TO DELETE")
        actor = Actor.query.get(actor_id)

        if actor is None:
            abort(404)

        actor.delete()

        return jsonify({
            'success': True,
            'actor_id': actor_id
        })

    @app.route('/movies/<int:movie_id>', methods=['DELETE'])
    @requires_auth('delete:movies')
    def delete_movie(jwt, movie_id):
        movie = Movie.query.get(movie_id)

        if movie is None:
            abort(404)

        movie.delete()

        return jsonify({
            'success': True,
            'movie_id': movie_id
        })

    @app.errorhandler(404)
    def not_found(err):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Resource not found'
        }), 404

    @app.errorhandler(422)
    def unprocessable(err):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable'
        }), 422

    @app.errorhandler(AuthError)
    def auth_error(err):
        return jsonify({
            'success': False,
            'error': err.status_code,
            'message': err.error['code']
        }), err.status_code

    return app

