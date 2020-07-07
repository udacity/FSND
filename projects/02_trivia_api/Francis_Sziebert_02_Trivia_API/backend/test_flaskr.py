import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        setup_db(self.app, database_name=self.database_name)

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

    def test_api_categories_get(self):
        response = self.client().get('/api/categories')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))
        self.assertTrue(data['total_categories'])

    def test_api_categories_405_client_tries_posting(self):
        response = self.client().post('/api/categories', data={"type": "Mystery"})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')
        self.assertEqual(data['error'], 405)

    def test_api_questions_get(self):
        response = self.client().get('/api/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(data['categories'], dict))
        self.assertTrue(data['current_category'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['page'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(isinstance(data['questions'], list))

    def test_api_questions_404_get_page_past_max(self):
        response = self.client().get('/api/questions?page=1000000')
        print(f'\nresponse.data:\n{response.data}\n')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found: requested page beyond maximum')
        self.assertEqual(data['error'], 404)







# Make the tests conveniently executable


if __name__ == "__main__":
    unittest.main()