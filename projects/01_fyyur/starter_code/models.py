#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
from app import db

class Venue(db.Model):
    __tablename__ = 'Venue'
    __table_args__ = (db.UniqueConstraint('name', 'city'), )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False, default='')
    facebook_link = db.Column(db.String(120), nullable=False, default='')
    genres = db.Column(db.ARRAY(db.Text), nullable=False)
    website = db.Column(db.String(120), nullable=False, default='')
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String, nullable=False, default='')
    shows=db.relationship('Show', backref='show_venue', cascade='all, delete, delete-orphan')

class Artist(db.Model):
    __tablename__ = 'Artist'
    __table_args__ = (db.UniqueConstraint('name', 'city'), )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.Text), nullable=False)
    image_link = db.Column(db.String(500), nullable=False, default='')
    facebook_link = db.Column(db.String(120), nullable=False, default='')
    website = db.Column(db.String(120), nullable=False, default='')
    seeking_venues = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String, nullable=False, default='')
    shows=db.relationship('Show', backref='show_artist', cascade='all, delete, delete-orphan')

class Show(db.Model):
    __tablename__ = 'Show'
    __table_args__ = (db.UniqueConstraint('artist_id', 'start_time'), )

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
