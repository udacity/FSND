import os
from sqlalchemy import Column, String, Integer, Date
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import json

db = SQLAlchemy()

"""
setup_db(app)
    binds a flask application and a SQLAlchemy service
"""


def setup_db(app):
    migrate = Migrate(app, db)
    db.app = app
    db.init_app(app)
    db.create_all()


"""
db_drop_and_create_all()
    drops the database tables and starts fresh
    can be used to initialize a clean database
    !!NOTE you can change the database_filename variable to have multiple verisons of a database
"""


def db_drop_and_create_all():
    db.drop_all()
    db.create_all()


"""
movies_actors join table
"""
# this is an association table for actors and movies... capturing 'roles' that actors have held in specific movies
movies_actors = db.Table(
    "movies_actors",
    db.Column(
        "movie_id", db.Integer, db.ForeignKey("movies.id"), primary_key=True
    ),
    db.Column(
        "actor_id", db.Integer, db.ForeignKey("actors.id"), primary_key=True
    ),
)

"""
Actors
"""


class Actor(db.Model):
    __tablename__ = "actors"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(80), nullable=False)

    def __init__(self, name, age, gender):
        self.name = name
        self.age = age
        self.gender = gender

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
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
        }


"""
Movies
"""


class Movie(db.Model):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True)
    title = Column(String(120), nullable=False)
    release_date = Column(Date)
    actors = db.relationship(
        "Actor",
        secondary=movies_actors,
        backref=db.backref("movies", lazy="dynamic"),
        lazy="dynamic",
    )

    def __init__(self, title, release_date):
        self.title = title
        self.release_date = release_date

    def insert(self):
        db.session.add(self)
        db.session.commit(self)

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            "id": self.id,
            "title": self.title,
            "release_date": self.release_date,
        }
