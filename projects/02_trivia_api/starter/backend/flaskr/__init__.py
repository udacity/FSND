import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from models import setup_db, Question, Category
import logging

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  
 
  #TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  
  CORS(app,resources={r"/*":{'origins':'*'}})  
  #CORS() 
  logging.getLogger('flask_cors').level = logging.DEBUG

  
  #TODO: Use the after_request decorator to set Access-Control-Allow
  
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
    return response
 
  #TODO: Create an endpoint to handle GET requests for all available categories.
  #return example: [{'id': 1, 'type': 'Science'}, {'id': 2, 'type': 'Art'}, {'id': 3, 'type': 'Geography'}, {'id': 4, 'type': 'History'}, {'id': 5, 'type': 'Entertainment'}, {'id': 6, 'type': 'Sports'}]
  @app.route('/categories', methods=['GET'])
  def get_categories():
    #categories = Category.query.order_by(Category.id).all()
    try: 
      categories = [x[0] for x in Category.query.order_by(Category.id).with_entities(Category.type).all()]
      #categories = Category.query.order_by(Category.id).all()
      #categories = tuple(categories)
      return jsonify({
        'success': True,
        'categories': categories
      })
    except:
      abort(422)

  '''
  TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  def paginate_questions(request,questions):
    page = request.args.get('page',1,type=int)
    start = (page-1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
   # current_questions = [x.format() for x in questions][start:end]
    current_questions = questions[start:end]
    return current_questions


  @app.route('/questions', methods = ['GET'])
  def get_questions():
    try:
      questions = [x.format() for x in Question.query.order_by(Question.id).all()]
      current_questions = paginate_questions(request,questions)

    #categories = [x.format() for x in Category.query.order_by(Category.id).all()]
      categories = [x[0] for x in Category.query.order_by(Category.id).with_entities(Category.type).all()]

      if len(current_questions) == 0:
        abort(404)

      return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': len(current_questions),
        'categories': categories,
        'current_Category': categories[0]
      })
    except:
      abort(422)
    
  '''
  TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods = ['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id==question_id).one_or_none()
      if question_id is None:
        abort(404)
      else:
        question.delete()

      questions = [x.format() for x in Question.query.order_by(Question.id).all()]
      current_questions = paginate_questions(request,questions)

      categories = [x[0] for x in Category.query.order_by(Category.id).with_entities(Category.type).all()]


      return jsonify({
        'success': True
        # 'sucess': True,
        # 'questions': current_questions,
        # 'total_questions': len(questions),
        # 'categories': categories,
        # 'current_category': categories[0]
      })
    except:
      abort(422)



  '''
  TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions/add', methods = ['POST'])
  def create_question():
    body = request.get_json()
    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_category = body.get('category', None)
    new_difficulty = body.get('difficulty', None)

    try:
      question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
      question.insert()

      questions = [x.format() for x in Question.query.order_by(Question.id).all()]
      current_questions = paginate_questions(request,questions)

      return jsonify({
        'success': True,
        'created': question.id,
        'questions': current_questions,
        'total questions': len(questions)
      })
    except:
      abort(422)
  
  '''
  TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_questions_submission():
    body = request.get_json()
    search_term = body.get('searchTerm',None)
    #search_term=request.form.get('search_term', '')

    try:
      questions = [x.format() for x in Question.query.order_by(Question.id).all()]
    except:
      abort(404)
    
    if len(questions)!=0:
      matched_questions = [i for i in questions if search_term in i['question']]

    return jsonify({
        'success': True,
        'questions': matched_questions,
        'total questions': len(matched_questions)
    })

  '''
  TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>', methods=['GET'])
  def show_questions(category_id):
    try:
      query = Question.query.filter(Question.category==category_id).order_by(Question.id).all()
      questions = [x.format() for x in query]
      current_questions = paginate_questions(request,questions)
      current_category = Category.query.with_entities(Category.id,Category.type).filter(Category.id==category_id).one_or_none()
      if current_category is None:
        abort(404)
    except:
      abort(422)
    
    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(current_questions),
      'current_category': current_category
    })


  '''
  TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def next_question():
    body = request.get_json()
    quiz_category = body.get('quiz_category', None)['type']
    
    previous_questions = body.get('previous_questions', None)
    
    try:
      if quiz_category == 'click':
        query = Question.query.with_entities(Question.id).all()
      else:
        quiz_category_id = Category.query.with_entities(Category.id).filter(Category.type==quiz_category).one_or_none()[0]
        query = Question.query.with_entities(Question.id).filter(Question.category==quiz_category_id).all()

      question_ids = [x[0] for x in query]
      ids = [i for i in question_ids if i not in previous_questions]
      current_question_id = random.choice(ids)
      current_question = Question.query.filter(Question.id==current_question_id).one_or_none().format()
    except:
      abort(422)

    return jsonify({
    'success': True,
    'question': current_question
    })

  '''
  TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'Resource Not Found'
    }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': 'Unprocessable'
    }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message': 'Bad Request'
    }), 400

  @app.errorhandler(500)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 500,
      'message': 'Internal Server Error'
    }), 500

  return app

    