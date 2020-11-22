#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
#import datetime
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import ScalarListType  #added by lili
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)      # db is interface for interacting with database

migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
# class Genres(db.Model):
#   id = db.Column(db.Integer, primary_key=True)
#   name = db.Column(db.String(250), nullable=False)
#   venues = db.relationship('Venue_Genres', backref='Genres', lazy=True)
#   artists = db.relationship('Artist_Genres', backref='Genres', lazy=True)

# genres_list = ['Alternative','Blues','Classical','Country','Electronic','Folk','Hip-Hop','Heavy Metal','Instrumental','Jazz','Musical Theatre','Pop','Punk','R&B','Reggae','Rock n Roll', 'Soul', 'other']
# def add_genres()

# class Venue_Genres(db.Model):
#   id = db.Column(db.Integer, primary_key=True)
#   venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
#   genre_id = db.Column(db.Integer, db.ForeignKey('Genres.id'),nullable=False)

# class Artist_Genres(db.Model):
#   id = db.Column(db.Integer, primary_key=True)
#   artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
#   genre_id = db.Column(db.Integer, db.ForeignKey('Genres.id'), nullable=False)

class Venue(db.Model):  
  __tablename__ = 'Venue'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  address = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))

  # TODO: implement any missing fields, as a database migration using Flask-Migrate

  # -----------------------added by lili start-------------------
  #genres = db.Column(ScalarListType(int))
  #genres = db.Column(db.ARRAY(db.String))
  genres = db.Column(db.Text)
  website = db.Column(db.Text)
  seeking_talent = db.Column(db.Boolean)
  seeking_description = db.Column(db.Text)
  image_link = db.Column(db.String(500))
  shows = db.relationship('Show', backref='Venue', passive_deletes=True, cascade="all,delete,delete-orphan", lazy=True)

  # -----------------------added by lili end-------------------


class Artist(db.Model):
  __tablename__ = 'Artist'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  # genres = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  genres = db.Column(db.Text)
  #genres = db.Column(db.String(120))
  website = db.Column(db.Text)
  seeking_venue = db.Column(db.Boolean)
  seeking_description = db.Column(db.Text)
  shows = db.relationship('Show', backref='Artist', passive_deletes=True, cascade="all,delete,delete-orphan", lazy=True)
  
  def __repr__(self):
    return f'<Artist ID: {self.id}, name: {self.name}, city: {self.city}, state:{self.state}, phone: {self.phone}'
  


#------------------added by lili start-------------------------
class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column (db.DateTime, nullable = False, default=datetime.today())
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id',ondelete='CASCADE'), nullable=False)
  artist_id = db.Column(db.Integer,db.ForeignKey('Artist.id',ondelete='CASCADE'), nullable=False)
  # venue_id = db.Column(db.Integer, nullable=False)
  # artist_id = db.Column(db.Integer, nullable=False)
#------------------added by lili end----------------------------

#db.create_all()

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
 # babel.dates.LC_TIME = Locale.parse('en_US')
  if isinstance(value,str):
    date = dateutil.parser.parse(value)
  else:
    date = value
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  class Venue_With_Shows:
    def __init__(self,venue_id,venue_name):
      r=Venue.query.with_entities(Venue.id,Venue.name).join(Show).filter(Venue.id==Show.venue_id).filter(Venue.id==venue_id).filter(Show.start_time>datetime.today()).all()
      self.id=venue_id
      self.name=venue_name
      if len(r)==0:
        self.num_upcoming_shows=0
      else:
        self.num_upcoming_shows=len(r)

  class Venues_Per_City:
    def __init__(self,venue_city,venue_state):
      self.city=venue_city
      self.state=venue_state
      #res = Venue.query.with_entities(Venue.id,Venue.name).join(Show).filter(Venue.id==Show.venue_id).filter(Venue.city=='Princeton').filter(Venue.state=='NJ').all()
      l=Venue.query.with_entities(Venue.id,Venue.name).filter(Venue.city==venue_city).filter(Venue.state==venue_state).all()
      self.venues=[]
      for i in l:
        venue=Venue_With_Shows(i.id, i.name)
        self.venues.append(venue)

  r = Venue.query.with_entities(Venue.state,Venue.city).distinct().all()
  data=[]
  for i in r:
    area_venues = Venues_Per_City(i.city,i.state)
    data.append(area_venues)


  #   data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search',methods=['GET'])
def search_venues():
    return render_template('layouts/main.html')

@app.route('/venues/search', methods=['POST'])
def search_venues_submission():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  class Data:
    def __init__(self,venue_id,venue_name):
      self.id = venue_id
      self.name = venue_name
      q = Venue.query.join(Show).filter(Venue.id==venue_id).filter(Venue.id==Show.venue_id).filter(Show.start_time>datetime.now()).all()
      self.num_upcoming_shows= len(q)

  search_term=request.form.get('search_term', '')
  venue_names =Venue.query.with_entities(Venue.id,Venue.name).all()
  #artist_names = [x[1] for x in artist_names_list]
  matched_venues = [i for i in venue_names if search_term in i[1]]  #id
  data=[]
  for i in matched_venues:
    data.append(Data(i[0],i[1]))

  response={
    "count": len(matched_venues),
    "data": data
  }
  
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  class venue:
    def __init__(self, venue_id):
      venue_info = Venue.query.filter(Venue.id==venue_id).first()
      if venue_info is not None:
        self.id = venue_id
        self.name = venue_info.name
        self.genres = venue_info.genres.split(",")
        self.address = venue_info.address
        self.city = venue_info.city
        self.state = venue_info.state
        self.phone = venue_info.phone
        self.website = venue_info.website
        self.facebook_link = venue_info.facebook_link
        self.seeking_talent = venue_info.seeking_talent
        self.seeking_description = venue_info.seeking_description
        self.image_link = venue_info.image_link
        past_show_info = Show.query.with_entities(Show.artist_id,Artist.name,Artist.image_link,Show.start_time).join(Artist).filter(Show.artist_id==Artist.id).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.today()).all()
        self.past_shows = past_show_info
        upcoimg_show_info = Show.query.with_entities(Show.artist_id,Artist.name,Artist.image_link,Show.start_time).join(Artist).filter(Show.artist_id==Artist.id).filter(Show.venue_id==venue_id).filter(Show.start_time>datetime.today()).all()
        self.upcoming_shows = upcoimg_show_info
        self.past_shows_count = len(self.past_shows)
        self.upcoming_shows_count = len(self.upcoming_shows)

  data = venue(venue_id)  
  return render_template('pages/show_venue.html', venue=data)
   
  # data1={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #   "past_shows": [{
  #     "artist_id": 4,
  #     "artist_name": "Guns N Petals",
  #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 2,
  #   "name": "The Dueling Pianos Bar",
  #   "genres": ["Classical", "R&B", "Hip-Hop"],
  #   "address": "335 Delancey Street",
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "914-003-1132",
  #   "website": "https://www.theduelingpianos.com",
  #   "facebook_link": "https://www.facebook.com/theduelingpianos",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 3,
  #   "name": "Park Square Live Music & Coffee",
  #   "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
  #   "address": "34 Whiskey Moore Ave",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "415-000-1234",
  #   "website": "https://www.parksquarelivemusicandcoffee.com",
  #   "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #   "past_shows": [{
  #     "artist_id": 5,
  #     "artist_name": "Matt Quevedo",
  #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [{
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 1,
  # }
  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  #return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # -----------------------added by lili start-------------------
  venue_name = request.form.get('name','')
  venue_city = request.form.get('city')
  venue_state = request.form.get('state')
  venue_address = request.form.get('address')
  venue_phone = request.form.get('phone')
  genre_list = request.form.getlist('genres')
  venue_genres = genre_list[0]
  if len(genre_list)>1:
    for i in genre_list[1:]:
      venue_genres= venue_genres + ', ' + i
#  type(venue_genres).__name__
  venue_facebook_link = request.form.get('facebook_link')
  
  
  try:
    new_venue = Venue(name=venue_name,city=venue_city,state=venue_state,address=venue_address,phone=venue_phone,genres=venue_genres,facebook_link=venue_facebook_link)
    db.session.add(new_venue)
   # db.session.flush()
    db.session.commit()
  #  flash('Artist ' + request.form['name'] + ' was successfully listed!')
    flash('Venue ' + venue_name + ' was successfully listed!')
  except:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    db.session.rollback()

  finally:
    db.session.close()
  # -----------------------added by lili end-------------------

  # on successful db insert, flash success
  #flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    flash('Venue ' + venue_id + ' was successfully deleted!')
  except:
    flash('An error occurred. Venue ' + venue_id + ' could not be deleted.')
    db.session.rollback()
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  #return redirect(url_for('venues'))
  return render_template('pages/home.html')


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  # data1=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]

  data = Artist.query.with_entities(Artist.id, Artist.name).all()
  return render_template('pages/artists.html', artists=data)

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  artist_name = request.form.get('name','')
  artist_city = request.form.get('city')
  artist_state = request.form.get('state')
  artist_phone = request.form.get('phone')
  genre_list = request.form.getlist('genres')
  artist_genres = genre_list[0]
  if len(genre_list)>1:
    for i in genre_list[1:]:
      artist_genres= artist_genres + ', ' + i 
  artist_facebook_link = request.form.get('facebook_link')
  
  try:
    new_artist = Artist(name=artist_name,city=artist_city,state=artist_state,phone=artist_phone,genres=artist_genres,facebook_link=artist_facebook_link)
    db.session.add(new_artist)
   # db.session.flush()
    db.session.commit()
  #  flash('Artist ' + request.form['name'] + ' was successfully listed!')
    flash('Artist ' + artist_name + ' was successfully listed!')
  except:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    db.session.rollback()

  finally:
    db.session.close()


  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')

@app.route('/artists/search',methods=['GET'])
def search_artists():
  return render_template('layouts/main.html')
  
@app.route('/artists/search', methods=['POST'])
def search_artists_submission():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  class Data:
    def __init__(self,artist_id,artist_name):
      self.id=artist_id
      self.name=artist_name
      q = Artist.query.join(Show).filter(Artist.id==artist_id).filter(Artist.id==Show.artist_id).filter(Show.start_time>datetime.now()).all()
      self.num_upcoming_shows= len(q)

  search_term=request.form.get('search_term', '')
  artist_names =Artist.query.with_entities(Artist.id,Artist.name).all()
  #artist_names = [x[1] for x in artist_names_list]
  matched_artists = [i for i in artist_names if search_term in i[1]]  #id
  data=[]
  for i in matched_artists:
    data.append(Data(i[0],i[1]))

  response={
    "count": len(matched_artists),
    "data": data
  }

  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": matched_names[0],
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  class artist:
    def __init__(self, artist_id):
      artist_info = Artist.query.filter(Artist.id==artist_id).first()
      if artist_info is not None:
        self.id = artist_id
        self.name = artist_info.name
        self.genres = artist_info.genres.split(",")
        self.city = artist_info.city
        self.state = artist_info.state
        self.phone = artist_info.phone
        self.website = artist_info.website
        self.facebook_link = artist_info.facebook_link
        self.seeking_venue = artist_info.seeking_venue
        self.seeking_description = artist_info.seeking_description
        self.image_link = artist_info.image_link
        past_show_info = Show.query.with_entities(Show.venue_id,Venue.name,Venue.image_link,Show.start_time).join(Venue).filter(Show.venue_id==Venue.id).filter(Show.artist_id==artist_id).filter(Show.start_time<datetime.today()).all()
        self.past_shows = past_show_info
        upcoming_show_info = Show.query.with_entities(Show.venue_id,Venue.name,Venue.image_link,Show.start_time).join(Venue).filter(Show.venue_id==Venue.id).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.today()).all()
        self.upcoming_shows = upcoming_show_info
        self.past_shows_count = len(self.past_shows)
        self.upcoming_shows_count = len(self.upcoming_shows)

  data = artist(artist_id)  
  return render_template('pages/show_artist.html', artist=data)


# #--------------
#   class Artist_Past_Upcoming_Single_Show:
#     def __init__(self,venue_id, venue_name,venue_image_link,show_id,start_time):
#       self.venue_id=venue_id
#       self.venue_name=venue_name
#       self.venue_image_link=venue_image_link
#       self.show_id=show_id
#       self.start_time = start_time
      
#       def __repr__(self):
#         return '<Artist_Past_Upcoming_Single_Show {}>'.format(self.show_id)
  
#   class Single_Artist_Data:
#     def __init__(self,id,name,genres,city,state,phone,website,facebook_link,seeking_venue,seeking_description,image_link,past_shows,upcoming_shows,past_shows_count,upcoming_shows_count):
#       self.id=id
#       self.name=name
#       self.genres=genres
#       self.city=city
#       self.state=state
#       self.phone=phone
#       self.website=website
#       self.facebook_link=facebook_link
#       self.seeking_venue=seeking_venue
#       self.seeking_description=seeking_description
#       self.image_link=image_link
#       self.past_shows=past_shows
#       self.upcoming_shows=upcoming_shows
#       self.past_shows_count= past_shows_count
#       self.upcoming_shows_count=upcoming_shows_count

#     def __repr__(self):
#       return '<Single_Artist_Data {}>'.format(self.id)



  # """ data1={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 5,
  #   "name": "Matt Quevedo",
  #   "genres": ["Jazz"],
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "300-400-5000",
  #   "facebook_link": "https://www.facebook.com/mattquevedo923251523",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "past_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  #   "genres": ["Jazz", "Classical"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "432-325-5432",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 3,
  # } """
#   #data_fake = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]

#   current_time = datetime.now()
#   artist_chosen = Artist.query.filter_by(id=artist_id).first()
#   past_shows = db.session.query(Venue.id,Venue.name,Venue.image_link,Show.start_time).join(Show).filter(Show.artist_id==1).filter(Show.start_time<current_time).all()
#   upcoming_shows = db.session.query(Venue.id,Venue.name,Venue.image_link,Show.start_time).join(Show).filter(Show.artist_id==1).filter(Show.start_time>current_time).all()
#   past_shows_count = len(past_shows)
#   upcoming_shows_count = len(upcoming_shows)
#   data = Single_Artist_Data(artist_chosen.id,artist_chosen.name,artist_chosen.genres,artist_chosen.city,artist_chosen.state,artist_chosen.phone,artist_chosen.website,artist_chosen.facebook_link,artist_chosen.seeking_venue,artist_chosen.seeking_description,artist_chosen.image_link, past_shows, upcoming_shows, past_shows_count,upcoming_shows_count)

#   return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  artist_info = Artist.query.filter_by(id=artist_id).first()
  return render_template('forms/edit_artist.html', form=form, artist=artist_info)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
#   artist_name = request.form.get('name','')
#   artist_city = request.form.get('city')
#   artist_state = request.form.get('state')
#   artist_address = request.form.get('address')
#   artist_phone = request.form.get('phone')
#   genre_list = request.form.getlist('genres')
#   artist_genres = genre_list[0]
#   if len(genre_list)>1:
#     for i in genre_list[1:]:
#       artist_genres= venue_genres + ', ' + i
# #  type(venue_genres).__name__
#   artist_facebook_link = request.form.get('facebook_link')
#   artist_website = request.form.get('website')
#   artist_seeking_venue = request.form.get('seeking_venue')
#   artist_seeking_description = request.form.get('seeking_description')
#   artist_image_link = request.form.get('image_link')

  try:
    flag = False
    artist_info = Artist.query.filter_by(id=artist_id).first()
    if artist_info.name != request.form.get('name'):
      artist_info.name = request.form.get('name')
      flag = True
    if artist_info.city != request.form.get('city'):
      artist_info.city = request.form.get('city')
      flag=True
    if artist_info.state != request.form.get('state'):
      artist_info.state = request.form.get('state')
      flag=True
    if artist_info.address != request.form.get('address'):
      artist_info.address = request.form.get('address')
      flag=True
    if artist_info.phone != request.form.get('phone'):
      artist_info.phone = request.form.get('phone')
      flag=True
    if artist_info.genres != request.form.get('genres'):
      artist_info.genres = request.form.get('genres')
      flag=True
    if artist_info.facebook_link != request.form.get('facebook_link'):
      artist_info.facebook_link = request.form.get('facebook_link')
      flag=True
    if artist_info.website != request.form.get('website'):
      artist_info.website = request.form.get('website')
      flag=True    
    if artist_info.seeking_venue != request.form.get('seeking_venue'):
      artist_info.seeking_venue = request.form.get('seeking_venue')
      flag=True
    if artist_info.seeking_description != request.form.get('seeking_description'):
      artist_info.seeking_description = request.form.get('seeking_description')
      flag=True
    if artist_info.image_link != request.form.get('image_link'):
      artist_info.image_link = request.form.get('image_link')
      flag=True
    if flag == True:
      db.session.commit()
      flash('Venue ' + venue_name + ' was successfully updated!')
    else:
      flash('Venue ' + venue_name + ' information is not changed!')
  except:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    db.session.rollback()

  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  venue_info = Venue.query.filter_by(id=venue_id).first()
  return render_template('forms/edit_venue.html', form=form, venue=venue_info)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
#   venue_name = request.form.get('name','')
#   venue_city = request.form.get('city')
#   venue_state = request.form.get('state')
#   venue_address = request.form.get('address')
#   venue_phone = request.form.get('phone')
#   genre_list = request.form.getlist('genres')
#   venue_genres = genre_list[0]
#   if len(genre_list)>1:
#     for i in genre_list[1:]:
#       venue_genres= venue_genres + ', ' + i
# #  type(venue_genres).__name__
#   venue_facebook_link = request.form.get('facebook_link')
   
  try:
    flag = False
    venue_info = Venue.query.filter_by(id=venue_id).first()
    if venue_info.name != request.form.get('name'):
      venue_info.name = request.form.get('name')
      flag = True
    if venue_info.city != request.form.get('city'):
      venue_info.city = request.form.get('city')
      flag=True
    if venue_info.state != request.form.get('state'):
      venue_info.state = request.form.get('state')
      flag=True
    if venue_info.address != request.form.get('address'):
      venue_info.address = request.form.get('address')
      flag=True
    if venue_info.phone != request.form.get('phone'):
      venue_info.phone = request.form.get('phone')
      flag=True
    if venue_info.genres != request.form.get('genres'):
      venue_info.genres = request.form.get('genres')
      flag=True
    if venue_info.facebook_link != request.form.get('facebook_link'):
      venue_info.facebook_link = request.form.get('facebook_link')
      flag=True
    if flag == True:
      db.session.commit()
      flash('Venue ' + venue_name + ' was successfully updated!')
    else:
      flash('Venue ' + venue_name + ' information is not changed!')
  except:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    db.session.rollback()

  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))




#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  
  
  show_info = Show.query.with_entities(Show.start_time,Show.venue_id,Venue.name,Show.artist_id,Artist.name,Artist.image_link).join(Venue).filter(Show.venue_id==Venue.id).join(Artist).filter(Show.artist_id==Artist.id).all()

  return render_template('pages/shows.html', shows=show_info)

  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  show_start_time = request.form.get('start_time')
  show_venue_id = request.form.get('venue_id')
  show_artist_id = request.form.get('artist_id')
  
  
  try:
    new_show = Show(start_time=show_start_time,venue_id=show_venue_id,artist_id=show_artist_id)
    db.session.add(new_show)
   # db.session.flush()
    db.session.commit()
  #  flash('Artist ' + request.form['name'] + ' was successfully listed!')
    flash('Show was successfully listed!')
  except Exception as e:
    flash('An error occurred. Show could not be listed.')
    db.session.rollback()
    print(e)
  finally:
    db.session.close()
  # on successful db insert, flash success
  # flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':

    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))


    lkk
    app.run(host='0.0.0.0', port=port)

'''
