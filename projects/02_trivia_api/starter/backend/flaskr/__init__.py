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
  CORS(app, resources={r"/questions/*": {'origins': '*'} })

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
    return response

  def paginate_questions(request, questions):
      # Paginate the request of questions
      page = request.args.get('page', 1, type=int)
      start = (page - 1) * QUESTIONS_PER_PAGE
      end = start + QUESTIONS_PER_PAGE

      selection = [question.format() for question in questions]
      current_questions = selection[start:end]
      return current_questions

  def get_categories():
    categories = {}
    try:
      question_categories = Category.query.order_by(Category.id).all()
      for category in question_categories:
        categories[category.id] = category.type
      
      return categories

    except:
      # Return empty dictionary if empty
      return {}


  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=['GET'])
  def get_all_categories():
    categories = {}
    try:
      categories = get_categories()

      return jsonify({
        'success': True, 
        'categories': categories
      })
    except:
      abort(404)

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
  @app.route('/questions', methods=['GET'])
  def get_all_questions():
    errorCode = 400
    try:
      questions = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, questions)

      # Get all categories
      categories = get_categories()

      if len(current_questions) == 0:
        errorCode = 404
        abort(404)
    
      return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': len(questions),
        'current_category': 'Geography',
        'categories': categories
      })

    except:
      abort(errorCode)

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    errorCode = 422
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()
      
      if question is None:
        errorCode = 404
        abort(404)

      question.delete()
      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, selection)

      return jsonify({
        'success': True,
        'deleted': question_id,
        'questions': current_questions,
        'total_questions': len(Question.query.all())
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
  @app.route('/questions', methods=['POST'])
  def ask_new_question():

    body = request.get_json()

    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_category = body.get('category', None)
    new_difficulty = body.get('difficulty', None)

    try:
      category = Category.query.get(new_category)

      if category is None:
        abort(422)

      # After running tests, realized I missed checks for empty questions/answers
      if new_question is None or new_question == '':
        abort(422)
      if new_answer is None or new_answer == '':
        abort(422)

      question = Question(
        question=new_question, 
        answer=new_answer,
        category=category.id, 
        difficulty=new_difficulty)
      
      question.insert()

      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, selection)

      return jsonify({
        'success': True,
        'created': question.id,
        'questions': current_questions,
        'total_questions': len(Question.query.all())
      })

    except:
      abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    body = request.get_json()

    # If no body was passed or the body didn't contain the correct json
    if body is None or not body['searchTerm']:
      abort(422)

    search = body.get('searchTerm', None)
    if search is None:
      abort(422)

    try:
      selection = Question.query.order_by(Question.id).filter(
        Question.question.ilike('%{}%'.format(search)))
      current_questions = paginate_questions(request, selection)

      return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': len(selection.all())
      })
    except:
      abort(422)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_questions_by_category(category_id):
    errorCode = 422
    try:
      category = Category.query.get(category_id)

      if category is None:
        errorCode = 404
        abort(errorCode)

      selection = Question.query.order_by(Question.id).filter(
        Question.category == category.id)
      current_questions = paginate_questions(request, selection)

      return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': len(selection.all())
      })
    except:
      abort(errorCode)

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
  @app.route('/quizzes', methods=['POST'])
  def get_questions_for_quiz():
    body = request.get_json()
    quizCategory = body.get('quiz_category', None)
    prevQuestions = body.get('previous_questions', [])

    try:
      if not quizCategory:
        abort(400)
      
      selection = None
      if quizCategory['id'] == 0:
        # Get questions in any category
        # Filter out questions in array of ids
        selection = Question.query.filter(
          ~Question.id.in_(prevQuestions)
        ).all()

      else:
        # Get questions in specific category
        # Filter out questions in array of ids
        selection = Question.query.filter(
            Question.category == quizCategory['id'],
            ~Question.id.in_(prevQuestions)
        ).all()
      
      if len(selection) == 0:
        return jsonify({
          'success': True,
          'total_questions': len(selection)
        })

      selected_question = random.choice(selection)

      return jsonify({
        'success': True,
        'question': {
          'id': selected_question.id,
          'question': selected_question.question,
          'answer': selected_question.answer,
          'category': selected_question.category,
          'difficulty': selected_question.difficulty,
        },
        'total_questions': len(selection)
      })
    except:
      abort(422)

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "Resource not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "Unprocessable"
      }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message": "bad request"
      }), 400

  @app.errorhandler(405)
  def not_allowed(error):
    return jsonify({
      "success": False, 
      "error": 405,
      "message": "Not allowed"
      }), 405

  @app.errorhandler(500)
  def not_allowed(error):
    return jsonify({
      "success": False, 
      "error": 500,
      "message": "Server Error"
      }), 500
  
  return app

    