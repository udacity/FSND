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
  print('Setup Database Connection')
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={r'/*': {'origins': '*'}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''

  @app.after_request
  def after_request(respone):
    respone.headers.add(
      'Access-Control-Allow-Headers',
      'Content-Type, Authorization, true'
    )
    respone.headers.add(
      'Access-Control-Allow-Methods',
      'GET, POST, PATCH, DELETE, OPTIONS'
    )
    return respone

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_all_categories():
    try:
      categories = Category.query.all()
      for category in categories:
        print(category)
      
      categories_dict = {}
      for category in categories:
        categories_dict[category.id] = category.type

      #response
      return jsonify({
        'success': True,
        'categories': categories_dict
      })
    except Exception:
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
  @app.route('/questions')
  def get_questions():
    questions = Question.query.order_by(Question.id).all()
    for question in questions:
      print(question)
    total_questions = len(Question.query.order_by(Question.id).all())
    print('Total questions= ', total_questions)
    categories = Category.query.order_by(Category.id).all()
    for categorie in categories:
      print(categorie)

    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in questions]
    current_questions = questions[start:end]

    categories_dict = {}
    for category in categories:
      categories_dict[category.id] = category.type
      print(category)
    
    return jsonify({
      'success': True,
      'total_questions': total_questions,
      'categories': categories_dict,
      'questions': current_questions
    }), 200


  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 
  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_question(id):
    print(id)
    try:
      question = Question.query.get(id)
      print(question)
      question.delete()
      print('Delete completed')

      return jsonify({
        'success': True,
        'message': "Question " + question.question + " successfully deleted"
      }), 200
    except Exception:
      print('Delete failed')
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
  def create_question():
    data = request.get_json()
    print(data)

    question = data.get('question', '')
    print(question)
    answer = data.get('answer', '')
    print(answer)
    difficulty = data.get('difficulty', '')
    print(difficulty)
    category = data.get('category', '')
    print(category)

    if ((question == '') or (answer == '')) or (difficulty == '') or (category == ''):
      print('One information in json was empty.')
      abort(422)

    try:
      question = Question(
        question = question,
        answer = answer,
        difficulty = difficulty,
        category = category
      )

      question.insert()
      print('Insert was successful')

      return jsonify({
        'success': True,
        'message': 'Question created'
      })

    except Exception:
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

      data = request.get_json()
      search_term = data.get('searchTerm', '')
      print('Search term: ', search_term)

      if search_term == '':
        print('Search term was empty')
        abort(422)

      print('Before try')
      try:
        questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
        for question in questions:
          print(question)

        if len(questions) == 0:
          print('Select with search term was empty')
          abort(404)
        
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        questions = [question.format() for question in questions]
        paginated_questions = questions[start:end]
        print('Paginated questions: ', paginated_questions)

        return jsonify({
          'success': True,
          'questions': paginated_questions,
          'total_questions': len(Question.query.all())
        }), 200

      except Exception:
        abort(404)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 
  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:id>/questions')
  def get_questions_by_category(id):
    print('Category-ID: ', id)

    category = Category.query.filter_by(id=id).one_or_none()
    print('Category-Name: ', category)

    if(category is None):
      print('No category was found in table.')
      abort(422)
    
    questions = Question.query.filter_by(category=id).all()
    for question in questions:
      print(question)
    
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in questions]
    paginated_questions = questions[start:end]
    print('Paginated questions: ', paginated_questions)    

    return jsonify({
      'success': True,
      'questions': paginated_questions,
      'total_questkions': len(questions),
      'current_category': category.type
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
  def play_quiz_question():
    
    data = request.get_json()
    previous_questions = data.get('previous_questions')
    print('Previous question: ', previous_questions)
    quiz_category = data.get('quiz_category')
    print('Quiz category: ', quiz_category)

    if (quiz_category is None):
      print('Quiz category was empty.')
      abort(400)
    if (previous_questions is None):
      print('Previous question was empty.')
      abort(400)

    if (quiz_category['id'] == 0):
      questions = Question.query.all()
      for question in questions:
        print(questions)
    else:
      questions = Question.query.filter_by(category=quiz_category['id']).all()
    
    def get_random_question():
      return questions[random.randint(0, len(questions)-1)]
    
    next_question = get_random_question()
    print(next_question)

    var_while_loop = True

    while var_while_loop:
      if next_question.id in previous_questions:
        next_question = get_random_question()
      else:
        var_while_loop = False

    return jsonify({
      'success': True,
      'question': next_question.format()
    }), 200

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  #Bad request error (400)
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message': 'Bad request error'
    }), 400

  #Bad request error (404)
  @app.errorhandler(404)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'Resource not found'
    }), 404

  #Bad request error (500)
  @app.errorhandler(500)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 500,
      'message': 'Internal Server Error'
    }), 500
  
  #Bad request error (422)
  @app.errorhandler(422)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': 'Unprocessable entity'
    }), 422

  return app
