
import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Actor, Movie


class CATestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.DB_HOST = os.getenv('DB_HOST', '127.0.0.1:5432')
        self.DB_USER = os.getenv('DB_USER', 'postgres')
        self.DB_PASSWORD = os.getenv('DB_PASSWORD', 'gravity')
        self.DB_NAME = os.getenv('DB_NAME', 'postgres')
        self.DB_PATH = 'postgresql+psycopg2://{}:{}@{}/{}'.format(self.DB_USER, self.DB_PASSWORD, self.DB_HOST, self.DB_NAME)
        # self.database_path = "postgresql://postgres:gravity@localhost:5432/trivia_test"
        setup_db(self.app, self.DB_PATH)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_actors(self):
        res = self.client().get('/actors')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))


    def test_add_actor(self):
        test_actor = {'name': '', 'age': '', 'gender': ''}
        res = self.client().post('/actors', json = test_actor)
        data = json.loads(res.data)
        if data['error'] == 404:
            self.assertEqual(res.status_code, 404)
            self.assertEqual(data['success'], False)
        else:
            self.assertEqual(res.status_code, 200)
            self.assertEqual(data['success'], True)

    def test_404_add_actor(self):
        test_actor = {}
        res = self.client().post('/actors', json = test_actor)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_delete_actor(self):
        res = self.client().delete('/actor/1')
        data = json.loads(res.data)
        actor = Actor.query.filter(Actor.id == 14).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(actor, None)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()