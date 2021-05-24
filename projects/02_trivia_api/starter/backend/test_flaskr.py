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
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            'postgres', 'postgres','localhost:5432', self.database_name)

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
    def test_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    def test_categories_with_invalid_method(self):
        res = self.client().post('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)

    def test_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
    
    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=100')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Resource not found")

    def test_delete_question(self):
        res = self.client().delete('/questions/9')
        data = json.loads(res.data)

        # Verify deleted question is now None (doesn't exist in DB)
        question = Question.query.filter(Question.id == 9).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 9)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertEqual(question, None)

    def test_422_if_question_does_not_exist(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')

    def test_add_question(self):
        new_question = {
            'question': 'In which year did the Tampa Bay Rays make their 1st World Series debut?',
            'answer': '2008',
            'difficulty': 3,
            'category': 6 # SPORTS
        }

        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])

    def test_add_empty_question(self):
        new_question = {
            'question': '',
            'answer': '',
            'difficulty': 1,
            'category': 1
        }

        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')
    
    def test_405_if_add_question_not_allowed(self):
        new_question = {
            'question': 'Test question?',
            'answer': 'Test answer',
            'difficulty': 1,
            'category': 1
        }
        res = self.client().post('/questions/450', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not allowed')
    
    def test_search_questions(self):
        search = {
            'searchTerm': 'What'
        }
        res = self.client().post('/questions/search', json=search)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
    
    def test_bad_search_questions(self):
        res = self.client().post('/questions/search')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')
    
    def test_get_questions_by_category(self):
        res = self.client().get('/categories/6/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
    
    def test_get_questions_by_invalid_category(self):
        res = self.client().get('/categories/7/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Resource not found")
    
    def test_initial_quiz_questions(self):
        quiz_criteria = {
            'quiz_category': {
                'id': 1,
                'type': 'Geography'
            },
            'previous_questions': []
        }
        res = self.client().post('/quizzes', json=quiz_criteria)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertTrue(data['total_questions'])
    
    def test_quiz_questions_invalid_method(self):
        quiz_criteria = {
            'quiz_category': {
                'id': 1,
                'type': 'Geography'
            },
            'previous_questions': []
        }
        res = self.client().get('/quizzes', json=quiz_criteria)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'], 'Not allowed')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()