import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from operator import itemgetter 

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

#
# Method the cover following cases: 
# Paginate all Question-Results to a Limit of: * QUESTIONS_PER_PAGE * 
def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start =  (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

#
# Initial Method to create the App
#
def create_app(test_config=None):
  app = Flask(__name__)
  setup_db(app)
  
  # 
  # CORS Headers
  #
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  #
  # Home Route: 
  # 
  @app.route('/', methods=['GET'])
  def home_route():
    
    return jsonify({
      'success': True,
      'message': "Welcome! You are requesting to the API!"
    })

  #
  # Route for the following cases: 
  # Get Questions by Category-ID
  @app.route('/categories/<int:categorie_id>/questions', methods=['GET'])
  def retrieve_categories(categorie_id):
    
    category = db.session.query(Category) \
      .filter(Category.id == categorie_id) \
      .one_or_none()
    
    if category is None:
      abort(404)

    elif category is not None: 
      selection = db.session.query(Question) \
        .filter(Question.category == categorie_id) \
        .all()

      questionResult = paginate_questions(request, selection)

      return jsonify({
        'success': True,
        'questions': questionResult,
        'total_questions': len(db.session.query(Question)
                                .filter(Question.category == categorie_id)
                                .all()
                              ),
        'current_category': category.type
      })

  #
  # Route to cover the cases: 
  # Get all Questions, Search Questions, Add Questions
  @app.route('/questions', methods=['GET', 'POST'])
  def retrieve_questions():

    # GET Method
    if request.method == 'GET':
      selection = db.session.query(Question) \
        .order_by(Question.id) \
        .all()

      categories = db.session.query(Category) \
        .order_by(Category.id) \
        .all()
        
      categoriesResult = []

      for categorie in categories:
        categoriesResult.append(categorie.type) 

      questionResult = paginate_questions(request, selection)

      if len(questionResult) == 0:
        abort(404)

      return jsonify({
        'success': True,
        'questions': questionResult,
        'total_questions': len(db.session.query(Question).all()),
        'categories': categoriesResult
      })

    # POST Method for Search questions
    elif request.method == 'POST':

      # Check refering URL to differ between Search Submit and Create new Question
      if  request.headers.get('Referer') is not None \
          and '/add' in request.headers.get('Referer'):
        
        try: 
          newInsert = Question( \
                                question = request.json.get('question'), \
                                answer = request.json.get('answer'), \
                                difficulty = request.json.get('difficulty'), \
                                category = request.json.get('category')
                              )
          newInsert.insert()
          newInsert.id

          return jsonify({
            'success': True,
            'id': newInsert.id,
          }) 

        except: 
          abort(422)

      elif request.json.get('searchTerm') is not None:
        
        try: 
          data = request.json.get('searchTerm')

          selection = db.session.query(Question) \
            .filter(Question.question.ilike('%' + data + '%')) \
            .order_by(Question.id) \
            .all()


          questionResult = paginate_questions(request, selection)

          return jsonify({
            'success': True,
            'questions': questionResult,
            'total_hits_in_database': len(selection)
          })

        except: 
          abort(400)

  #
  # Get Category to display them
  #
  @app.route('/categories', methods=['GET'])
  def get_categories():

    categories = db.session.query(Category) \
      .order_by(Category.id) \
      .all()
        
    categoriesResult = []

    for categorie in categories:
      categoriesResult.append(categorie.type)

    return jsonify({
      'success': True,
      'categories': categoriesResult
    })

  #
  # Route for deleting Objects
  #
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):

    try: 
      deleteObj = db.session.query(Question) \
        .get(question_id)
      deleteObj.delete()

      return jsonify({
        'success': True,
        'id': question_id
      })

    except: 
      abort(422)

  # 
  # Route for getting data to play the Quiz-game
  #
  @app.route('/quizzes', methods=['POST'])
  def get_results_for_the_game():
    
    # Get JSON data from request
    prev_Question_ID  = request.json['previous_questions']
    category          = request.json['quiz_category']['id']

    # See if we have a specific category to choose from or not
    if category == 0:
      question_List = db.session.query(Question) \
        .all()

    # And if not
    elif category != 0: 
      question_List = db.session.query(Question) \
        .filter(Question.category == category) \
        .all()

    questions = [question.format() for question in question_List]

    # Exclude the list of previous questions to prevent to get
    # the same questions again
    AcutualList = [i for i in questions if i['id'] not in prev_Question_ID]

    if len(AcutualList) != 0:
    # Check if we have questions left
      currentQuestion = random.choice(AcutualList)
      return jsonify({
        'success': True,
        'question': currentQuestion,
      })

    elif len(AcutualList) == 0:
      return jsonify({
        'success': True,
      })

  #
  # Route for 404 Error
  #
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "resource not found"
    }), 404

  #
  # Route for 422 Error
  #
  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
        "success": False, 
        "error": 422,
        "message": "unprocessable"
      }), 422

  #
  # Route for 400 Error
  #
  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({
        "success": False, 
        "error": 400,
        "message": "bad request"
      }), 400

  return app

    