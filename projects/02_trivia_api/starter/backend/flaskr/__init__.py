import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random
import json

from models import db, setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    
    # load the instance config, if it exists, when not testing
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    # load the test config if passed in
    else:
        app.config.from_mapping(test_config)


    setup_db(app)


    '''
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    '''
    # CORS(app)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''
    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, PATCH, POST, DELETE, OPTIONS')
        return response

    # home page
    @app.route('/', methods=['GET'])
    @cross_origin()
    def hello_world():
        return 'Hello, World!'


    '''
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    '''
    @app.route('/api/categories', methods=['GET'])
    def get_categories():
        all_categories = Category.query.order_by(Category.type).all()
        category_names = [c.type for c in all_categories]

        # categories_serialized = json.dumps({
        #     "categories": [c.format() for c in all_categories]
        # })
        return jsonify(categories=category_names)


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
    @app.route('/api/questions', methods=['GET'])
    def get_questions():
        # page default value of 1
        page = request.args.get('page', 1, type=int)

        data = {
            "questions": [
                {"id": 1, "question": "test", "answer": "a1", "category": 0, "difficulty": 0}
            ],
            "total_questions": 0, 
            "categories": ["sports"],
            "current_category": ""
        }

        return jsonify(data)


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
    @app.route('/api/questions', methods=['POST'])
    def create_questions():
        # page default value of 1
        question = json.loads(request.data)

        new_question = Question(**question)

        # db_insert(new_question)
        try:
            db.session.add(new_question)
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.refresh(new_question)
            # db.session.close()

        data={
            'success': True,
            'qid': new_question.id
        }

        return jsonify(data)


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
