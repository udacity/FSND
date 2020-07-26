#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import os
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from sqlalchemy import func
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:@localhost:5432/fyur'
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# TODO: connect to a local postgresql database - done

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres =db.Column(db.ARRAY(db.String()))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String())
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean())
    seeking_description = db.Column(db.String(400))
    shows = db.relationship('Shows', backref='venue', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

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
    seeking_venue = db.Column(db.Boolean())
    seeking_description = db.Column(db.String(400))
    shows = db.relationship('Shows', backref='artist', lazy=True)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Shows(db.Model):
  __tablename__ = 'Shows'

  id = db.Column(db.Integer, primary_key=True)
  date = db.Column(db.DateTime, nullable = False)
  venue_id = db.Column(db.Integer, db.ForeignKey(Venue.id), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey(Artist.id), nullable=False)
  

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

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
  # TODO: add num_shows

  locations = Venue.query.with_entities(func.count(Venue.id), Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
  data= []

  for location in locations:
    venueLocation = Venue.query.filter_by(city=location.city, state=location.state).all()
    venueInfo = []

    for venue in venueLocation:
      venueInfo.append({
        "id": venue.id,
        "name": venue.name,
      })
    data.append({
      "city": venue.city,
      "state": venue.state,
      "venues": venueInfo
    })

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: add number of appearances 
  search_term = '%{}'.format(request.form.get('search_term', ''))
  data = []


  search_result = Venue.query.filter(func.lower(Venue.name).contains(search_term.lower())).all()

  for result in search_result:
    data.append({
      "id": result.id,
      "name": result.name
    })
  
  response = ({
    "count": len(search_result),
    "data": data
  })

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data = []
  upcoming_shows = []
  past_shows = []

  venue = Venue.query.get(venue_id)

  if not venue:
    return render_template('pages/home.html')

  shows = Shows.query.filter(Shows.venue_id==venue_id).all()

  #TODO: make sure that with show data, we can get info here
  if not shows:
    return render_template('pages/home.html')

  # future_shows = db.session.query(Shows).join(Artist).filter_by(Shows.venue_id==venue_id, Shows.date > datetime.now()).all()

  # previous_shows = db.session.query(Shows).join(Artist).filter_by(Shows.venue_id==venue_id, Shows.date < datetime.now()).all()

  for show in shows:
    artist = Artist.query.filter_by(id=show.artist_id).first()
    if show.date > datetime.now():
      upcoming_shows.append({
        "artist_id": artist.id,
        "artist_name": artist.name,
        "artist_imagie_link": artist.artist_image_link,
        "start_time" : show.date

      })
    else:
      past_shows.append({
        "artist_id": artist.id,
        "artist_name": artist.name,
        "artist_imagie_link": artist.artist_image_link,
        "start_time" : show.date

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
    "seeking_description": venue.seeking_description,
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
  error = False
  try:
    name = request.form['name']
    genres = request.form.getlist('genres')
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    website = request.form['website']
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    seeking_talent = True if 'seeking_talent' in request.form else False
    seeking_description = request.form['seeking_description']

    venue = Venue(name=name, genres=genres, city=city, state=state, address=address, phone=phone, website=website, image_link=image_link, facebook_link=facebook_link, seeking_talent=seeking_talent, seeking_description=seeking_description)
    db.session.add(venue)
    db.session.commit()
        
  except():
      db.session.rollback()
      error = True
      print(sys.exc_info())
  finally:
      db.session.close()
  if error:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  else:
      flash('Venue ' + request.form['name'] + ' was successfully listed!')

# TODO: insert form data as a new Venue record in the db, instead
# TODO: modify data to be the data object returned from db insertion

# on successful db insert, flash success

# TODO: on unsuccessful db insert, flash an error instead.
# e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
# see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  error = False
  try:
      venue = Venue.query.get(venue_id)
      db.session.delete(venue)
      db.session.commit()
  except():
      db.session.rollback()
      error = True
  finally:
      db.session.close()
  if error:
      flash('An error occurred. Venue ' + {venue_id} + ' could not be listed.')
  else:
      flash('Venue ' + {venue_id} + ' was successfully deleted!')

  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = db.session.query(Artist).all()

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = '%{}'.format(request.form.get('search_term', ''))
  data = []

  search_result = Venue.query.filter(func.lower(Artist.name).contains(search_term.lower())).all()

  for result in search_result:
    num_upcoming_shows = len(db.session.query(Show).fliter_by(Show.artist_id ==result.id, Show.date > datetime.now()))
    data.append({
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": num_upcoming_shows
    })
  
  response = ({
    "count": len(search_result),
    "data": data
  })

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data = []
  upcoming_shows = []
  past_shows = []

  artist = Artist.query.get(artist_id)

  if not artist:
    return render_template('pages/home.html')

  shows = Shows.query.filter(Shows.artist_id==artist_id).all()

  #TODO: make sure that with show data, we can get info here
  if not shows:
    return render_template('pages/home.html')

  # future_shows = db.session.query(Shows).join(Artist).filter_by(Shows.venue_id==venue_id, Shows.date > datetime.now()).all()

  # previous_shows = db.session.query(Shows).join(Artist).filter_by(Shows.venue_id==venue_id, Shows.date < datetime.now()).all()

  for show in shows:
    venue = Venue.query.filter_by(id=show.venue_id).first()
    if show.date > datetime.now():
      upcoming_shows.append({
        "venue_id": venue.id,
        "venue_name": venue.name,
        "venue_image_link": venue.venue_image_link,
        "start_time" : show.date

      })
    else:
      past_shows.append({
        "venue_id": venue.id,
        "venue_name": venue.name,
        "venue_image_link": venue.venue_image_link,
        "start_time" : show.date

    })

  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
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
  
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  error = False
  artist = Artist.query.get(artist_id)
  try:
   
    artist.name: request.form['name']
    artist.genres: request.form.getlist('genres')
    artist.city: request.form['city']
    artist.state: request.form['state']
    artist.phone: request.form['phone']
    artist.website: request.form['website']
    artist.facebook_link: request.form['facebook_link']
    artist.seeking_venue: True if 'seeking_venue' in request.form else False
    artist.seeking_description: request.form['seeking_description']
    artist.image_link: request.form['image_link']
    
    db.session.add(artist)
    db.session.commit()
        
  except():
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist could not be update.')
  else:
    flash('Artist was successfully updated!')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  form.name.data = venue.name
  form.genres.data = venue.genres
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.website.data = venue.website
  form.facebook_link.data = venue.facebook_link
  form.seeking_artist.data = venue.seeking_artist
  form.seeking_description.data = venue.seeking_description
  form.image_link.data = venue.image_link
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False
  artist = Artist.query.get(artist_id)
  try:
   
    venue.name: request.form['name']
    venue.genres: request.form.getlist('genres')
    venue.city: request.form['city']
    venue.state: request.form['state']
    venue.address: request.form['address']
    venue.phone: request.form['phone']
    venue.website: request.form['website']
    venue.facebook_link: request.form['facebook_link']
    venue.seeking_artit: True if 'seeking_artist' in request.form else False
    venue.seeking_description: request.form['seeking_description']
    venue.image_link: request.form['image_link']
    
    db.session.add(venue)
    db.session.commit()
        
  except():
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue could not be updated.')
  else:
    flash('Venue was successfully updated!')


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
  error = False
  try:
    name = request.form['name']
    genres = request.form.getlist('genres')
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    website = request.form['website']
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    seeking_venue = True if 'seeking_venue' in request.form else False
    seeking_description = request.form['seeking_description']

    artist = Artist(name=name, genres=genres, city=city, state=state, address=address, phone=phone, website=website, image_link=image_link, facebook_link=facebook_link, seeking_venue=seeking_venue, seeking_description=seeking_description)
    db.session.add(artist)
    db.session.commit()
        
  except():
      db.session.rollback()
      error = True
      print(sys.exc_info())
  finally:
      db.session.close()
  if error:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  else:
      flash('Artist ' + request.form['name'] + ' was successfully listed!')


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
