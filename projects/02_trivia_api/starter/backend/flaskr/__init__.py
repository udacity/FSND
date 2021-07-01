import os
from flask import Flask, request, abort, jsonify
from flask.config import Config
from flask.globals import session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random
import json
from models import db, setup_db, Question, Category
import config

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    app_version = config.APP_VERSION
    
    # load the instance config, if it exists, when not testing
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    # load the test config if passed in
    else:
        app.config.from_mapping(test_config)


    setup_db(app)


    '''
    Set up CORS. Allow '*' for origins.
    '''
    CORS(app)
    # cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


    '''
    Use the after_request decorator to set Access-Control-Allow
    '''
    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    
    # home page
    @app.route('/', methods=['GET'])
    @cross_origin()
    def hello_world():
        return 'Hello, World!'

    # helper function
    def get_category_names():
        all_categories = Category.query.order_by(Category.type.asc()).all()
        category_names = [c.format() for c in all_categories]
        return category_names

    '''
    Create an endpoint to handle GET requests
    for all available categories.
    '''
    @app.route(f'/api/{app_version}/categories', methods=['GET'])
    def get_categories():
        category_names = get_category_names()

        return jsonify(categories=category_names)


    '''
    Create an endpoint to handle GET requests for questions, 
    including pagination (every 10 questions). 
    This endpoint should return a list of questions, 
    number of total questions, current category, categories. 

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions. 
    '''
    @app.route(f'/api/{app_version}/questions', methods=['GET'])
    def get_questions():
        # page default value of 1
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * 10
        end = start + 10

        all_questions = db.session.query(Question, Category).join(Category, Question.category == Category.id).order_by(Question.difficulty.asc())
        questions = [q.Question.format() for q in all_questions[start:end]]

        data = {
            "questions": questions,
            "total_questions": all_questions.count(), 
            "categories": get_category_names(),
            "current_category": ""
        }

        return jsonify(data)


    '''
    Create an endpoint to DELETE question using a question ID. 

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    '''
    @app.route(f'/api/{app_version}/questions/<int:question_id>', methods=['DELETE'])
    def delete_questions(question_id):
        question = Question.query.filter(Question.id==question_id).one_or_none()
        if question is None:
            abort(404)
        else:
            try:
                question.delete()
                db.session.commit()
                db.session.refresh(question)
            except:
                db.session.rollback()
                abort(500)
            finally:

                if question is None:
                    abort(404)
                else:
                    data = { "success": True, "message": f'Deleted {question_id}' }
                    return jsonify(data)


    '''
    Create an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.  
    '''
    @app.route(f'/api/{app_version}/questions', methods=['POST'])
    def create_questions():
        # page default value of 1
        question = json.loads(request.data)

        new_question = Question(**question)

        try:
            db.session.add(new_question)
            db.session.commit()
            db.session.refresh(new_question)
        except:
            db.session.rollback()
        finally:
            data = {
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
    @app.route(f'/api/{app_version}/search/questions', methods=['POST'])
    @cross_origin()
    def search_questions():
        searchTerm = json.loads(request.data).get('searchTerm')
        results = Question.query.filter(Question.question.ilike(f'%{searchTerm}%')).order_by(Question.difficulty.asc()).all()
        questions = [q.format() for q in results]

        data = {
            "questions": questions,
            "total_questions": len(questions), 
            "categories": get_category_names(),
            "current_category": ""
        }

        return jsonify(data)

    '''
    @TODO: 
    Create a GET endpoint to get questions based on category. 

    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    '''
    @app.route(f'/api/{app_version}/categories/<int:category_id>/questions', methods=['GET'])
    def get_category_questions(category_id):
        questions = Question.query.filter(Question.category==category_id).order_by(Question.difficulty.asc())
        category = Category.query.filter(Category.id==category_id).one_or_none()
        data = {
            "questions": [q.format() for q in questions],
            "total_questions": questions.count(), 
            "categories": get_category_names(),
            "current_category": category.type
        }
        return jsonify(data)


    '''
    Create a POST endpoint to get questions to play the quiz. 
    This endpoint should take category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. 
    '''
    @app.route(f'/api/{app_version}/quizzes', methods=['POST'])
    def get_quiz():
        total_questions = 0
        query = None
        
        request_data = json.loads(request.data)

        # filter by category if provided
        quiz_category = request_data.get('quiz_category')
        category_id = None
        if quiz_category is not None:
            category_id = quiz_category.get('id')

        if category_id is not None:
            query = Question.query.filter(Question.category == category_id)
            total_questions = len(query.all())

        # filter by previously unanswered questions only
        previous_questions = request_data.get('previous_questions')
        unanswered_questions = None
        if previous_questions is not None:
            unanswered_questions = query.filter(Question.id.notin_(previous_questions)).all()

        # select random one from previously unanswered questions
        random_question = None
        if len(unanswered_questions) > 0:
            random_question = unanswered_questions[random.randint(0, len(unanswered_questions))]

        data = {
            "question": random_question.format() if random_question is not None else '',
            "total_questions": total_questions, 
            "categories": get_category_names(),
            "current_category": category_id,
        }
        return jsonify(data)


    '''
    Create error handlers for all expected errors 
    including 404 and 422. 
    '''
    @app.errorhandler(400)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad request due to invalid syntax."
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource not found."
        }), 404

    @app.errorhandler(422)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable"
        }), 422

    @app.errorhandler(500)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal error"
        }), 422

    return app
