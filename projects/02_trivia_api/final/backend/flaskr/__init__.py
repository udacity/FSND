import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

def get_all_categories():
    categoryList = Category.query.order_by(Category.type).all()
    categories = [category.formatkeyvalue() for category in categoryList]

    if len(categories) == 0:
      abort(404)

    categories_dict = {k:v for category in categories for k,v in category.items()}
    return categories_dict  

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  CORS(app)

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
    return response

  @app.route('/categories', methods=['GET'])
  def retrieve_categories():
    return jsonify({'categories': get_all_categories()})
  
  @app.route('/questions', methods=['GET'])
  def retrieve_questions():
    questions = Question.query.all()

    current_questions = paginate_questions(request, questions)
    if len(current_questions) == 0:
      abort(404)

    return jsonify({
      'questions': current_questions,
      'total_questions': len(questions),
      'category': "",
      'categories': get_all_categories()
    })

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_questions(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()

      question.delete()
      questions = Question.query.all()

      current_questions = paginate_questions(request, questions)
      if len(current_questions) == 0:
        abort(404)

      return jsonify({
        'questions': current_questions,
        'total_questions': len(questions),
        'category': "",
        'categories': get_all_categories()
      })

    except:
      abort(422)

  @app.route('/questions', methods=['POST'])
  def add_or_search_question():
    body = request.get_json()

    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_difficulty = body.get('difficulty', None)
    new_category = body.get('category', None)
    searchTerm = body.get('searchTerm')

    try:
      if searchTerm is None:
        new_question = Question(question=new_question, answer=new_answer, difficulty=new_difficulty, category=new_category)
        new_question.insert()

        questions = Question.query.order_by(Question.id).all()
      else:
        questions = Question.query.filter(Question.question.ilike(f'%{searchTerm}%')).all()

      current_questions = paginate_questions(request, questions)
      if len(current_questions) == 0:
        abort(404)

      return jsonify({
        'questions': current_questions,
        'total_questions': len(questions),
        'category': "",
        'categories': get_all_categories()
      })

    except:
      abort(422)

  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def retrieve_questions_by_category(category_id):
    try:
      questions = Question.query.filter(Question.category == category_id).all()

      current_questions = paginate_questions(request, questions)
      if len(current_questions) == 0:
        abort(404)

      return jsonify({
        'questions': current_questions,
        'total_questions': len(current_questions),
        'category': category_id,
        'categories': get_all_categories()
      })
  
    except:
      abort(400)

  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
    parameters = request.get_json()
    previous_questions = parameters.get('previous_questions', None)
    quiz_category = parameters['quiz_category']['id']

    try:
      if quiz_category == 0:
        questions = Question.query.filter(~Question.id.in_(previous_questions)).all()
      else:
        questions = Question.query.filter(Question.category == quiz_category).filter(~Question.id.in_(previous_questions)).all()

      if len(questions) == 0:
        return jsonify({'question': None})

      question = random.choice(questions).format()

      return jsonify({
        'question': question
      })

    except:
      abort(422)

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
          "message": "Resource not found"
      }), 404

  @app.errorhandler(405)
  def not_found(error):
      return jsonify({
          "success": False,
          "error": 405,
          "message": "Method not allowed"
      }), 405

  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
          "success": False,
          "error": 422,
          "message": "Unprocessable"
      }), 422

  @app.errorhandler(500)
  def not_allowed(error):
      return jsonify({
          "success": False,
          "error": 500,
          "message": "Internal server error"
      }), 500

  return app
