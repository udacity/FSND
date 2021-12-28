import os
import sys
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
    @TODO: Set up CORS.
    Allow '*' for origins. Delete the sample route after completing the TODOs
    '''
    CORS(app, resources={r"/*": {"origins": "*"}})

    '''
    @TODO: Use the after_request decorator
    to set Access-Control-Allow
    '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PATCH, DELETE, OPTION')
        return response

    '''Pagination Function for Questions'''
    def paginate_questions(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page-1)*QUESTIONS_PER_PAGE
        end = start+QUESTIONS_PER_PAGE

        formatted_questions = [question.format() for question in selection]
        current_questions = formatted_questions[start:end]
        return current_questions

    '''Function to get all Categories'''
    def get_categories_from_db():
        categories = Category.query.order_by(Category.id).all()
        formatted_categories = [category.format() for category in categories]
        retCat = {}
        for category in categories:
            retCat[category.id] = category.type

        return retCat

    '''@TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    '''
    @app.route('/')
    def hello():
        return jsonify({'message': 'Hello World from Trivia Application!'})

    @app.route('/categories', methods=['GET'])
    def get_categories():

        formatted_categories = get_categories_from_db()

        if len(formatted_categories) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'categories': formatted_categories,
        }), 200

    '''@TODO:Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the
    bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    '''

    @app.route('/questions', methods=['GET'])
    def get_all_questions():

        questions = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, questions)
        formatted_categories = get_categories_from_db()

        count = len(current_questions)

        if count == 0:
            abort(404)
        else:
            return jsonify({
                'success': True,
                'questions': current_questions,
                'categories': formatted_categories,
                'currentCategory': formatted_categories.get("0", "All"),
                'totalQuestions': Question.query.count()
            }), 200

    '''Get an individual Question'''
    @app.route('/questions/<int:question_id>', methods=['GET'])
    def get_specific_question(question_id):

        question = Question.query.filter(
            Question.id == question_id).one_or_none()

        if question is None:
            abort(404)
        else:
            return jsonify({
                'success': True,
                'question': question.format(),
                'totalQuestions': Question.query.count()
            }), 200

    '''
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question,
    the question will be removed.This removal will persist in
    the database and when you refresh the page.
    '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_specific_question(question_id):

        question = Question.query.filter(
            Question.id == question_id).one_or_none()

        if question is None:
            abort(404)
        else:
            try:
                question.delete()
            except:
                abort(500)

            return jsonify({
                'success': True,
                'totalQuestions': Question.query.count()
            })

    '''
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear
    at the end of the last page of the questions list
    in the "List" tab.
    '''
    @app.route('/questions', methods=['POST'])
    def create_newquestion():

        newQuestionReq = request.get_json()

        answer = newQuestionReq['answer']
        category = int(newQuestionReq['category'])
        difficulty = int(newQuestionReq['difficulty'])
        question = newQuestionReq['question']

        newQuestion = Question(
            question=question,
            answer=answer,
            category=category,
            difficulty=difficulty)

        try:
            newQuestion.insert()
        except:
            print(sys.exc_info())
            abort(422)

        formattedNewQuestion = newQuestion.format()
        return jsonify({
            'success': True,
            'question': formattedNewQuestion
        }), 200

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

        searchReq = request.get_json()

        search_term = searchReq['searchTerm']

        q = "%{}%".format(search_term)
        questions = Question.query.filter(Question.question.ilike(q)).all()
        current_questions = paginate_questions(request, questions)

        count = len(questions)

        if count == 0:
            abort(404)
        else:
            return jsonify({
                'success': True,
                'questions': current_questions,
                'totalQuestions': Question.query.count()
            }), 200

    '''
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    '''
    @app.route('/categories/<int:cat_id>/questions', methods=['GET'])
    def get_questions_by_catid(cat_id):

        category = Category.query.filter(Category.id == cat_id).one_or_none()

        if category is None:
            abort(404)
        else:
            cat = category.type
            questions = Question.query.filter(
                Question.category == cat_id).all()
            current_questions = paginate_questions(request, questions)

            if len(current_questions) == 0:
                abort(404)
            else:
                return jsonify({
                    'success': True,
                    'questions': current_questions,
                    'currentCategory': cat
                }), 200

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
    def play_quizzes():

        quizReq = request.get_json()

        categoryJson = quizReq['quiz_category']
        category = categoryJson['id']
        idList = quizReq['previous_questions']

        if category == 0:
            if idList is None:
                question = Question.query.first()
            else:
                question = Question.query.filter(
                    Question.id.notin_(idList)).first()
        else:
            if idList is None:
                question = Question.query.filter(
                    Question.category == category).first()
            else:
                question = Question.query.filter(
                    Question.category == category).filter(
                        Question.id.notin_(idList)).first()

        if question is None:
            abort(404)
        else:
            formatted_Question = question.format()
            return jsonify({
                'question': formatted_Question,
                'success': True
            }), 200

    '''
    @TODO: Create error handlers for all expected errors
    including 404 and 422.
    '''

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Resource Not Found'

        }), 404

    @app.errorhandler(422)
    def unprocessable_error(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Not Processable'

        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'Internal Server Error'

        }), 500

    @app.errorhandler(405)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 405,
                    "message": "Method Not Allowed"}),
            405,
        )

    return app
