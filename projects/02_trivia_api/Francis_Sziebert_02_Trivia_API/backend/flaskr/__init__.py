import os
import json
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
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

        if len(current_questions == 0):
            abort(404, 'requested page beyond maximum')

        body = {
            'success': True,
            'categories': quest
        }
        return jsonify(body)


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
        base_message = 'internal server error'
        if hasattr(error, 'message'):
            print(error.message)
            message = f'{base_message}: {str(error.message)}'
        else:
            message = base_message
        return jsonify({
            'success': False,
            'error': 500,
            'message': message
        }), 500

    @app.errorhandler(422)
    def unprocessable(error):
        base_message = 'unprocessable'
        if hasattr(error, 'message'):
            print(error.message)
            message = f'{base_message}: {str(error.message)}'
        else:
            message = base_message
        return jsonify({
            'success': False,
            'error': 422,
            'message': message
        }), 422

    @app.errorhandler(405)
    def method_not_allowed(error):
        base_message = 'method not allowed'
        if hasattr(error, 'message'):
            print(error.message)
            message = f'{base_message}: {str(error.message)}'
        else:
            message = base_message
        return jsonify({
            'success': False,
            'error': 405,
            'message': message
        }), 405

    return app


if __name__ == '__main__':
    app = create_app()
    app.run()