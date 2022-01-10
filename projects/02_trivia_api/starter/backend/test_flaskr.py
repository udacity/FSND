import os
import re
import unittest
import json
from flask.json import jsonify
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
        self.database_path = "postgresql://{}:{}@{}/{}".format("postgres","7907", "localhost:5432", self.database_name)
        setup_db(self.app, self.database_path)



        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.new_question = {
            'question':'Which dung beetle was worshipped by the ancient Egyptians?',
            'answer':'Scarab',
            'difficulty':4,
            'category':4
        }

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))

    def test_404_send_request_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "The requested resource doesn't exist.")

    # def test_delete_question(self):
    #     res = self.client().delete('/questions/25')
    #     data = json.loads(res.data)

    #     question  = Question.query.filter(Question.id==25).one_or_none()

    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data['success'], True)
    #     self.assertTrue(data['id'])
    #     self.assertEqual(question, None)

    # def test_422_if_question_does_not_exist(self):
    #     res = self.client().delete('/questions/1000')
    #     data = json.loads(res.data)

    #     self.assertEqual(res.status_code, 422)
    #     self.assertEqual(data['success'], False)
    #     self.assertEqual(data['message'], 'Unprocessable Entity.')


    # def test_create_question(self):
    #     res = self.client().post('/questions', json = self.new_question)
    #     data = json.loads(res.data)

    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data['success'], True)
    #     self.assertTrue(data['created'])

    def test_405_if_plant_creation_not_allowed(self):
        res = self.client().post('/questions/50', json = self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Method Not Allowed.')




    def test_get_questions_serch_term_with_results(self):
        res = self.client().post('/questions', json = {'searchTerm':'What'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))

    def test_get_questions_serch_term_without_results(self):
        res = self.client().post('/questions', json = {"searchTerm":"Shahzod"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 0)


    def test_get_questions_by_categories(self):
        res = self.client().get('/categories/4/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len('total_questions'))


    def test_404_send_requesting_beyond_valid_category(self):
        res = self.client().get('/categories/100/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'],"The requested resource doesn't exist.")









# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()