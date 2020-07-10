import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page-1)* QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  database_connection = 'postgresql://postgres:adil1234@localhost:5432/triviapp'
  setup_db(app, database_connection)
  CORS(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
    return response


  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=['GET'])
  def get_categories():
    try:
      categories = Category.query.all()
      formatted_categories = [category.format() for category in categories]
    except:
      abort(404)
    return jsonify({
      'success': True,
      'categories': {
        category.id: category.type for category in categories
      },
      'total_categories': len(categories)
    })


  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  num
  ber of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions', methods=['GET'])
  def get_questions():
    try:
      categories = [category.format() for category in Category.query.all()]
      formatted_questions = paginate_questions(request, Question.query.all())
    except:
      abort(404)
    return jsonify({
      'success': True,
      'questions': formatted_questions,
      'total_questions': len(Question.query.all()),
      'current_category': None,
      'categories': categories
    })


  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    
    try:
      question = Question.query.get(question_id)

      if question is None:
        app.logger.info('aborted 404')
        abort(422)

      question.delete()
      formatted_questions = paginate_questions(request, Question.query.all())

    except:
      abort(422)

    return jsonify({
      'success': True,
      'deleted': question.id,
      'total_questions': len(Question.query.all())
    })


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
  def create_question_or_search():
    search_term = request.get_json().get('searchTerm', None)
    #app.logger.info('we in here: ' + search_term)
    if search_term is not None:
      questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
      formatted_questions = [question.format() for question in questions]
 
    
      return jsonify({
        'success': True,
        'questions': formatted_questions,
        'total_questions': len(questions),
        'current_category': None
      })    
    else:
      try:
        body = request.get_json()
        app.logger.info('we in here pap')

        question = body.get('question', None)
        answer = body.get('answer', None)
        category = body.get('category', None)
        difficulty = body.get('difficulty', None)

        if len(question) == 0 or len(answer) == 0:
          abort(400)

        new_question = Question(question=question, answer=answer, category=category, difficulty=difficulty)
        new_question.insert()
        page= request.args.get('page', 1, type=int)
        questions = Question.query.all()
        start = (page-1) *10
        end = start+10
        questions_formatted = [questione.format() for questione in questions]
  

      except:
        abort(400)

      return jsonify({
        'success': True,
        'created_id': new_question.id,
        'new_question': new_question.format(),
        'questions': questions_formatted,
        'total_questions': len(Question.query.all())
      }), 201
    
    
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_category_questions(category_id):
    
    category = Category.query.get(category_id)

    if category is None:
      abort(404)

    questions = Question.query.filter(str(category_id) == Question.category).all()
    app.logger.info(questions)
    
    formatted_questions = [question.format() for question in questions]

    return jsonify({
      'success': True,
      'questions': formatted_questions,
      'total_questions': len(Question.query.all()),
      'total_in_category': len(formatted_questions),
      'current_category': category.format()
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

  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
    body = request.get_json()

    previous_questions = body.get('previous_questions', None)
    quiz_category = body.get('quiz_category', None)
    app.logger.info(previous_questions)
    category_id = quiz_category['id']
    if category_id == 0:
      questions = Question.query.all()
    else:
      questions = Question.query.filter(category_id == Question.category).all()
    
    current_question = None
    for question in questions:
      if question.id not in previous_questions:
        current_question = question.format()
        previous_questions.append(current_question)
        break
    app.logger.info(current_question)



    return jsonify({
      'success': True,
      'previous_questions': previous_questions,
      'question': current_question
    })



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
        "message": error.description
    }), 400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': "resource not found"
    }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': 'unprocessable'
    }), 422


  
  return app

    