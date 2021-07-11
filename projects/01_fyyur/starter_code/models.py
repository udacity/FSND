#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from flask_sqlalchemy import SQLAlchemy
import datetime
from datetime import datetime
# from app import app , today


db = SQLAlchemy()
db.create_all


today = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__= 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(), nullable=True)
    seeking_talent=db.Column(db.Boolean, default=False)
    seeking_description=db.Column(db.String(), nullable=True)
    website_link = db.Column(db.String(120), nullable=True)
    # shows = db.relationship('Show', backref='venues')
    shows = db.relationship('Show', backref='venues', lazy='joined', cascade="all, delete")


    def __repr__(self):
        return f"<Venue {self.id} {self.name}>"



class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link= db.Column(db.String(120), nullable=True)
    seeking_venue=db.Column(db.Boolean, default=False)
    seeking_description=db.Column(db.String(), nullable=True)
    shows = db.relationship('Show', backref='artists', lazy='joined', cascade="all, delete")


    def __repr__(self):
        return f"<Artist {self.id} {self.name}>"

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)

    artist_id = db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id'))
    venue_id = db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id'))
    start_time = db.Column('start_time', db.String, default=today)

    def __repr__(self):
        return f"<Show {self.id} {self.start_time}>"