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
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
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
    def test_cors_http_headers(self):
        res = self.client().get('/')
        self.assertEqual(res.access_control_allow_origin, '*')
        self.assertEqual(res.access_control_allow_headers.as_set(), {'content-type', 'authorization'})
        self.assertEqual(res.access_control_allow_methods.as_set(), {'get', 'post', 'delete'})

    def test_get_categories(self):
        res = self.client().get('/categories')
        self.assertEqual(res.status_code, 200)
    
    def test_get_questions(self):
        res = self.client().get('/questions')
        self.assertEqual(res.status_code, 200)

    def test_get_questions_pagination_in_range(self):
        res = self.client().get('/questions?page=2')
        self.assertEqual(res.status_code, 200)

    def test_get_questions_pagination_out_of_range(self):
        res = self.client().get('/questions?page=20')
        self.assertEqual(res.status_code, 404)

    def test_delete_question_by_id(self):
        res = self.client().delete('/questions/11')
        self.assertEqual(res.status_code, 200)
        q=Question.query.filter(Question.id==11).count()
        self.assertEqual(q, 0)

    def test_delete_question_by_invalid_id(self):
        res = self.client().delete('/questions/1000')
        self.assertEqual(res.status_code, 404)

    def test_get_questions_by_category(self):
        res = self.client().get('categories/4/questions')
        self.assertEqual(res.status_code, 200)
    
    def test_get_questions_by_invalid_category(self):
        res = self.client().get('categories/900/questions')
        self.assertEqual(res.status_code, 404)

    def test_get_questions_by_search_term(self):
        res = self.client().post('/questions', json={"searchTerm":"title"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json['questions']), 2)

    def test_get_questions_by_search_term_bad_request(self):
        res = self.client().post('/questions', json={})
        self.assertEqual(res.status_code, 400)

    def test_insert_question(self):
        res = self.client().post('/questions', json={"question": "what is my name?", "answer": "sameh abouelsaad", "difficulty": "3", "category": "4"})
        self.assertEqual(res.status_code, 200)
        question=Question.query.filter(Question.question=="what is my name?").one_or_none()
        self.assertIsNotNone(question)

    def test_insert_invalid_question(self):
        res = self.client().post('/questions', json={"question": "what is my name?"})
        self.assertEqual(res.status_code, 400)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()