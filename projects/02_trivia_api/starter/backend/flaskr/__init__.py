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
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
    return response

  # ---------------- Get all categories ----------------

  @app.route('/categories',methods=['GET'])
  def get_categories():
    try:
      page=request.args.get('page',1,type=int)
      start=(page-1)*QUESTIONS_PER_PAGE
      end=start+QUESTIONS_PER_PAGE
      categories=Category.query.all()
      formatted_categories={category.id:category.type for category in categories}
      return jsonify({
        'success':True,
        'categories':formatted_categories,
        })
    except:
      abort(500)

  # ---------------- Get all questions ----------------

  @app.route('/questions',methods=['GET'])
  def get_questions():
    page=request.args.get('page',1,type=int)
    start=(page-1)*QUESTIONS_PER_PAGE
    end=start+QUESTIONS_PER_PAGE
    questions=Question.query.all()
    formatted_questions=[question.format() for question in questions]
    categories=Category.query.all()
    formatted_categories={category.id:category.type for category in categories}
    return jsonify({
      'success':True,
      'questions':formatted_questions[start:end],
      'total_questions':len(formatted_questions),
      'categories':formatted_categories,
      'current_category':None
      })

  
  # ---------------- delete a question using its ID ----------------

  @app.route('/questions/<int:question_id>',methods=['DELETE'])
  def delete_question(question_id):

    print(question_id)
    question = Question.query.get(question_id)
    reference_copy=question.format()
    if question:
        Question.delete(question)
        result = {
            "success": True,
            "deleted_question":reference_copy
          }
        return jsonify(result)
    abort(404)
      

  # ---------------- Add a new question ----------------

  @app.route('/questions/new', methods=['POST'])
  def add_question():
    body=request.get_json()
    new_question=body.get('question',None)
    new_answer=body.get('answer',None)
    new_difficulty=body.get('difficulty',None)
    new_category=body.get('category',None)
    
    try:
      question=Question(question=new_question,answer=new_answer,difficulty=new_difficulty,category=new_category)
      question.insert()

      return jsonify({'success':True,
                      'new_question':question.format()})

    except:
      abort(422)

  # ---------------- Search for questions ----------------

  @app.route('/questions',methods=['POST'])
  def search():
    page=1
    start=(page-1)*QUESTIONS_PER_PAGE
    end=start+QUESTIONS_PER_PAGE
    try:
      body=request.get_json()
      search_term=body.get('searchTerm',None)
      questions = Question.query.filter(
                      Question.question.ilike('%{}%'.format(search_term)))
      questions=[question.format() for question in questions]
      questions=questions[start:end]

      return jsonify({
                      'success': True,
                      'questions': questions,
                      'total_questions': len(questions),
                      'current_category': None
                  })
    except():
      abort(404)

    # ---------------- Get questions based on category ----------------

  @app.route('/categories/<category_id>/questions',methods=['GET'])
  def get_questions_by_category(category_id):
    page=1
    start=(page-1)*QUESTIONS_PER_PAGE
    end=start+QUESTIONS_PER_PAGE
    try:
      questions = Question.query.filter(Question.category == category_id).all()
      questions=[question.format() for question in questions]
      questions=questions[start:end]

      return jsonify({
                'success': True,
                'questions': questions,
                'total_questions': len(questions),
                'current_category': category_id
                })
    except:
      abort(422)


  # ---------------- get questions for the quiz ----------------

  @app.route('/quizzes', methods=['POST'])
  def create_quiz():
    body=request.get_json()
    chosen_category=body.get('quiz_category',None)
    previous_questions=body.get('previous_questions',None)

    try:
      if chosen_category['id']:
          questions = Question.query.filter(Question.id.notin_(previous_questions),Question.category == chosen_category['id']).all()
      else:
          questions = Question.query.filter(Question.id.notin_(previous_questions)).all()

      next_question=random.choice(questions).format()
      
      return jsonify({
          'success':True,
          'question':next_question})
    except:
      abort(500)
    

  # ---------------- Error handlers ----------------

  # Error 404
  @app.errorhandler(404)
  def notFound(error):
    return jsonify({
      "success":False,
      "error":404,
      "message":"resource not found"
      }),404

  # Error 422
  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success":False,
      "error":422,
      "message":"unprocessable"
      }),422

  # Error 500
  @app.errorhandler(500)
  def serverError(error):
    return jsonify({
      "success":False,
      "error":500,
      "message":"internal server error"
      }),500
  
  return app

    