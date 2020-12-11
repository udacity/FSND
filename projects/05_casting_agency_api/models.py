import os
from sqlalchemy import Column, String, Integer, Date
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import date
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
    create_test_records()


def create_test_records():
    new_actor = Actor(name="clay", gender="male", age=92)

    new_movie = Movie(title="titanic", release_date=date.today())

    new_role = Role.insert().values(
        movie_id=new_movie.id, actor_id=new_actor.id
    )

    new_actor.insert()
    new_movie.insert()
    db.session.execute(new_role)
    db.session.commit()


"""
movies_actors join table (not sure if this is needed)
"""
# this is an association table for actors and movies... capturing 'roles' that actors have held in specific movies
Role = db.Table(
    "roles",
    db.Model.metadata,
    db.Column("movie_id", db.Integer, db.ForeignKey("movies.id")),
    db.Column("actor_id", db.Integer, db.ForeignKey("actors.id")),
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
    title = Column(String)
    release_date = Column(Date)
    actors = db.relationship(
        "Actor", secondary=Role, backref=db.backref("roles", lazy="joined"),
    )

    def __init__(self, title, release_date):
        self.title = title
        self.release_date = release_date

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
            "title": self.title,
            "release_date": self.release_date,
        }
