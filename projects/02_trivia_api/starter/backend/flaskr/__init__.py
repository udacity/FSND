import os
import re
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category,db

QUESTIONS_PER_PAGE = 10

def paginated_questions(request, existing_questions):
  page = request.args.get('page',1,type=int)
  start = (page-1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE
  formatted_questions = [question.format() for question in existing_questions]
  current_questions = formatted_questions[start:end]
  return current_questions


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTION')
    return response

  '''
  @TODO:
  Create an endpoint to handle GET requests
  for all available categories.
  '''

  @app.route('/categories', methods=['GET'])
  def categories():
    categories = Category.query.order_by(Category.id).all()
    list_categories = {category.id : category.type for category in categories}
    return jsonify({
      'success':True,
      'categories':list_categories
    })


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
  def get_questions():
    existing_questions = Question.query.order_by(Question.id).all()
    current_questions = paginated_questions(request, existing_questions)

    if len(current_questions)==0:
      abort(404)


    categories = Category.query.order_by(Category.id).all()
    list_categories = {category.id : category.type for category in categories}

    return jsonify({
      'success':True,
      'questions':current_questions,
      'total_questions':len(Question.query.all()),
      'current_category':None,
      'categories':list_categories
    })



  '''
  @TODO:
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''
  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_question(id):
    try:
      question = Question.query.filter(Question.id==id).one_or_none()
      if question is None:
        abort(404)
      question.delete()
      return jsonify({
        "success":True,
        "id":id,
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
  '''
  @TODO:
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  '''
  @app.route('/questions', methods=['POST'])
  def create_new_and_search_question():

    try:
      body = request.get_json()
      search_term = body.get("searchTerm",None)
      if search_term:
        existing_questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
        current_questions = paginated_questions(request, existing_questions)
        return jsonify({
          "success":True,
          "questions":current_questions,
          "total_questions":len(existing_questions),
          "current_category":None
        })
      else:
        question = body.get("question")
        answer = body.get("answer")
        difficulty = body.get("difficulty")
        category = body.get("category")
        question = Question(question=question,answer=answer,difficulty=difficulty,category=category)
        question.insert()
        return jsonify({
          "success":True,
          "created":question.id
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
  @app.route('/categories/<int:id>/questions', methods=['GET'])
  def get_questions_by_categories(id):
    current_category = Category.query.filter(Category.id==id).first()
    existing_questions = Question.query.filter(Question.category==id).all()
    current_questions = paginated_questions(request, existing_questions)

    if len(current_questions) == 0:
      abort(404)

    return jsonify({
      'success':True,
      'questions':current_questions,
      'total_questions':len(existing_questions),
      'currentCategory':current_category.type
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
  def quezzes():
    body = request.get_json()
    previous_questions = body.get("previous_questions")
    category_id = body.get("quiz_category")['id']

    try:
      if category_id:
        questions = Question.query.filter(Question.category==category_id).filter(~Question.id.in_(previous_questions)).all()
      else:
        questions = Question.query.filter(~Question.id.in_(previous_questions)).all()

      if len(questions)>0:
        new_question = random.choice(questions).format()
      else:
        new_question = None


      if new_question is None:
        return jsonify({})
      return jsonify({
        "success":True,
        "question":new_question
      }),200
    except:
      abort(422)











  '''
  @TODO:
  Create error handlers for all expected errors
  including 404 and 422.
  '''

  @app.errorhandler(404)
  def not_found(error):
    return (jsonify({
      "success":False,
      "error":404,
      "message":"The requested resource doesn't exist."
    }), 404)

  @app.errorhandler(422)
  def unprocessable(error):
    return (jsonify({
      "success":False,
      "error":422,
      "message":"Unprocessable Entity."
    }), 422)

  @app.errorhandler(405)
  def method_not_allowed(error):
    return (
      jsonify({
        "success": False,
        "error": 405,
        "message": "Method Not Allowed."
    }), 405)

  @app.errorhandler(500)
  def server_error(error):
    return (jsonify({
      "success":False,
      'error':500,
      "message":"Internal Server Error."
    }), 500)

  @app.errorhandler(400)
  def bad_request(error):
    return (jsonify({
      "success":False,
      "error":400,
      "message":"Bad Request"
    }))

  return app
