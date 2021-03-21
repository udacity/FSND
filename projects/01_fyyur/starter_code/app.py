#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from types import SimpleNamespace
from datetime import datetime
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
### Muath TODO: import Migrate class from Flask-Migrate ((Done))
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database ((Done)) 
### Muath TODO: define migrate instence for the app and db ((Done))
migrate = Migrate(app,db,compare_type=True)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
### Muath TODO: Implement a genre model ((Done))
class Genre(db.Model):
    __tablename__ = 'genre'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)

    def __repr__(self):
      return f'<Genre {self.id}: {self.name}>'

### Muath TODO: Implement an association table venue_themes ((Done))
venue_themes = db.Table('venue_themes',
db.Column('venue_id', db.Integer, db.ForeignKey('venue.id'), primary_key=True),
db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True))

class Venue(db.Model):
  ### Muath TODO: changing table name to lower case i.e:venue (it's annoying to put the name in double qoutes when using psql to inspect the database!) ((Done))
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String)
    genres = db.relationship('Genre', secondary=venue_themes, backref=db.backref('venues', lazy=True))
    shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
      return f'<Venue {self.id}: {self.name}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate ((Done))

### Muath TODO: Implement an association table artist_themes ((Done))
artist_themes = db.Table('artist_themes',
db.Column('artist_id', db.Integer, db.ForeignKey('artist.id'), primary_key=True),
db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True))

class Artist(db.Model):
    ### Muath TODO: changing table names to lower case i.e:artist (it's annoying to put the name in double qoutes when using psql to inspect the database!) ((Done))
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    ### Muath TODO: removing the genres column and have it in seprate table ((Done))
    ### genres = db.Column(db.String(120)) ###
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String)
    genres = db.relationship('Genre', secondary=artist_themes, backref=db.backref('artists', lazy=True))
    shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
      return f'<Artist {self.id}: {self.name}>'
    
    # TODO: implement any missing fields, as a database migration using Flask-Migrate ((Done))

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration. ((Done))

### Muath TODO: Implement a show model ((Done))
class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    start_time = db.Column(db.DateTime(timezone=True))

    def __repr__(self):
      return f'<Show {self.id}: Artist {self.artist_id} at Venue {self.venue_id}>'

### Muath TODO: implement a function to populate the genre table in the database with a list of genres as specified in the form.py module.
def populate_genre():
  genres_list = ['Alternative',
            'Blues',
            'Classical',
            'Country',
            'Electronic',
            'Folk',
            'Funk',
            'Hip-Hop',
            'Heavy Metal',
            'Instrumental',
            'Jazz',
            'Musical Theatre',
            'Pop',
            'Punk',
            'R&B',
            'Reggae',
            'Rock n Roll',
            'Soul',
            'Other']
  for name in genres_list:
    new_genre = Genre(name=name)
    db.session.add(new_genre)
    db.session.commit()
  return print("genre table populated successfuly")

### Please uncomment the function call statment below after creating all models by running latest migration script !!! please notice that you need to run the function ONE TIME ONLY then you should comment it out again !!!

#populate_genre()


### Implement function get_or_create: this code is NOT mine I copied it from StackOverFlow "https://stackoverflow.com/questions/2546207/does-sqlalchemy-have-an-equivalent-of-djangos-get-or-create" and applied minor tweaks. ### used this to prevent dublicate inserts.

def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, True
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.flush()
        return instance, False
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  artist_records = db.session.query(Artist).limit(10)
  venue_records = db.session.query(Venue).limit(10)
  
  data_artists=[{
    "id": artist.id,
    "name": artist.name,
    "city": artist.city,
    "state": artist.state
  } for artist in artist_records]
  
  data_venues=[{
    "id": venue.id,
    "name": venue.name,
    "city": venue.city,
    "state": venue.state
  } for venue in venue_records]

  return render_template('pages/home.html', venues=data_venues, artists=data_artists)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue. ((Done with comments))
  state_rows = db.session.query(Venue.state)
  states_set = set(state_row.state for state_row in state_rows)
  areas_list = []
  todays_datetime = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
  for state in states_set:
    city_rows = db.session.query(Venue.city).filter_by(state=state)
    cities_set = set(city_row.city for city_row in city_rows)
    for city in cities_set:
      venue_rows = db.session.query(Venue.id, Venue.name).filter_by(city=city)
      area_dict = {}
      area_dict['state'] = state
      area_dict['city'] = city
      venues_list = []
      for venue_row in venue_rows:
        shows_count = db.session.query(Show).join(Venue).filter(Show.start_time > todays_datetime).filter(Venue.id==venue_row.id).count()
        venue_dict = {}
        venue_dict['id'] = venue_row.id
        venue_dict['name'] = venue_row.name
        venue_dict['num_upcoming_shows'] = shows_count
        venues_list.append(venue_dict)
      area_dict['venues'] = venues_list
      areas_list.append(area_dict)

  return render_template('pages/venues.html', areas=areas_list);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id ((Done with comments))
  todays_datetime = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
  venue_data = Venue.query.filter_by(id=venue_id).first()
  past_shows_data = db.session.query(Show).join(Venue).filter(Show.start_time < todays_datetime).filter(Venue.id==venue_data.id).all()
  upcoming_shows_data = db.session.query(Show).join(Venue).filter(Show.start_time > todays_datetime).filter(Venue.id==venue_data.id).all()
  
  data={
    "id": venue_data.id,
    "name": venue_data.name,
    "genres": venue_data.genres,
    "address": venue_data.address,
    "city": venue_data.city,
    "state": venue_data.state,
    "phone": venue_data.phone,
    "website_link": venue_data.website_link,
    "facebook_link": venue_data.facebook_link,
    "seeking_talent": venue_data.seeking_talent,
    "seeking_description": venue_data.seeking_description,
    "image_link": venue_data.image_link,
    "past_shows": [{'artist_id':show.artist.id, 'artist_name':show.artist.name, 'artist_image_link':show.artist.image_link, 'start_time':str(show.start_time)} for show in past_shows_data],
    "upcoming_shows": [{'artist_id':show.artist.id, 'artist_name':show.artist.name, 'artist_image_link':show.artist.image_link, 'start_time':str(show.start_time)} for show in upcoming_shows_data],
    "past_shows_count": len(past_shows_data),
    "upcoming_shows_count": len(upcoming_shows_data),
  }
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead ((Done))
  # TODO: modify data to be the data object returned from db insertion ((Done))
  
  # Retrieving data from form.(ImmutableMultiDict)
  form_data = request.form
  
  # Shallow copy the object to convert to MutableMultiDict
  mutable_form_data = form_data.copy()
  
  
  # Pop out the list of genres from the Dict
  genres = mutable_form_data.poplist('genres')
  
  # Retrive a list of the genre records corrosponding to genres items from genre table. (used list comprihension). 
  genres_records = [genre for genre in Genre.query.all() if genre.name in genres]
  
  # Checking the seeking_talent value
  if 'seeking_talent' in mutable_form_data:
    mutable_form_data['seeking_talent'] = True
  
  # Processing name and city fields for case-insensitivity
  mutable_form_data['name'].title()
  mutable_form_data['city'].title()
  # Create a new venue instance from Venue class by passing the dictionary ((Insted of using commneted line, use new_function get_or_create))
  #new_venue = Venue(**mutable_form_data)
  
  my_venue, flag = get_or_create(db.session,Venue,**mutable_form_data)

  my_venue_name = my_venue.name

  if flag:
    flash('An error occurred. Venue ' + my_venue_name + ' already listed!')
    return render_template('pages/home.html')
  
  else:
  # Adding and commiting to database
    error = None
    try:
      # Passing the genres_records to the new_venue object (through venue_themes association table)
      my_venue.genres = genres_records
      db.session.add(my_venue)
      db.session.commit()
    except:
      error = True
      db.session.rollback()
    finally:
      db.session.close()
      if not error:
        # on successful db insert, flash success ((Done))
        flash('Venue ' + my_venue_name + ' was successfully listed!')
      else:
      # TODO: on unsuccessful db insert, flash an error instead. ((Done))
        flash('An error occurred. Venue ' + my_venue_name + ' could not be listed.')

      return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail. ((Done))
  venue = Venue.query.filter_by(id=venue_id).first()
  
  error = None
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
    if not error:
      # on successful db insert, flash success
      flash('Venue ' + venue.name + ' was successfully deleted!')
    else:
  # TODO: on unsuccessful db insert, flash an error instead.((Done))
      flash('An error occurred. Venue ' + venue.name + ' could not be deleted.')
    return render_template('pages/home.html')
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage ((Done))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database ((Done))
  
  artist_records = db.session.query(Artist).all()
  data=[{
    "id": artist.id,
    "name": artist.name,
  } for artist in artist_records]

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id ((Done))
  todays_datetime = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
  artist_data = Venue.query.filter_by(id=venue_id).first()
  past_shows_data = db.session.query(Show).join(Artist).filter(Show.start_time < todays_datetime).filter(Artist.id==artist_data.id).all()
  upcoming_shows_data = db.session.query(Show).join(Artist).filter(Show.start_time > todays_datetime).filter(Artist.id==artist_data.id).all()
  
  data = {
    "id": artist_data.id,
    "name": artist_data.name,
    "genres": artist_data.genres,
    "city": artist_data.city,
    "state": artist_data.state,
    "phone": artist_data.phone,
    "website": artist_data.website_link,
    "facebook_link": artist_data.facebook_link,
    "seeking_venue": artist_data.seeking_venue,
    "seeking_description": artist_data.seeking_description,
    "image_link": artist_data.image_link,
    "past_shows": [{
      "venue_id": show.venue.id,
      "venue_name": show.artist.name,
      "venue_image_link": shows.venue.image_link,
      "start_time": str(show.start_time)
    } for show in past_shows_data],
    "upcoming_shows": [{
      "venue_id": show.venue.id,
      "venue_name": show.artist.name,
      "venue_image_link": shows.venue.image_link,
      "start_time": str(show.start_time)
    } for show in upcoming_shows_data],
    "past_shows_count": len(past_shows_data),
    "upcoming_shows_count": len(upcoming_shows_data),
  }
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist_record = Artist.query.filter_by(id=artist_id).first()
  if artist_record:  
    form = VenueForm()
    genres_list = [genre.name for genre in artist_record.genres]
    artist_record = artist_record.__dict__
    artist_record['genres'] = genres_list
    artist_record = SimpleNamespace(**artist_record)
    form.__init__(obj=artist_record)
  else:
    flash('An error occurred. Artist not found')
    return render_template('pages/home.html')

  # TODO: populate form with fields from artist with ID <artist_id> ((Done))
  return render_template('forms/edit_artist.html', form=form, artist=artist_record)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes ((Done))

  # Retrieving data from form.(ImmutableMultiDict)
  form_data = request.form
  
  # Shallow copy the object to convert to MutableMultiDict
  mutable_form_data = form_data.copy()
  
  # Pop out the list of genres from the Dict
  genres = mutable_form_data.poplist('genres')
  
  # Retrive a list of the genre records corrosponding to genres items from genre table. (used list comprihension). 
  genres_records = [genre for genre in Genre.query.all() if genre.name in genres]

  # Checking the seeking_talent value
  if 'seeking_talent' in mutable_form_data:
    mutable_form_data['seeking_talent'] = True
  
  # Processing name and city fields for case-insensitivity
  mutable_form_data['name'].title()
  mutable_form_data['city'].title()

  #Retrive artist original record
  artist_record = Artist.query.filter_by(id = venue_id).first()
  #Update record with new data
  artist_record.__init__(**mutable_form_data)
  artist_record.genres = genres_records

  error = None
  artist_name = artist_record.name
  try:
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
    if not error:
      # on successful db insert, flash success ((Done))
      flash('Artist ' + artist_name + ' was successfully updated!')
    else:
  # TODO: on unsuccessful db insert, flash an error instead.((Done))
      flash('An error occurred. Artist ' + artist_name + ' could not be updated.')
    return render_template('pages/home.html')

  #return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue_record = Venue.query.filter_by(id=venue_id).first()
  if venue_record:  
    form = VenueForm()
    genres_list = [genre.name for genre in venue_record.genres]
    venue_record = venue_record.__dict__
    venue_record['genres'] = genres_list
    venue_record = SimpleNamespace(**venue_record)
    form.__init__(obj=venue_record)
  else:
    flash('An error occurred. Venue not found')
    return render_template('pages/home.html')
  # TODO: populate form with values from venue with ID <venue_id> ((Done))
  return render_template('forms/edit_venue.html', form=form, venue=venue_record)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing ((Done))
  # venue record with ID <venue_id> using the new attributes
  
  # Retrieving data from form.(ImmutableMultiDict)
  form_data = request.form
  
  # Shallow copy the object to convert to MutableMultiDict
  mutable_form_data = form_data.copy()
  
  # Pop out the list of genres from the Dict
  genres = mutable_form_data.poplist('genres')
  
  # Retrive a list of the genre records corrosponding to genres items from genre table. (used list comprihension). 
  genres_records = [genre for genre in Genre.query.all() if genre.name in genres]

  # Checking the seeking_talent value
  if 'seeking_talent' in mutable_form_data:
    mutable_form_data['seeking_talent'] = True
  
  # Processing name and city fields for case-insensitivity
  mutable_form_data['name'].title()
  mutable_form_data['city'].title()

  #Retrive venue original record
  venue_record = Venue.query.filter_by(id = venue_id).first()
  #Update record with new data
  venue_record.__init__(**mutable_form_data)
  venue_record.genres = genres_records

  error = None
  venue_name = venue_record.name
  try:
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
    if not error:
      # on successful db insert, flash success ((Done))
      flash('Venue ' + venue_name + ' was successfully updated!')
    else:
  # TODO: on unsuccessful db insert, flash an error instead.((Done))
      flash('An error occurred. Venue ' + venue_name + ' could not be updated.')
    return render_template('pages/home.html')
  
  #return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Artist record in the db, instead ((Done))
  # TODO: modify data to be the data object returned from db insertion ((Done))

  # Retrieving data from form.(ImmutableMultiDict)
  form_data = request.form
  
  # Shallow copy the object to convert to MutableMultiDict
  mutable_form_data = form_data.copy()
  
  
  # Pop out the list of genres from the Dict
  genres = mutable_form_data.poplist('genres')
  
  # Retrive a list of the genre records corrosponding to genres items from genre table. (used list comprihension). 
  genres_records = [genre for genre in Genre.query.all() if genre.name in genres]
  
  # Checking the seeking_talent value
  if 'seeking_venue' in mutable_form_data:
    mutable_form_data['seeking_venue'] = True
  
  # Processing name and city fields for consistancy
  mutable_form_data['name'].title()
  mutable_form_data['city'].title()

  # Create a new artist instance from Artist class by passing the dictionary ((Insted of using commneted line, use new_function get_or_create))
  #new_artist = Artist(**mutable_form_data)
  
  my_artist, flag = get_or_create(db.session,Artist,**mutable_form_data)

  my_artist_name = my_artist.name

  if flag:
    flash('An error occurred. Artist ' + my_artist_name + ' already listed!')
    return render_template('pages/home.html')
  
  else:
  # Adding and commiting to database
    error = None
    try:
      # Passing the genres_records to the my_artist object (through artist_themes association table)
      my_artist.genres = genres_records
      db.session.add(my_artist)
      db.session.commit()
    except:
      error = True
      db.session.rollback()
    finally:
      db.session.close()
      if not error:
        # on successful db insert, flash success ((Done))
        flash('Artist ' + my_artist_name + ' was successfully listed!')
      else:
      # TODO: on unsuccessful db insert, flash an error instead. ((Done))
        flash('An error occurred. Artist ' + my_artist_name + ' could not be listed.')

      return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue. ((Done))
  shows_data = db.session.query(Show).all()
  data=[{
    "venue_id": show.venue.id,
    "venue_name": show.venue.name,
    "artist_id": show.artist.id,
    "artist_name": show.artist.name,
    "artist_image_link": show.artist.image_link,
    "start_time": str(show.start_time)
  } for show in shows_data ]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead ((Done))

  # Retrieving data from form.(ImmutableMultiDict)
  form_data = request.form
  
  # Shallow copy the object to convert to MutableMultiDict
  mutable_form_data = form_data.copy()

  # Create a new show instance from Show class by passing the dictionary ((Insted of using commneted line, use new_function get_or_create))
  #new_show = Show(**mutable_form_data)
  try:
    my_show, flag = get_or_create(db.session,Show,**mutable_form_data)

    if flag:
      flash('An error occurred. Show already listed!')
      return render_template('pages/home.html')
  
    else:
    # Adding and commiting to database
      error = None
      try:
        db.session.commit()
      except:
        error = True
        db.session.rollback()
      finally:
        db.session.close()
        if not error:
          # on successful db insert, flash success ((Done))
          flash('Show was successfully listed!')
        else:
        # TODO: on unsuccessful db insert, flash an error instead. ((Done))
          flash('An error occurred. Show could not be listed.')

        return render_template('pages/home.html')
  except:
    db.session.rollback()
    db.session.close()
    flash('An error occurred. either the venue_id or artist_id dose not exit!')
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
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
