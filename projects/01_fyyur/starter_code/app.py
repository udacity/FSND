#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import sys
from datetime import datetime
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
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
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
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

  # Need a way to link shows/artists - might be many to many

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

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  showdate = db.Column(db.DateTime, nullable=False, default=datetime.now)
  # Foreign key reference to this show's venue
  venue_id = db.Column(
    db.Integer,
    db.ForeignKey('Venue.id'),
    nullable=False)
  artists = db.relationship(
    'Artist', secondary=artist_shows, backref=db.backref('shows', lazy=True)
  )
    # upcoming_shows calculated based on Date?
    # past_shows calculated based on Date?
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

def get_shows_by_date(venue):
  timeNow = datetime.now().total_seconds()
  showsByDate = ['pastShows', 'upcomingShows']
  for show in venue.shows:
    print(show.showdate)
    if show.showdate.total_seconds() >= timeNow:
      showsByDate['upcomingShows'].append({
        'artist_id': show.artists[0].id,
        'artist_name': show.artists[0].name,
        'artist_image_link': show.artists[0].image_link,
        'start_time': format_datetime(show.showdate)
      })
    else:
      showsByDate['pastShows'].append({
        'artist_id': show.artists[0].id,
        'artist_name': show.artists[0].name,
        'artist_image_link': show.artists[0].image_link,
        'start_time': format_datetime(show.showdate)
      })
  return showsByDate


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
  venuesErrors = False
  try:
    # select venues, order/filter by city
    venuesByArea = []
    existingAreas = []
    venues = Venue.query.all()
    
    for venue in venues:
      areaFound = False
      venueData = {
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": 0 # hardcoded for now
      }

      # Check existing areas
      areaKey = venue.city.lower() + "-" + venue.state.lower()
      if areaKey in existingAreas:
        areaFound = True

      if areaFound:
        # just add venue to existing area
        areaIndex = venuesByArea.index(areaKey) 
        areaVenue = venuesByArea[areaIndex]
        areaVenue["venues"].append(venueData)
      else:
        # Make new area entry for venues in this area
        existingAreas.append(areaKey)
        areaVenue = {
          "city": venue.city, 
          "state": venue.state,
          "venues": [venueData]
        }
        # Append venue data to area venue
        venuesByArea.append(areaVenue)
  except:
    venuesErrors = True
    
  return render_template('pages/venues.html', areas=venuesByArea)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  venueSearchTerm = request.form['search_term'].lower()
  searchTerm = "%{}%".format(venueSearchTerm)
  print(searchTerm)
  error = False
  venueSearchResults = []
  try:
    venues = Venue.query.filter(Venue.name.ilike(searchTerm)).all()
    for venue in venues:
      print(venue.id)
      venueData = {
        'id': venue.id,
        'name': venue.name,
        'num_upcoming_shows': 0 #hardcoded for now
      }
      venueSearchResults.append(venueData)
  except:
    error = True

  response={
    "count": len(venues),
    "data": venueSearchResults
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venueError = False
  venueData = {}
  try: 
    venue = Venue.query.get(venue_id)
    genre_list = venue.genres.split(",")
    showData = get_shows_by_date(venue)
    venueData = {
      "id": venue.id,
      "name": venue.name,
      "genres": genre_list,
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link,
      "past_shows": showData['pastShows'],
      "upcoming_shows": showData['upcomingShows'],
      "past_shows_count": len(showData['pastShows']),
      "upcoming_shows_count": len(showData['upcomingShows']),
    }
  except:
    venueError = True
  return render_template('pages/show_venue.html', venue=venueData)

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
  createError = False
  try:
    venueName = request.form['name']
    venueCity = request.form['city']
    venueState = request.form['state']
    venueAddr = request.form['address']
    venuePhone = request.form['phone']
    venueImg = request.form['image_link']
    venueWebsite = request.form['website']
    venueGenres = ','.join(request.form.getlist('genres'))
    print(venueGenres)
    venueFb = request.form['facebook_link']
    venueTalent = request.form['seeking_talent']
    print(venueTalent)
    seekingTalent = True
    venueTalentDescr = request.form['seeking_description']
    newVenue = Venue(
      name=venueName, 
      city=venueCity,
      state=venueState,
      address=venueAddr,
      phone=venuePhone,
      image_link=venueImg,
      facebook_link=venueFb,
      website=venueWebsite,
      genres=venueGenres,
      seeking_talent=seekingTalent)

    if venueTalent:
      newVenue.seeking_description = venueTalentDescr

    db.session.add(newVenue)
    db.session.commit()
  except:
    createError = True
    db.session.rollback()

  finally:
    db.session.close()

  if createError:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  else:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
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
  artistData = []
  error = False
  try:
    artists = Artist.query.order_by('id').all()

    for artist in artists:
      artistObj = {
        'id': artist.id,
        'name': artist.name
      }
      print(artistObj)
      artistData.append(artistObj)

  except:
    error = True

  return render_template('pages/artists.html', artists=artistData)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  artistSearchTerm = request.form['search_term'].lower()
  searchTerm = "%{}%".format(artistSearchTerm)
  print(searchTerm)
  error = False
  artistSearchResults = []
  try:
    artists = Artist.query.filter(Artist.name.ilike(searchTerm)).all()
    for artist in artists:
      print(artist.id)
      artistData = {
        'id': artist.id,
        'name': artist.name,
        'num_upcoming_shows': 0 #hardcoded for now
      }
      artistSearchResults.append(artistData)
  except:
    error = True

  response={
    "count": len(artists),
    "data": artistSearchResults
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  
  try:
    artist = Artist.query.get(artist_id)
    genre_list = artist.genres.split(",")
    artistData = {
    "id": artist.id,
    "name": artist.name,
    "genres": genre_list,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "image_link": artist.image_link,
    "past_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  except:
    error = True

  return render_template('pages/show_artist.html', artist=artistData)

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
  createError = False
  try:
    artistName = request.form['name']
    artistCity = request.form['city']
    artistState = request.form['state']
    artistPhone = request.form['phone']
    artistImg = request.form['image_link']
    artistWebsite = request.form['website']
    artistGenres = ','.join(request.form.getlist('genres'))
    artistFb = request.form['facebook_link']
    artistSeeking = False
    # seekingFormval = request.form['seeking_venue']
    # if seekingFormval == 'y':
    #   artistSeeking = True
    # print("Artist seeking venues?" + artistSeeking)
    newArtist = Artist(
      name=artistName, 
      city=artistCity,
      state=artistState,
      phone=artistPhone,
      genres=artistGenres,
      image_link=artistImg,
      facebook_link=artistFb,
      website=artistWebsite,
      seeking_venue=artistSeeking)

    db.session.add(newArtist)
    db.session.commit()
  except:
    createError = True
    print(sys.exc_info())
    db.session.rollback()

  finally:
    db.session.close()

  if createError:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  data = []
  try:
    shows = Show.query.order_by('id').all()
    for show in shows:
      artist = show.artists[0]
      venue = Venue.query.get(show.venue_id)
      showData = {
        "venue_id": venue.id,
        "venue_name": venue.name,
        "artist_id": artist.id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": "2019-05-21T21:30:00.000Z" #hardcoded for now
      }
      data.append(showData)

  except:
    error = True
    print(sys.exc_info())

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  createError = False
  try:
    venueId = request.form['venue_id']
    artistId = request.form['artist_id']
    startTime = request.form['start_time']
    artist = Artist.query.get(artistId)
    # TODO Checkexisting start times with same arttist/venue
    newShow = Show(
      venue_id=int(venueId))
    newShow.artists = [artist]

    db.session.add(newShow)
    db.session.commit()
  except:
    createError = True
    print(sys.exc_info())
    db.session.rollback()

  finally:
    db.session.close()

  if createError:
    flash('An error occurred. Show could not be listed.')
  else:
    flash('Show was successfully listed!')
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
