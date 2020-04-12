# Standard Libs
import os
import sys
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

import time
import inspect

# Own models
from flaskr import create_app
from models import setup_db, Question, Category, db

# Log Array 
logging_function = []

# Defines sentence to show up in console 
print_successfull_sentence = "Status: OK and took: {} seconds. Method: {}"

#
# Provide my own logging feature 
#
def create_new_logging_entry(function_name, time):

    new_logging_entry = {
        "function": function_name,
        "time":     '%.3f'%(time)
    }

    logging_function.append(new_logging_entry)

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    #
    # Set-up Method
    # 
    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_path = "postgres://{}:{}@{}/{}".format("Dominik", "test", "localhost:5432", "trivia_test")
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    #
    # teardown is not used 
    #  
    def tearDown(self):
        """Executed after reach test"""
        pass

    #
    # Method requests for all questions in all categorys and checks
    # if there is data available
    def test_01_1_get_all_questions_and_categories(self): 

        # Set varbs for logging 
        frame = inspect.currentframe()
        start_time = time.time()
        
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['questions'])) 
        self.assertTrue(len(data['categories']))

        end_time = time.time()

        # Save logging
        create_new_logging_entry(
                                    inspect.getframeinfo(frame).function,
                                    time.time() - start_time
                                )

    #
    # Method requests for all questions in all categorys
    # param is a site out of the range so expecting 404
    def test_01_2_get_all_questions_and_categories_and_fail(self): 

        # Set varbs for logging 
        frame = inspect.currentframe()
        start_time = time.time()
        
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertTrue(data['success'] is False)

        end_time = time.time()

        # Save logging
        create_new_logging_entry(
                                    inspect.getframeinfo(frame).function,
                                    time.time() - start_time
                                )

    #
    # Method requests questions by category and compares the requested
    # category with the category in the results
    def test_02_1_get_questions_by_category(self):

        # Set varbs for logging 
        frame = inspect.currentframe()
        start_time = time.time()

        # Define category
        getCategoryById = 1

        res = self.client().get('/categories/{}/questions'.format(getCategoryById))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['current_category']))
        for row in data['questions']:
            self.assertTrue(row.get('category') == getCategoryById)
        
        # Print logging
        create_new_logging_entry(
                                    inspect.getframeinfo(frame).function,
                                    time.time() - start_time
                                )

    #
    # Method requests questions by category
    # category is out of the range, so expect to fail
    def test_02_2_get_questions_by_category_and_fail(self):

        # Set varbs for logging 
        frame = inspect.currentframe()
        start_time = time.time()

        # Define category
        getCategoryById = 1000

        res = self.client().get('/categories/{}/questions'.format(getCategoryById))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)

        # Print logging
        create_new_logging_entry(
                                    inspect.getframeinfo(frame).function,
                                    time.time() - start_time
                                )

    #
    # Method requests the /questions API to search for questions
    # with result 
    def test_03_1_get_search_results(self):
   
        # Set varbs for logging 
        frame = inspect.currentframe()
        start_time = time.time()

        # Define Testdata: 
        requestData = {
                        "searchTerm": "a"
                        }
        
        res = self.client().post('/questions', json=requestData)
        data = res.json

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['questions'])) # In this case, there should be data 

        # Save logging
        create_new_logging_entry(
                                    inspect.getframeinfo(frame).function,
                                    time.time() - start_time
                                )        

    # 
    # Method requests the /questions API to search for questions
    # without results
    def test_03_2_get_no_search_results(self):

        # Set varbs for logging 
        frame = inspect.currentframe()
        start_time = time.time()

        # Define Testdata: 
        requestData = {
                        "searchTerm": "test"
                        }
        
        res = self.client().post('/questions', json=requestData)
        data = res.json

        self.assertEqual(res.status_code, 200)
        self.assertFalse(len(data['questions'])) # In this case, there should be no returning questions

        # Save logging
        create_new_logging_entry(
                                    inspect.getframeinfo(frame).function,
                                    time.time() - start_time
                                )

    #
    # Tests if new questions can be added
    # 
    def test_04_1_add_new_question(self):

        # Set varbs for logging 
        frame = inspect.currentframe()
        start_time = time.time()

        # Define Testdata: 
        json_Body = {
                        "question": "This is an example question",
                        "answer": "This is an example answer",
                        "difficulty": 1,
                        "category": 1
                        }

        headers     = {
                        'referer': "/add"
                        }
        
        res = self.client().post('/questions', json = json_Body, headers = headers)
        data = res.json
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'] is True)
        self.assertTrue(data['id'] is not None) # Check if response contains an ID
        new_Entry = db.session.query(Question) \
            .filter(Question.id == data['id']) \
            .one_or_none()
        self.assertTrue(new_Entry is not None) # Check this ID in the DB

        # Save logging
        create_new_logging_entry(
                                    inspect.getframeinfo(frame).function,
                                    time.time() - start_time
                                )

    #  
    # Tests if new questions can be added but get an error caused by wrong or no data which is sent
    #
    def test_04_2_add_new_question_and_fail(self):
        
        # Set varbs for logging 
        frame = inspect.currentframe()
        start_time = time.time()

        # Define Testdata: 
        json_Body = {
                        "question": "Test new",
                        "answer": "Test new",
                        "difficulty": "This should be an Integer",
                        "category": 1
                        }
        headers     = {
                        'referer': "/add"
                        } 

        res = self.client().post('/questions', json = json_Body, headers = headers)
        data = res.json
        self.assertEqual(res.status_code, 422)
        self.assertTrue(data['message'] == 'unprocessable')
        self.assertTrue(data["success"] == False)

        # Save logging
        create_new_logging_entry(
                                    inspect.getframeinfo(frame).function,
                                    time.time() - start_time
                                )

    #
    # Tests if the created Question from "test_04_1_add_new_question", can be deleted
    #  
    def test_05_1_delete_Entry(self):
    
        # Set varbs for logging 
        frame = inspect.currentframe()
        start_time = time.time()

        # Define Testdata: 
        delete_Entry = db.session.query(Question) \
            .filter(Question.question == "This is an example question") \
            .one_or_none()

        delete_Entry.format()

        res = self.client().delete(
                                        '/questions/{}'
                                        .format(delete_Entry.id)
                                    )
        data = res.json
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'] is True)
        self.assertTrue(data['id'] is not None)

        # Save logging
        create_new_logging_entry(
                                    inspect.getframeinfo(frame).function,
                                    time.time() - start_time
                                )

    #
    # Tests if Question can be deleted
    # but sends an ID out of range
    def test_05_2_delete_Entry_and_fail(self):
    
        # Set varbs for logging 
        frame = inspect.currentframe()
        start_time = time.time()

        # Define Testdata: 
        delete_ID = 1000 

        res = self.client().delete(
                                        '/questions/{}'
                                        .format(delete_ID)
                                    )
        data = res.json
        self.assertEqual(res.status_code, 422)

        # Save logging
        create_new_logging_entry(
                                    inspect.getframeinfo(frame).function,
                                    time.time() - start_time
                                )

    # 
    # Method requests the /quizzes API with no previous questions
    # 
    def test_06_1_quiz_data_first_question(self):
    
        # Set varbs for logging 
        frame = inspect.currentframe()
        start_time = time.time()

        # Define Testdata:
        json_Body = {
                        "previous_questions": [],
                        "quiz_category":    {
                                                "id": 5,
                                                "type": "Sports"
                                            }
                    }

        res = self.client().post(
                                        '/quizzes',
                                        json = json_Body
                                    )
        data = res.json
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'] is True)
        self.assertTrue(data['question'] is not None)

        # Save logging
        create_new_logging_entry(
                                    inspect.getframeinfo(frame).function,
                                    time.time() - start_time
                                )

    # 
    # Method requests the /quizzes API with all questions from "Sports"
    # as previous questions and expect no questions as response
    def test_06_2_quiz_data_last_question_with_no_more_data(self):
    
        # Set varbs for logging 
        frame = inspect.currentframe()
        start_time = time.time()

        # Define Testdata:
        json_Body = {
                        "previous_questions": [11,10],
                        "quiz_category":    {
                                                "id": 5,
                                                "type": "Sports"
                                            }
                    }

        res = self.client().post(
                                        '/quizzes',
                                        json = json_Body
                                    )
        data = res.json
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'] is True)

        # Save logging
        create_new_logging_entry(
                                    inspect.getframeinfo(frame).function,
                                    time.time() - start_time
                                )

    #
    #  Print all the results - Counts as Test
    # 
    def test_99_get_results_together(self):
        print("\n-----------------------Result Section-----------------------------------")
        for row in logging_function:
            
            print(
                "Status: OK I Duration: {} Method: {}"
                .format(row['time'], row['function'])
                )
        print("----------------------------End------------------------------------------")

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()