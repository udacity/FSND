import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from api import create_app
from models import setup_db, db_drop_and_create_all, Actor, Movie

from config import bearer_tokens
from sqlalchemy import desc
from datetime import date

ca_auth = {"Authorization": bearer_tokens["casting_assistant"]}

cd_auth = {"Authorization": bearer_tokens["casting_director"]}

ep_auth = {"Authorization": bearer_tokens["executive_producer"]}


# ----------------------------------------------------------------------------#
# setup
# ----------------------------------------------------------------------------#


class APITestCase(unittest.TestCase):
    def setUp(self):

        self.app = create_app()
        self.client = self.app.test_client
        setup_db(self.app)
        db_drop_and_create_all()

        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            self.db.create_all()

        self.new_actor = {"name": "Richard Gere", "age": 99, "gender": "male"}

        self.new_movie = {"title": "Batman", "release_date": date.today()}

    def tearDown(self):
        """Executed after each test"""
        # db_drop_and_create_all() does clean up
        pass

    # /actor endpoint tests

    def test_create_actor(self):
        """test create new actor"""

        res = self.client().post(
            "/actors", json=self.new_actor, headers=cd_auth
        )

        self.assertEqual(res.status_code, 200)

    def test_error_401_create_actor(self):
        """test create actor error when not authorized"""

        res = self.client().post("/actors", json=self.new_actor)

        self.assertEqual(res.status_code, 401)

    def test_error_422_create_actor(self):
        """test error for invalid create actor."""

        bad_actor = {"age": 25}

        res = self.client().post("/actors", json=bad_actor, headers=cd_auth)

        self.assertEqual(res.status_code, 400)

    def test_get_all_actors(self):
        """test to get all actors"""
        count_actors = Actor.query.count()

        res = self.client().get("/actors", headers=ca_auth)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data.get("actors")), count_actors)

    def test_error_401_get_all_actors(self):
        """test get all actors fails when not authorized"""
        res = self.client().get("/actors")

        self.assertEqual(res.status_code, 401)

    def test_edit_actor(self):
        """test for patch/update of existing actor"""
        edit_actor = {"age": 99}
        res = self.client().patch("/actors/1", json=edit_actor, headers=cd_auth)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])

    def test_error_404_edit_actor(self):
        """test edit fails w/ non existent actor_id"""
        edit_actor = {"age": 99}
        res = self.client().patch(
            "/actors/1299999", json=edit_actor, headers=cd_auth
        )

        self.assertEqual(res.status_code, 404)

    def test_error_401_delete_actor(self):
        """test actor delete fails w/o auth"""
        res = self.client().delete("/actors/1")

        self.assertEqual(res.status_code, 401)

    def test_delete_actor(self):
        """test delete actor"""
        res = self.client().delete("/actors/1", headers=cd_auth)

        self.assertEqual(res.status_code, 200)

    def test_error_404_delete_actor(self):
        """Test error for delete on non existing actor_id"""
        res = self.client().delete("/actors/99999", headers=cd_auth)

        self.assertEqual(res.status_code, 404)

    # tests for /movies endpoints

    def test_create_new_movie(self):
        """test create new movie"""

        res = self.client().post(
            "/movies", json=self.new_movie, headers=ep_auth
        )

        self.assertEqual(res.status_code, 200)

    def test_error_422_create_new_movie(self):
        """test error invalid movie payload"""

        bad_movie = {"release_date": date.today()}

        res = self.client().post("/movies", json=bad_movie, headers=ep_auth)

        self.assertEqual(res.status_code, 400)

    def test_get_all_movies(self):
        """test get all movies"""
        res = self.client().get("/movies", headers=ca_auth)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data["movies"]) > 0)

    def test_error_401_get_all_movies(self):
        """test error get all movies w/o auth"""
        res = self.client().get("/movies")

        self.assertEqual(res.status_code, 401)

    def test_edit_movie(self):
        """test patch movie"""
        res = self.client().patch(
            "/movies/1", json=self.new_movie, headers=ep_auth
        )

        self.assertEqual(res.status_code, 200)

    def test_error_401_delete_movie(self):
        """test error on delete w/ no auth"""
        res = self.client().delete("/movies/1")

        self.assertEqual(res.status_code, 401)

    def test_delete_movie(self):
        """test delete movie success"""
        res = self.client().delete("/movies/1", headers=ep_auth)

        self.assertEqual(res.status_code, 200)


# make tests executable
if __name__ == "__main__":
    unittest.main()
