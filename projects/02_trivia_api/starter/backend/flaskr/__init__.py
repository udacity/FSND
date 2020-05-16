import os
from sqlalchemy.sql.expression import func
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
required_attribute_template = "A value is required for the attribute \"{}\"."
integer_expected_template = "The attribute \"{}\" must be an integer."
integer_out_of_range_template = "The attribute \"{}\" must be an integer from {} and {}."
list_expected_template = "The attribute \"{}\" must be a list."
object_expected_template = "The attribute \"{}\" must be an object"
not_found_template = "A resource for the attribute \"{}\" with the value \"{}\" was not found."


def create_app(test_config=None):
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

    @app.route('/questions')
    def retrieve_questions():
        page = request.args.get('page', 1, type=int)
        questions_page = Question.query.\
            order_by(Question.id.asc()).\
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
                order_by(Question.id.asc()).\
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
            order_by(Question.id.asc()).\
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

    def validate_send_quiz_input(data):
        previous_questions = data.get("previous_questions", [])
        quiz_category = data.get("quiz_category")

        validation_errors = []
        if "quiz_category" not in data:
            validation_errors.append({
                "type": "attribute_expected",
                "attribute": "quiz_category",
                "message": required_attribute_template.format("quiz_category")
            })
        elif type(quiz_category) is not dict:
            validation_errors.append({
                "type": "object_expected",
                "attribute": "quiz_category",
                "message": object_expected_template.format("quiz_category")
            })
        elif "id" not in data["quiz_category"]:
            validation_errors.append({
                "type": "attribute_expected",
                "attribute": "quiz_category.id",
                "message": required_attribute_template.format("quiz_category.id")
            })

        if "previous_questions" not in data:
            validation_errors.append({
                "type": "attribute_expected",
                "attribute": "previous_questions",
                "message": required_attribute_template.format("previous_questions")
            })
        elif type(previous_questions) is not list:
            validation_errors.append({
                "type": "invalid_type",
                "attribute": "previous_questions",
                "message": list_expected_template.format("previous_questions")
            })

        return validation_errors

    @app.route("/quizzes", methods=["POST"])
    def send_quiz():
        data = request.get_json()
        if not data:
            abort(400)

        validation_errors = validate_send_quiz_input(data)
        if validation_errors:
            return jsonify({
                "success": False,
                "type": "invalid_request_error",
                "message": "The request could not be processed because of invalid data.",
                "validation_errors": validation_errors
            }), 400

        previous_questions = data["previous_questions"]
        category_id = data["quiz_category"]["id"]
        category_query = Category.query.filter(Category.id == category_id)
        if category_id != 0 and category_query.one_or_none() is None:
            return jsonify({
                "success": False,
                "type": "invalid_request_error",
                "message": "The request could not be processed because of invalid data.",
                "validation_errors": [{
                    "type": "not_found",
                    "attribute": "quiz_category.id",
                    "message": not_found_template.format("quiz_category.id", category_id)
                }]
            }), 400

        question_category_condition = True
        if category_id != 0:
            question_category_condition = Question.category == category_id

        question = Question.query.\
            filter(
                ~Question.id.in_(previous_questions),
                question_category_condition
            ).\
            order_by(func.random()).\
            first()

        return jsonify({
            "success": 200,
            "question": question.format() if question else None
        })

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
