import os
import json
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import psycopg2.errors
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    # any external origin site (*) is allowed to access resources with the /api/* routes
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    '''
    after_request()
        returns a response to a pre-flight OPTIONS request from a cross-domain and describes what
        headers and methods can be used to access resources. 
    '''
    @app.after_request
    def after_request(response):
        # Allow resource requests with 'Content-Type' and 'Authorization' headers.
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        # Allow resource requests made with the listed methods.
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    '''
    api_get_categories()
        returns a json response with all the available categories
    '''
    @app.route('/api/categories')
    def api_get_categories():
        try:
            categories = Category.format_all()
            total_categories = len(categories)
            body = {
                'success': True,
                'categories': categories,
                'total_categories': total_categories
            }
            return jsonify(body)
        except Exception as e:
            message = str(e)
            abort(500, message)

    '''
    api_get_questions()
        Returns a json response with the requested page of up to 10 questions.
        If no page is provided, the first page of questions will be returned.  
    '''
    @app.route('/api/questions')
    def api_get_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)
        if len(current_questions) == 0:
            abort(404, 'Requested page beyond page maximum.')
        else:
            total_questions = len(selection)
            page = request.args.get('page', 1, type=int)

        body = {
            'success': True,
            'categories': Category.format_all(),
            'total_questions': total_questions,
            'current_category': "ALL",
            'questions': current_questions,
            'page': page
        }
        return jsonify(body)

    @app.route('/api/questions/<int:question_id>', methods=['GET'])
    def api_get_a_question(question_id):
        question = Question.query.get(question_id)
        if question is None:
            abort(404, 'Requested question not found.')
        body = {
            'success': True,
            'question': question.format()
        }
        return jsonify(body)

    @app.route('/api/questions/<int:question_id>', methods=['DELETE'])
    def api_delete_a_question(question_id):
        question = Question.query.get(question_id)
        if question is None:
            abort(404, 'Requested question not found.')
        question.delete()
        body = {
            'success': True,
            'deleted': question_id
        }
        return jsonify(body)

    @app.route('/api/questions', methods=['POST'])
    def api_post_a_question():
        data = json.loads(request.data)
        if not all([data.get(key) for key in Question.required_keys()]):
            abort(422, f'Requires Fields: {",".join(Question.required_keys())}')

        question = Question(question=data.get('question'),
                            answer = data.get('answer'),
                            category = data.get('category'),
                            difficulty = data.get('difficulty')
                            )
        if data.get('id'):
            question.id = data.get('id')

        try:
            question.insert()
        except Exception as e:
            if '(psycopg2.errors.UniqueViolation)' in str(e):
                abort(422, f"id={data.get('id')} already exists.")
            else:
                abort(500)

        body = {
            'success': True,
            'question': question.format()
        }
        return jsonify(body)


    '''
    @TODO: 
    Create an endpoint to DELETE question using a question ID. 
  
    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    '''

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

    @app.errorhandler(500)
    def internal_server_error(error):
        base_message = 'InternalServerError'
        if hasattr(error, 'description'):
            message = f'{base_message}: {str(error.description)}'
        else:
            message = base_message
        return jsonify({
            'success': False,
            'error': 500,
            'message': message
        }), 500

    @app.errorhandler(422)
    def unprocessable(error):
        base_message = 'Unprocessable'
        if hasattr(error, 'description'):
            message = f'{base_message}: {str(error.description)}'
        else:
            message = base_message
        return jsonify({
            'success': False,
            'error': 422,
            'message': message
        }), 422

    @app.errorhandler(405)
    def method_not_allowed(error):
        base_message = 'MethodNotAllowed'
        if hasattr(error, 'description'):
            message = f'{base_message}: {str(error.description)}'
        else:
            message = base_message
        return jsonify({
            'success': False,
            'error': 405,
            'message': message
        }), 405

    @app.errorhandler(404)
    def not_found(error):
        base_message = 'NotFound'
        if hasattr(error, 'description'):
            message = f'{base_message}: {str(error.description)}'
        else:
            message = base_message
        return jsonify({
            'success': False,
            'error': 404,
            'message': message
        }), 404

    return app


if __name__ == '__main__':
    app = create_app()
    app.run()