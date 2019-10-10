import os
from flask import Flask, request, abort, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
  """
  A function to paginate response
  :param request: Any
  :param selection: List
  :return: List
  """
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  books = [book.format() for book in selection]
  current_books = books[start:end]

  return current_books

def create_app(test_config=None):
  """
  Function to create the main app
  :param test_config:
  :return:
  """
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
    return response

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False,
      "error": 404,
      "message": "Not found"
    }), 404
  
  @app.errorhandler(422)
  def not_found(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Not found"
    }), 422

  @app.route('/categories')
  @cross_origin()
  def categories():
    cats = Category.query.all()
    current_cats = paginate_questions(request, cats)
    return jsonify({
            'success': True,
            'categories': current_cats,
            'total_books': len(cats)
      }), 200

  @app.route('/questions', methods=['GET', 'POST'])
  @cross_origin()
  def questions():
    if request.method == 'POST':
     q = request.args.get('question')
     a = request.args.get('answer')
     c = request.args.get('category')
     d = request.args.get('difficulty')
     question = Question(
       question=q,
       answer=a,
       category=c,
       difficulty=d
     )
     question.update()
     return jsonify({'success': True}), 200
    else:
      questions = Question.query.all()
      questions_paginated = paginate_questions(request, questions)
      questions_formatted = [[q.get("question"), q.get(
          "answer"), q.get("category"), q.get("difficulty")] for q in questions_paginated]
      categories = Category.query.all()
      formatted_categories = [category.format() for category in categories]
      formatted_categories = [c.get("type") for c in formatted_categories]
      return jsonify({
        'success': True,
        'questions': questions_formatted,
        'total_questions': len(questions),
        'categories': formatted_categories,
        'current_category': formatted_categories
        }), 200

  @app.route('/questions/<int:question_id>', methods=['GET', 'DELETE', 'POST'])
  @cross_origin()
  def question(question_id):
    try:
      question = Question.query.get(question_id)
      if request.method == 'GET':
        return jsonify({
          'success': True,
          'question': question.format()
        })
      elif request.method == 'DELETE':
        question.delete()
        return jsonify({'success': True}), 200
    except:
      abort(404)

  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''


  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  
  return app

    
