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
    cors = CORS(app, resources={r"*": {"origins": "*"}})
    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''

    @app.after_request
    def add_cors_headers(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,DELETE')
        return response

    '''
    @TODO: 
    Create an endpoint to handle GET requests 
    for all available categories.
    '''
    @app.route('/categories')
    def get_all_categories():
        """
        GET '/categories'
        - Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
        - Request Arguments: None
        - Returns: An object with a single key, categories, that contains an object of id: category_string 
        """
        categories = Category.query.all()
        data = dict([d.format().values() for d in categories])
        return jsonify({
            "categories": data
        })

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
        """
        GET '/questions'
        - fetches questions, including pagination (every 10 questions).
        - Request Arguments: page (default is 1)
        - Returns: An object with multible keys, questions, total_questions, categories, current_category 
        """
        page = request.args.get('page', 1, int)
        questions_pagination = Question.query.paginate(
            page, QUESTIONS_PER_PAGE, True)
        total_questions = questions_pagination.total
        questions = questions_pagination.items
        categories = Category.query.all()
        data = dict([d.format().values() for d in categories])
        current_category = ''
        return jsonify({
            "questions": [question.format() for question in questions],
            "total_questions": total_questions,
            "categories": data,
            "current_category": current_category
        })
    '''
    @TODO: 
    Create an endpoint to DELETE question using a question ID. 

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        """
        DELETE '/questions/<id>'
        - DELETE question using a question ID.
        """
        question = Question.query.get_or_404(question_id)
        question.delete()
        return jsonify({
            "success": True
        })
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
    @app.route('/questions', methods=["POST"])
    def questions_post_router():
        """
        POST '/questions'
        - this function will handle both search and insert new question functionality based on the payload content.
        - it is call one of two functions (add_new_question, search_questions) or abort with 400 http error.
        """
        search_term = request.json.get('searchTerm', None)
        if search_term:
            return search_questions(search_term)
        else:
            submitted_question = request.json.get('question', None)
            submitted_answer = request.json.get('answer', None)
            submitted_category_id = request.json.get('category', None)
            submitted_difficulty = request.json.get('difficulty', None)
            if all([submitted_question, submitted_answer, submitted_category_id, submitted_difficulty]):
                return add_new_question(submitted_question, submitted_answer, submitted_category_id, submitted_difficulty)
            else:
                abort(400)

    def add_new_question(submitted_question, submitted_answer, submitted_category_id, submitted_difficulty):
        category = Category.query.get_or_404(submitted_category_id)
        question = Question(question=submitted_question, answer=submitted_answer,
                            category=category.id, difficulty=submitted_difficulty)
        question.insert()
        return jsonify({
            "success": True
        })

    def search_questions(search_term):
        questions = Question.query.filter(
            Question.question.ilike(f'%{search_term}%')).all()
        total_questions = len(questions)
        current_category = ''
        return jsonify({
            "questions": [question.format() for question in questions],
            "total_questions": total_questions,
            "current_category": current_category
        })

    '''
    @TODO: 
    Create a GET endpoint to get questions based on category. 

    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    '''
    @app.route('/categories/<int:cat_id>/questions')
    def get_questions_by_category(cat_id):
        """
        GET '/questions/<int:cat_id>/questions'
        - fetches questions in specific category.
        - Returns: An object with multible keys, questions, total_questions, current_category 
        """
        category = Category.query.get_or_404(cat_id)
        questions = Question.query.filter(Question.category == cat_id).all()
        total_questions = len(questions)
        return jsonify({
            "questions": [question.format() for question in questions],
            "total_questions": total_questions,
            "current_category": category.format()
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
    @app.route('/quizzes', methods=["POST"])
    def play():
        """
        POST '/quizzes'
        - This endpoint should take category and previous question parameters 
        and return a random questions within the given category, 
        if provided, and that is not one of the previous questions. 
        """
        previous_questions = request.json.get("previous_questions", [])
        quiz_category = request.json.get("quiz_category", None)

        if quiz_category and quiz_category["id"] != 0:
            category = Category.query.get_or_404(quiz_category["id"])
            questions = Question.query.filter(Question.category == category.id)
        else:
            questions = Question.query
        questions = questions.filter(Question.id.notin_(
            previous_questions)).all() if previous_questions else questions.all()
        if questions:
            random_question = random.choice(
                [question.format() for question in questions])
        else:
            # give signal to front end to force end the quizze if no more questions left
            random_question = False
        return jsonify({
            "question": random_question,
            "quiz_category": quiz_category
        })
    '''
    @TODO: 
    Create error handlers for all expected errors 
    including 404 and 422. 
    '''
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Not Found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable Request"
        }), 422

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Server Error"
        }), 500

    return app
