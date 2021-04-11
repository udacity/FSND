#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import datetime


# Connect to a local postgresql database
app = Flask(__name__)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500), nullable=False,
      default='https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60')
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(256))
    genres = db.Column(db.String(256), nullable=False, default='Other')
    shows = db.relationship(
      'Show',
      backref='venue',
      lazy=True
    )

artist_shows = db.Table('artist_shows',
  db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id'), primary_key=True),
  db.Column('show_id', db.Integer, db.ForeignKey('Show.id'), primary_key=True)
)   

class Artist(db.Model):
  __tablename__ = 'Artist'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  genres = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  website = db.Column(db.String(120))
  seeking_venue = db.Column(db.Boolean, nullable=False, default=False)

class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  showdate = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())
  # Foreign key reference to this show's venue
  venue_id = db.Column(
    db.Integer,
    db.ForeignKey('Venue.id'),
    nullable=False)
  artists = db.relationship(
    'Artist', secondary=artist_shows, backref=db.backref('shows', lazy=True)
  )
