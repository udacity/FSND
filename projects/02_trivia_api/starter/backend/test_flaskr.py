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
        self.database_path = "postgresql://{}/{}".format(
            'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after each test"""
        pass

    def test_get_categories(self):
        res = self.client().get('/api/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(len(data['categories']))

    def test_get_questions(self):
        res = self.client().get('/api/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        self.assertTrue(len(data['categories']))
        self.assertTrue(data['current_category'] == 'All')

    def test_404_sent_for_invalid_page(self):
        res = self.client().get('/api/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'not_found')

    def test_delete_question(self):
        q = Question(
            question="question", answer="answer", category="1", difficulty=2
        )
        q.insert()
        question_id = str(q.format()['id'])
        res = self.client().delete('/api/questions/' + question_id)
        data = json.loads(res.data)

        question = Question.query.filter(
            Question.id == question_id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(question, None)

    def test_delete_invalid_id_question(self):
        res = self.client().delete('/api/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'not_found')

    def test_create_question(self):
        res = self.client().post('/api/questions', json={
            'question': 'question',
            'answer': 'answer',
            'category': 2,
            'difficulty': 3
        })

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertEqual(data['question']['difficulty'], 3)
        self.assertEqual(data['question']['category'], 2)

    def test_create_invalid_question(self):
        res = self.client().post('/api/questions', json={
            'question': 'question',
        })

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable_entity')

    def test_get_question_search_with_results(self):
        res = self.client().post(
            '/api/questions', json={'searchTerm': 'title'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertEqual(len(data['questions']), 2)

    def test_get_question_search_without_results(self):
        res = self.client().post(
            '/api/questions', json={'searchTerm': 'yuujhiuhyfg'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], 0)
        self.assertEqual(len(data['questions']), 0)

    def test_get_questions_by_category(self):
        res = self.client().get('/api/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'] == 'Science')

    def test_get_questions_by_invalid_category(self):
        res = self.client().get('/api/categories/60/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'not_found')

    def test_get_quiz_question(self):
        res = self.client().post('/api/quizzes', json={
            'quiz_category': {'type': 'Science', 'id': 1},
            'previous_questions': []
        })

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertTrue(len(data['question']))
        self.assertEqual(data['question']['category'], 1)

        # Switch category
        res = self.client().post('/api/quizzes', json={
            'quiz_category': {'type': 'Art', 'id': 2},
            'previous_questions': []
        })

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['question']['category'], 2)

    def test_get_quiz_without_category_question(self):
        res = self.client().post('/api/quizzes', json={
            'previous_questions': []
        })

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertTrue(len(data['question']))

    def test_get_quiz_question_without_parameters_category(self):
        res = self.client().post('/api/quizzes')

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)

    def test_method_not_allowed_error(self):
        res = self.client().delete('/api/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method_not_allowed')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
