import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import and_, func
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
    CORS enabled to Allow all origins and for routes starting with /api.
    Allows browsers to send the Content-Type and Authorization header.
    Allows all methods.
    '''
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    @app.after_request
    def after_request(response):
        response.headers.add(
          'Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
        response.headers.add(
          'Access-Control-Allow-Methods', 'GET,PUT,PATCH,POST,DELETE,OPTIONS')
        return response

    def all_categories():
        '''
        Helper function to get all categories from DB
        Args: None
        Returns: Object of categories mapped as id:type
        {
            "1": "Science",
            "2": "Art",
            "3": "Geography",
            "4": "History"
        }
        '''
        categories = Category.query.all()
        categoriesObj = {}
        for category in categories:
            formattedCategory = category.format()
            categoriesObj[formattedCategory['id']] = formattedCategory['type']
        return categoriesObj

    @app.route("/api/categories", methods=['GET'])
    def get_categories():
        '''
        GET /api/categories
        Args: None
        Response: Object with categories mapped as id:type and success message
        {
            "categories: {
                "1": "Science",
                "2": "Art",
                "3": "Geography",
                "4": "History"
            },
            "success": True
        }
        '''
        return jsonify({'categories': all_categories(), 'success': True})

    def paginate_questions(request, questions):
        '''
        Helper function to paginate questions, limited by QUESTIONS_PER_PAGE
        Args: request, questions:array of Question objects
        Returns: QUESTIONS_PER_PAGE number of questions formatted
        [
            {
            "answer": "Muhammad Ali",
            "category": 4,
            "difficulty": 1,
            "id": 9,
            "question": "What boxer's original name is Cassius Clay?"
            },
            {
            "answer": "George Washington Carver",
            "category": 4,
            "difficulty": 2,
            "id": 12,
            "question": "Who invented Peanut Butter?"
            }...
        ]
        '''
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        formatted_questions = [
            question.format() for question in questions]
        return formatted_questions[start:end]

    @app.route("/api/questions", methods=['GET'])
    def get_questions():
        '''
        GET /api/questions
        Args: None
        Response: An object with a list of questions, number of
        total_questions, current_category, categories and success.
        {
            "categories": {
                "1": "Science",
                "4": "History"...
            },
            "current_category": "All",
            "questions": [
                {
                "answer": "George Washington Carver",
                "category": 4,
                "difficulty": 2,
                "id": 12,
                "question": "Who invented Peanut Butter?"
                }...
            ],
            "success": True,
            "total_questions": 19
        }
        '''
        questions = Question.query.order_by(Question.id).all()
        paginated_questions = paginate_questions(request, questions)

        if len(paginated_questions) == 0:
            abort(404)

        return jsonify({
            'questions': paginated_questions,
            'success': True,
            'total_questions': len(questions),
            'categories': all_categories(),
            'current_category': 'All'
        })

    @app.route("/api/questions/<int:question_id>", methods=['DELETE'])
    def delete_question(question_id):
        '''
        DELETE /api/questions/<question_id>
        Args: question_id, Id of question to be deleted.
        Response: {"success": True} or passed to the 404 error handler
        '''

        question = Question.query.filter(
            Question.id == question_id).one_or_none()

        if question is None:
            abort(404)

        question.delete()
        return jsonify({
            'success': True
        })

    def is_valid(data):
        '''
        Validates that data is not None
        Args: data
        Returns: True if presents and False if absent
        '''
        if data is '' or data is None:
            return False
        return True

    def validate_or_abort(data):
        '''
        Abort request if data is not valid
        Args: data
        '''
        if not is_valid(data):
            abort(422)

    @app.route("/api/questions", methods=['POST'])
    def create_questions():
        '''
        POST /api/questions -d {"searchTerm": "title"}
        to get questions based on a search term.
        Response: Questions for whom the search term
        is a substring of the question
        {
            "current_category": "All",
            "questions": [
                {
                "answer": "Maya Angelou",
                "category": 4,
                "difficulty": 2,
                "id": 5,
                "question": "Whose autobiography is entitled?"
                },
                {
                "answer": "Edward Scissorhands",
                "category": 5,
                "difficulty": 3,
                "id": 6,
                "question": "What was the title of the 1990 fantasy directed?"
                }
            ],
            "success": True,
            "total_questions": 2
        }

        POST /api/questions -d {
            "question": "question",
            "answer": "answer",
            "category": 2,
            "difficulty": 3
        }
        To create new question
        Response: newly created question and success message
        {
            "success": True,
            "question": {
                "question": "question",
                "answer": "answer",
                "category": 2,
                "difficulty": 3
                "id": 12,
            }
        }
        Error: 422 for any validation errors
        '''
        try:
            data = request.get_json()
            searchTerm = data.get('searchTerm', None)
            if is_valid(searchTerm):
                questions = Question.query.order_by(Question.id).filter(
                    Question.question.ilike('%{}%'.format(searchTerm))).all()
                paginated_questions = paginate_questions(request, questions)

                return jsonify({
                    'questions': paginated_questions,
                    'success': True,
                    'total_questions': len(questions),
                    'current_category': 'All'
                })
            else:
                question = data.get('question', None)
                answer = data.get('answer', None)
                category = data.get('category', None)
                difficulty = data.get('difficulty', None)

                # validate data before creating
                validate_or_abort(question)
                validate_or_abort(answer)
                validate_or_abort(category)
                validate_or_abort(difficulty)

                newQuestion = Question(
                    question=question,
                    answer=answer,
                    category=category,
                    difficulty=difficulty
                )

                newQuestion.insert()

                return jsonify({
                    'success': True,
                    'question': newQuestion.format()
                })
        except Exception:
            abort(422)

    @app.route("/api/categories/<int:category_id>/questions", methods=['GET'])
    def get_questions_by_category(category_id):
        '''
        GET /api/categories/<category_id>/questions
        Fetches a list of questions that have same category as category_id
        {
            "current_category": "Science",
            "questions": [
                {
                    "answer": "The Liver",
                    "category": 1,
                    "difficulty": 4,
                    "id": 20,
                    "question": "What is the heaviest organ in the human body?"
                    },
                    {
                    "answer": "Alexander Fleming",
                    "category": 1,
                    "difficulty": 3,
                    "id": 21,
                    "question": "Who discovered penicillin?"
                }
            ],
            "success": True,
            "total_questions": 2
        }
        '''
        try:
            current_category = Category.query.filter_by(
                id=category_id).one().format()['type']
            questions = Question.query.order_by(Question.id).filter(
                Question.category == category_id).all()
            paginated_questions = paginate_questions(request, questions)

            return jsonify({
                'questions': paginated_questions,
                'success': True,
                'total_questions': len(questions),
                'current_category': current_category
            })
        except Exception:
            abort(404)

    @app.route("/api/quizzes", methods=['POST'])
    def get_quiz_question():
        '''
        POST /api/quizzes -d {
            "quiz_category": {"type": "Science", "id": 1},
            "previous_questions": []
        }
        JsonData: Takes quiz_category and previous_questions parameters.
        Response: A random question within the given category provided,
        and that is not one of the previous questions.
        NOTE: If questions in quiz_category have been exhausted and number of
        answered questions is not yet equal to questionsPerPlay, a random
        question from another category is returned
        '''
        try:
            data = request.get_json()
            prev_questions = data.get('previous_questions', [])
            quiz_category = data.get('quiz_category', {'id': 0})

            question = Question.query.filter(
                quiz_filter(quiz_category, prev_questions)).order_by(
                    func.random()).limit(1).one_or_none()
            if question is None:
                question = Question.query.filter(
                    quiz_filter({'id': 0}, prev_questions)).order_by(
                        func.random()).limit(1).one_or_none()

            if question is not None:
                question = question.format()

            return jsonify({
                'question': question,
                'success': True
            })
        except Exception:
            abort(422)

    def quiz_filter(quiz_category, previous_questions):
        '''
        Creates a filter query for quiz questions
        Args: quiz_category object and previous_questions array
        Returns: Filter query for questions matching the category and not in
        the previous_questions array
        quiz_filter({'type': 'Science', 'id': 1}, [2])
        '''
        filter = Question.id.notin_(previous_questions)
        if quiz_category['id'] is 0:
            return filter
        else:
            return and_(filter, Question.category == quiz_category['id'])

    '''
    Error handlers for expected errors.
    '''

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad_request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "not_found"
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method_not_allowed"
        }), 405

    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable_entity"
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal_server_error"
        }), 500

    return app
