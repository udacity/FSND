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
        self.database_path = "postgresql://{}/{}".format('localhost:5432', self.database_name)
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


    def test_get_all_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['categories'])

    def test_get_questions(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])

    def test_delete_question(self):
        # insert a test question to be deleted
        new_question = Question(question='new question', answer='new answer',
                            difficulty=1, category=1)
        new_question.insert()
        question_id = new_question.id
         
        res = self.client().delete(f'/questions/{question_id}')
        data = json.loads(res.data)
        
        self.assertEqual(data['success'], True)
        self.assertTrue(data['deleted'])

    def test_delete_question_fail(self):
        res = self.client().delete('/questions/100000000')
        data = json.loads(res.data)
    
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_post_question(self):
        sample_question = {
            'question': 'What is a test question?',
            'answer': 'Answer',
            'difficulty': '1',
            'category': '1'
        }
        res = self.client().post('/questions',
                                 data=json.dumps(sample_question),
                                 content_type='application/json')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'], )
        self.assertTrue(data['question_created'])
        self.assertTrue(data['questions'])
        self.assertTrue((data['total_questions']))
        

    def test_post_question_fail(self):
        res = self.client().post('/questions',
                                 data=json.dumps({}),
                                 content_type='application/json')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_search_question(self):
        request_data = {'searchTerm': 'Which'}
        res = self.client().post('/questions/search', data=json.dumps(request_data),
                                 content_type='application/json')
        data = json.loads(res.data)
    
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue((data['total_questions']))
        
    def test_search_fail(self):
        request_data = {}
        res = self.client().post('/questions/search', data=json.dumps(request_data),
                                 content_type='application/json')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_questions_by_category(self):
        res = self.client().get(f'/categories/1/questions')
        data = json.loads(res.data)
    
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue((data['total_questions']))
        self.assertTrue(data['current_category'])

    def test_get_questions_by_category_fail(self):
        res = self.client().get(f'/categories/100/questions')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')
        

    def test_get_quiz_questions(self):
        request_data = {
            'previous_questions': [1, 2, 3],
            'quiz_category': {'id': 3, 'type': 'Geography'}
        }
        res = self.client().post('/quizzes', data=json.dumps(request_data),
                                 content_type='application/json')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
            
    def test_get_quiz_questions_fail(self):
        res = self.client().post('/quizzes', data=json.dumps({}),
                                 content_type='application/json')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()