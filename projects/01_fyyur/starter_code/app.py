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
from datetime import datetime
from wtforms import ValidationError

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
    name = db.Column(db.String, nullable=False)
    genres = db.Column(db.ARRAY(db.String(120)), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    website_link = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)
    talent_wanted = db.Column(db.Boolean, nullable=False, default=False)
    talent_desc = db.Column(db.String())
    shows = db.relationship('Show', backref='venue', lazy=True)

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String(120)), nullable=False)
    website_link = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_desc = db.Column(db.String())
    shows = db.relationship('Show', backref="artist", lazy=True)

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    date_time = db.Column(db.DateTime, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)

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

# phone number validator 
def phone_validator(num):
    parsed = phonenumbers.parse(num, "US")
    if not phonenumbers.is_valid_number(parsed):
        raise ValidationError('Must be a valid US phone number.')

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
  # query for all venues in db
  venues = Venue.query.order_by('state').order_by('city').all()
  data = []
  cityStateInfo = {}
  prevCity = ''

  for venue in venues:
    currCity = venue.city

    # add next venue to current city's venues
    if prevCity == currCity:
      if cityStateInfo["city"] == venue.city and cityStateInfo["state"] == venue.state:
        newVenue = {
          "id": venue.id,
          "name": venue.name,
        }

        cityStateInfo["venues"].append(newVenue)

      # add new city/state combo to data list w/ venue
      # edge case where the city is the same, but states are different
      else: 
        if cityStateInfo != {}:
          data.append(cityStateInfo)

        cityStateInfo = {
          "city": venue.city,
          "state": venue.state,
          "venues": [{
            "id": venue.id,
            "name": venue.name,
          }]
        }
    else: # add new city/state combo to data list w/ venue
      if cityStateInfo != {}:
        data.append(cityStateInfo)

      cityStateInfo = {
        "city": venue.city,
        "state": venue.state,
        "venues": [{
          "id": venue.id,
          "name": venue.name,
        }]
      }
      
    prevCity = currCity # update current city

  data.append(cityStateInfo) # append last group of venues

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # query db for venues using search term
  # returns all matching results; case insensitive
  search_term = request.form.get('search_term')
  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()

  data = []

  for venue in venues:
    venueInfo = {
      "id": venue.id,
      "name": venue.name,
    }

    data.append(venueInfo)

  response = {
    "count": len(venues),
    "data": data
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # query respective venue and venue shows
  venue = Venue.query.filter_by(id = venue_id).first()
  shows = Show.query.filter_by(venue_id = venue_id).all()
  upcoming_shows = []
  past_shows = []

  # categorize past and upcoming shows based on date & time
  for show in shows:
    artist = Artist.query.filter_by(id = show.artist_id).first()

    if str(datetime.now()) > str(show.date_time):
      past_shows.append({
        "artist_id": show.artist_id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": str(show.date_time)
      })
    else:
      upcoming_shows.append({
        "artist_id": show.artist_id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": str(show.date_time)
      })

  print(venue.genres)
  data = {    
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.talent_wanted,
    "seeking_description": venue.talent_desc,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),}

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
    form = VenueForm()
    name = form.name.data
    city = form.city.data
    state = form.state.data
    address = form.address.data
    phone = form.phone.data
    genres = form.genres.data
    facebook_link = form.facebook_link.data
    website_link = form.website_link.data
    image_link = form.image_link.data
    talent_wanted = True if form.talent_wanted.data == 'Yes' else False
    talent_desc = form.talent_desc.data
    
    # add Venue to db
    venue = Venue(name=name, city=city, state=state, address=address, 
                  phone=phone, genres=genres, facebook_link=facebook_link,
                  website_link=website_link, image_link=image_link,
                  talent_wanted=talent_wanted, talent_desc=talent_desc)
    db.session.add(venue)
    db.session.commit()

    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    
  except ValidationError as error:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed. ' + str(error))
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
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
  # query all artists from db
  artists = Artist.query.order_by('name').all()
  data=[]

  for artist in artists:
    artistInfo = {
      "id": artist.id,
      "name": artist.name
    }

    # add each artist to the data to be displayed
    data.append(artistInfo)

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # query db for artists using search term
  # returns all matching results; case insensitive
  search_term = request.form.get('search_term')
  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()

  data = []

  for artist in artists:
    artistInfo = {
      "id": artist.id,
      "name": artist.name,
    }

    data.append(artistInfo)

  response = {
    "count": len(artists),
    "data": data
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # query respective artist and artist shows
  artist = Artist.query.filter_by(id = artist_id).first()
  shows = Show.query.filter_by(artist_id = artist_id).all()
  upcoming_shows = []
  past_shows = []

  # categorize past and upcoming shows based on date & time
  for show in shows:
    venue = Venue.query.filter_by(id = show.venue_id).first()

    if str(datetime.now()) > str(show.date_time):
      past_shows.append({
        "venue_id": show.venue_id,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": str(show.date_time)
      })
    else:
      upcoming_shows.append({
        "venue_id": show.venue_id,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": str(show.date_time)
      })

  print(artist.genres)

  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
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
  artist = Artist.query.filter_by(id=artist_id).first()
  form = ArtistForm()

  # must process first before form is loaded
  form.genres.default = artist.genres
  form.state.default = artist.state
  form.seeking_venue.default = 'Yes' if artist.seeking_venue == True else 'No'
  form.process()

  # populate rest of form
  form.name.data = artist.name
  form.city.data = artist.city
  form.phone.data = artist.phone
  form.facebook_link.data = artist.facebook_link
  form.website_link.data = artist.website_link
  form.image_link.data = artist.image_link
  form.seeking_desc.data = artist.seeking_desc

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  try:
    form = ArtistForm()
    artist = Artist.query.filter_by(id=artist_id).first()

    # update Artist
    artist.name = form.name.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.genres = form.genres.data
    artist.facebook_link = form.facebook_link.data,
    artist.website_link = form.website_link.data
    artist.image_link = form.image_link.data
    artist.seeking_venue = True if form.seeking_venue.data == 'Yes' else False
    artist.seeking_desc = form.seeking_desc.data

    db.session.commit()

    # on successful db update, flash success
    flash('Artist ' + request.form['name'] + ' was successfully updated!')

  except ValidationError as error:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated. ' + str(error))
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.filter_by(id=venue_id).first()
  form = VenueForm()

  # must process first before form is loaded
  form.genres.default = venue.genres
  form.state.default = venue.state
  form.talent_wanted.default = 'Yes' if venue.talent_wanted == True else 'No'
  form.process()

  # populate rest of form
  form.name.data = venue.name
  form.city.data = venue.city
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.facebook_link.data = venue.facebook_link
  form.website_link.data = venue.website_link
  form.image_link.data = venue.image_link
  form.talent_desc.data = venue.talent_desc

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and existing
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
  try:
    form = ArtistForm()
    name = form.name.data
    city = form.city.data
    state = form.state.data
    phone = form.phone.data
    genres = form.genres.data
    facebook_link = form.facebook_link.data
    website_link = form.website_link.data
    image_link = form.image_link.data
    seeking_venue = True if form.seeking_venue.data == 'Yes' else False
    seeking_desc = form.seeking_desc.data
    
    # add Artist to db
    artist = Artist(name=name, city=city, state=state, phone=phone, 
                  genres=genres, facebook_link=facebook_link,
                  website_link=website_link, image_link=image_link,
                  seeking_venue=seeking_venue, seeking_desc=seeking_desc)
    db.session.add(artist)
    db.session.commit()

    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    
  except ValidationError as error:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed. ' + str(error))
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    form = ShowForm()
    artist_id = form.artist_id.data
    venue_id = form.venue_id.data
    start_time = form.start_time.data

    show = Show(artist_id=artist_id, venue_id=venue_id, date_time=start_time)
    db.session.add(show)
    db.session.commit()

    # on successful db insert, flash success
    flash('Show was successfully listed!')

  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')

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
