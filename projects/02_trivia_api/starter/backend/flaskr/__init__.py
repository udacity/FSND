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
  CORS(app)
  cors = CORS(app, resources={r'/api/*': {'origins': '*'}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 
                        'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods',
                        'GET,PATCH,POST,DELETE,OPTIONS')
    return response         
    
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
    try:
        categories = Category.query.all()
        categories_col = {}

        for category in categories:
            categories_col[category.id] = category.type

        if (len(categories_col) > 0):      
            return jsonify({
                'success': True,
                'categories': categories_col,
                'message': 'Categories retrieved'
            })
        else: 
            abort(500)
    except:
        abort(500)
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
  
  def paginate_q(request, selection):
    try:
        num_page = request.args.get('page', 1, type = int)
        start_page = QUESTIONS_PER_PAGE + (num_page - 1)
        end_page = QUESTIONS_PER_PAGE + start_page
        formatted_questions = [question.format() for question in selection]
        questions = formatted_questions[start_page:end_page]
        return questions
    except:
        abort(500)
    
  @app.route('/questions')
  def get_questions():    
    try:
        questions = Question.query.all()

        total_questions = len(questions)
        current_questions = paginate_q(request, questions)
          
        categories = Category.query.order_by(Category.type).all()
        categories_col = {}
        for category in categories:
            categories_col[category.id] = category.type

        if (len(categories_col)==0 or len(current_questions)==0):
            abort(404)    
            
        return jsonify({
            'success': True,
            'questions': current_questions,
            'number of total questions':  total_questions,
            'categories': categories_col,
            'message': 'Questions and categories retrieved'
        })
    except:
        abort(500)
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_questions(id):
    try:
        question = Question.query.get(id)
        question.delete()

        return jsonify({
            'success': True,
            'deleted': id        
        })
    except:
        abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the 'Add' tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the 'List' tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def add_question():
    try:
        jsonBody = request.get_json()

        question_val = jsonBody.get('question')
        answer_val = jsonBody.get('answer')
        category_val = jsonBody.get('category')
        difficulty_val = jsonBody.get('difficulty')             

        question = Question(
            question = question_val,
            answer = answer_val,
            category = category_val,
            difficulty = difficulty_val
        )

        question.insert()

        return jsonify({
            'success': True,
            'created': question.id
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
  Try using the word 'title' to start. 
  '''
  
  @app.route('/questions/search', methods=['POST'])
  def search_question():
    try:
        jsonBody = request.get_json()                  
        search_val = jsonBody.get('searchTerm')
        searched_questions = Question.query.filter(Question.question.ilike(f'%{search_val}%')).all()
        
        return jsonify({
            'success': True,
            'number of total questions': len(searched_questions),
            'questions': [question.format() for question in searched_questions]
        })
    except:
        abort(422)
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the 'List' tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:id>/questions')
  def get_question_by_categories(id):    
    try:
        category = Category.query.get(id)
        questions = Question.query.filter_by(category=str(category.id)).all()
        current_questions = paginate_q(request, questions)
    
        return jsonify({
            'success': True,
            'questions': current_questions,
            'number of total questions': len(current_questions)
        })
    except:
        abort(500)
  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the 'Play' tab, after a user selects 'All' or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quiz', methods=['POST'])
  def start_quiz():
    try:
        jsonBody = request.get_json()
              
        category = jsonBody.get('category')
        previous_question = jsonBody.get('previous_question')
        
        if (category == 0):
            questions = Question.query.all()
        else:
            questions = Question.query.filter_by(category=category).all()

        total_questions = len(questions)

        random_index = random.randint(0, len(questions)-1)
        new_question = questions[random_index].format()


        while new_question['id'] not in previous_question:
            new_question = questions[random_index].format()     
            return jsonify({
               'success': True,
               'question': new_question,
               'previous question': previous_question,
               'number of total questions': total_questions
            })
        return jsonify({
               'success': True,
               'question': 'Quiz Completed',
               'previous question': previous_question,
               'number of total questions': total_questions
            })
    except:
        abort(422)
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  ''' 
  @app.errorhandler(404)
  def page_not_found(ex):
    return jsonify({
        'error': 404,
        'success': False,
        'message': 'Page not found'
    }), 404
    
  @app.errorhandler(422)
  def incorrect_input(ex):
    return jsonify({
        'error': 422,
        'success': False,
        'message': 'Incorrect input'
    }), 422

  @app.errorhandler(500)
  def internal_server_error(ex):
    return jsonify({
        'error': 500,
        'success': False,
        'message': 'Internal server error'
    }), 500
        
  return app

    