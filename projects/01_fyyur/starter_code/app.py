#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

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
from flask_migrate import Migrate
import phonenumbers
from wtforms.validators import ValidationError

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
  __tablename__ = 'Venue'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(), nullable=False)
  city = db.Column(db.String(120), nullable=False)
  state = db.Column(db.String(120), nullable=False)
  address = db.Column(db.String(120), nullable=False)
  phone = db.Column(db.String(120), nullable=False)
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  genres = db.Column(db.ARRAY(db.String(120)), nullable=False)
  website = db.Column(db.String(120))
  seeking_talent = db.Column(db.Boolean, default=False)
  seeking_desc = db.Column(db.String())
  shows = db.relationship('Show', backref='venue', lazy=True)

  def __repr__(self):
    return f'<Venue {self.id} {self.name}>'

class Artist(db.Model):
  __tablename__ = 'Artist'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(), nullable=False)
  city = db.Column(db.String(120), nullable=False)
  state = db.Column(db.String(120), nullable=False)
  phone = db.Column(db.String(120), nullable=False)
  genres = db.Column(db.ARRAY(db.String(120)), nullable=False)
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  website = db.Column(db.String(120))
  seeking_venue = db.Column(db.Boolean, default=False)
  seeking_desc = db.Column(db.String())
  shows = db.relationship('Show', backref='artist', lazy=True)

  def __repr__(self):
    return f'<Artist {self.id} {self.name}>'

class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  start_time = db.Column(db.DateTime, nullable=False)

  def __repr__(self):
    return f'<Show {self.id} Venue {self.venue.id} Artist {self.artist.id}>'

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
# Validators.
#----------------------------------------------------------------------------#
def phone_validation(number):
  parsed_num = phonenumbers.parse(number, "US") #assuming US phone numbers
  if not phonenumbers.is_valid_number(parsed_num):
    raise ValidationError('Invalid phone number.')


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
  # list to store data from the Venues table
  data = [] 

  city_state = {}
  venues = []
  previous_state = ''
  previous_city = ''
  
  ordered_venues = Venue.query.order_by(Venue.state).order_by(Venue.city).all()

  for venue in ordered_venues:
    current_state = venue.state
    current_city = venue.city

    #add all venues that reside in the same city and state
    if current_city == previous_city and current_state == previous_state:
      print(current_state)
      print(current_city)
      add_venue = {
        "id": venue.id,
        "name": venue.name
      }
      venues.append(add_venue)
      print(venues)
      if not (city_state["city"] == current_city or city_state["state"] == current_state) and not (city_state == {}):
        data.append(city_state)

    #if the city and state is different than before, add a new city/state to the list
    else:
      venues = [] #reset venues dictionary when city and state changes
      add_venue = {
        "id": venue.id,
        "name": venue.name
      }
      city_state = {
        "city": current_city,
        "state": current_state,
        "venues": venues
      }
      venues.append(add_venue)
      data.append(city_state)
    previous_city = current_city
    previous_state = current_state

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
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
  venue = Venue.query.filter_by(id = venue_id).first()

  #get all the shows for the particular venue
  shows = Show.query.filter_by(venue_id = venue_id).order_by(Show.start_time).all()
  upcoming_shows = []
  past_shows = []

  #query the database to find upcoming and past shows for each venue
  for show in shows:
    if show.start_time > datetime.now():
      upcoming_shows.append({
        "artist_id": show.artist_id,
        "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
        "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
        "start_time": format_datetime(str(show.start_time))
      })
    else:
      past_shows.append({
        "artist_id": show.artist_id,
        "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
        "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
        "start_time": format_datetime(str(show.start_time))
      })

  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city, 
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_desc,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
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
  try:
    venue_form = VenueForm()

    #check if phone is valid before moving on; else error will throw
    phone_validation(venue_form.phone.data)

    venue = Venue(name = venue_form.name.data, city = venue_form.city.data, state = venue_form.state.data,
      address = venue_form.address.data, phone = venue_form.phone.data, genres = venue_form.genres.data, 
      facebook_link = venue_form.facebook_link.data, image_link = venue_form.image_link.data, 
      seeking_talent = venue_form.seeking_talent.data, seeking_desc = venue_form.seeking_desc.data,
      website = venue_form.website.data)

    db.session.add(venue)
    db.session.commit()

    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  except ValidationError as error:
    db.session.rollback()
    flash('An error occured listing Venue ' + request.form['name'] + ". " + str(error))
  except:
    db.session.rollback()
    flash('An error occured. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = []
  ordered_artists = Artist.query.order_by(Artist.name).all()

  for artist in ordered_artists:
    artist_to_add = {
      "id": artist.id,
      "name": artist.name
    }

    data.append(artist_to_add)

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
  #shows the artist page with the given artist_id
  artist = Artist.query.filter_by(id = artist_id).first()

  #get all the shows for the particular artist
  shows = Show.query.filter_by(artist_id = artist_id).order_by(Show.start_time).all()
  upcoming_shows = []
  past_shows = []

  #query the database to find upcoming and past shows for each artist
  for show in shows:
    if show.start_time > datetime.now():
      upcoming_shows.append({
        "venue_id": show.venue_id,
        "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
        "venue_image_link": Venue.query.filter_by(id=show.venue_id).first().image_link,
        "start_time": format_datetime(str(show.start_time))
      })
    else:
      past_shows.append({
        "venue_id": show.venue_id,
        "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
        "venue_image_link": Venue.query.filter_by(id=show.venue_id).first().image_link,
        "start_time": format_datetime(str(show.start_time))
      })

  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city, 
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_desc,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.filter_by(id=artist_id).first()

  #populate form with data from the artist
  form.genres.default = artist.genres
  form.state.default = artist.state
  form.process()

  form.name.data = artist.name
  form.city.data = artist.city
  form.phone.data = artist.phone
  form.website.data = artist.website
  form.facebook_link.data = artist.facebook_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_desc.data = artist.seeking_desc
  form.image_link.data = artist.image_link

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  #called upon submitting the edit artist listing form
  try:
    artist_form = ArtistForm()
    artist = Artist.query.filter_by(id=artist_id).first()

    #check if phone is valid before moving on; else error will throw
    phone_validation(artist_form.phone.data)

    #update artist in database
    artist.name = artist_form.name.data
    artist.city = artist_form.city.data
    artist.state = artist_form.state.data
    artist.phone = artist_form.phone.data
    artist.genres = artist_form.genres.data
    artist.website = artist_form.website.data
    artist.facebook_link = artist_form.facebook_link.data
    artist.seeking_venue = artist_form.seeking_venue.data
    artist.seeking_desc = artist_form.seeking_desc.data
    artist.image_link = artist_form.image_link.data

    db.session.commit()

    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully updated!')

  except ValidationError as error:
    db.session.rollback()
    flash('An error occured updating Artist ' + request.form['name'] + ". " + str(error))
  except:
    db.session.rollback()
    flash('An error occured. Artist ' + request.form['name'] + ' could not be updated.')
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
  try:
    artist_form = ArtistForm()

    #check if phone is valid before moving on; else error will throw
    phone_validation(artist_form.phone.data)

    artist = Artist(name = artist_form.name.data, city = artist_form.city.data, state = artist_form.state.data, phone = artist_form.phone.data, genres = artist_form.genres.data, 
      facebook_link = artist_form.facebook_link.data, image_link = artist_form.image_link.data, 
      seeking_venue = artist_form.seeking_venue.data, seeking_desc = artist_form.seeking_desc.data,
      website = artist_form.website.data)

    db.session.add(artist)
    db.session.commit()

    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  except ValidationError as error:
    db.session.rollback()
    flash('An error occured listing Artist ' + request.form['name'] + ". " + str(error))
  except:
    db.session.rollback()
    flash('An error occured. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  data = []

  #get all of the shows from the database
  shows = Show.query.order_by(Show.start_time).all()

  for show in shows:
    if show.start_time > datetime.now():
      data.append({
        "venue_id": show.venue_id,
        "venue_name": Venue.query.filter_by(id = show.venue_id).first().name,
        "artist_id": show.artist_id,
        "artist_name": Artist.query.filter_by(id= show.artist_id).first().name,
        "artist_image_link": Artist.query.filter_by(id = show.artist_id).first().image_link,
        "start_time": format_datetime(str(show.start_time))
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
  try:
    show_form = ShowForm()

    show = Show(artist_id = show_form.artist_id.data, venue_id = show_form.venue_id.data,
      start_time = show_form.start_time.data)

    db.session.add(show)
    db.session.commit()

    # on successful db insert, flash success
    flash('Show was successfully listed!')

  except:
    db.session.rollback()
    flash('An error occured. Show could not be listed.')
  finally:
    db.session.close()

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