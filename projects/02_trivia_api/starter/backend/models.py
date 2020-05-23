import os
from sqlalchemy import Column, String, Integer, create_engine, ForeignKey
from flask_sqlalchemy import SQLAlchemy
import json


def create_db_path(**kwargs):
    """Returns the database URI after prompting the user for the password. Supports only localhost.

    Keyword arguments:
    db_user -- user with which to access the database
    db_name -- the database name
    Return: Returns a URI-string formatted as '<RDBMS-dialect>://<db_user>:<password>@localhost:5432/<db_name>'
    """
    db_user = kwargs.get('db_user', 'postgres')
    database_name = kwargs.get('db_name', 'trivia')

    # default_or_testing = 'default' if database_name == 'trivia' else 'testing'
    # ask_for_pw = f"Insert password for {default_or_testing} database user: "
    # user_pw = input(ask_for_pw)
    password = '234107'  # if user_pw is not None else user_pw
    return f"postgresql://{db_user}:{password}@localhost:5432/{database_name}"


database_path = create_db_path()
db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''


def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


'''
Question

'''


class Question(db.Model):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    question = Column(String)
    answer = Column(String)
    category_id = Column(
        Integer,
        ForeignKey('categories.id'),
        nullable=False,
        default=7)
    difficulty = Column(Integer)

    def __init__(self, question, answer, difficulty, category_id=7):
        self.question = question
        self.answer = answer
        self.category_id = category_id
        self.difficulty = difficulty

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'category_id': self.category_id,
            'difficulty': self.difficulty
        }


'''
Category

'''


class Category(db.Model):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    type = Column(String)
    questions = db.relationship('Question', backref='category', lazy=True)

    def __init__(self, type):
        self.type = type

    def format(self):
        return {
            'id': self.id,
            'type': self.type
        }
