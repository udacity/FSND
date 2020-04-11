from flask import Flask, jsonify, request, jsonify, abort
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import random

from models import Question, Category, setup_db

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    question_list = [question.format() for question in selection]
    current_questions = question_list[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type,Authorization,true')
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    @app.route('/categories', methods=['GET'])
    def list_categories():
        cat_list = []
        categories = Category.query.all()
        for category in categories:
            cat_list.append(category.type)

        return jsonify({
            'status_code': 200,
            'success': True,
            'categories': cat_list,
            'total_categories': len(categories)
        })

    @app.route('/questions', methods=['GET'])
    def list_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        current_cat = request.args.get('currentCategory', 'None', type=str)

        cat_list = []
        categories = Category.query.all()
        for category in categories:
            cat_list.append(category.type)

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'status_code': 200,
            'success': True,
            'questions': current_questions,
            'total_questions': len(selection),
            'current_category': current_cat,
            'categories': cat_list
        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()

            return jsonify({
                'status_code': 200,
                'success': True,
                'total_questions': len(Question.query.all()),
            })

        except BaseException:
            abort(422)

    @app.route('/questions', methods=['POST'])
    def add_new_question():
        body = request.get_json()

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_difficulty = body.get('difficulty', None)
        new_category = body.get('category', None)
        search_term = body.get('searchTerm', None)

        try:
            if search_term:
                selection = Question.query.order_by(Question.id).filter(
                    Question.question.ilike('%{}%'.format(search_term)))
                current_questions = paginate_questions(request, selection)

                return jsonify({
                    'success': True,
                    'questions': current_questions,
                    'total_questions': len(selection.all()),
                    'current_category': None
                })

            else:
                question = Question(
                    question=new_question,
                    answer=new_answer,
                    category=new_category,
                    difficulty=new_difficulty)
                question.insert()

                selection = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request, selection)

                return jsonify({
                    'success': True,
                    'created': question.id,
                    'questions': current_questions,
                    'total_questions': len(Question.query.all())
                })

        except BaseException:
            abort(422)

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def retrieve_questions_by_category(category_id):
        try:
            category_id = str(category_id + 1)
            selection = Question.query.filter(
                Question.category == category_id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(Question.query.all()),
                'current_category': category_id
            })
        except BaseException:
            abort(422)

    @app.route('/quizzes', methods=['POST'])
    def get_quiz_questions():
        body = request.get_json()
        if not body:
            abort(400)
        previous_q = body['previous_questions']
        category_id = body['quiz_category']['id']
        category_id = str(int(category_id) + 1)

        if category_id == 0:
            if previous_q is not None:
                questions = Question.query.filter(
                    Question.id.notin_(previous_q)).all()
            else:
                questions = Question.query.all()
        else:
            if previous_q is not None:
                questions = Question.query.filter(
                    Question.id.notin_(previous_q),
                    Question.category == category_id).all()
            else:
                questions = Question.query.filter(
                    Question.category == category_id).all()

        next_question = random.choice(questions).format()
        if not next_question:
            abort(404)
        if next_question is None:
            next_question = False

        return jsonify({
            'success': True,
            'question': next_question
        })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    return app
