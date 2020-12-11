import os
from flask import Flask, request, jsonify, abort, make_response
from sqlalchemy import exc
import json
from flask_cors import CORS

from models import db_drop_and_create_all, setup_db, Movie, Actor
from auth import (
    AuthError,
    requires_auth,
    AUTH0_DOMAIN,
    AUTH0_CLIENT_ID,
    AUTH0_CALLBACK_URL,
    API_AUDIENCE,
)
from config import Config


def create_app():
    # create app
    app = Flask(__name__)

    app.config.from_object("config.Config")

    # setup db
    setup_db(app)

    # set up cors for app. allows all origins
    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    db_drop_and_create_all()

    # decorate response with headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,POST,DELETE,OPTIONS"
        )

        return response

    """
    AUTH Route /auth
    """

    @app.route("/auth")
    def generate_auth_url():
        url = (
            f"https://{AUTH0_DOMAIN}/authorize"
            f"?audience={API_AUDIENCE}"
            f"&response_type=token&client_id="
            f"{AUTH0_CLIENT_ID}&redirect_uri="
            f"{AUTH0_CALLBACK_URL}"
        )

        return jsonify({"auth_url": url})

    ## ROUTES
    """
    GET /actors
    """

    @app.route("/actors")
    @requires_auth("get:actors")
    def get_actors(payload):
        selection = Actor.query.all()

        actors = [a.format() for a in selection]

        return jsonify({"success": True, "actors": actors})

    """
    POST /actors
    """

    @app.route("/actors", methods=["POST"])
    @requires_auth("post:actors")
    def create_actor(payload):
        body = request.get_json()

        name = body.get("name")
        age = body.get("age")
        gender = body.get("gender")

        # enforce required fields validation
        if not all([name, age, gender]):
            abort(400, description="Required fields are missing")

        # create Drink and insert to db
        new_actor = Actor(name=name, age=age, gender=gender)
        # add to db
        new_actor.insert()

        return jsonify({"success": True, "actor_id": new_actor.id})

    """
    PATCH /actors/<id>
    """

    @app.route("/actors/<int:actor_id>", methods=["PATCH"])
    @requires_auth("patch:actors")
    def update_actor(payload, actor_id):
        body = request.get_json()

        # check to see if drink exists
        actor = Actor.query.filter_by(id=actor_id).first_or_404()

        if not any([body.get("name"), body.get("age"), body.get("gender")]):
            abort(400, description="Required fields are missing")

        new_actor = actor

        for k, v in body.items():
            if k == "name":
                new_actor.name = v
            elif k == "age":
                new_actor.age = v
            elif k == "gender":
                new_actor.gender = v

        new_actor.update()

        return jsonify({"success": True, "actor": new_actor.format()})

        # check for required parts of payload

    """
    DELETE /actors/<id>
    """

    @app.route("/actors/<int:actor_id>", methods=["DELETE"])
    @requires_auth("delete:actors")
    def delete_actor(payload, actor_id):
        actor = Actor.query.filter_by(id=actor_id).first_or_404()

        actor.delete()

        res = make_response(jsonify({"success": True, "delete": actor_id}), 200)

        return res

    """
    GET /movies
    """

    @app.route("/movies", methods=["GET"])
    @requires_auth("get:movies")
    def get_movies(payload):
        selection = Movie.query.all()

        movies = [m.format() for m in selection]

        return jsonify({"success": True, "movies": movies})

    """
    POST /movies
    """

    @app.route("/movies", methods=["POST"])
    @requires_auth("post:movies")
    def create_movie(payload):
        body = request.get_json()

        title = body.get("title")
        release_date = body.get("release_date")

        if not all([title, release_date]):
            abort(400, description="Required fields are missing")

        new_movie = Movie(title=title, release_date=release_date)

        new_movie.insert()

        return jsonify({"success": True, "movie": new_movie.id})

    @app.route("/movies/<movie_id>", methods=["PATCH"])
    @requires_auth("patch:movies")
    def update_movie(payload, movie_id):

        body = request.get_json()

        if not movie_id:
            abort(400, {"message": "no movie id provided"})

        movie = Movie.query.filter_by(id=movie_id).first_or_404()

        if not movie:
            abort(404, {"message": "Movie not found"})

        title = body.get("title", movie.title)
        release_date = body.get("release_date", movie.release_date)

        # Set new field values
        movie.title = title
        movie.release_date = release_date

        # Delete movie with new values
        movie.update()

        # Return success, updated movie id and updated movie as formatted list
        return jsonify(
            {"success": True, "updated": movie.id, "movie": [movie.format()]}
        )

    @app.route("/movies/<movie_id>", methods=["DELETE"])
    @requires_auth("delete:movies")
    def delete_movie(payload, movie_id):

        if not movie_id:
            abort(400, {"message": "please include movie id"})

        movie = Movie.query.filter_by(id=movie_id).first_or_404()

        if not movie:
            abort(404, {"message": "Movie not found"})

        movie.delete()

        return jsonify({"success": True, "deleted": movie_id})

    ## Error Handling
    """
    Example error handling for unprocessable entity
    """

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify(
                {"success": False, "error": 422, "message": "unprocessable"}
            ),
            422,
        )

    """
    implement error handlers using the @app.errorhandler(error) decorator
        each error handler should return (with approprate messages):
                 jsonify({
                        "success": False, 
                        "error": 404,
                        "message": "resource not found"
                        }), 404

    """

    """
    error handler should conform to general task above 
    """

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify(
                {
                    "success": False,
                    "error": 404,
                    "message": "resource not found",
                },
            ),
            404,
        )

    """
    implement error handler for AuthError
    error handler should conform to general task above 
    """

    # @app.errorhandler(403)
    # def unauthorized(error):
    #     return (
    #         jsonify(
    #             {"succcess": False, "error": 403, "message": "unauthorized"},
    #         ),
    #         403,
    #     )

    @app.errorhandler(AuthError)
    def handle_auth_error(ex):
        res = jsonify(ex.error)
        res.status_code = ex.status_code

        return res

    return app
