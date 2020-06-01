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
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
    return response


  def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    question_list = [question.format() for question in selection]
    current_questions = question_list[start:end]

    return current_questions

  '''
  @TODO: DONE!
  Create an endpoint to handle GET requests 
  for all available categories.
  '''

  @app.route('/categories',methods=['GET'])
  def get_categories():
    page=request.args.get('page',1,type=int)
    start=(page-1)*10
    end=start+10
    categories=Category.query.all()
    formatted_categories={category.id:category.type for category in categories}
    return jsonify({
      'success':True,
      'categories':formatted_categories,
      })



  '''
  @TODO: DONE!
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 
  

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  @app.route('/questions',methods=['GET'])
  def get_questions():
    page=request.args.get('page',1,type=int)
    start=(page-1)*10
    end=start+10
    questions=Question.query.all()
    formatted_questions=[question.format() for question in questions]
    categories=Category.query.all()
    formatted_categories={category.id:category.type for category in categories}
    return jsonify({
      'success':True,
      'questions':formatted_questions[start:end],
      'total_questions':len(formatted_questions),
      'categories':formatted_categories,
      'current_category':'None'
      })

  '''
  @TODO: Done!
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>',methods=['DELETE'])
  def delete_question(question_id):
    page=1
    start=(page-1)*10
    end=start+10
    
    print(question_id)
    question = Question.query.get(question_id)
    if question:
        Question.delete(question)
        result = {
            "success": True,
        }
        return jsonify(result)
    abort(404)
      


  '''
  @TODO: DONE!
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  @app.route('/questions/new', methods=['POST'])
  def add_question():
    page=1
    start=(page-1)*10
    end=start+10
    body=request.get_json()
    new_question=body.get('question',None)
    new_answer=body.get('answer',None)
    new_difficulty=body.get('difficulty',None)
    new_category=body.get('category',None)
    
    try:
      question=Question(question=new_question,answer=new_answer,difficulty=new_difficulty,category=new_category)
      question.insert()

      # selection=Question.query.all()
      # current_questions=selection[start:end]

      return jsonify({'success':True,
      # 'questions':current_questions,
      # 'total_questions':len(current_questions)
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
  @app.route('/questions',methods=['POST'])
  def search():
    try:
      body=request.get_json()
      search_term=body.get('searchTerm',None)
      #questions=Question.query.
      selection = Question.query.order_by(Question.id).filter(
                      Question.question.ilike('%{}%'.format(search_term)))
      current_questions = paginate_questions(request, selection)

      return jsonify({
                      'success': True,
                      'questions': current_questions,
                      'total_questions': len(selection.all()),
                      'current_category': None
                  })
    except():
      abort(404)
  '''
  @TODO: Done!
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<category_id>/questions',methods=['GET'])
  def get_questions_by_category(category_id):

    try:
      selection = Question.query.filter(Question.category == category_id).all()
      questions = paginate_questions(request, selection)

      return jsonify({
                'success': True,
                'questions': questions,
                'total_questions': len(questions),
                'current_category': category_id
                })
    except:
      abort(422)
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
  @TODO: Done!
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

  @app.errorhandler(404)
  def unprocessable(error):
    return jsonify({
      "success":False,
      "error":404,
      "message":"resource not found"
      }),404


  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success":False,
      "error":422,
      "message":"unprocessable"
      }),422
  
  return app

    