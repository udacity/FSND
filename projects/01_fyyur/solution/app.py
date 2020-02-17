#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort, make_response
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime
import itertools
from flask_wtf.csrf import CSRFProtect
import logging

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)
logger = logging.getLogger(__name__)

# DONE: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    genres = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)

    def __init__(self, name, genres, city, state, address, phone, facebook_link):
      self.name = name
      self.genres = genres
      self.city = city
      self.state = state
      self.address = address
      self.phone = phone
      self.facebook_link = facebook_link

    def insert(self):
      db.session.add(self)
      db.session.commit()

    def update(self):
      db.session.commit()

    def delete(self):
      db.session.delete(self)
      db.session.commit()

    @property
    def past_shows(self):
      past_shows = list(filter(lambda show: show.start_time < datetime.now(), self.shows))
      return [
        {
          'artist_id': show.artist.id,
          'artist_name': show.artist.name,
          'artist_image_link': show.artist.image_link,
          'start_time': show.start_time.isoformat()
        } for show in past_shows]

    @property
    def upcoming_shows(self):
      upcoming_shows = list(filter(lambda show: show.start_time > datetime.now(), self.shows))
      return [
        {
          'artist_id': show.artist.id,
          'artist_name': show.artist.name,
          'artist_image_link': show.artist.image_link,
          'start_time': show.start_time.isoformat()
        } for show in upcoming_shows]

    @property
    def past_shows_count(self):
      return len(self.past_shows)

    @property
    def upcoming_shows_count(self):
      return len(self.past_shows)

    def format(self):
      return {
        'id': self.id,
        'name': self.name,
        'genres': self.genres.split(', '),
        'address': self.address,
        'city': self.city,
        'state': self.state,
        'phone': self.phone,
        'website': self.website,
        'facebook_link': self.facebook_link,
        'seeking_talent': self.seeking_talent,
        'seeking_description': self.seeking_description,
        'image_link': self.image_link,
        'past_shows': self.past_shows,
        'upcoming_shows': self.upcoming_shows,
        'past_shows_count': self.past_shows_count,
        'upcoming_shows_count': self.upcoming_shows_count
      }

    def __repr__(self):
      return f'<Venue name={self.name}, city={self.city}, state={self.state}, address={self.address}, past_shows_count={self.past_shows_count}, upcoming_shows_count={self.upcoming_shows_count}>'

    def __getitem__(self, key):
      return getattr(self, key)

    # DONE: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(200), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)

    @property
    def past_shows(self):
      past_shows = list(filter(lambda show: show.start_time < datetime.now(), self.shows))
      return [
        {
          "venue_id": show.venue.id,
          "venue_name": show.venue.name,
          "venue_image_link": show.venue.image_link,
          "start_time": show.start_time.isoformat()
        } for show in past_shows]

    @property
    def upcoming_shows(self):
      upcoming_shows = list(filter(lambda show: show.start_time > datetime.now(), self.shows))
      return [
        {
          "venue_id": show.venue.id,
          "venue_name": show.venue.name,
          "venue_image_link": show.venue.image_link,
          "start_time": show.start_time.isoformat()
        } for show in upcoming_shows]

    @property
    def past_shows_count(self):
      return len(self.past_shows)

    @property
    def upcoming_shows_count(self):
      return len(self.past_shows)

    def format(self):
      return {
        'id': self.id,
        'name': self.name,
        'genres': self.genres.split(', '),
        'city': self.city,
        'state': self.state,
        'phone': self.phone,
        'website': self.website,
        'facebook_link': self.facebook_link,
        'seeking_venue': self.seeking_venue,
        'seeking_description': self.seeking_description,
        'image_link': self.image_link,
        'past_shows': self.past_shows,
        'upcoming_shows': self.upcoming_shows,
        'past_shows_count': self.past_shows_count,
        'upcoming_shows_count': self.upcoming_shows_count
      }

    def __repr__(self):
      return f'<Artist name={self.name}, city={self.city}, state={self.state}, genres={self.genres}, past_shows_count={self.past_shows_count}, upcoming_shows_count={self.upcoming_shows_count}>'

    # DONE: implement any missing fields, as a database migration using Flask-Migrate

# DONE Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = 'show'

  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
  venue = db.relationship('Venue', backref='shows', lazy=True)
  artist = db.relationship('Artist', backref='shows', lazy=True)
  start_time = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

  def format(self):
    return {
      'venue_id': self.venue.id,
      'venue_name': self.venue.name,
      'artist_id': self.artist.id,
      'artist_name': self.artist.name,
      'artist_image_link': self.artist.image_link,
      'start_time': self.start_time.isoformat()
    }

  def __repr__(self):
    return f'<Show start_time={self.start_time}, venue={self.venue}, artist={self.artist}>'

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/', methods=['GET', 'DELETE'])
def index():
  return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # DONE: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  venues = Venue.query.all()
  
  keyfunc = lambda v: (v['city'], v['state'])
  sorted_venues = sorted(venues, key=keyfunc)
  grouped_venues = itertools.groupby(sorted_venues, key=keyfunc)

  data = [
    {
      'city': key[0],
      'state': key[1],
      'venues': list(data)
    }
    for key, data in grouped_venues]

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # DONE: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_term = request.form.get('search_term', '')

  venues_found = Venue.query.filter(Venue.name.match(f'%{search_term}%')).all()

  formatted_venues = [
    {
      'id': venue.id,
      'name': venue.name,
      'num_upcoming_shows': venue.upcoming_shows_count
    }
    for venue in venues_found]
  response = {'count': len(venues_found), 'data': list(formatted_venues)}

  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # DONE: replace with real venue data from the venues table, using venue_id

  venue = Venue.query.filter_by(id=venue_id).first()

  if venue is None:
    return abort(404)

  data = venue.format()

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # DONE: insert form data as a new Venue record in the db, instead
  # DONE: modify data to be the data object returned from db insertion
  form = VenueForm(request.form)

  error = None
  if not form.validate_on_submit():
    error = 'There''s errors within the form. Please review it firstly.'

  if error is None:
    venue_name = form.name.data
    exists = db.session.query(Venue.id).filter_by(name=venue_name).scalar() is not None

    if exists:
      error = f'Venue {venue_name} is already registered!'

  if error is None:    
    try:
      new_venue = Venue(
        name = venue_name,
        genres = ', '.join(form.genres.data),
        city = form.city.data,
        state = form.state.data,
        address = form.address.data,
        phone = form.phone.data,
        facebook_link = form.facebook_link.data
      )
      new_venue.insert()

      # on successful db insert, flash success
      flash(f'Venue {new_venue.name} was successfully created!', 'success')
      # DONE: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      return render_template('pages/home.html')
    except:
      error = f'An error occurred. Venue {form.name.data} could not be listed.'
      logger.exception(error, exc_info=True)
    
  if error:
    flash(error, 'danger')
    
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # DONE: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  venue = Venue.query.filter_by(id=venue_id).first()

  if venue is None:
    return abort(404)

  try:
    venue.delete()
    flash(f'Venue {venue.name} was successfully deleted!', 'success')
    
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return redirect(url_for('index'))
  except exc.IntegrityError:
    logger.exception(f'Error trying to delete venue {venue}', exc_info=True)
    flash(f'Venue {venue.name} can''t be deleted.', 'danger')

#  Artists
#  ----------------------------------------------------------------

@app.route('/artists')
def artists():
  # DONE: replace with real data returned from querying the database

  artists = Artist.query.order_by(Artist.name.asc()).all()
  data = [{ 'id': artist.id, 'name': artist.name } for artist in artists]
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')

  artists_found = Artist.query.filter(Artist.name.match(f'%{search_term}%')).all()

  formatted_artists = [{
    'id': artist.id,
    'name': artist.name,
    'num_upcoming_shows': artist.upcoming_shows_count
  }
  for artist in artists_found]
  response = {'count': len(artists_found), 'data': list(formatted_artists)}

  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # DONE: replace with real venue data from the venues table, using venue_id

  artist = Artist.query.filter_by(id=artist_id).first()

  if artist is None:
    return abort(404)

  data = artist.format()
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist_found = Artist.query.filter_by(id=artist_id).first()

  if artist_found is None:
    return abort(404)

  form = ArtistForm()

  artist = {
    'id': artist_found.id,
    'name': artist_found.name,
    'genres': artist_found.genres.split(', '),
    'city': artist_found.city,
    'state': artist_found.state,
    'phone': artist_found.phone,
    'website': artist_found.website,
    'facebook_link': artist_found.facebook_link,
    'seeking_venue': artist_found.seeking_venue,
    'seeking_description': artist_found.seeking_description,
    'image_link': artist_found.image_link,
  }
  # DONE: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

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
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

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

  # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # DONE: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  shows = Show.query.order_by(Show.start_time.asc()).all()
  data = [show.format() for show in shows]

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
  return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
  db.session.rollback()
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
