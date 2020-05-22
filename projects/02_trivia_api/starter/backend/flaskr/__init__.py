import os
import random
import traceback
import json
from flask import Flask, request, abort, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from flask_cors import CORS
from flask_migrate import Migrate
from models import setup_db, Question, Category
from werkzeug.exceptions import BadRequest, NotFound, UnprocessableEntity, MethodNotAllowed


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

def format_search_response(search_term, paginated_questions=None, total_questions=None, categories=None, total_categories=None, page=1):
  """Formats JSON-encoded API-response after search operation. 
  Supports search for categry and question.
  
  Keyword arguments:
  search_term* -- The text string for which to search
  paginated_questions -- List of 1 page of questions with details to returned by query
  page -- Page of questions (default 1)
  total_questions -- Total number questions returned by query
  categories -- List of categories with details returned by query
  total_categories -- Total number of categories returned by query

  
  Return: dict with some standard attributes for search:
    - success,
    - page,
    - search_term,
    - total_categories (relevant for both category & question search)
  Adding the following if relevant to CRUD operation:
    - paginated_questions (question search only)
    - total_questions (question search only),
    - categories (category search only)
    """
  res = {
    "success": True
    , "page": page
    , "search_term": search_term
    , "total_categories": total_categories
  }
  if paginated_questions is not None: # returning empty list if without result
    res.update({'questions': paginated_questions})
    res.update({'total_questions': total_questions})
  if categories:
    res.update({'categories': categories})
  return res
def format_crud_response(deleted=None, created=None, paginated_questions=None, page=1, total_questions=None, current_category='all', categories=None, total_categories=None):
  """Formats JSON-encoded API-response after CRUD operation
  
  Keyword arguments:
  deleted -- The deleted question with id, question, answer, difficulty, category_id
  created -- The created question with id, question, answer, difficulty, category_id
  paginated_questions -- List of 1 page of questions with details to render to frontend
  page -- Page of questions (default 1)
  total_questions -- Total number questions
  current_category -- Current category_id (default 'all')
  categories --List of categories with details to render to frontend
  total_categories -- Total number of categories

  
  Return: dict with some standard attributes for CRUD:
    - success,
    - total_questions,
    - current_category,
    - total_categories
  Adding the following if relevant to CRUD operation:
    - deleted,
    - created,
    - paginated_questions OR categories
    - page,
    - total_questions OR total_categories
    """
  res =  {
    "success": True
    , "total_questions": total_questions
    , "current_category": current_category
    , "total_categories": total_categories
  }
  if deleted:
    res.update({"deleted": deleted})
  if created:
    res.update({"created": created})
  if paginated_questions:
    res.update({"questions": paginated_questions})
  if page:
    res.update({"page": page})
  if total_questions is None:
    res.update({"total_questions": len(Question.query.order_by(Question.id).all())})
  if categories:
    res.update({"categories": categories})
  if total_categories is None:
    res.update({"total_categories": len(Category.query.order_by(Category.id).all())})

  return res
def format_play_response(question, current_category):
  """Formats random question to JSON-encoded API-response
  
  Keyword arguments:
  question -- Random Question
  answer -- Question's answer
  current_category -- Question's category
  
  Return: dict adding success attribute
  """
  
  return {
    "success": True
    , "question": question
    , "current_category": current_category
  }

def format_error(error_code, error_name, error_description):
  """Formats a JSON-encoded API-response for the respective error.
  Please refer to werkzeug docs for info:
  https://werkzeug.palletsprojects.com/en/1.0.x/exceptions/#werkzeug.exceptions.BadRequest
  
  Keyword arguments:
  error_code -- werkzeug's error code
  error_name -- werkzeugs's error name
  error_description -- werkzeugs's error description
  
  Return: dict adding success attribute
  """
  
  return {
    'success': False
    , 'error_code': error_code
    , 'error_name': error_name
    , 'error_description': error_description
  }

def create_app(test_config=None):
  # create and configure the app
  cwd = os.getcwd()
  backend_ix = cwd.find('\\backend')
  end = len(cwd) if backend_ix == -1 else backend_ix
  template_dir,static_dir = os.path.abspath(cwd[:end] + '/frontend/public'), os.path.abspath(cwd[:end] + '/frontend/build/static')

  app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
  
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

  @app.route('/', defaults={'path': ''})
  @app.route('/<path:path>')
  def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
      return send_from_directory(app.static_folder, path)
    else:
      return render_template('index.html')



  # def index():
  #   """"Returns the homepage of the API."""
    
  #   return render_template('index.html')

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
    all_categories = {category.id: category.type for category in Category.query.all()}
    return jsonify(format_crud_response(categories=all_categories))

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
      args = {key: int(val) if key == 'page' else val for key, val in request.args.items()}
      return get_all_questions(**args)
    elif request.method == 'POST':
      data = request.get_json()
      if isinstance(data, str):
        data = json.loads(data)
      try:
        return create_question(**data['question'])
      except TypeError as e:
        abort(400)
  
  def get_all_questions(page=1):
    """"
    Returns a JSON-encoded response with paginated questions and standard attributes:
      - success (standard)
      - categories (standard)
      - total_questions (standard)
      - current_category (default: 'all')
      - questions
    """
    try:
      page = int(page)
      result = Question.query.order_by(Question.id).all()
      if len(result)<1:
        abort(404)
      paginated_questions = paginate_result(result, page) 
      categories = {question.category.id: question.category.type for question in result}
      
      return jsonify(
          format_crud_response(paginated_questions=paginated_questions, categories=categories)
        )
    except Exception as e:
      db.session.rollback()
      if e.code == 404:
        abort(404)
      else:
        print(e, traceback.print_exc())
        abort(400)
  
  def create_question(question, answer, difficulty, **kwargs):
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
    response_attr = {}
    qst = {
      'question': question
      , 'answer': answer
      , 'difficulty': difficulty
    }
    if 'category' in kwargs:
      qst.update({'category_id': kwargs['category']})
    
    if 'current_category' in kwargs:
      response_attr.update({'current_category': current_category})
    
    paginate_result_attr = {
      "result": Question.query.order_by(Question.id).all()
    }
    if 'page' in kwargs:
      paginate_result_attr.update({'page': page})
      response_attr.update({'page': page}) 
    
    response_attr.update({
      'paginated_questions': paginate_result(**paginate_result_attr)
    })

    try: # If no duplicate is found, create question
      dupes = Question.query.filter(Question.question.ilike(f"%{qst['question']}%")).all()
      if len(dupes)>0:
        abort(422)
      
      new_question = Question(**qst)
      new_question.insert()
      
      response_attr.update({
        'created': new_question.format()
      })

      return jsonify(
        format_crud_response(**response_attr)
      )
    except Exception as e:
      db.session.rollback()
      if e.code:
        if e.code == 422:
          abort(422)
      else:
        print('Rolled back. ERROR:', traceback.print_exc())
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
      if len(result)<1:
        abort(404)
      paginated_questions = paginate_result(result) 
      return jsonify(
          format_crud_response(paginated_questions=paginated_questions, total_questions=len(result), current_category=category_id)
        )
    except Exception as e:
      db.session.rollback()
      if e.code == 404:
        abort(404)
      else:
        abort(422)

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
      to_delete.delete()
      return jsonify(
        format_crud_response(deleted=to_delete.format())
      )
    except AttributeError as e:
      db.session.rollback()
      print('Rolled back. AttributeError:', e)
      abort(404)
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
  @app.route('/api/questions/searches', methods=['POST'])
  def search_question():
    try:
      data = json.loads(request.get_json())  
    except TypeError as e:
      abort(400)
    
    if not 'searchTerm' in data:
      abort(400)
    
    if 'searchOnAnswer' in data:
      if not isinstance(data['search_on_answer'], bool):
        return 'Bad Request - Malformatted (e.g. boolean value)', 400
      filter_on = Question.answer
    else:
      filter_on = Question.question

    page = data['page'] if 'page' in data else 1
    try:
      search_result = Question.query.filter(filter_on.ilike(f'%{data["searchTerm"]}%')).all()
      paginated_questions = paginate_result(search_result, page)
      categories = {question.category_id for question in search_result}
      return jsonify(
        format_search_response(
          paginated_questions=paginated_questions,
          search_term=data['searchTerm'],
          total_questions=len(search_result),
          total_categories=len(categories)
        )
      )
    except AttributeError as e:
      print(e)
      db.session.rollback()
      abort(422)
    finally:
      db.session.close()
  
  @app.route('/api/categories/searches', methods=['POST'])
  def search_categories():
    try:
      data = json.loads(request.get_json())
    except TypeError as e:
      abort(400)
    if not 'searchTerm' in data:
      abort(400)
    
    try:
      search_result = Category.query.filter(Category.type.ilike(f'%{data["searchTerm"]}%')).all()
      categories = [category.format() for category in search_result]
      return jsonify(
        format_search_response(
          categories=categories,
          search_term=data['searchTerm'],
          total_categories=len(search_result)
          )
      )
    except AttributeError as e:
      print(e)
      db.session.rollback()
      abort(422)
    finally:
      db.session.close()
        
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
  @app.route('/api/questions/random', methods=['POST'])
  def get_random_question():
    data = request.get_json()
    if isinstance(data, str):
      data = json.loads(data)
    previous_questions, category_id = data['previous_questions'], data['quiz_category']['id']

    categories_to_include = [c.id for c in Category.query.all()] if category_id == 0 else [category_id]
    # store query filter conditions for readbility
    for_categories = Question.category_id.in_(categories_to_include)
    not_in_previous_questions = ~Question.id.in_(previous_questions)
    
    available_questions = Question.query.filter(and_(for_categories, not_in_previous_questions)).all()    
    if len(available_questions) < 1:
      abort(404)
    
    rand_ix = random.randint(0, len(available_questions)-1)
    questions = [qst for qst in available_questions]
    q = questions[rand_ix].format()
    return jsonify(
      format_play_response(question=q, current_category=q['category_id'])
    )
    

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(BadRequest)
  def handle_bad_request(e):
    """"returns a JSON response with error information"""
    # message = 'something I want the user to know.'
    response_attributes = {'error_name': e.name
      , 'error_code': e.code
      , 'error_description': e.description}
    response = e.get_response()
    response.data = json.dumps(format_error(**response_attributes))
    response.content_type = 'application/json'
    return response
  @app.errorhandler(NotFound)
  def handle_bad_request(e):
    """"returns a JSON response with error information"""
    # message = 'something I want the user to know.'
    response_attributes = {'error_name': e.name
      , 'error_code': e.code
      , 'error_description': e.description}
    response = e.get_response()
    response.data = json.dumps(format_error(**response_attributes))
    response.content_type = 'application/json'
    return response
  @app.errorhandler(UnprocessableEntity)
  def handle_bad_request(e):
    """"returns a JSON response with error information"""
    # message = 'something I want the user to know.'
    response_attributes = {'error_name': e.name
      , 'error_code': e.code
      , 'error_description': e.description}
    response = e.get_response()
    response.data = json.dumps(format_error(**response_attributes))
    response.content_type = 'application/json'
    return response
  @app.errorhandler(MethodNotAllowed)
  def handle_bad_request(e):
    """"returns a JSON response with error information"""
    # message = 'something I want the user to know.'
    response_attributes = {'error_name': e.name
      , 'error_code': e.code
      , 'error_description': e.description}
    response = e.get_response()
    response.data = json.dumps(format_error(**response_attributes))
    response.content_type = 'application/json'
    return response
  
  return app

    