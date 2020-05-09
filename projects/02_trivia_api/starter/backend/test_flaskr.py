import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flaskr import create_app
from models import setup_db, Question, Category, create_db_path


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_path = create_db_path(db_user='postgres', db_name='trivia_test')
        setup_db(self.app, self.database_path)

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
    def test_get_homepage(self):
        res = self.client().get('/')
        data = json.loads(res.data) if res.status_code == 200 else None
        print(res)
        
        self.assertEqual(res.status_code, 200)
        if data:
            self.assertIn(data, b'World')

    def test_405_post_homepage(self):
        res = self.client().post('/', json={'question': 'Is this working?'})
        data = json.loads(res.data) if res.status_code == 200 else None

        self.assertEqual(res.status_code, 405)
        if data:
            self.assertIn(data, b'error')



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()