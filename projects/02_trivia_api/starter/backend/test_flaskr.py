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
    self.database_path = "postgres://{}/{}".format('postgres@localhost:5432', self.database_name)
    setup_db(self.app, self.database_path)

    self.new_question = {
      'question': 'Test question',
      'answer': 'Test',
      'category': 5,
      'difficulty': 1
    }

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
  TODO -- done
  Write at least one test for each test for successful operation and for expected errors.
  """
  def test_get_paginated_questions(self):
    res = self.client().get('/questions')
    data = json.loads(res.data)

    self.assertEqual(res.status_code, 200)
    self.assertEqual(data['success'], True)
    self.assertTrue(data['total_questions'])
    self.assertTrue(len(data['categories']))
    self.assertTrue(len(data['questions']))

  def test_404_sent_requesting_beyond_valid_page(self):
    res = self.client().get('/questions?page=1000')
    data = json.loads(res.data)

    self.assertEqual(res.status_code, 404)
    self.assertEqual(data['success'], False)
    self.assertEqual(data['message'], 'Not found')

  def test_get_categories(self):
    res = self.client().get('/categories')
    data = json.loads(res.data)

    self.assertEqual(res.status_code, 200)
    self.assertEqual(data['success'], True)
    self.assertTrue(data['total_categories'])
    self.assertTrue(len(data['categories']))

  def test_delete_question(self):
    res = self.client().delete('/questions/5',)
    data = json.loads(res.data)

    question = Question.query.filter(Question.id == 5).one_or_none()

    self.assertEqual(res.status_code, 200)
    self.assertEqual(data['success'], True)
    self.assertEqual(data['deleted'], 5)
    self.assertTrue(data['total_questions'])
    self.assertTrue(len(data['questions']))
    self.assertEqual(question, None)

  def test_404_if_question_does_not_exist(self):
    res = self.client().delete('/questions/1000')
    data = json.loads(res.data)

    self.assertEqual(res.status_code, 422)
    self.assertEqual(data['success'], False)
    self.assertEqual(data['message'], 'Unprocessable')

  def test_create_new_question(self):
    res = self.client().post('/questions', json=self.new_question)
    data = json.loads(res.data)

    self.assertEqual(res.status_code, 200)
    self.assertEqual(data['success'], True)
    self.assertTrue(data['total_questions'])
    self.assertTrue(data['created'])
    self.assertTrue(len(data['questions']))

  def test_405_if_question_creation_not_allowed(self):
    res = self.client().post('/questions/45', json=self.new_question)
    data = json.loads(res.data)

    self.assertEqual(res.status_code, 405)
    self.assertEqual(data['success'], False)
    self.assertEqual(data['message'], 'Method not allowed')

  def test_get_questions_search_with_results(self):
    res = self.client().post('/questions', json={'searchTerm': 'Tom Hanks'})
    data = json.loads(res.data)

    self.assertEqual(res.status_code, 200)
    self.assertEqual(data['success'], True)
    self.assertTrue(data['total_questions'])
    self.assertEqual(len(data['questions']), 1)

  def test_get_questions_search_without_results(self):
    res = self.client().post('/questions', json={'searchTerm': 'manzana'})
    data = json.loads(res.data)

    self.assertEqual(res.status_code, 200)
    self.assertEqual(data['success'], True)
    self.assertEqual(data['total_questions'], 0)
    self.assertEqual(len(data['questions']), 0)

  def test_get_questions_by_category(self):
    res = self.client().get('/categories/1/questions')
    data = json.loads(res.data)

    self.assertEqual(res.status_code, 200)
    self.assertEqual(data['success'], True)
    self.assertTrue(data['total_questions'])
    self.assertTrue(len(data['questions']))
    self.assertEqual(data['current_category'], 1)

  def test_404_if_questions_for_category_does_not_exist(self):
    res = self.client().get('/categories/1000/questions')
    data = json.loads(res.data)

    self.assertEqual(res.status_code, 404)
    self.assertEqual(data['success'], False)
    self.assertEqual(data['message'], 'Not found')

  def test_get_questions_for_quizzes(self):
    res = self.client().post('/quizzes',
      json={'previous_questions': [1],
      'quiz_category': {
        'id': '1',
        'type': 'Science'
      }})
    data = json.loads(res.data)

    self.assertEqual(res.status_code, 200)
    self.assertEqual(data['success'], True)
    self.assertTrue(data['question'])

  def test_422_if_quizzes_body_is_empty(self):
    res = self.client().get('/quizzes', json={})
    data = json.loads(res.data)

    self.assertEqual(res.status_code, 405)
    self.assertEqual(data['success'], False)
    self.assertEqual(data['message'], 'Method not allowed')

# Make the tests conveniently executable
if __name__ == "__main__":
  unittest.main()