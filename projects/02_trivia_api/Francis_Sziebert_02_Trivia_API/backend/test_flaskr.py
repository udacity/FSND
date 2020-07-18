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
        self.assertEqual(data['message'], 'MethodNotAllowed: The method is not allowed for the requested URL.')
        self.assertEqual(data['error'], 405)

    def test_api_questions_get(self):
        response = self.client().get('/api/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(isinstance(data['categories'], dict))
        self.assertTrue(data['current_category'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['page'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(isinstance(data['questions'], list))

    def test_api_questions_get_404_page_past_max(self):
        response = self.client().get('/api/questions?page=1000000')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'NotFound: Requested page beyond page maximum.')
        self.assertEqual(data['error'], 404)

    def test_api_get_a_question(self):
        response = self.client().get('/api/questions/5')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(isinstance(data['question'], dict))
        self.assertTrue(isinstance(data['question']['id'], int))
        self.assertTrue(data['question']['category'])
        self.assertTrue(isinstance(data['question']['difficulty'], int))
        self.assertTrue(isinstance(data['question']['answer'], str))
        self.assertTrue(isinstance(data['question']['question'], str))

    def test_api_get_a_question_404_not_found(self):
        response = self.client().get('/api/questions/10000000000')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'NotFound: Requested question not found.')
        self.assertEqual(data['error'], 404)

    def test_api_post_a_question(self):
        in_data = {
            'id': 1,
            'category': "5",
            'answer': 'Nowhere',
            'question': 'There is a Korean Film titled "The Man From _________"',
            'difficulty': 3
        }
        response = self.client().post('/api/questions', data=json.dumps(in_data))
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(isinstance(data['question'], dict))
        self.assertEqual(data['question']['id'], in_data['id'])
        self.assertEqual(str(data['question']['category']), in_data['category'])
        self.assertEqual(data['question']['difficulty'], in_data['difficulty'])
        self.assertEqual(data['question']['answer'], in_data['answer'])
        self.assertEqual(data['question']['question'], in_data['question'])

    def test_api_post_a_question_422_id_already_exists(self):
        in_data = {
            'id': 1,
            'category': "5",
            'answer': 'Nowhere',
            'question': 'There is a Korean Film titled "The Man From _________"',
            'difficulty': 3
        }
        response = self.client().post('/api/questions', data=json.dumps(in_data))
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable: id=1 already exists.')
        self.assertEqual(data['error'], 422)

    def test_api_post_a_question_422_missing_required(self):
        in_data = {
            'answer': 'Nowhere',
            'question': 'There is a Korean Film titled "The Man From _________"',
            'difficulty': 3
        }
        response = self.client().post('/api/questions', data=json.dumps(in_data))
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable: Requires Fields: question,answer,category,difficulty')
        self.assertEqual(data['error'], 422)

    def test_api_delete_a_question(self):
        response = self.client().delete('/api/questions/1')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 1)

    def test_api_delete_a_question_404_not_found(self):
        response = self.client().delete('/api/questions/10000000000')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'NotFound: Requested question not found.')
        self.assertEqual(data['error'], 404)

    def test_api_get_category_questions(self):
        response = self.client().get('/api/categories/1/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(isinstance(data['categories'], dict))
        self.assertEqual(data['current_category'], '1')
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['page'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(isinstance(data['questions'], list))

    def test_api_get_category_questions_404_NotFound(self):
        response = self.client().get('/api/categories/7/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'NotFound: No Questions Available')
        self.assertEqual(data['error'], 404)

    def test_api_post_quizzes_All(self):
        in_data = {
            "previous_questions": [],
            "quiz_category": {
                "type": "click",
                "id": 0
            }
        }
        response = self.client().post('/api/quizzes', data=json.dumps(in_data))
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(isinstance(data['previous_questions'], list))
        self.assertTrue(isinstance(data['question'], dict))

    def test_api_post_quizzes_Geography(self):
        in_data = {
            "previous_questions": [],
            "quiz_category": {
                "type": "Geography",
                "id": "3"
            }
        }
        response = self.client().post('/api/quizzes', data=json.dumps(in_data))
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(isinstance(data['previous_questions'], list))
        self.assertTrue(isinstance(data['question'], dict))

    def test_api_post_quizzes_422_bad_inputs(self):
        in_data = {
            "previous_questions": [],
            "quiz_category": ["Geography", "3"]
        }
        response = self.client().post('/api/quizzes', data=json.dumps(in_data))
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['message'], "Unprocessable: api/quizzes requires previous_questions(list) and quiz_category(dict)")








# Make the tests conveniently executable


if __name__ == "__main__":
    unittest.main()