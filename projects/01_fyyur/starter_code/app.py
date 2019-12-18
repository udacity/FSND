#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import logging
from logging import Formatter, FileHandler
# from flask_wtf import Form
from flask_wtf import FlaskForm
from forms import *
import sys
import numpy as np
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# Added by me
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
    # "website": "https://www.themusicalhop.com",
    # "facebook_link": "https://www.facebook.com/TheMusicalHop",
    # "seeking_talent": True,
    # "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    # "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
        return (
          f"""<Venue ID: {self.id}, name: {self.name}, city: {self.city}, state: {self.state}, address: {self.address}, phone: {self.phone},' 
          'genres: {self.genres}, website: {self.website}, image_link: {self.image_link}, facebook_link: {self.facebook_link}, seeking_talent: {self.seeking_talent}'
          'seeking_description: {self.seeking_description}, shows: {self.shows}""")
    # artists = db.relationship('Artist', secondary=show, back_ref=db.backref('venues', lazy=True))
    # products = db.relationship('Product', secondary=order_items,
    #   backref=db.backref('orders', lazy=True))

    def serialize(self):
      return {
        'id': self.id,
        'name': self.name,
        'city': self.city,
        'state': self.state,
        'address': self.address,
        'genres': self.genres,
        'website': self.website,
        'phone': self.phone,
        'image_link': self.image_link,
        'facebook_link': self.facebook_link,
        'seeking_talent': self.seeking_talent,
        'seeking_description': self.seeking_description,
        'past_shows': self.past_shows,
        'upcoming_shows': self.future_shows,
        'past_shows_count': self.past_shows_count,
        'upcoming_shows_count': self.future_shows_count
      }

    @property
    def past_shows(self):
      now = datetime.now()
      # '%Y-%m-%dT%H:%M:%S.%fZ'
      past_shows = [show for show in self.shows if datetime.strptime(show.start_time, '%Y-%m-%d %H:%M:%S') < now]
      return past_shows

    @property
    def past_shows_count(self):
      return len(self.past_shows)

    @property
    def future_shows(self):
      now = datetime.now()
      # '%Y-%m-%dT%H:%M:%S.%fZ'
      future_shows = [show for show in self.shows if datetime.strptime(show.start_time, '%Y-%m-%d %H:%M:%S') > now]
      return future_shows

    @property
    def future_shows_count(self):
      return len(self.future_shows)

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
        return (
          f"""<Venue ID: {self.id}, name: {self.name}, city: {self.city}, state: {self.state}, phone: {self.phone},' 
          'genres: {self.genres}, website: {self.website}, image_link: {self.image_link}, facebook_link: {self.facebook_link}, seeking_venue: {self.seeking_venue}'
          'seeking_description: {self.seeking_description}, shows: {self.shows}""")

    def serialize(self):
      return {
        'id': self.id,
        'name': self.name,
        'city': self.city,
        'state': self.state,
        'phone': self.phone,
        'genres': self.genres,
        'website': self.website,
        'image_link': self.image_link,
        'facebook_link': self.facebook_link,
        'seeking_venue': self.seeking_venue,
        'seeking_description': self.seeking_description,
        'past_shows': self.past_shows,
        'upcoming_shows': self.future_shows,
        'past_shows_count': self.past_shows_count,
        'upcoming_shows_count': self.future_shows_count
      }
    
    @property
    def past_shows(self):
      now = datetime.now()
      # '%Y-%m-%dT%H:%M:%S.%fZ'
      past_shows = [show for show in self.shows if datetime.strptime(show.start_time, '%Y-%m-%d %H:%M:%S') < now]
      return past_shows

    @property
    def past_shows_count(self):
      return len(self.past_shows)

    @property
    def future_shows(self):
      now = datetime.now()
      future_shows = [show for show in self.shows if datetime.strptime(show.start_time, '%Y-%m-%d %H:%M:%S') > now]
      return future_shows

    @property
    def future_shows_count(self):
      return len(self.future_shows)

class Show(db.Model):
  __tablename__ = 'Show'
  # __table_args__ = (
  #   PrimaryKeyConstraint('venue_id', 'artist_id')
  # )
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False, primary_key=True)
  start_time = db.Column(db.String(), nullable=False)

  def serialize(self):
    return {
      'venue_id': self.venue_id,
      'artist_id': self.artist_id,
      'start_time': self.start_time
    }


# show = db.Table('show',
# db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id'), primary_key=True),
# db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id'), primary_key=True),
# db.Column('start_time', db.DateTime)
# )

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

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # Replaced with real venues data. num_shows should be aggregated based on number of upcoming shows per venue.
  unique_city_states = Venue.query.with_entities(Venue.city, Venue.state).distinct().all()
  print(f'Data = {unique_city_states}')
  data = []
  for ucs in unique_city_states:
    venues = Venue.query.filter_by(city=ucs[0], state=ucs[1]).all()
    data.append({'city': ucs[0], 'state': ucs[1], 'venues': venues})
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues(): 
  search_term = request.form['search_term']
  print(f'Search Term => {search_term}')
  
  search_results = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term))).all()
  # search_results = Venue.query.filter(Venue.name.like(search_term)).all()
  count = len(search_results)
  print(f'Search Result => {search_results}, count={count}')
  response={
    "count": count,
    "data": [result.serialize() for result in search_results]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))
  

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  print(f'Venue <before Serialization> => {venue}')
  return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  data = request.form
  venues = Venue.query.filter_by(name=data['name']).all()
  if (len(venues) > 0):
    flash(f"An error occurred. {request.form['name']} already exist")
    return render_template('pages/home.html')
  # genres=[data['genres']]
  try:
    venue = Venue(name=data['name'], city=data['city'], state=data['state'], address=data['address'], phone=data['phone'], genres=data.getlist('genres'), facebook_link=data['facebook_link'])
    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Venue ' + data['name'] + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    print(f'delete_venue :: session rollback due to an error.')
    print(sys.exc_info())
    db.session.rollback()
  finally:
    db.session.close()

  return jsonify({
    'Success': True
  })

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = []
  artists = Artist.query.all()
  for artist in artists:
    data.append({
      'id': artist.id,
      'name': artist.name
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form['search_term']
  search_results = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term))).all()
  count = len(search_results)
  print(f'Search Result => {search_results}, count={count}')
  data = []
  for result in search_results:
    data.append({
      'id': result.id,
      'name': result.name,
      'num_upcoming_shows': result.future_shows_count
    })
  response={
    "count": count,
    "data": data
  }
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # } 
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)
  return render_template('pages/show_artist.html', artist=artist.serialize())

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # artist={
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
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }

  artist = Artist.query.get(artist_id)
  form.name.data = artist.name
  form.genres.data = artist.genres
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.website.data = artist.website
  form.facebook_link.data = artist.facebook_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description
  form.image_link.data = artist.image_link
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  
  try:
    artist = Artist.query.get(artist_id)
    artist.name = request.form['name']
    artist.genres = request.form.getlist('genres')
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.website = request.form['website']
    artist.facebook_link = request.form['facebook_link']
    artist.seeking_venue = request.form['seeking_venue']
    artist.image_link = request.form['image_link']
    db.session.commit()
  except:
    print(f'Rolling back since some problems occured.')
    db.session.rollback()
  finally:
    print(f'Closing the session.')
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(artist_id)
  form.name.data = venue.name
  form.address.data = venue.address
  form.genres.data = venue.genres
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.website.data = venue.website
  form.facebook_link.data = venue.facebook_link
  form.seeking_venue.data = venue.seeking_venue
  form.seeking_description.data = venue.seeking_description
  form.image_link.data = venue.image_link
  
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  try:
    venue = Venue.query.get(venue_id)
    venue.name = request.form['name']
    venue.genres = request.form.getlist('genres')
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.phone = request.form['phone']
    venue.website = request.form['website']
    venue.facebook_link = request.form['facebook_link']
    venue.seeking_venue = request.form['seeking_venue']
    venue.image_link = request.form['image_link']
    db.session.commit()
  except:
    print(f'Rolling back since some problems occured.')
    db.session.rollback()
  finally:
    print(f'Closing the session.')
    db.session.close()
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
  # Insert form data as a new Venue record in the db, instead
  # modify data to be the data object returned from db insertion

  artists = Artist.query.filter_by(name=request.form['name']).all()
  if (len(artists) > 0):
    flash(f"An error occurred. {request.form['name']} already exist")
    return render_template('pages/home.html')

  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  phone = request.form['phone']
  genres = request.form.getlist('genres')
  facebook_link = request.form['facebook_link']
  print(f'name = {name}, city = {city}, state = {state}, phone = {phone}, genres = {genres}, facebook_link={facebook_link}')

  try:
    artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link)
    db.session.add(artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Artist ' + name + ' could not be listed.')
  finally:
    db.session.close()
  
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows = Show.query.all()
  data = []
  for show in shows:
    artist = Artist.query.get(show.artist_id)
    data.append({
      'venue_id': show.venue_id,
      'artist_id': show.artist_id,
      'start_time': show.start_time,
      'venue_name': Venue.query.get(show.venue_id).name,
      'artist_name': artist.name,
      'artist_image_link': artist.image_link
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  artist_id = request.form['artist_id']
  venue_id = request.form['venue_id']
  start_time = request.form['start_time']
  try:
    show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
    
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
  # on unsuccessful db insert, flash an error instead.
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
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
