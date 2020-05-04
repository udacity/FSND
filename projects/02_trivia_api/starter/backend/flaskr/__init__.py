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
    CORS(app)

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
    def retrieve_categories():
        categories = Category.query.all()
        formatted_categories = {
            category.id: category.type
            for category in categories
        }

        return jsonify({
            "success": True,
            "categories": formatted_categories
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
    def retrieve_questions():
        page = request.args.get('page', 1, type=int)
        questions_page = Question.query.\
            order_by(Question.id.desc()).\
            paginate(page, per_page=QUESTIONS_PER_PAGE)
        total_questions = questions_page.total

        formatted_questions = [
            question.format()
            for question in questions_page.items]

        current_category = None
        categories = {
            category.id: category.type.lower()
            for category in Category.query.all()}

        return jsonify({
            "success": True,
            "questions": formatted_questions,
            "total_questions": total_questions,
            "categories": categories,
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
        question = Question.query.\
            filter(Question.id == question_id).\
            one_or_none()

        if question is None:
            abort(422)

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
    required_attribute_template = "A value is required for the attribute \"{}\"."
    integer_expected_template = "The attribute \"{}\" must be an integer."
    integer_out_of_range_template = "The attribute \"{}\" must be an integer from {} and {}."

    def validate_create_question_input(data):
        errors = []
        if "question" not in data:
            errors.append({
                "type": "attribute_required",
                "attribute": "question",
                "message": required_attribute_template.format("question")
            })

        if "answer" not in data:
            errors.append({
                "type": "attribute_require",
                "attribute": "answer",
                "message": required_attribute_template.format("answer")
            })

        if "category" not in data:
            errors.append({
                "type": "attribute_required",
                "attribute": "category",
                "message": required_attribute_template.format("category")
            })
        elif not is_integer(data["category"]):
            errors.append({
                "type": "integer_expected",
                "attribute": "category",
                "message": integer_expected_template.format("category")
            })

        if "difficulty" not in data:
            errors.append({
                "type": "attribute_required",
                "attribute": "difficulty",
                "message": required_attribute_template.format("difficulty")
            })
        elif not is_integer(data["difficulty"]):
            errors.append({
                "type": "integer_expected",
                "attribute": "difficulty",
                "message": integer_expected_template.format("difficulty")
            })
        elif int(data["difficulty"]) < 1 or int(data["difficulty"]) > 5:
            errors.append({
                "type": "number_out_of_range",
                "attribute": "difficulty",
                "message": integer_out_of_range_template.format("difficulty", 1, 5)
            })

        return errors

    @app.route("/questions", methods=["POST"])
    def create_question():
        data = request.get_json()

        if not data:
            abort(400)

        if "searchTerm" in data:
            search_term = data.get("searchTerm", "")
            questions = Question.query.\
                filter(
                    Question.question.ilike(f"%{search_term}%")
                ).\
                order_by(Question.id.desc()).\
                all()

            formatted_questions = [
                question.format()
                for question in questions
            ]

            return jsonify({
                "success": True,
                "questions": formatted_questions,
                "total_questions": len(formatted_questions),
                "current_category": None
            })
        else:
            validation_errors = validate_create_question_input(data)
            if validation_errors:
                return jsonify({
                    "success": False,
                    "type": "invalid_request_error",
                    "message": "The request could not be processed because of invalid data.",
                    "validation_errors": validation_errors
                }), 400

            question = Question(
                question=data.get("question"),
                answer=data.get("answer"),
                category=data.get("category"),
                difficulty=data.get("difficulty")
            )
            question.insert()

            return jsonify({
                "success": True
            })

    '''
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    '''
    @app.route('/categories/<int:category_id>/questions')
    def search_by_category(category_id):
        category = Category.query.\
            filter(
                Category.id == category_id
            ).\
            one_or_none()

        if category is None:
            abort(404)

        questions = Question.query.\
            filter(Question.category == category_id).\
            order_by(Question.id.desc()).\
            all()

        formatted_questions = [
            question.format()
            for question in questions
        ]

        return jsonify({
            "questions": formatted_questions,
            "total_questions": len(formatted_questions),
            "current_category": category_id
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

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "type": "invalid_request_error",
            "message": error.description
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "type": "invalid_request_error",
            "message": error.description
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "type": "invalid_request_error",
            "message": error.description
        }), 405

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "type": "invalid_request_error",
            "message": error.description
        }), 422

    @app.errorhandler(500)
    def internal_server_errro(error):
        return jsonify({
            "success": False,
            "type": "api_error",
            "message": error.description
        }), 500

    return app


def is_integer(value):
    try:
        if type(value) is int:
            return True
        elif type(value) is str:
            int(value)
        else:
            return False
    except:
        return False

    return True
