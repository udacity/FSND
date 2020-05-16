import os
import random
import traceback
import json
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from models import setup_db, Question, Category


QUESTIONS_PER_PAGE = 10

def paginate_result(result, page=1):
  """Paginates the query result by the globally defined QUESTIONS_PER_PAGE

  Arguments:
      result {list} -- 
          A list of results return from SQLAlchemy Query object.
          See: https://docs.sqlalchemy.org/en/13/orm/query.html#sqlalchemy.orm.query.Query.all
        

  Keyword Arguments:
      page {int} -- 
          The page to be returned by the API (e.g. to update the frontend)
          (default: {1})

  Returns:
      list -- 
          List of questions as dicts with a maximum length defined by QUESTIONS_PER_PAGE per page.
  """
  start = QUESTIONS_PER_PAGE * (page-1)
  end = min(len(result), start+QUESTIONS_PER_PAGE)
  return [result[ix].format() for ix in range(start, end)]

def get_cats_and_format_response(paginated_questions=None, current_category='all', created=None, deleted=None):
  """
  Provides the default response layout with and adds `questions` (paginated) & `created` if present:
      - success
      - total_questions
      - categories
      - current_category
      - questions (optional) 
      - created (optional)

  Arguments:
    paginated_questions {list} -- List of questions as dicts with a maximum length defined by QUESTIONS_PER_PAGE per page.]
    current_category {int} -- the id of the current category (default: 'all')
  
  Returns:
      dict -- A dictionary to be formatted as a JSON-encoded server response.
  """
  
  categories = [category.format() for category in Category.query.all()]
  total_questions = len(Question.query.all())
  res = {
        'success': True,
        'total_questions': total_questions,
        'current_category': current_category,
        'categories': categories
  }
  if paginated_questions:
    res.update({'questions': paginated_questions})
  if created:
    res.update({'created': created})
  if deleted:
    res.update({'deleted': deleted})
  return res

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  
  db = SQLAlchemy()
  Migrate(app, db)

  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  #!OK
  '''
  cors = CORS(app, resources={r'/api/*': {"origins": "*"}})
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  #!OK
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  @app.route('/')
  def index():
    """"Returns the homepage of the API."""
    
    return 'Hello, World!'

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/api/categories')
  def get_all_categories():
    """"Returns a JSON-encoded response with attributes:
      - success
      - categories
      - current_category
      - total_questions
    """
    
    return jsonify(get_cats_and_format_response()) # no need to query categories as they are provided by default response format

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
  @app.route('/api/questions', methods=['GET', 'POST'])
  def handle_questions():
    if request.method == 'GET':
      return get_all_questions()
    elif request.method == 'POST':
      data = json.loads(request.get_json())
      return create_question(data)
  
  def get_all_questions():
    """"
    Returns a JSON-encoded response with paginated questions and standard attributes:
      - success (standard)
      - categories (standard)
      - total_questions (standard)
      - current_category
      - questions
    """
    try:
      result = Question.query.order_by(Question.id).all()
      if not len(result):
        return 'Resource does not exist', 404
      paginated_questions = paginate_result(result) 
      return jsonify(
          get_cats_and_format_response(paginated_questions)
        )
    except:
      print(traceback.print_exc())
      return 'ERROR:' + str(traceback.print_exc()), 400
  
  def create_question(data):
    """"
    Inserts the question into DB if:
      - body contains a 'question' property
      - all required args are present in 'question' property
      - No duplicate question is found

    Returns the standard JSON response, adding:
      - created: details of the newly created question
    
    The standard response includes the following attr:
      - success
      - categories
      - total_questions
      - current_category
    """
    if not 'question' in data:
      return 'Bad Request - Malformatted (e.g. missing required parameter)', 400
    if not all (key in data['question'] for key in ('question', 'answer', 'difficulty', 'category_id')):
      return 'Bad Request - Malformatted (e.g. missing required parameter)', 400
  
    try: # if current_category is present pass it on to response formatter later
      cur_cat = data['current_category']
    except KeyError as e:
      cur_cat = None

    qst = data['question']
    try: # If no duplicate is found, create question
      dupes = Question.query.filter(Question.question.ilike(f"%{qst['question']}%")).all()
      if len(dupes) > 0:
        return 'Unprocessable - Resource already present', 422
      
      new_question = Question(**qst)
      new_question.insert()
      return jsonify(
        get_cats_and_format_response(created=new_question.format(), current_category=cur_cat)
      )
    except:
      print('Rolled back. ERROR:', traceback.print_exc())
      db.session.rollback()
      return 'Unprocessable' + str(traceback.print_exc()), 422
    finally:
      db.session.close()    

  @app.route('/api/questions/categories/<int:category_id>')
  def get_all_questions_by_category(category_id):
    """"
    Returns a JSON-encoded response with paginated questions for a given category_id and standard attributes:
      - success (standard)
      - categories (standard)
      - total_questions (standard)
      - current_category (required)
      - questions
    """
    try:
      result = Question.query.filter_by(category_id=category_id).order_by(Question.id).all()
      if not len(result):
        return 'Resource does not exist', 404
      paginated_questions = paginate_result(result) 
      return jsonify(
          get_cats_and_format_response(paginated_questions, current_category=category_id)
        )
    except:
      print(traceback.print_exc())
      return 'ERROR:' + str(traceback.print_exc()), 400

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/api/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      to_delete = Question.query.get(question_id)
      print(to_delete.format())
      to_delete.delete()
      return get_cats_and_format_response(deleted=to_delete.format())
    except:
      db.session.rollback()
      print('Rolled back. ERROR:', traceback.print_exc())
      return 'Something went wrong:' + str(traceback.print_exc()), 422
    finally:
      db.session.close()
    return 

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

    