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
        self.database_path = "postgresql://{}:{}@{}/{}".format('postgres', 'adil1234','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.new_question = {
            'question': 'What is 1 + 1?',
            'answer': '2',
            'difficulty': 1,
            'category': '1'
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

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
    
    def test_delete_question(self):
        test_question = Question(question="test", answer="test", category=1,difficulty=1)

        test_question.insert()

        test_question_id = test_question.id


        res = self.client().delete(f'/questions/{test_question_id}')
        data = json.loads(res.data)

        question = Question.query.get(test_question_id)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], test_question_id)
        self.assertEqual(data['total_questions'], len(Question.query.all()))
        self.assertEqual(question, None)

    def test_add_question(self):


        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 201)
        self.assertTrue(data['created_id'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_get_trivia_questions_all_categories(self):
        res = self.client().post('/quizzes', json={
            'previous_questions': [],
            'quiz_category': {'id': 0}
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()