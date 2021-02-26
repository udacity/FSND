
from sqlalchemy import Column, String, Integer, create_engine, ForeignKey
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import json
import os

# Postgres database info here
database_path = os.environ.get('DATABASE_URL')
if(database_path is None):
  database_path = 'postgresql://postgres:postgres@localhost:5432/capstone'

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
    with app.app_context():
        db.create_all()
        migrate = Migrate(app, db)
    


'''
Movie Class
Have title and release date
'''
class Movie(db.Model):  
  __tablename__ = 'Movie'

  id = Column(Integer, primary_key=True)
  title = Column(String)
  release_date = Column(String)
  casting = db.relationship('Casting', backref='Movie', passive_deletes=True, cascade="all,delete,delete-orphan", lazy=True)

  def __init__(self, id, title, release_date):
    if id is not None:
        self.id = id
    self.title = title
    self.release_date = release_date

  def format(self):
    return {
      'id': self.id,
      'title': self.title,
      'release_date': self.release_date}

  def insert(self):
    db.session.add(self)
    db.session.commit()
  
  def update(self):
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()


'''
Actor
Have title and release date
'''
class Actor(db.Model):  
  __tablename__ = 'Actor'

  id = Column(Integer, primary_key=True)
  name = Column(String)
  age = Column(String)
  gender = Column(String)
  casting = db.relationship('Casting', backref='Actor', passive_deletes=True, cascade="all,delete,delete-orphan", lazy=True)


  def __init__(self, id, name, age, gender):
    if id is not None:
        self.id = id
    self.name = name
    self.age = age
    self.gender = gender

  def format(self):
    return {
      'id': self.id,
      'name': self.name,
      'age': self.age,
      'gender': self.gender
      }

  def insert(self):
    db.session.add(self)
    db.session.commit()
  
  def update(self):
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

'''
Casting
Have title and release date
'''
class Casting(db.Model):
  __tablename__ = 'Casting'

  id = Column(Integer, primary_key=True)
  movie_id = Column(Integer, ForeignKey('Actor.id', ondelete='CASCADE'), nullable=False)
  actor_id = Column(Integer, ForeignKey('Movie.id', ondelete='CASCADE'), nullable=False)

  def __init__(self, id, movie_id, actor_id):
    if id is not None:
        self.id = id
    self.movie_id = movie_id
    self.actor_id = actor_id

  def insert(self):
    db.session.add(self)
    db.session.commit()
  
  def update(self):
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

