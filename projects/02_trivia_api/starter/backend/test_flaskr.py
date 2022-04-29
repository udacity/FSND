import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represponseents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.client
        self.database_name = "trivia_test"
        self.database_path = "postgresponse://{}/{}".format('localhost:5432', self.database_name)
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
    def get_all_categories(self):   
        response = self.client().get('/categories')
        returned_data = json.loads(response.data)

        self.assertEqual(returned_data['success'], True)
        self.assertTrue(returned_data['categories'])
        self.assertEqual(response.status_code, 200, 'Test Failed') 
        
    def get_questions(self):  
        response = self.client().get('/questions') 
        returned_data = json.loads(response.data)

        self.assertEqual(returned_data['success'], True)
        self.assertTrue(returned_data['questions'])
        self.assertEqual(response.status_code, 200, 'Test Failed')
        
    def delete_question(self):
        #delete question and get response
        response = self.client().delete('questions/20')
        returned_data = json.loads(response.data)

        self.assertEqual(returned_data['success'], True)
        self.assertEqual(returned_data['deleted'], 20, 'Test Failed')        
        self.assertEqual(response.status_code, 200, 'Test Failed')
        
    def add_question(self):
        #prepare input data
        new_question = {
         'question': 'Testing Question',
         'answer': 'Testing Answer',        
         'difficulty': 1,
         'category': 1
        }
        response = self.client().post('/questions', json=new_question)
        returned_data = json.loads(response.data)

        self.assertEqual(returned_data['success'], True)
        self.assertEqual(response.status_code, 200, 'Test Failed')
    
    def search_question(self):
        response = self.client().post('questions/search', json={'searchTerm': 'Test'})
        returned_data = json.loads(response.data)

        self.assertEqual(returned_data['success'], True)
        self.assertEqual(response.status_code, 200, 'Test Failed')
        
    def play_quiz(self):
        #prepare input data
        input_data = {
            "category": 2,
            "previous_question":[1,3,18,25,36,31,27,34,35,16,26,33,29,17,28,19,30]
        }
        # response
        response = self.client().post('/quiz', json=input_data)
        returned_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(returned_data['success'], True)
        self.assertEqual(returned_data['question'],'Quiz Completed')

    
    
    def incorrect_search(self):
        response = self.client().post('questions/search', json={"searchTerm": "1423efbe"})
        returned_data = json.loads(response.data)

        self.assertEqual(returned_data['success'], False)
        self.assertEqual(returned_data['error'], 404, 'Test Failed')
        
    def item_not_found(self):
        response = self.client().get('/categories/99999/questions')
        returned_data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(returned_data['success'], False)
    
    
    def incorrect_input(self):
        wrong_input = {
        'question': 200,
        'category': '1',
        'answer':'',
        'difficulty': 1
        }

        response = self.client().post('/questions', json=wrong_input)
        returned_data = json.loads(response.data)

        self.assertEqual(returned_data['success'], False)
        self.assertEqual(returned_data['error'], 422)
    
    
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()