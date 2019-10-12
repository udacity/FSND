import os
from flask import Flask, request, abort, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
  """
  A function to paginate response
  :param request: Any
  :param selection: List
  :return: List
  """
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  books = [book.format() for book in selection]
  current_books = books[start:end]

  return current_books

def create_app(test_config=None):
  """
  Function to create the main app
  :param test_config:
  :return:
  """
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
    return response

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False,
      "error": 404,
      "message": "Not found"
    }), 404
  
  @app.errorhandler(422)
  def not_found(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Not found"
    }), 422

  @app.route('/categories')
  @cross_origin()
  def categories():
    cats = Category.query.all()
    cats_formatted = [c.format() for c in cats]
    categories_formatted = [(c.get('id'), c.get('type')) for c in cats_formatted]
    return jsonify({
            'success': True,
            'categories': categories_formatted,
            'total_books': len(cats)
      }), 200

  @app.route('/questions', methods=['GET', 'POST'])
  @cross_origin()
  def questions():
    if request.method == 'POST':
     q = request.args.get('question')
     a = request.args.get('answer')
     c = request.args.get('category')
     d = request.args.get('difficulty')
     question = Question(
       question=q,
       answer=a,
       category=c,
       difficulty=d
     )
     question.update()
     return jsonify({'success': True}), 200
    elif request.method == 'POST' and request.args.get('search'):
      search_term = request.args.get('search')
      search = f"%{search_term}%"
      questions = Question.query.filter(Question.question.like(search)).all()
      questions_formatted = [q.format() for q in questions]
      categories = Category.query.all()
      formatted_categories = [category.format() for category in categories]
      formatted_categories = [c.get("type") for c in formatted_categories]
      return jsonify({
        'questions': questions_formatted,
        'totalQuestions': len(questions),
        'categories': formatted_categories,
        'currentCategory': formatted_categories
                     })
    else:
      questions = Question.query.all()
      questions_paginated = paginate_questions(request, questions)
      questions_formatted = [[q.get("question"), q.get(
          "answer"), q.get("category"), q.get("difficulty")] for q in questions_paginated]
      categories = Category.query.all()
      formatted_categories = [category.format() for category in categories]
      formatted_categories = [c.get("type") for c in formatted_categories]
      return jsonify({
        'questions': questions_formatted,
        'totalQuestions': len(questions),
        'categories': formatted_categories ,
        'currentCategory': formatted_categories
                     })

  @app.route('/questions/<int:question_id>', methods=['GET', 'DELETE', 'POST'])
  @cross_origin()
  def question(question_id):
    try:
      question = Question.query.get(question_id)
      if request.method == 'GET':
        return jsonify({
          'success': True,
          'question': question.format()
        })
      elif request.method == 'DELETE':
        question.delete()
        return jsonify({'success': True}), 200
    except:
      abort(404)

  @app.route('/categories/<int:category_id>/question')
  @cross_origin()
  def categories_id_question(category_id):
    cat = Category.query.get(category_id).first()
    cat_type = cat.type
    questions = Question.question.filter(Question.category==cat_type).all()
    questions_formatted = [q.format() for q in questions]
    questions_formatted_tuple = [[q.get("question"), q.get(
          "answer"), q.get("category"), q.get("difficulty")] for q in questions_formatted]
    return jsonify({
      'questions': questions_formatted_tuple,
      'totalQuestions': len(questions),
      'currentCategory': cat_type
    })

  @app.route('/quizzes', methods=['POST'])
  @cross_origin()
  def quizzez():
    category_id = request.args.get('id')
    cat = Category.query.get(category_id).first()
    cat_type = cat.type
    questions = Question.question.filter(Question.category==cat_type).all()
    questions_formatted = [q.format() for q in questions]
    questions_formatted_tuple = [[q.get("question"), q.get(
          "answer"), q.get("category"), q.get("difficulty")] for q in questions_formatted]

  return app

    
