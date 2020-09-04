import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={r"/api/*":{"origins":"*"}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type,Authorization,true')
    response.headers.add(
            'Access-Control-Allow-Methods',
            'GET,PUT,POST,DELETE,OPTIONS')
    return response
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/api/categories')
  def retrieve_categories():
    all_categories = Category.query.all()
    all_categories = [ category.format() for category in all_categories]
    if(len(all_categories) == 0):
      abort(404)
      
    return jsonify({
      'success': True,
       'categories': all_categories,
       'total_categories': len(all_categories)
    })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, (current category, categories). ????????????????

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions.
  '''
  def paginate_questions(request, all_questions):
    page = request.args.get("page", 1, type=int)
    start = (page-1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    all_questions = [ question.format() for question in all_questions]
    current_questions = all_questions[start:end]
    return current_questions

  @app.route('/api/questions')
  def retrieve_questions():
    all_questions = Question.query.all()
    current_questions = paginate_questions(request, all_questions)
    categories = Category.query.all()
    categories = [ category.format() for category in categories]

    if(len(current_questions) == 0):
      abort(404)
      
    return jsonify({
      'success': True,
       'questions': current_questions,
       'total_questions': len(all_questions),
       'categories':categories
    })
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/api/questions/<int:id>', methods=['DELETE'])
  def delete_question(id):
    try:
      Question.query.get(id).delete()
      return jsonify({
      'success': True,
    })
    except:
      abort(422)
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/api/questions', methods=['POST'])
  def create_question():
    try:
      question = request.get_json().get('question', '') 
      answer = request.get_json().get('answer', '') 
      difficulty = request.get_json().get('difficulty', '') 
      category = request.get_json().get('category', '') 
      Question(question, answer, category, difficulty)
      return jsonify({
        'success': True,
      })
    except:
      abort(400)
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/api/questions/search', methods=['POST'])
  def search_questions():
    term = request.get_json().get('searchTerm', '')
    all_questions = Question.query.filter(Question.question.ilike("%"+term.strip()+"%")).all()
    current_questions = paginate_questions(request, all_questions)

    if(len(current_questions) == 0):
      abort(404)
      
    return jsonify({
      'success': True,
       'questions': current_questions,
       'total_questions': len(all_questions),
    })

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

  @app.route('/api/categories/<int:category>/questions')
  def retrieve_category_questions(category):
    all_questions = Question.query.filter_by(category=category).all()
    current_questions = paginate_questions(request, all_questions)

    if(len(current_questions) == 0):
      abort(404)
      
    return jsonify({
      'success': True,
       'questions': current_questions,
       'total_questions': len(all_questions),
    })
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
  @app.route('/api/quizzes', methods=['POST'])
  def play_quiz():
    # try:
    previous_questions = request.get_json().get('previous_questions', '') 
    category = request.get_json().get('quiz_category')
    category = category["id"]
    if category==0:
      questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
    else:
      questions = Question.query.filter(Question.category==category, Question.id.notin_(previous_questions)).all()
    
    if len(questions) > 0:
      question = random.choice(questions)
      question = question.format()
    else:
      question = False

    return jsonify({
      'success': True,
      'question': question
    })
    # except:
    #   abort(404)
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
        "success": False, 
        "error": 400,
        "message": "Bad request"
        }), 400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "Not found"
        }), 404

  @app.errorhandler(422)
  def unprocessable_request(error):
    return jsonify({
        "success": False, 
        "error": 422,
        "message": "Unprocessable request"
        }), 422

  return app

