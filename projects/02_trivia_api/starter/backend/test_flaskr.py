import os
import unittest
import json
import subprocess
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import query

from flaskr import create_app
from models import setup_db, Question, Category

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_pw = 'Ran!dom101'
        self.database_path = "postgresql://{}:{}@{}/{}".format('postgres', self.database_pw, 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            # self.db.create_all()

        # psql_command = "psql -U postgres -d {} -f trivia.psql".format(self.database_name)
        # subprocess.call(psql_command)

    def tearDown(self):
        """Executed after reach test"""
        # psql_command = "psql -U postgres -d {} -f trivia_teardown.psql".format(self.database_name)
        # subprocess.call(psql_command)
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    # def test_given_behavior(self):
    #     """Test _____________ """
    #     res = self.client().get('/')

    #     self.assertEqual(res.status_code, 200)

    def test_get_categories(self):
        res = self.client().get('/api/v1.0/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertGreater(len(data['categories']), 0)
        self.assertTrue(data['categories'][0]['type'])
        self.assertTrue(data['categories'][0]['id'])

    def test_get_paginated_questions(self):
        res = self.client().get('/api/v1.0/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['categories'])

    def test_delete_question(self):
        question = Question.query.first()
        self.assertIsNotNone(question)

        res = self.client().delete('/api/v1.0/questions/{}'.format(question.id))
        data = json.loads(res.data)

        after_question = Question.query.filter(Question.id == question.id).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], "Deleted {}".format(question.id))
        self.assertEqual(after_question, None)
        
    def test_zero_questions_returned_when_requesting_beyond_valid_page(self):
        res = self.client().get('/api/v1.0/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data['questions']), 0)
        self.assertTrue(data['total_questions'])

    new_question = {
        'question': "What is the answer?",
        'answer': "testing",
        'category': "6",
        'difficulty': "1"
    }

    def test_create_question(self):
        res = self.client().post('/api/v1.0/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertGreaterEqual(data['qid'], 0)

        qid = data['qid']
        question = Question.query.filter(Question.id==qid).first()
        self.assertEquals(question.question, 'What is the answer?')

    def test_get_questions_in_category(self):
        cat_id = 3
        total_questions = len(Question.query.filter(Question.category==cat_id).all())

        res = self.client().get(f"/api/v1.0/categories/{cat_id}/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['total_questions'], total_questions)
        
        self.assertGreaterEqual(total_questions, 1) # sanity test
        self.assertEquals(data['current_category'], Category.query.filter(Category.id==cat_id).first().type)

    def test_get_quiz_question(self):
        cat_id = 4

        cat_questions = Question.query.filter(Question.category==cat_id).all()
        self.quiz = {
            'quiz_category': { 'type': 'History', 'id': cat_id},
            'previous_questions': []
        }
        res = self.client().post('/api/v1.0/quizzes', json=self.quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['total_questions'], len(cat_questions))
        self.assertTrue(data['categories'])
        self.assertEqual(data['current_category'], cat_id)

    def test_get_previously_unanswered_quiz_question(self):
        cat_id = 4

        cat_question_ids = [q.id for q in Question.query.filter(Question.category==cat_id).all()]
        new_question_id = cat_question_ids[0]
        prev_question_ids = cat_question_ids[1:len(cat_question_ids)]

        self.quiz = {
            'quiz_category': { 'type': 'History', 'id': cat_id},
            'previous_questions': prev_question_ids
        }
        res = self.client().post('/api/v1.0/quizzes', json=self.quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])
        self.assertEqual(data['question']['id'], new_question_id)
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['total_questions'], len(cat_question_ids))
        self.assertTrue(data['categories'])
        self.assertEqual(data['current_category'], cat_id)

    def test_search_questions(self):
        matches = Question.query.filter(Question.question.ilike('%world%')).all()
        res = self.client().post('/api/v1.0/search/questions', json={'searchTerm':'world'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertEqual(data['total_questions'], len(matches))
        self.assertTrue(data['categories'])
        self.assertEqual(data['current_category'], '')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()