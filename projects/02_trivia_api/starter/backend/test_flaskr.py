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
        self.database_path = "postgres://{}@{}/{}".format('sibo','localhost:5432', self.database_name)
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

    def test_no_data_to_play_quiz(self):
        #response from request with no data
        response = self.client().post('/quizzes', json={})
        data = json.loads(response.data)

        #Assertions
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Bad request error')

    def test_play_quiz_question(self):
        #test request data
        request_data = {
            'previous_questions': [5, 9],
            'quiz_category': {
                'type': 'History',
                'id': 4
            }
        }

        #request and process response
        response = self.client().post('/quizzes', json=request_data)
        data = json.loads(response.data)

        #Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

        #check request for 5 and 9 is not returned
        self.assertNotEqual(data['question']['id'], 5)
        self.assertNotEqual(data['question']['id'], 9)

        #check category from request
        self.assertEqual(data['question']['category'], 4)

    def test_invalid_category_id(self):
        #
        response = self.client().get('/categories/0815/questions')
        data = json.loads(response.data)

        #assertions
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable entity')

    def test_get_questions_by_category(self):
        #request for category id 6
        response = self.client().get('/categories/6/questions')
        data = json.loads(response.data)

        #assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertNotEqual(len(data['questions']), 0)
        self.assertEqual(data['current_category'], 'Sports')
    
    def test_search_term_not_found(self):
        #create search term
        request_data = {
            'searchTerm': 'aksdjfaslködfjaskdfj'
        }

        #make response
        response = self.client().post('/questions/search', json=request_data)
        data = json.loads(response.data)

        #Assertions
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test_empty_search_term_response(self):
        #create empty search term
        request_data = {
            'searchTerm': ''
        }

        #make response
        response = self.client().post('/questions/search', json=request_data)
        data = json.loads(response.data)

        #assertions
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable entity')

    def test_search_questions(self):
        #create search term
        request_data = {
            'searchTerm': 'largest lake in Africa',
        }

        # make request and process response
        response = self.client().post('/questions/search', json=request_data)
        data = json.loads(response.data)

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 1)    
    
    def test_create_question_with_empty_data(self):
        #create request data
        request_data = {
            'question': '',
            'answer': '',
            'difficulty': 1,
            'category': 1,
        }

        # make request and process response
        response = self.client().post('/questions', json=request_data)
        data = json.loads(response.data)

        # Assertions
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable entity')

    def test_create_questions(self):
        #create mock data
        mock_data = {
            'question': 'This is a mock question',
            'answer': 'this is a mock answer',
            'difficulty': 1,
            'category': 1,
        }

        # make request and process response
        response = self.client().post('/questions', json=mock_data)
        data = json.loads(response.data)

        # asserions to ensure successful request
        self.assertEqual(response.status_code, 200)

        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], 'Question successfully created!')

    def test_get_all_categories(self):
        # make request and process response
        response = self.client().get('/categories')
        data = json.loads(response.data)

        # make assertions on the response data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertEqual(len(data['categories']), 6)

    def test_get_paginated_questions(self):
        # make request and process response
        response = self.client().get('/questions')
        data = json.loads(response.data)

        # make assertions on the response data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['questions'])
        self.assertEqual(len(data['questions']), 10)

    def test_error_for_out_of_bound_page(self):
        # make request and process response
        response = self.client().get('/questions?page=123456789')
        data = json.loads(response.data)

        # make assertions on the response data
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test_successful_question_delete(self):
        # insert mock qestion into Question constructor
        question = Question(
            question='This is a test question that should deleted',
            answer='this answer should be deleted',
            difficulty=1,
            category='1')

        # create a new mock question in the database
        question.insert()        
        # create mock question and get id
        mock_question_id = question.id

        # delete mock question and process response
        response = self.client().delete(
            '/questions/{}'.format(mock_question_id))
        data = json.loads(response.data)

        # ensure question does not exist
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], "Question successfully deleted")

    def test_delete_same_question_twice(self):
        # insert mock qestion into Question constructor
        question = Question(
            question='This is a test question that should deleted',
            answer='this answer should be deleted',
            difficulty=1,
            category='1')

        # create a new mock question in the database
        question.insert()

        mock_question_id = question.id

        # this tests if resource has already been deleted
        self.client().delete('/questions/{}'.format(mock_question_id))
        response = self.client().delete(
            '/questions/{}'.format(mock_question_id))
        data = json.loads(response.data)

        # make assertions on the response data
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable entity')

    def test_delete_question_id_not_exist(self):
        # this tests an id that doesn't exist
        response = self.client().delete('/questions/1211256')
        data = json.loads(response.data)

        # make assertions on the response data
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable entity')

    def test_delete_question_with_invalid_id(self):
        # this tests an invalid id
        response = self.client().delete('/questions/asdfagasdgsa45')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
